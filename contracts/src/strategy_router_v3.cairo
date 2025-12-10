use starknet::ContractAddress;

#[starknet::interface]
pub trait IStrategyRouterV3<TContractState> {
    // Allocation management
    fn update_allocation(
        ref self: TContractState,
        jediswap_pct: felt252,
        ekubo_pct: felt252
    );
    fn get_allocation(self: @TContractState) -> (felt252, felt252);
    
    // User deposits and withdrawals (SEPARATE from protocol integration)
    fn deposit(ref self: TContractState, amount: u256);
    fn withdraw(ref self: TContractState, amount: u256) -> u256;
    fn get_user_balance(self: @TContractState, user: ContractAddress) -> u256;
    
    // Protocol deployment (SEPARATE action - called after deposit)
    fn deploy_to_protocols(ref self: TContractState);
    
    // Individual protocol testing (for testing before full integration)
    fn approve_token_for_testing(ref self: TContractState, token: ContractAddress, spender: ContractAddress, amount: u256);
    fn test_jediswap_only(ref self: TContractState, amount: u256);
    fn test_ekubo_only(ref self: TContractState, amount: u256);
    
    // Yield and rebalancing
    fn accrue_yields(ref self: TContractState) -> u256;
    fn accrue_jediswap_yields(ref self: TContractState) -> u256;
    fn accrue_ekubo_yields(ref self: TContractState) -> u256;
    fn rebalance(ref self: TContractState);
    
    // Slippage protection
    fn update_slippage_tolerance(ref self: TContractState, swap_slippage_bps: u256, liquidity_slippage_bps: u256);
    fn get_slippage_tolerance(self: @TContractState) -> (u256, u256);
    
    // Protocol info
    fn get_protocol_addresses(self: @TContractState) -> (ContractAddress, ContractAddress);
    fn get_total_value_locked(self: @TContractState) -> u256;
    
    // Position tracking
    fn get_jediswap_position(self: @TContractState, index: u256) -> u256;
    fn get_ekubo_position(self: @TContractState, index: u256) -> u64;
    fn get_jediswap_position_count(self: @TContractState) -> u256;
    fn get_ekubo_position_count(self: @TContractState) -> u256;
}

#[starknet::contract]
mod StrategyRouterV3 {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address, get_block_timestamp
    };
    use starknet::storage::{
        StoragePointerWriteAccess, 
        StoragePointerReadAccess, 
        Map,
        StoragePathEntry
    };
    use super::super::interfaces::erc20::{IERC20Dispatcher, IERC20DispatcherTrait};
    // Protocol integration interfaces
    use super::super::interfaces::jediswap::{
        IJediSwapV2SwapRouterDispatcher,
        IJediSwapV2SwapRouterDispatcherTrait,
        IJediSwapV2NFTPositionManagerDispatcher, 
        IJediSwapV2NFTPositionManagerDispatcherTrait,
        ExactInputSingleParams,
        MintParams,
        I32, // Custom i32 struct for ticks
        CollectParams // For fee collection
    };
    use super::super::interfaces::ekubo::{
        IEkuboCoreDispatcher,
        IEkuboCoreDispatcherTrait,
        IEkuboPositionsDispatcher,
        IEkuboPositionsDispatcherTrait,
        PoolKey,
        Bounds,
        i129
    };
    use core::array::{Span, ArrayTrait};
    
    #[storage]
    struct Storage {
        // Allocation percentages (basis points, 10000 = 100%)
        jediswap_allocation: u256,
        ekubo_allocation: u256,
        
        // Protocol addresses
        jediswap_router: ContractAddress,  // Swap Router (for swaps)
        jediswap_nft_manager: ContractAddress,  // NFT Position Manager (for liquidity)
        ekubo_core: ContractAddress,  // Core (for direct operations)
        ekubo_positions: ContractAddress,  // Positions (for adding liquidity - THIS IS WHAT WE NEED!)
        
        // Position tracking - store actual NFT position IDs
        jediswap_position_count: u256,  // Total number of positions
        jediswap_position_ids: Map<u256, u256>,  // position_index -> token_id (NFT ID)
        ekubo_position_count: u256,  // Total number of positions
        ekubo_position_ids: Map<u256, u64>,  // position_index -> token_id (position ID)
        
        // Ekubo position metadata (needed for fee collection) - flattened structs
        ekubo_position_token0: Map<u256, ContractAddress>,  // position_index -> token0
        ekubo_position_token1: Map<u256, ContractAddress>,  // position_index -> token1
        ekubo_position_fee: Map<u256, u128>,  // position_index -> fee
        ekubo_position_tick_spacing: Map<u256, u128>,  // position_index -> tick_spacing
        ekubo_position_extension: Map<u256, ContractAddress>,  // position_index -> extension
        ekubo_position_salt: Map<u256, felt252>,  // position_index -> salt (token_id from Positions)
        ekubo_position_tick_lower_mag: Map<u256, u128>,  // position_index -> tick_lower magnitude
        ekubo_position_tick_lower_sign: Map<u256, bool>,  // position_index -> tick_lower sign
        ekubo_position_tick_upper_mag: Map<u256, u128>,  // position_index -> tick_upper magnitude
        ekubo_position_tick_upper_sign: Map<u256, bool>,  // position_index -> tick_upper sign
        
        // Total deposits (simplified - not tracking per-user for now)
        total_deposits: u256,
        
        // Pending deposits (funds waiting to be deployed to protocols)
        pending_deposits: u256,
        
        // Slippage protection (basis points, 10000 = 100%)
        // swap_slippage_bps: 100 = 1% slippage tolerance for swaps
        // liquidity_slippage_bps: 50 = 0.5% slippage tolerance for liquidity provision
        swap_slippage_bps: u256,  // Slippage tolerance for swaps (default: 100 = 1%)
        liquidity_slippage_bps: u256,  // Slippage tolerance for liquidity (default: 50 = 0.5%)
        
        // Owner address
        owner: ContractAddress,
        
        // Ekubo operation state (for lock/callback pattern)
        ekubo_pending_token0: ContractAddress,
        ekubo_pending_token1: ContractAddress,
        ekubo_pending_amount0: u256,
        ekubo_pending_amount1: u256,
        ekubo_pending_fee: u128,
        
        // Ekubo fee collection state (for lock/callback pattern) - flattened structs
        ekubo_collecting_fees: bool,  // Flag to indicate we're collecting fees
        ekubo_collect_position_index: u256,  // Which position we're collecting from
        ekubo_collect_token0: ContractAddress,  // Pool key token0
        ekubo_collect_token1: ContractAddress,  // Pool key token1
        ekubo_collect_fee: u128,  // Pool key fee
        ekubo_collect_tick_spacing: u128,  // Pool key tick_spacing
        ekubo_collect_extension: ContractAddress,  // Pool key extension
        ekubo_collect_salt: felt252,  // Salt (token_id) for fee collection
        ekubo_collect_tick_lower_mag: u128,  // Bounds tick_lower magnitude
        ekubo_collect_tick_lower_sign: bool,  // Bounds tick_lower sign
        ekubo_collect_tick_upper_mag: u128,  // Bounds tick_upper magnitude
        ekubo_collect_tick_upper_sign: bool,  // Bounds tick_upper sign
        
        // Primary deposit token (ETH - users deposit ETH, we swap half to STRK for pools)
        asset_token: ContractAddress,  // ETH address
        
        // Governance
        owner: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        
        // Performance tracking
        last_decision_id: felt252,  // Links to RiskEngine decision
        jediswap_position_value: u256,
        ekubo_position_value: u256,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        AllocationUpdated: AllocationUpdated,
        Deposit: Deposit,
        Withdrawal: Withdrawal,
        ProtocolsDeployed: ProtocolsDeployed,
        YieldsAccrued: YieldsAccrued,
        Rebalanced: Rebalanced,
        PerformanceLinked: PerformanceLinked,
    }
    
    #[derive(Drop, starknet::Event)]
    struct AllocationUpdated {
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        timestamp: u64,
        decision_id: felt252,  // Links to RiskEngine decision
    }
    
    #[derive(Drop, starknet::Event)]
    struct PerformanceLinked {
        jediswap_value: u256,
        ekubo_value: u256,
        timestamp: u64,
        decision_id: felt252,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Deposit {
        user: ContractAddress,
        amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Withdrawal {
        user: ContractAddress,
        amount: u256,
        yield_amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct ProtocolsDeployed {
        jediswap_amount: u256,
        ekubo_amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct YieldsAccrued {
        total_yield: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Rebalanced {
        old_jediswap: felt252,
        old_ekubo: felt252,
        new_jediswap: felt252,
        new_ekubo: felt252,
        timestamp: u64,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        jediswap_router: ContractAddress,
        jediswap_nft_manager: ContractAddress,
        ekubo_core: ContractAddress,
        ekubo_positions: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        asset_token: ContractAddress,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
    ) {
        self.owner.write(owner);
        self.jediswap_router.write(jediswap_router);
        self.jediswap_nft_manager.write(jediswap_nft_manager);
        self.ekubo_core.write(ekubo_core);
        self.ekubo_positions.write(ekubo_positions);
        self.risk_engine.write(risk_engine);
        self.dao_manager.write(dao_manager);
        self.asset_token.write(asset_token);
        self.jediswap_allocation.write(jediswap_pct.into());
        self.ekubo_allocation.write(ekubo_pct.into());
        self.total_deposits.write(0);
        // Initialize slippage tolerance (default: 1% for swaps, 0.5% for liquidity)
        self.swap_slippage_bps.write(100);  // 1% = 100 basis points
        self.liquidity_slippage_bps.write(50);  // 0.5% = 50 basis points
        self.pending_deposits.write(0);
        self.jediswap_position_count.write(0);
        self.ekubo_position_count.write(0);
        
        // Initialize Ekubo pending operation state
        self.ekubo_pending_amount0.write(0);
        self.ekubo_pending_amount1.write(0);
    }
    
    #[external(v0)]
    fn update_allocation(
        ref self: ContractState,
        jediswap_pct: felt252,
        ekubo_pct: felt252
    ) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        let risk_engine = self.risk_engine.read();
        
        assert(caller == owner || caller == risk_engine, 'Unauthorized');
        assert((jediswap_pct + ekubo_pct) == 10000, 'Allocation must sum to 100%');
        
        let old_jedi = self.jediswap_allocation.read();
        let old_ekubo = self.ekubo_allocation.read();
        
        self.jediswap_allocation.write(jediswap_pct.into());
        self.ekubo_allocation.write(ekubo_pct.into());
        
        self.emit(Rebalanced {
            old_jediswap: old_jedi.try_into().unwrap(),
            old_ekubo: old_ekubo.try_into().unwrap(),
            new_jediswap: jediswap_pct,
            new_ekubo: ekubo_pct,
            timestamp: get_block_timestamp(),
        });
        
        self.emit(AllocationUpdated {
            jediswap_pct,
            ekubo_pct,
            timestamp: get_block_timestamp(),
            decision_id: 0,  // TODO: Link to RiskEngine decision
        });
    }
        
    #[external(v0)]
    fn get_allocation(self: @ContractState) -> (felt252, felt252) {
        let jedi: felt252 = self.jediswap_allocation.read().try_into().unwrap();
        let ekubo: felt252 = self.ekubo_allocation.read().try_into().unwrap();
        (jedi, ekubo)
    }
    
    // ============================================
    // DEPOSIT FUNCTION - SIMPLE, NO PROTOCOL INTEGRATION
    // ============================================
    // This function ONLY accepts funds and stores them.
    // Protocol deployment happens separately via deploy_to_protocols()
    #[external(v0)]
    fn deposit(ref self: ContractState, amount: u256) {
        let caller = get_caller_address();
        let contract_addr = get_contract_address();
        let asset_token = self.asset_token.read();  // ETH address (primary deposit token)
        
        // Transfer tokens from user to this contract
        let token = IERC20Dispatcher { contract_address: asset_token };
        let success = token.transfer_from(caller, contract_addr, amount);
        assert(success, 'Transfer failed');
        
        // Update total deposits
        let total = self.total_deposits.read();
        self.total_deposits.write(total + amount);
        
        // Track pending deposits (funds waiting to be deployed)
        let pending = self.pending_deposits.read();
        self.pending_deposits.write(pending + amount);
        
        self.emit(Deposit {
            user: caller,
            amount,
            timestamp: get_block_timestamp(),
        });
    }
    
    // ============================================
    // PROTOCOL DEPLOYMENT - SEPARATE ACTION
    // ============================================
    // This function deploys pending deposits to protocols.
    // Can be called by owner, risk_engine, or automated backend.
    #[external(v0)]
    fn deploy_to_protocols(ref self: ContractState) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        let risk_engine = self.risk_engine.read();
        
        // Only owner or risk_engine can deploy (or make it public if you want)
        // For now, allowing owner/risk_engine only
        assert(caller == owner || caller == risk_engine, 'Unauthorized');
        
        let pending = self.pending_deposits.read();
        assert(pending > 0, 'No pending deposits');
        
        // Reset pending deposits (we're about to deploy them)
        self.pending_deposits.write(0);
        
        // Get current allocation
        let jediswap_pct = self.jediswap_allocation.read();
        let ekubo_pct = self.ekubo_allocation.read();
        
        // Calculate amounts for each protocol
        let jediswap_amount = (pending * jediswap_pct) / 10000;
        let ekubo_amount = (pending * ekubo_pct) / 10000;
        
        let contract_addr = get_contract_address();
        let asset_token = self.asset_token.read();
        
        // STRK token address (Sepolia) - convert felt252 to ContractAddress
        let strk_token_felt: felt252 = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d;
        let strk_token: ContractAddress = strk_token_felt.try_into().unwrap();
        
        // ETH token address (Sepolia) - needed for STRK/ETH pairs
        let eth_token_felt: felt252 = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7;
        let eth_token: ContractAddress = eth_token_felt.try_into().unwrap();
        let jediswap_router = self.jediswap_router.read();
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        
        // Deploy to JediSwap via NFT Position Manager
        // Step 1: Swap half STRK to ETH (we need both tokens for liquidity)
        if jediswap_amount > 0 {
            let strk_token_erc20 = IERC20Dispatcher { contract_address: strk_token };
            let eth_token_erc20 = IERC20Dispatcher { contract_address: eth_token };
            
            // Swap half STRK to ETH
            let swap_amount = jediswap_amount / 2;
            let remaining_strk = jediswap_amount - swap_amount;
            
            // Approve router for swap
            strk_token_erc20.approve(jediswap_router, swap_amount);
            
            // Perform swap: STRK → ETH (using V2 router)
            let router_v2 = IJediSwapV2SwapRouterDispatcher { contract_address: jediswap_router };
            let deadline = get_block_timestamp() + 1800; // 30 minutes from now
            
            // Note: token0 must be < token1 (sorted by address)
            let (token_in, token_out) = if strk_token < eth_token {
                (strk_token, eth_token)
            } else {
                (eth_token, strk_token)
            };
            
            // Calculate minimum output with slippage protection
            // We'll estimate output as input (1:1 for now, actual would use oracle/quote)
            // In production, you'd get a quote first, then apply slippage
            let swap_slippage_bps = self.swap_slippage_bps.read();
            // For now, we'll use a conservative estimate: assume we get at least 95% of input value
            // In production, use a quote from the router first
            let estimated_output = swap_amount * 95 / 100; // Conservative 95% estimate
            let slippage_amount = estimated_output * swap_slippage_bps / 10000;
            let amount_out_minimum = if estimated_output > slippage_amount {
                estimated_output - slippage_amount
            } else {
                0
            };
            
            // Create swap params
            let swap_params = ExactInputSingleParams {
                token_in: strk_token,
                token_out: eth_token,
                fee: 10000, // 1% fee tier
                recipient: contract_addr,
                deadline: deadline,
                amount_in: swap_amount,
                amount_out_minimum: amount_out_minimum, // Slippage protection
                sqrt_price_limit_x96: 0, // No price limit
            };
            
            let eth_received = router_v2.exact_input_single(swap_params);
            
            // Step 2: Approve NFT Position Manager for both tokens
            strk_token_erc20.approve(jediswap_nft_manager, remaining_strk);
            eth_token_erc20.approve(jediswap_nft_manager, eth_received);
            
            // Step 3: Add liquidity via NFT Position Manager
            // Note: token0 must be < token1 (sorted by address)
            let (token0, token1, amount0, amount1) = if strk_token < eth_token {
                (strk_token, eth_token, remaining_strk, eth_received)
            } else {
                (eth_token, strk_token, eth_received, remaining_strk)
            };
            
            let deadline = get_block_timestamp() + 1800; // 30 minutes from now
            let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
            
            // Convert ticks to I32 struct (mag: u32, sign: bool)
            // Full range: ticks must be aligned to tick spacing (200 for 1% fee tier)
            // -887200 and 887200 are multiples of 200 (tick spacing)
            let tick_lower_mag: u32 = 887200; // Magnitude (aligned to tick spacing 200)
            let tick_lower_sign: bool = true; // Negative
            let tick_lower_i32 = I32 { mag: tick_lower_mag, sign: tick_lower_sign };
            
            let tick_upper_mag: u32 = 887200; // Magnitude (aligned to tick spacing 200)
            let tick_upper_sign: bool = false; // Positive
            let tick_upper_i32 = I32 { mag: tick_upper_mag, sign: tick_upper_sign };
            
            // Calculate minimum amounts with slippage protection
            let liquidity_slippage_bps = self.liquidity_slippage_bps.read();
            let slippage_amount0 = amount0 * liquidity_slippage_bps / 10000;
            let slippage_amount1 = amount1 * liquidity_slippage_bps / 10000;
            let amount0_min = if amount0 > slippage_amount0 {
                amount0 - slippage_amount0
            } else {
                0
            };
            let amount1_min = if amount1 > slippage_amount1 {
                amount1 - slippage_amount1
            } else {
                0
            };
            
            let mint_params = MintParams {
                token0: token0,
                token1: token1,
                fee: 10000, // 1% fee tier (STRK/ETH pools exist at 0.05% and 1% on Sepolia)
                tick_lower: tick_lower_i32,
                tick_upper: tick_upper_i32,
                amount0_desired: amount0,
                amount1_desired: amount1,
                amount0_min: amount0_min, // Slippage protection
                amount1_min: amount1_min, // Slippage protection
                recipient: contract_addr,
                deadline: deadline,
            };
            let (token_id, _liquidity, _amount0, _amount1) = nft_manager.mint(mint_params);
            
            // Store position NFT ID
            let count = self.jediswap_position_count.read();
            self.jediswap_position_ids.entry(count).write(token_id);
            self.jediswap_position_count.write(count + 1);
        }
        
        // Deploy to Ekubo using Positions contract
        // NOTE: Router swap is failing, so we'll add liquidity with STRK only
        // Ekubo Positions will handle the ratio based on current pool price
        if ekubo_amount > 0 {
            let strk_token_erc20 = IERC20Dispatcher { contract_address: strk_token };
            let eth_token_erc20 = IERC20Dispatcher { contract_address: eth_token };
            
            // Approve Ekubo Positions contract for STRK (full amount)
            // Positions contract handles Core's lock pattern internally!
            let ekubo_positions = self.ekubo_positions.read();
            strk_token_erc20.approve(ekubo_positions, ekubo_amount);
            // Approve 0 ETH for now - positions might swap internally
            eth_token_erc20.approve(ekubo_positions, 0);
            
            // Create PoolKey for STRK/ETH pair
            // Note: token0 must be < token1 (sorted by address)
            let (token0, token1) = if strk_token < eth_token {
                (strk_token, eth_token)
            } else {
                (eth_token, strk_token)
            };
            
            let pool_key = PoolKey {
                token0: token0,
                token1: token1,
                fee: 10000, // 1% fee tier (STRK/ETH pools exist at 0.05% and 1% on Sepolia)
                tick_spacing: 60, // Standard tick spacing
                extension: 0.try_into().unwrap(), // No extension
            };
            
            // Create Bounds for full range liquidity
            // Full range: lower = -887280, upper = 887280 (rounded to tick_spacing 60)
            let tick_lower_mag: u128 = 887280;
            let tick_upper_mag: u128 = 887280;
            let bounds = Bounds {
                lower: i129 { mag: tick_lower_mag, sign: true },  // Negative
                upper: i129 { mag: tick_upper_mag, sign: false },  // Positive
            };
            
            // Call mint_and_deposit on Positions contract
            // This handles Core's lock pattern internally - no need for locked() callback!
            let positions = IEkuboPositionsDispatcher { contract_address: ekubo_positions };
            let min_liquidity = 0_u128; // No minimum for now
            let (token_id, _liquidity) = positions.mint_and_deposit(pool_key, bounds, min_liquidity);
            
            // Store position ID and metadata (needed for fee collection) - flattened
            // The token_id from Positions contract is used as the salt for collect_fees()
            let count = self.ekubo_position_count.read();
            self.ekubo_position_ids.entry(count).write(token_id);
            self.ekubo_position_token0.entry(count).write(pool_key.token0);
            self.ekubo_position_token1.entry(count).write(pool_key.token1);
            self.ekubo_position_fee.entry(count).write(pool_key.fee);
            self.ekubo_position_tick_spacing.entry(count).write(pool_key.tick_spacing);
            self.ekubo_position_extension.entry(count).write(pool_key.extension);
            // Convert token_id (u64) to felt252 for salt
            let salt: felt252 = token_id.into();
            self.ekubo_position_salt.entry(count).write(salt);
            self.ekubo_position_tick_lower_mag.entry(count).write(bounds.lower.mag);
            self.ekubo_position_tick_lower_sign.entry(count).write(bounds.lower.sign);
            self.ekubo_position_tick_upper_mag.entry(count).write(bounds.upper.mag);
            self.ekubo_position_tick_upper_sign.entry(count).write(bounds.upper.sign);
            self.ekubo_position_count.write(count + 1);
        }
        
        self.emit(ProtocolsDeployed {
            jediswap_amount,
            ekubo_amount,
            timestamp: get_block_timestamp(),
        });
    }
    
    #[external(v0)]
    fn withdraw(ref self: ContractState, amount: u256) -> u256 {
        let caller = get_caller_address();
        let total = self.total_deposits.read();
        
        assert(total >= amount, 'Insufficient balance');
        
        // TODO: Withdraw from protocols proportionally
        // This would call protocol withdraw functions
        
        // For now, simple withdrawal without yields
        let asset_token = self.asset_token.read();
        let token = IERC20Dispatcher { contract_address: asset_token };
        let success = token.transfer(caller, amount);
        assert(success, 'Transfer failed');
        
        // Update total deposits
        self.total_deposits.write(total - amount);
        
        self.emit(Withdrawal {
            user: caller,
            amount,
            yield_amount: 0,
            timestamp: get_block_timestamp(),
        });
        
        amount
    }
    
    #[external(v0)]
    fn get_user_balance(self: @ContractState, user: ContractAddress) -> u256 {
        // Simplified: returns total deposits (not tracking per-user yet)
        // TODO: Implement per-user tracking
        self.total_deposits.read()
    }
    
    // Internal function to collect fees from JediSwap positions
    fn collect_jediswap_fees(ref self: ContractState) -> (u256, u256) {
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
        let position_count = self.jediswap_position_count.read();
        let mut total_fees_0 = 0_u256;
        let mut total_fees_1 = 0_u256;
        let contract_addr = get_contract_address();
        
        // Iterate through all positions and collect fees
        let mut i = 0_u256;
        loop {
            if i >= position_count {
                break;
            }
            
            let token_id = self.jediswap_position_ids.entry(i).read();
            
            // Collect fees from this position
            // Using max amounts to collect all available fees
            let max_amount = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff_u256;
            let collect_params = CollectParams {
                token_id,
                recipient: contract_addr,
                amount0_max: max_amount,
                amount1_max: max_amount,
            };
            
            let (amount0, amount1) = nft_manager.collect(collect_params);
            total_fees_0 += amount0;
            total_fees_1 += amount1;
            
            i += 1;
        };
        
        (total_fees_0, total_fees_1)
    }
    
    // Internal function to collect fees from Ekubo positions
    // Note: This function initiates fee collection by calling Core.lock()
    // The actual withdrawal happens in the locked() callback
    fn collect_ekubo_fees(ref self: ContractState) -> (u256, u256) {
        let ekubo_core = self.ekubo_core.read();
        let position_count = self.ekubo_position_count.read();
        let mut total_fees_0 = 0_u256;
        let mut total_fees_1 = 0_u256;
        
        // Iterate through all Ekubo positions and collect fees
        let mut i = 0_u256;
        loop {
            if i >= position_count {
                break;
            }
            
            // Get position metadata (flattened)
            let token0 = self.ekubo_position_token0.entry(i).read();
            let token1 = self.ekubo_position_token1.entry(i).read();
            let fee = self.ekubo_position_fee.entry(i).read();
            let tick_spacing = self.ekubo_position_tick_spacing.entry(i).read();
            let extension = self.ekubo_position_extension.entry(i).read();
            let tick_lower_mag = self.ekubo_position_tick_lower_mag.entry(i).read();
            let tick_lower_sign = self.ekubo_position_tick_lower_sign.entry(i).read();
            let tick_upper_mag = self.ekubo_position_tick_upper_mag.entry(i).read();
            let tick_upper_sign = self.ekubo_position_tick_upper_sign.entry(i).read();
            
            // Set up fee collection state (flattened)
            self.ekubo_collecting_fees.write(true);
            self.ekubo_collect_position_index.write(i);
            self.ekubo_collect_token0.write(token0);
            self.ekubo_collect_token1.write(token1);
            self.ekubo_collect_fee.write(fee);
            self.ekubo_collect_tick_spacing.write(tick_spacing);
            self.ekubo_collect_extension.write(extension);
            self.ekubo_collect_tick_lower_mag.write(tick_lower_mag);
            self.ekubo_collect_tick_lower_sign.write(tick_lower_sign);
            self.ekubo_collect_tick_upper_mag.write(tick_upper_mag);
            self.ekubo_collect_tick_upper_sign.write(tick_upper_sign);
            
            // Call Core.lock() to initiate fee collection
            // This will trigger our locked() callback
            let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
            let empty_data = ArrayTrait::new().span();
            let _result = ekubo.lock(empty_data);
            
            // After locked() callback completes, fees should be in our contract
            // We'll track the balance change (this is a simplified approach)
            // In a full implementation, we'd track balances before/after
            
            // Clear collection state
            self.ekubo_collecting_fees.write(false);
            
            i += 1;
        };
        
        // Note: The actual fee amounts are collected in locked() callback
        // For now, return 0 as we need to track balance changes
        // TODO: Track token balances before/after to calculate actual fees collected
        (total_fees_0, total_fees_1)
    }
    
    #[external(v0)]
    fn accrue_yields(ref self: ContractState) -> u256 {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can accrue yields');
        
        // Collect fees from both protocols
        // Inline the collection logic since internal functions aren't accessible
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
        let position_count = self.jediswap_position_count.read();
        let mut jedi_fees_0 = 0_u256;
        let mut jedi_fees_1 = 0_u256;
        let contract_addr = get_contract_address();
        
        // Iterate through all JediSwap positions and collect fees
        let mut i = 0_u256;
        loop {
            if i >= position_count {
                break;
            }
            
            let token_id = self.jediswap_position_ids.entry(i).read();
            
            // Collect fees from this position
            let max_amount = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff_u256;
            let collect_params = CollectParams {
                token_id,
                recipient: contract_addr,
                amount0_max: max_amount,
                amount1_max: max_amount,
            };
            
            let (amount0, amount1) = nft_manager.collect(collect_params);
            jedi_fees_0 += amount0;
            jedi_fees_1 += amount1;
            
            i += 1;
        };
        
        // Ekubo fee collection - inline logic (can't call internal function from external)
        let ekubo_core = self.ekubo_core.read();
        let ekubo_position_count = self.ekubo_position_count.read();
        let mut ekubo_fees_0 = 0_u256;
        let _ekubo_fees_1 = 0_u256;
        
        // Iterate through all Ekubo positions and collect fees
        let mut i = 0_u256;
        loop {
            if i >= ekubo_position_count {
                break;
            }
            
            // Get position metadata (flattened)
            let token0 = self.ekubo_position_token0.entry(i).read();
            let token1 = self.ekubo_position_token1.entry(i).read();
            let fee = self.ekubo_position_fee.entry(i).read();
            let tick_spacing = self.ekubo_position_tick_spacing.entry(i).read();
            let extension = self.ekubo_position_extension.entry(i).read();
            let salt = self.ekubo_position_salt.entry(i).read();
            let tick_lower_mag = self.ekubo_position_tick_lower_mag.entry(i).read();
            let tick_lower_sign = self.ekubo_position_tick_lower_sign.entry(i).read();
            let tick_upper_mag = self.ekubo_position_tick_upper_mag.entry(i).read();
            let tick_upper_sign = self.ekubo_position_tick_upper_sign.entry(i).read();
            
            // Set up fee collection state (flattened)
            self.ekubo_collecting_fees.write(true);
            self.ekubo_collect_position_index.write(i);
            self.ekubo_collect_token0.write(token0);
            self.ekubo_collect_token1.write(token1);
            self.ekubo_collect_fee.write(fee);
            self.ekubo_collect_tick_spacing.write(tick_spacing);
            self.ekubo_collect_extension.write(extension);
            self.ekubo_collect_salt.write(salt);
            self.ekubo_collect_tick_lower_mag.write(tick_lower_mag);
            self.ekubo_collect_tick_lower_sign.write(tick_lower_sign);
            self.ekubo_collect_tick_upper_mag.write(tick_upper_mag);
            self.ekubo_collect_tick_upper_sign.write(tick_upper_sign);
            
            // Call Core.lock() to initiate fee collection
            // This will trigger our locked() callback
            let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
            let empty_data = ArrayTrait::new().span();
            let _result = ekubo.lock(empty_data);
            
            // After locked() callback completes, fees should be in our contract
            // TODO: Track token balances before/after to calculate actual fees collected
            // For now, we'll need to track this in the locked() callback
            
            // Clear collection state
            self.ekubo_collecting_fees.write(false);
            
            i += 1;
        };
        
        // Sum up total yield (assuming token0 is STRK for JediSwap)
        // For now, we'll use jedi_fees_0 as the primary yield metric
        // TODO: Convert all fees to a common token (STRK) for accurate reporting
        let total_yield = jedi_fees_0 + ekubo_fees_0;
        
        // Update total deposits to include yields (reinvestment strategy)
        // This compounds the yields back into the pool
        let current_deposits = self.total_deposits.read();
        self.total_deposits.write(current_deposits + total_yield);
        
        self.emit(YieldsAccrued {
            total_yield,
            timestamp: get_block_timestamp(),
        });
        
        total_yield
    }
    
    #[external(v0)]
    fn accrue_jediswap_yields(ref self: ContractState) -> u256 {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can accrue yields');
        
        // Collect fees from JediSwap positions only
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
        let position_count = self.jediswap_position_count.read();
        let mut jedi_fees_0 = 0_u256;
        let mut jedi_fees_1 = 0_u256;
        let contract_addr = get_contract_address();
        
        // Iterate through all JediSwap positions and collect fees
        let mut i = 0_u256;
        loop {
            if i >= position_count {
                break;
            }
            
            let token_id = self.jediswap_position_ids.entry(i).read();
            
            // Collect fees from this position
            let max_amount = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff_u256;
            let collect_params = CollectParams {
                token_id,
                recipient: contract_addr,
                amount0_max: max_amount,
                amount1_max: max_amount,
            };
            
            let (amount0, amount1) = nft_manager.collect(collect_params);
            jedi_fees_0 += amount0;
            jedi_fees_1 += amount1;
            
            i += 1;
        };
        
        // Update total deposits to include yields (reinvestment strategy)
        let current_deposits = self.total_deposits.read();
        self.total_deposits.write(current_deposits + jedi_fees_0);
        
        self.emit(YieldsAccrued {
            total_yield: jedi_fees_0,
            timestamp: get_block_timestamp(),
        });
        
        jedi_fees_0
    }
    
    #[external(v0)]
    fn accrue_ekubo_yields(ref self: ContractState) -> u256 {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can accrue yields');
        
        // Collect fees from Ekubo positions only
        let ekubo_core = self.ekubo_core.read();
        let ekubo_position_count = self.ekubo_position_count.read();
        let mut ekubo_fees_0 = 0_u256;
        
        // Iterate through all Ekubo positions and collect fees
        let mut i = 0_u256;
        loop {
            if i >= ekubo_position_count {
                break;
            }
            
            // Get position metadata (flattened)
            let token0 = self.ekubo_position_token0.entry(i).read();
            let token1 = self.ekubo_position_token1.entry(i).read();
            let fee = self.ekubo_position_fee.entry(i).read();
            let tick_spacing = self.ekubo_position_tick_spacing.entry(i).read();
            let extension = self.ekubo_position_extension.entry(i).read();
            let salt = self.ekubo_position_salt.entry(i).read();
            let tick_lower_mag = self.ekubo_position_tick_lower_mag.entry(i).read();
            let tick_lower_sign = self.ekubo_position_tick_lower_sign.entry(i).read();
            let tick_upper_mag = self.ekubo_position_tick_upper_mag.entry(i).read();
            let tick_upper_sign = self.ekubo_position_tick_upper_sign.entry(i).read();
            
            // Set up fee collection state (flattened)
            self.ekubo_collecting_fees.write(true);
            self.ekubo_collect_position_index.write(i);
            self.ekubo_collect_token0.write(token0);
            self.ekubo_collect_token1.write(token1);
            self.ekubo_collect_fee.write(fee);
            self.ekubo_collect_tick_spacing.write(tick_spacing);
            self.ekubo_collect_extension.write(extension);
            self.ekubo_collect_salt.write(salt);
            self.ekubo_collect_tick_lower_mag.write(tick_lower_mag);
            self.ekubo_collect_tick_lower_sign.write(tick_lower_sign);
            self.ekubo_collect_tick_upper_mag.write(tick_upper_mag);
            self.ekubo_collect_tick_upper_sign.write(tick_upper_sign);
            
            // Call Core.lock() to initiate fee collection
            // This will trigger our locked() callback
            let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
            let empty_data = ArrayTrait::new().span();
            let _result = ekubo.lock(empty_data);
            
            // Clear collection state
            self.ekubo_collecting_fees.write(false);
            
            i += 1;
        };
        
        // Update total deposits to include yields (reinvestment strategy)
        let current_deposits = self.total_deposits.read();
        self.total_deposits.write(current_deposits + ekubo_fees_0);
        
        self.emit(YieldsAccrued {
            total_yield: ekubo_fees_0,
            timestamp: get_block_timestamp(),
        });
        
        ekubo_fees_0
    }
    
    #[external(v0)]
    fn rebalance(ref self: ContractState) {
        // TODO: Implement rebalancing logic
        // 1. Calculate current positions in each protocol
        // 2. Calculate target positions based on allocation
        // 3. Move funds as needed
    }
    
    #[external(v0)]
    fn update_slippage_tolerance(ref self: ContractState, swap_slippage_bps: u256, liquidity_slippage_bps: u256) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can update slippage tolerance');
        
        // Validate slippage values (max 10% = 1000 basis points)
        assert(swap_slippage_bps <= 1000, 'Swap slippage too high (max 10%)');
        assert(liquidity_slippage_bps <= 1000, 'Liquidity slippage too high (max 10%)');
        
        self.swap_slippage_bps.write(swap_slippage_bps);
        self.liquidity_slippage_bps.write(liquidity_slippage_bps);
    }
    
    #[external(v0)]
    fn get_slippage_tolerance(self: @ContractState) -> (u256, u256) {
        (self.swap_slippage_bps.read(), self.liquidity_slippage_bps.read())
    }
    
    #[external(v0)]
    fn get_protocol_addresses(self: @ContractState) -> (ContractAddress, ContractAddress) {
        (self.jediswap_router.read(), self.ekubo_core.read())
    }
    
    #[external(v0)]
    fn get_total_value_locked(self: @ContractState) -> u256 {
        self.total_deposits.read()
    }
    
    // Position tracking getters
    #[external(v0)]
    fn get_jediswap_position(self: @ContractState, index: u256) -> u256 {
        self.jediswap_position_ids.entry(index).read()
    }
    
    #[external(v0)]
    fn get_ekubo_position(self: @ContractState, index: u256) -> u64 {
        self.ekubo_position_ids.entry(index).read()
    }
    
    #[external(v0)]
    fn get_jediswap_position_count(self: @ContractState) -> u256 {
        self.jediswap_position_count.read()
    }
    
    #[external(v0)]
    fn get_ekubo_position_count(self: @ContractState) -> u256 {
        self.ekubo_position_count.read()
    }
    
    // ============================================
    // EKUBO LOCK/CALLBACK IMPLEMENTATION
    // ============================================
    // This function is called by Ekubo Core after we call lock()
    // Reference: https://docs.ekubo.org/integration-guides/till-pattern
    
    #[external(v0)]
    fn locked(
        ref self: ContractState,
        id: u32,
        data: Span<felt252>
    ) -> Span<felt252> {
        // This is called by Ekubo Core after we call lock()
        // id is the lock identifier
        // data is the data we passed to lock()
        
        // Get Ekubo Core address
        let ekubo_core = self.ekubo_core.read();
        let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
        
        // Check if we're collecting fees
        let collecting_fees = self.ekubo_collecting_fees.read();
        
        if collecting_fees {
            // Fee collection mode: collect fees using collect_fees()
            // Reconstruct PoolKey and Bounds from flattened storage
            let pool_key = PoolKey {
                token0: self.ekubo_collect_token0.read(),
                token1: self.ekubo_collect_token1.read(),
                fee: self.ekubo_collect_fee.read(),
                tick_spacing: self.ekubo_collect_tick_spacing.read(),
                extension: self.ekubo_collect_extension.read(),
            };
            let bounds = Bounds {
                lower: i129 {
                    mag: self.ekubo_collect_tick_lower_mag.read(),
                    sign: self.ekubo_collect_tick_lower_sign.read(),
                },
                upper: i129 {
                    mag: self.ekubo_collect_tick_upper_mag.read(),
                    sign: self.ekubo_collect_tick_upper_sign.read(),
                },
            };
            let salt = self.ekubo_collect_salt.read();
            
            // Call collect_fees() - this is the ONLY way to collect fees from Ekubo positions
            let _delta = ekubo.collect_fees(pool_key, salt, bounds);
            
            // Fees are now in our contract (Core transfers them to us via lock mechanism)
            // The delta.amount0 and delta.amount1 represent the fees collected
            // Note: These are i129 (signed), negative values indicate transfers out of Core
            // TODO: Track delta amounts to calculate actual fees collected for reporting
            
        } else {
            // Normal liquidity addition mode
            // Get pending operation state
            let token0 = self.ekubo_pending_token0.read();
            let token1 = self.ekubo_pending_token1.read();
            let amount0 = self.ekubo_pending_amount0.read();
            let amount1 = self.ekubo_pending_amount1.read();
            
            // Verify we have a pending operation
            assert(amount0 > 0 || amount1 > 0, 'No pending Ekubo operation');
            
            // Pay tokens to Ekubo
            // Note: pay() takes full allowance - no amount parameter
            // We must approve before calling lock()
            if amount0 > 0 {
                ekubo.pay(token0);
            }
            if amount1 > 0 {
                ekubo.pay(token1);
            }
            
            // TODO: Update position using PoolKey and UpdatePositionParameters
            // This requires implementing the full Ekubo types (PoolKey, Bounds, i129, etc.)
            // For now, we'll skip position update and just pay tokens
            // The actual update_position signature is:
            // fn update_position(ref self: TContractState, pool_key: PoolKey, params: UpdatePositionParameters) -> Delta;
            
            // Clear pending operation state
            self.ekubo_pending_amount0.write(0);
            self.ekubo_pending_amount1.write(0);
        }
        
        // Return empty span (no data to return)
        ArrayTrait::new().span()
    }
    
    // ============================================
    // INDIVIDUAL PROTOCOL TESTING FUNCTIONS
    // ============================================
    // These functions test each protocol individually before full integration
    
    #[external(v0)]
    fn approve_token_for_testing(
        ref self: ContractState,
        token: ContractAddress,
        spender: ContractAddress,
        amount: u256
    ) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can approve');
        
        // Approve token on behalf of this contract
        let token_erc20 = IERC20Dispatcher { contract_address: token };
        token_erc20.approve(spender, amount);
    }
    
    #[external(v0)]
    fn test_jediswap_only(ref self: ContractState, amount: u256) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can test');
        
        let strk_token_felt: felt252 = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d;
        let strk_token: ContractAddress = strk_token_felt.try_into().unwrap();
        let asset_token = self.asset_token.read();
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        
        // For testing: Use STRK directly (no swap needed)
        // Approve NFT Manager for STRK
        let strk_token_erc20 = IERC20Dispatcher { contract_address: strk_token };
        strk_token_erc20.approve(jediswap_nft_manager, amount);
        
        // Also need ETH for the pair - for now, use 0 ETH (will fail but tests the flow)
        let eth_token_erc20 = IERC20Dispatcher { contract_address: asset_token };
        let zero_eth = 0_u256;
        eth_token_erc20.approve(jediswap_nft_manager, zero_eth);
        
        // Add liquidity via NFT Position Manager
        let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
        
        // Convert ticks to I32 struct (mag: u32, sign: bool)
        // Full range: ticks must be aligned to tick spacing (200 for 1% fee tier)
        // -887200 and 887200 are multiples of 200 (tick spacing)
        let tick_lower_mag: u32 = 887200; // Magnitude (aligned to tick spacing 200)
        let tick_lower_sign: bool = true; // Negative
        let tick_lower_i32 = I32 { mag: tick_lower_mag, sign: tick_lower_sign };
        
        let tick_upper_mag: u32 = 887200; // Magnitude (aligned to tick spacing 200)
        let tick_upper_sign: bool = false; // Positive
        let tick_upper_i32 = I32 { mag: tick_upper_mag, sign: tick_upper_sign };
        
        let contract_addr = get_contract_address();
        let mint_params = MintParams {
            token0: strk_token,
            token1: asset_token,
            fee: 10000, // 1% fee tier (STRK/ETH pools exist at 0.05% and 1% on Sepolia)
            tick_lower: tick_lower_i32,
            tick_upper: tick_upper_i32,
            amount0_desired: amount,
            amount1_desired: zero_eth,
            // Calculate minimum amounts with slippage protection
            amount0_min: {
                let liquidity_slippage_bps = self.liquidity_slippage_bps.read();
                let slippage_amount0 = amount * liquidity_slippage_bps / 10000;
                if amount > slippage_amount0 {
                    amount - slippage_amount0
                } else {
                    0
                }
            },
            amount1_min: 0, // No amount1 for single-sided liquidity
            recipient: contract_addr,
            deadline: get_block_timestamp() + 1800,
        };
        let (_token_id, _liquidity, _amount0, _amount1) = nft_manager.mint(mint_params);
    }
    
    #[external(v0)]
    fn test_ekubo_only(ref self: ContractState, amount: u256) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can test');
        
        let strk_token_felt: felt252 = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d;
        let strk_token: ContractAddress = strk_token_felt.try_into().unwrap();
        let asset_token = self.asset_token.read();
        let ekubo_positions = self.ekubo_positions.read();
        
        // Use Ekubo Positions contract - it handles Core's lock pattern internally!
        // First, approve Positions contract for both tokens
        let strk_token_erc20 = IERC20Dispatcher { contract_address: strk_token };
        strk_token_erc20.approve(ekubo_positions, amount);
        
        let eth_token_erc20 = IERC20Dispatcher { contract_address: asset_token };
        let eth_amount = amount; // Use same amount for both tokens (simplified)
        eth_token_erc20.approve(ekubo_positions, eth_amount);
        
        // Create PoolKey for STRK/ETH pair
        // Note: token0 must be < token1 (sorted by address)
        let (token0, token1) = if strk_token < asset_token {
            (strk_token, asset_token)
        } else {
            (asset_token, strk_token)
        };
        
        let pool_key = PoolKey {
            token0: token0,
            token1: token1,
            fee: 10000, // 1% fee tier (STRK/ETH pools exist at 0.05% and 1% on Sepolia)
            tick_spacing: 60, // Standard tick spacing
            extension: 0.try_into().unwrap(), // No extension
        };
        
        // Create Bounds for full range liquidity
        // Full range: lower = -887272, upper = 887272 (as i129)
        // For tick_spacing 60, we need to round to nearest multiple
        let tick_lower_mag: u128 = 887280; // Rounded to nearest multiple of 60
        let tick_upper_mag: u128 = 887280;
        let bounds = Bounds {
            lower: i129 { mag: tick_lower_mag, sign: true },  // Negative
            upper: i129 { mag: tick_upper_mag, sign: false },  // Positive
        };
        
        // Call mint_and_deposit on Positions contract
        // This handles the Core lock pattern internally!
        let positions = IEkuboPositionsDispatcher { contract_address: ekubo_positions };
        let min_liquidity = 0_u128; // No minimum for testing
        let (_token_id, _liquidity) = positions.mint_and_deposit(pool_key, bounds, min_liquidity);
        
        // Note: In test function, we don't store position ID
        // This is just for testing the integration
    }
}
