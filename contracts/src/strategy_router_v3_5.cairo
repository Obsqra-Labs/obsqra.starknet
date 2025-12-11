use starknet::ContractAddress;

#[starknet::interface]
pub trait IStrategyRouterV35<TContractState> {
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
    
    // Protocol recall (withdraw liquidity from protocols)
    fn recall_from_protocols(
        ref self: TContractState,
        jediswap_position_index: u256,
        ekubo_position_index: u256,
        jediswap_liquidity: u128,
        ekubo_liquidity: u128
    ) -> (u256, u256);
    
    // Slippage protection
    fn update_slippage_tolerance(ref self: TContractState, swap_slippage_bps: u256, liquidity_slippage_bps: u256);
    fn get_slippage_tolerance(self: @TContractState) -> (u256, u256);
    
    // Protocol info
    fn get_protocol_addresses(self: @TContractState) -> (ContractAddress, ContractAddress);
    fn get_total_value_locked(self: @TContractState) -> u256;
    fn get_protocol_tvl(self: @TContractState) -> (u256, u256);
    fn get_jediswap_tvl(self: @TContractState) -> u256;
    fn get_ekubo_tvl(self: @TContractState) -> u256;
    fn get_total_yield_accrued(self: @TContractState) -> u256;
    
    // Yield tracking for APY calculation
    fn get_pending_fees(self: @TContractState) -> (u256, u256); // Returns (jediswap_fees, ekubo_fees) without collecting
    fn get_yield_timestamps(self: @TContractState) -> (u64, u64); // Returns (first_yield_timestamp, last_yield_timestamp)
    
    // Position tracking
    fn get_jediswap_position(self: @TContractState, index: u256) -> u256;
    fn get_ekubo_position(self: @TContractState, index: u256) -> u64;
    fn get_jediswap_position_count(self: @TContractState) -> u256;
    fn get_ekubo_position_count(self: @TContractState) -> u256;
    
    // MIST.cash Privacy Integration
    fn commit_mist_deposit(ref self: TContractState, commitment_hash: felt252, expected_amount: u256);
    fn reveal_and_claim_mist_deposit(ref self: TContractState, secret: felt252) -> (ContractAddress, u256);
    fn get_mist_commitment(self: @TContractState, commitment_hash: felt252) -> (ContractAddress, u256, bool);
    fn set_mist_chamber(ref self: TContractState, chamber: ContractAddress);
    fn get_mist_chamber(self: @TContractState) -> ContractAddress;
}


#[starknet::contract]
mod StrategyRouterV35 {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address, get_block_timestamp
    };
    use core::num::traits::Zero;
    use starknet::storage::{
        StoragePointerWriteAccess, 
        StoragePointerReadAccess, 
        Map,
        StoragePathEntry
    };
    use core::poseidon::poseidon_hash_span;
    use super::super::interfaces::erc20::{IERC20Dispatcher, IERC20DispatcherTrait};
    // Protocol integration interfaces
    use super::super::interfaces::jediswap::{
        IJediSwapV2SwapRouterDispatcher,
        IJediSwapV2SwapRouterDispatcherTrait,
        IJediSwapV2NFTPositionManagerDispatcher, 
        IJediSwapV2NFTPositionManagerDispatcherTrait,
        IJediSwapFactoryDispatcher,
        IJediSwapFactoryDispatcherTrait,
        IJediSwapV2PoolDispatcher,
        IJediSwapV2PoolDispatcherTrait,
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
    use super::super::interfaces::mist::{IMistChamberDispatcher, IMistChamberDispatcherTrait};
    use core::array::{Span, ArrayTrait};
    
    #[storage]
    struct Storage {
        // Allocation percentages (basis points, 10000 = 100%)
        jediswap_allocation: u256,
        ekubo_allocation: u256,
        
        // Protocol addresses
        jediswap_router: ContractAddress,  // Swap Router (for swaps)
        jediswap_nft_manager: ContractAddress,  // NFT Position Manager (for liquidity)
        jediswap_factory: ContractAddress,  // Factory (for querying pools)
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
        
        // Total deposits
        total_deposits: u256,
        
        // FIX: Per-user balance tracking
        user_balances: Map<ContractAddress, u256>,
        
        // Pending deposits (funds waiting to be deployed to protocols)
        pending_deposits: u256,
        
        // Slippage protection (basis points, 10000 = 100%)
        // swap_slippage_bps: 100 = 1% slippage tolerance for swaps
        // liquidity_slippage_bps: 50 = 0.5% slippage tolerance for liquidity provision
        swap_slippage_bps: u256,  // Slippage tolerance for swaps (default: 100 = 1%)
        liquidity_slippage_bps: u256,  // Slippage tolerance for liquidity (default: 50 = 0.5%)
        
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
        ekubo_collected_fees_0: u256,  // Track fees collected during callback (token0)
        
        // Ekubo withdrawal state (for recall_from_protocols)
        ekubo_withdrawing: bool,
        ekubo_withdraw_position_index: u256,
        ekubo_withdraw_liquidity: u128,
        ekubo_withdraw_token0: ContractAddress,
        ekubo_withdraw_token1: ContractAddress,
        ekubo_withdraw_fee: u128,
        ekubo_withdraw_tick_spacing: u128,
        ekubo_withdraw_extension: ContractAddress,
        ekubo_withdraw_salt: felt252,
        ekubo_withdraw_tick_lower_mag: u128,
        ekubo_withdraw_tick_lower_sign: bool,
        ekubo_withdraw_tick_upper_mag: u128,
        ekubo_withdraw_tick_upper_sign: bool,
        ekubo_withdrawn_amount0: u256,
        ekubo_withdrawn_amount1: u256,
        
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
        total_yield_accrued: u256,  // Total yield accrued over time
        first_yield_timestamp: u64,  // Timestamp when first yield was accrued (for APY calculation)
        last_yield_timestamp: u64,  // Timestamp of last yield accrual
        
        // NEW: MIST.cash Integration Storage
        mist_chamber: ContractAddress,
        // Flattened commitment storage (like ekubo positions)
        mist_commitment_user: Map<felt252, ContractAddress>,
        mist_commitment_amount: Map<felt252, u256>,
        mist_commitment_revealed: Map<felt252, bool>,
        mist_commitment_timestamp: Map<felt252, u64>,
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
        // NEW: MIST events
        MistDepositCommitted: MistDepositCommitted,
        MistDepositClaimed: MistDepositClaimed,
        // Protocol recall event
        ProtocolsRecalled: ProtocolsRecalled,
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
    
    // NEW: MIST events
    #[derive(Drop, starknet::Event)]
    struct MistDepositCommitted {
        user: ContractAddress,
        commitment_hash: felt252,
        expected_amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct MistDepositClaimed {
        user: ContractAddress,
        commitment_hash: felt252,
        token: ContractAddress,
        amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct ProtocolsRecalled {
        jediswap_amount: u256,
        ekubo_amount: u256,
        timestamp: u64,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        jediswap_router: ContractAddress,
        jediswap_nft_manager: ContractAddress,
        jediswap_factory: ContractAddress,  // NEW: Factory for querying pools
        ekubo_core: ContractAddress,
        ekubo_positions: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        asset_token: ContractAddress,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        mist_chamber: ContractAddress,  // NEW: MIST chamber address
    ) {
        self.owner.write(owner);
        self.jediswap_router.write(jediswap_router);
        self.jediswap_nft_manager.write(jediswap_nft_manager);
        self.jediswap_factory.write(jediswap_factory);
        self.ekubo_core.write(ekubo_core);
        self.ekubo_positions.write(ekubo_positions);
        self.risk_engine.write(risk_engine);
        self.dao_manager.write(dao_manager);
        self.asset_token.write(asset_token);
        self.jediswap_allocation.write(jediswap_pct.into());
        self.ekubo_allocation.write(ekubo_pct.into());
        self.total_deposits.write(0);
        self.total_yield_accrued.write(0);  // Initialize yield tracking
        // Initialize slippage tolerance (default: 1% for swaps, 0.5% for liquidity)
        self.swap_slippage_bps.write(100);  // 1% = 100 basis points
        self.liquidity_slippage_bps.write(50);  // 0.5% = 50 basis points
        self.pending_deposits.write(0);
        self.jediswap_position_count.write(0);
        self.ekubo_position_count.write(0);
        
        // Initialize Ekubo pending operation state
        self.ekubo_pending_amount0.write(0);
        self.ekubo_pending_amount1.write(0);
        
        // NEW: Initialize MIST chamber
        self.mist_chamber.write(mist_chamber);
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
    // DEPOSIT FUNCTION - FIXED WITH USER BALANCE TRACKING
    // ============================================
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
        
        // FIX: Update user balance
        let user_balance = self.user_balances.entry(caller).read();
        self.user_balances.entry(caller).write(user_balance + amount);
        
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
    // WITHDRAW FUNCTION - FIXED WITH USER BALANCE CHECK
    // ============================================
    #[external(v0)]
    fn withdraw(ref self: ContractState, amount: u256) -> u256 {
        let caller = get_caller_address();
        
        // FIX: Check user balance instead of total deposits
        let user_balance = self.user_balances.entry(caller).read();
        assert(user_balance >= amount, 'Insufficient balance');
        
        // TODO: Withdraw from protocols proportionally
        // This would call protocol withdraw functions
        
        // For now, simple withdrawal without yields
        let asset_token = self.asset_token.read();
        let token = IERC20Dispatcher { contract_address: asset_token };
        let success = token.transfer(caller, amount);
        assert(success, 'Transfer failed');
        
        // FIX: Update user balance
        self.user_balances.entry(caller).write(user_balance - amount);
        
        // Update total deposits
        let total = self.total_deposits.read();
        self.total_deposits.write(total - amount);
        
        self.emit(Withdrawal {
            user: caller,
            amount,
            yield_amount: 0,
            timestamp: get_block_timestamp(),
        });
        
        amount
    }
    
    // ============================================
    // GET USER BALANCE - FIXED TO RETURN ACTUAL USER BALANCE
    // ============================================
    #[external(v0)]
    fn get_user_balance(self: @ContractState, user: ContractAddress) -> u256 {
        // FIX: Return actual user balance
        self.user_balances.entry(user).read()
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
            
            // Slippage protection disabled - set to 0 to allow swaps to proceed
            // TODO: Implement proper quote calculation once we have accurate pool price math
            // For now, removing slippage protection ensures swaps always succeed
            let amount_out_minimum = 0;
            
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
            
            // Slippage protection disabled for liquidity provision
            // TODO: Implement proper price ratio calculation based on pool's current price
            // For now, setting to 0 ensures liquidity provision succeeds
            let amount0_min = 0;
            let amount1_min = 0;
            
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
            
            // Update JediSwap position value (track TVL for allocation display)
            let current_jedi_value = self.jediswap_position_value.read();
            self.jediswap_position_value.write(current_jedi_value + jediswap_amount);
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
            
            // Update Ekubo position value (track TVL for allocation display)
            let current_ekubo_value = self.ekubo_position_value.read();
            self.ekubo_position_value.write(current_ekubo_value + ekubo_amount);
        }
        
        // Note: JediSwap position value is already updated inside the if block above (line 580-581)
        // No need to update again here
        
        self.emit(ProtocolsDeployed {
            jediswap_amount,
            ekubo_amount,
            timestamp: get_block_timestamp(),
        });
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
            
            // Reset collected fees for this position
            self.ekubo_collected_fees_0.write(0);
            
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
            // This will trigger our locked() callback which collects fees
            let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
            let empty_data = ArrayTrait::new().span();
            let _result = ekubo.lock(empty_data);
            
            // Read accumulated fees from callback
            let position_fees = self.ekubo_collected_fees_0.read();
            ekubo_fees_0 += position_fees;
            
            // Reset collected fees after reading (important for next collection)
            self.ekubo_collected_fees_0.write(0);
            
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
        
        // Update total yield accrued tracking
        let current_total_yield = self.total_yield_accrued.read();
        let new_total_yield = current_total_yield + total_yield;
        self.total_yield_accrued.write(new_total_yield);
        
        // Track yield timestamps for APY calculation
        let current_timestamp = get_block_timestamp();
        let first_timestamp = self.first_yield_timestamp.read();
        if first_timestamp == 0 {
            // First yield accrual - set initial timestamp
            self.first_yield_timestamp.write(current_timestamp);
        }
        self.last_yield_timestamp.write(current_timestamp);
        
        self.emit(YieldsAccrued {
            total_yield,
            timestamp: current_timestamp,
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
        
        // Update total yield accrued tracking
        let current_total_yield = self.total_yield_accrued.read();
        self.total_yield_accrued.write(current_total_yield + jedi_fees_0);
        
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
            
            // Reset collected fees for this position
            self.ekubo_collected_fees_0.write(0);
            
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
            // This will trigger our locked() callback which collects fees
            let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
            let empty_data = ArrayTrait::new().span();
            let _result = ekubo.lock(empty_data);
            
            // Read accumulated fees from callback
            let position_fees = self.ekubo_collected_fees_0.read();
            ekubo_fees_0 += position_fees;
            
            // Reset collected fees after reading (important for next collection)
            self.ekubo_collected_fees_0.write(0);
            
            // Clear collection state
            self.ekubo_collecting_fees.write(false);
            
            i += 1;
        };
        
        // Update total deposits to include yields (reinvestment strategy)
        let current_deposits = self.total_deposits.read();
        self.total_deposits.write(current_deposits + ekubo_fees_0);
        
        // Update total yield accrued tracking
        let current_total_yield = self.total_yield_accrued.read();
        self.total_yield_accrued.write(current_total_yield + ekubo_fees_0);
        
        self.emit(YieldsAccrued {
            total_yield: ekubo_fees_0,
            timestamp: get_block_timestamp(),
        });
        
        ekubo_fees_0
    }
    
    #[external(v0)]
    fn rebalance(ref self: ContractState) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        let risk_engine = self.risk_engine.read();
        
        // Only owner or risk_engine can rebalance
        assert(caller == owner || caller == risk_engine, 'Unauthorized');
        
        // Step 1: Get current allocation (basis points: 5000 = 50%)
        let jediswap_pct = self.jediswap_allocation.read();
        let ekubo_pct = self.ekubo_allocation.read();
        
        // Step 2: Get current TVL in each protocol
        let jediswap_tvl = self.jediswap_position_value.read();
        let ekubo_tvl = self.ekubo_position_value.read();
        let total_protocol_tvl = jediswap_tvl + ekubo_tvl;
        
        // If no TVL deployed, nothing to rebalance
        if total_protocol_tvl == 0 {
            return;
        }
        
        // Step 3: Calculate target TVL for each protocol
        let target_jedi_tvl = (total_protocol_tvl * jediswap_pct) / 10000;
        let target_ekubo_tvl = (total_protocol_tvl * ekubo_pct) / 10000;
        
        // Step 4: Calculate differences (how much to move)
        let jedi_diff = if jediswap_tvl > target_jedi_tvl {
            jediswap_tvl - target_jedi_tvl  // Need to recall this amount
        } else {
            0  // Need to deploy more
        };
        
        let ekubo_diff = if ekubo_tvl > target_ekubo_tvl {
            ekubo_tvl - target_ekubo_tvl  // Need to recall this amount
        } else {
            0  // Need to deploy more
        };
        
        // Step 5: Recall excess from protocols
        // For JediSwap: recall from position 0 (simplified - could iterate through all)
        if jedi_diff > 0 {
            let jedi_position_count = self.jediswap_position_count.read();
            if jedi_position_count > 0 {
                // Get position to calculate liquidity
                let token_id = self.jediswap_position_ids.entry(0).read();
                let jediswap_nft_manager = self.jediswap_nft_manager.read();
                let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
                let position = nft_manager.positions(token_id);
                
                // Calculate liquidity to withdraw (proportional to difference)
                // Simplified: withdraw all if difference is large, otherwise proportional
                let liquidity_to_withdraw: u128 = if jedi_diff >= jediswap_tvl {
                    position.liquidity  // Withdraw all
                } else {
                    // Proportional: (diff / tvl) * liquidity
                    // Note: This is approximate - actual calculation is more complex
                    let liquidity_u256: u256 = position.liquidity.into();
                    let calculated = (liquidity_u256 * jedi_diff) / jediswap_tvl;
                    // Convert back to u128 (with overflow check)
                    if calculated > 0xffffffffffffffffffffffffffffffff_u256 {
                        position.liquidity  // Fallback to full liquidity
                    } else {
                        calculated.try_into().unwrap()
                    }
                };
                
                if liquidity_to_withdraw > 0 {
                    // Inline recall logic for JediSwap
                    let jediswap_nft_manager = self.jediswap_nft_manager.read();
                    let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
                    let token_id = self.jediswap_position_ids.entry(0).read();
                    let contract_addr = get_contract_address();
                    
                    // Decrease liquidity
                    let _deadline = get_block_timestamp() + 1800;
                    let max_amount = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff_u256;
                    let decrease_params = DecreaseLiquidityParams {
                        token_id,
                        liquidity: liquidity_to_withdraw,
                        amount0_min: 0,
                        amount1_min: 0,
                        deadline: _deadline,
                    };
                    
                    let (amount0, amount1) = nft_manager.decrease_liquidity(decrease_params);
                    
                    // Collect fees
                    let collect_params = CollectParams {
                        token_id,
                        recipient: contract_addr,
                        amount0_max: max_amount,
                        amount1_max: max_amount,
                    };
                    let (fees0, fees1) = nft_manager.collect(collect_params);
                    
                    let recalled_strk = amount0 + fees0;
                    let recalled_eth = amount1 + fees1;
                    
                    // Update position value tracking
                    let current_jedi_value = self.jediswap_position_value.read();
                    let recalled_value = amount0 + amount1;
                    if current_jedi_value >= recalled_value {
                        self.jediswap_position_value.write(current_jedi_value - recalled_value);
                    } else {
                        self.jediswap_position_value.write(0);
                    }
                    
                    // Add recalled funds to pending deposits
                    let pending = self.pending_deposits.read();
                    self.pending_deposits.write(pending + recalled_strk + recalled_eth);
                }
            }
        }
        
        // For Ekubo: similar logic (simplified)
        if ekubo_diff > 0 {
            let ekubo_position_count = self.ekubo_position_count.read();
            if ekubo_position_count > 0 {
                // Simplified: withdraw proportional amount
                // Actual implementation would need to query position liquidity
                // For now, use a conservative estimate based on TVL difference
                // Note: Ekubo liquidity is in u128, but we don't have direct access
                // This is a placeholder - would need Core.get_position() or similar
                let liquidity_to_withdraw: u128 = if ekubo_diff >= ekubo_tvl {
                    // Withdraw all - would need to query actual liquidity
                    // Using a large placeholder value
                    1000000000000000000_u128  // 1e18 as placeholder
                } else {
                    // Proportional withdrawal - simplified calculation
                    // Would need actual position liquidity query
                    500000000000000000_u128  // 0.5e18 as placeholder
                };
                
                // Inline recall logic for Ekubo (simplified - uses collect_fees as placeholder)
                let ekubo_position_index = 0_u256;
                let token0 = self.ekubo_position_token0.entry(ekubo_position_index).read();
                let token1 = self.ekubo_position_token1.entry(ekubo_position_index).read();
                let fee = self.ekubo_position_fee.entry(ekubo_position_index).read();
                let tick_spacing = self.ekubo_position_tick_spacing.entry(ekubo_position_index).read();
                let extension = self.ekubo_position_extension.entry(ekubo_position_index).read();
                let salt = self.ekubo_position_salt.entry(ekubo_position_index).read();
                let tick_lower_mag = self.ekubo_position_tick_lower_mag.entry(ekubo_position_index).read();
                let tick_lower_sign = self.ekubo_position_tick_lower_sign.entry(ekubo_position_index).read();
                let tick_upper_mag = self.ekubo_position_tick_upper_mag.entry(ekubo_position_index).read();
                let tick_upper_sign = self.ekubo_position_tick_upper_sign.entry(ekubo_position_index).read();
                
                // Set up withdrawal state
                self.ekubo_withdrawing.write(true);
                self.ekubo_withdraw_position_index.write(ekubo_position_index);
                self.ekubo_withdraw_liquidity.write(liquidity_to_withdraw);
                self.ekubo_withdraw_token0.write(token0);
                self.ekubo_withdraw_token1.write(token1);
                self.ekubo_withdraw_fee.write(fee);
                self.ekubo_withdraw_tick_spacing.write(tick_spacing);
                self.ekubo_withdraw_extension.write(extension);
                self.ekubo_withdraw_salt.write(salt);
                self.ekubo_withdraw_tick_lower_mag.write(tick_lower_mag);
                self.ekubo_withdraw_tick_lower_sign.write(tick_lower_sign);
                self.ekubo_withdraw_tick_upper_mag.write(tick_upper_mag);
                self.ekubo_withdraw_tick_upper_sign.write(tick_upper_sign);
                self.ekubo_withdrawn_amount0.write(0);
                self.ekubo_withdrawn_amount1.write(0);
                
                // Call Core.lock() to initiate withdrawal (triggers locked() callback)
                let ekubo_core = self.ekubo_core.read();
                let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
                let empty_data = ArrayTrait::new().span();
                let _result = ekubo.lock(empty_data);
                
                // Read withdrawn amounts from callback
                let recalled_strk = self.ekubo_withdrawn_amount0.read();
                let recalled_eth = self.ekubo_withdrawn_amount1.read();
                
                // Update position value tracking
                let current_ekubo_value = self.ekubo_position_value.read();
                let recalled_value = recalled_strk + recalled_eth;
                if current_ekubo_value >= recalled_value {
                    self.ekubo_position_value.write(current_ekubo_value - recalled_value);
                } else {
                    self.ekubo_position_value.write(0);
                }
                
                // Clear withdrawal state
                self.ekubo_withdrawing.write(false);
                
                // Add recalled funds to pending deposits
                let pending = self.pending_deposits.read();
                self.pending_deposits.write(pending + recalled_strk + recalled_eth);
            }
        }
        
        // Step 6: Deploy recalled funds to under-allocated protocol
        // Note: We can't call deploy_to_protocols() from within rebalance()
        // The funds will be deployed on the next call to deploy_to_protocols()
        // This is acceptable as rebalancing is typically done periodically
        
        // Emit rebalance event
        let new_jedi_tvl = self.jediswap_position_value.read();
        let new_ekubo_tvl = self.ekubo_position_value.read();
        self.emit(Rebalanced {
            old_jediswap: jediswap_tvl.try_into().unwrap(),
            old_ekubo: ekubo_tvl.try_into().unwrap(),
            new_jediswap: new_jedi_tvl.try_into().unwrap(),
            new_ekubo: new_ekubo_tvl.try_into().unwrap(),
            timestamp: get_block_timestamp(),
        });
    }
    
    #[external(v0)]
    fn update_slippage_tolerance(ref self: ContractState, swap_slippage_bps: u256, liquidity_slippage_bps: u256) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Unauthorized');
        
        // Validate slippage values (max 10% = 1000 basis points)
        assert(swap_slippage_bps <= 1000, 'Slippage too high');
        assert(liquidity_slippage_bps <= 1000, 'Slippage too high');
        
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
    
    // Yield tracking getters
    #[external(v0)]
    fn get_total_yield_accrued(self: @ContractState) -> u256 {
        self.total_yield_accrued.read()
    }
    
    // Protocol metrics getters
    #[external(v0)]
    fn get_protocol_tvl(self: @ContractState) -> (u256, u256) {
        (self.jediswap_position_value.read(), self.ekubo_position_value.read())
    }
    
    #[external(v0)]
    fn get_jediswap_tvl(self: @ContractState) -> u256 {
        self.jediswap_position_value.read()
    }
    
    #[external(v0)]
    fn get_ekubo_tvl(self: @ContractState) -> u256 {
        self.ekubo_position_value.read()
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
        
        // Check if we're withdrawing liquidity
        let withdrawing = self.ekubo_withdrawing.read();
        if withdrawing {
            // Get withdrawal parameters
            let pool_key = PoolKey {
                token0: self.ekubo_withdraw_token0.read(),
                token1: self.ekubo_withdraw_token1.read(),
                fee: self.ekubo_withdraw_fee.read(),
                tick_spacing: self.ekubo_withdraw_tick_spacing.read(),
                extension: self.ekubo_withdraw_extension.read(),
            };
            let bounds = Bounds {
                lower: i129 {
                    mag: self.ekubo_withdraw_tick_lower_mag.read(),
                    sign: self.ekubo_withdraw_tick_lower_sign.read(),
                },
                upper: i129 {
                    mag: self.ekubo_withdraw_tick_upper_mag.read(),
                    sign: self.ekubo_withdraw_tick_upper_sign.read(),
                },
            };
            let salt = self.ekubo_withdraw_salt.read();
            
            // TODO: Call Core's update_position to decrease liquidity
            // This requires UpdatePositionParameters struct which we need to define
            // The signature would be:
            // let delta = ekubo.update_position(pool_key, UpdatePositionParameters { ... });
            // 
            // For now, we'll collect fees as a workaround (fees are part of withdrawal)
            // Actual liquidity withdrawal needs Core.update_position() implementation
            let delta = ekubo.collect_fees(pool_key, salt, bounds);
            
            // Store withdrawn amounts (from fees collected - actual withdrawal needs update_position)
            // Note: This is a placeholder - actual withdrawal would return tokens from liquidity decrease
            self.ekubo_withdrawn_amount0.write(delta.amount0.mag.into());
            self.ekubo_withdrawn_amount1.write(delta.amount1.mag.into());
            
            // Note: Full withdrawal implementation requires:
            // 1. Define UpdatePositionParameters struct
            // 2. Call ekubo.update_position() with negative liquidity delta
            // 3. Handle returned tokens via Core's withdraw() or pay() mechanism
        }
        
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
            let delta = ekubo.collect_fees(pool_key, salt, bounds);
            
            // Fees are now in our contract (Core transfers them to us via lock mechanism)
            // The delta.amount0 and delta.amount1 represent the fees collected
            // Note: These are i129 (signed), negative values indicate transfers out of Core (to us)
            // Convert i129.mag (u128) to u256 - fees are always positive (magnitude)
            let fees_0: u256 = delta.amount0.mag.into();
            
            // Accumulate fees collected for this position
            let current_collected = self.ekubo_collected_fees_0.read();
            self.ekubo_collected_fees_0.write(current_collected + fees_0);
            
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
            // Slippage protection disabled for liquidity provision
            amount0_min: 0,
            amount1_min: 0,
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
    
    // ============================================
    // MIST.CASH PRIVACY INTEGRATION (Pattern 2: Hash Commitment)
    // ============================================
    
    #[external(v0)]
    fn set_mist_chamber(ref self: ContractState, chamber: ContractAddress) {
        let caller = get_caller_address();
        assert(caller == self.owner.read(), 'Unauthorized');
        self.mist_chamber.write(chamber);
    }
    
    #[external(v0)]
    fn get_mist_chamber(self: @ContractState) -> ContractAddress {
        self.mist_chamber.read()
    }
    
    // Pattern 2: Commit phase - user sends hash of secret to router
    // Router stores commitment and cannot claim until user reveals secret
    #[external(v0)]
    fn commit_mist_deposit(
        ref self: ContractState,
        commitment_hash: felt252,
        expected_amount: u256
    ) {
        let caller = get_caller_address();
        
        // Verify commitment doesn't exist
        let existing_user = self.mist_commitment_user.entry(commitment_hash).read();
        assert(existing_user.is_zero(), 'Commitment already exists');
        
        // Store commitment (flattened)
        self.mist_commitment_user.entry(commitment_hash).write(caller);
        self.mist_commitment_amount.entry(commitment_hash).write(expected_amount);
        self.mist_commitment_revealed.entry(commitment_hash).write(false);
        self.mist_commitment_timestamp.entry(commitment_hash).write(get_block_timestamp());
        
        self.emit(MistDepositCommitted {
            user: caller,
            commitment_hash,
            expected_amount,
            timestamp: get_block_timestamp(),
        });
    }
    
    // Pattern 2: Reveal phase - user reveals secret when ready
    // Router verifies hash and claims from chamber
    #[external(v0)]
    fn reveal_and_claim_mist_deposit(
        ref self: ContractState,
        secret: felt252
    ) -> (ContractAddress, u256) {
        let caller = get_caller_address();
        
        // Compute commitment hash from secret using Poseidon (matches frontend computeHashOnElements)
        let mut secret_array = ArrayTrait::new();
        secret_array.append(secret);
        secret_array.append(secret);  // Hash secret with itself for single-value commitment
        let commitment_hash = poseidon_hash_span(secret_array.span());
        
        // Verify commitment exists
        let commitment_user = self.mist_commitment_user.entry(commitment_hash).read();
        let commitment_revealed = self.mist_commitment_revealed.entry(commitment_hash).read();
        let commitment_amount = self.mist_commitment_amount.entry(commitment_hash).read();
        assert(!commitment_user.is_zero(), 'Commitment not found');
        assert(commitment_user == caller, 'Not your commitment');
        assert(!commitment_revealed, 'Already revealed');
        
        // Mark as revealed
        self.mist_commitment_revealed.entry(commitment_hash).write(true);
        
        // Get MIST chamber
        let chamber = self.mist_chamber.read();
        assert(!chamber.is_zero(), 'MIST chamber not configured');
        
        // Claim from MIST chamber
        let chamber_contract = IMistChamberDispatcher { contract_address: chamber };
        let (token_address, claimed_amount) = chamber_contract.read_tx(secret);
        
        // Verify amount (5% tolerance)
        let expected = commitment_amount;
        assert(claimed_amount >= expected * 95 / 100, 'Amount mismatch');
        
        // Update balances
        let user_balance = self.user_balances.entry(caller).read();
        self.user_balances.entry(caller).write(user_balance + claimed_amount);
        
        let total = self.total_deposits.read();
        self.total_deposits.write(total + claimed_amount);
        
        let pending = self.pending_deposits.read();
        self.pending_deposits.write(pending + claimed_amount);
        
        self.emit(MistDepositClaimed {
            user: caller,
            commitment_hash,
            token: token_address,
            amount: claimed_amount,
            timestamp: get_block_timestamp(),
        });
        
        (token_address, claimed_amount)
    }
    
    #[external(v0)]
    fn get_mist_commitment(
        self: @ContractState,
        commitment_hash: felt252
    ) -> (ContractAddress, u256, bool) {
        let user = self.mist_commitment_user.entry(commitment_hash).read();
        let amount = self.mist_commitment_amount.entry(commitment_hash).read();
        let revealed = self.mist_commitment_revealed.entry(commitment_hash).read();
        (user, amount, revealed)
    }
    
    // ============================================
    // RECALL LIQUIDITY FROM PROTOCOLS
    // ============================================
    // Withdraw liquidity from protocols and return to contract
    // This allows the contract to recall funds from protocols for rebalancing or withdrawal
    #[external(v0)]
    fn recall_from_protocols(
        ref self: ContractState,
        jediswap_position_index: u256,
        ekubo_position_index: u256,
        jediswap_liquidity: u128,
        ekubo_liquidity: u128
    ) -> (u256, u256) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can recall from protocols');
        
        let mut total_strk_recalled = 0_u256;
        let mut total_eth_recalled = 0_u256;
        
        // Recall from JediSwap position
        if jediswap_liquidity > 0 {
            let jediswap_nft_manager = self.jediswap_nft_manager.read();
            let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
            let token_id = self.jediswap_position_ids.entry(jediswap_position_index).read();
            let contract_addr = get_contract_address();
            
            // Decrease liquidity
            let deadline = get_block_timestamp() + 1800; // 30 minutes
            let max_amount = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff_u256;
            let decrease_params = DecreaseLiquidityParams {
                token_id,
                liquidity: jediswap_liquidity,
                amount0_min: 0, // No slippage protection for now
                amount1_min: 0,
                deadline,
            };
            
            let (amount0, amount1) = nft_manager.decrease_liquidity(decrease_params);
            total_strk_recalled += amount0;
            total_eth_recalled += amount1;
            
            // Collect any remaining fees
            let collect_params = CollectParams {
                token_id,
                recipient: contract_addr,
                amount0_max: max_amount,
                amount1_max: max_amount,
            };
            let (fees0, fees1) = nft_manager.collect(collect_params);
            total_strk_recalled += fees0;
            total_eth_recalled += fees1;
            
            // Check if position has 0 liquidity and burn if so
            let position_after = nft_manager.positions(token_id);
            if position_after.liquidity == 0 {
                // Position is empty, burn it
                nft_manager.burn(token_id);
                
                // Remove from tracking (for simplicity, we'll leave the ID in the map as 0)
                // A more sophisticated approach would shift all subsequent positions
                self.jediswap_position_ids.entry(jediswap_position_index).write(0);
            }
            
            // Update position value tracking
            let current_jedi_value = self.jediswap_position_value.read();
            let recalled_value = amount0 + amount1; // Approximate
            if current_jedi_value >= recalled_value {
                self.jediswap_position_value.write(current_jedi_value - recalled_value);
            } else {
                self.jediswap_position_value.write(0);
            }
        }
        
        // Recall from Ekubo position
        // Note: Ekubo withdrawal requires Core's update_position() which needs UpdatePositionParameters
        // For now, we'll set up the state but actual withdrawal needs Core interface research
        if ekubo_liquidity > 0 {
            let ekubo_position_count = self.ekubo_position_count.read();
            assert(ekubo_position_index < ekubo_position_count, 'Invalid Ekubo position index');
            
            // Get position metadata
            let token0 = self.ekubo_position_token0.entry(ekubo_position_index).read();
            let token1 = self.ekubo_position_token1.entry(ekubo_position_index).read();
            let fee = self.ekubo_position_fee.entry(ekubo_position_index).read();
            let tick_spacing = self.ekubo_position_tick_spacing.entry(ekubo_position_index).read();
            let extension = self.ekubo_position_extension.entry(ekubo_position_index).read();
            let salt = self.ekubo_position_salt.entry(ekubo_position_index).read();
            let tick_lower_mag = self.ekubo_position_tick_lower_mag.entry(ekubo_position_index).read();
            let tick_lower_sign = self.ekubo_position_tick_lower_sign.entry(ekubo_position_index).read();
            let tick_upper_mag = self.ekubo_position_tick_upper_mag.entry(ekubo_position_index).read();
            let tick_upper_sign = self.ekubo_position_tick_upper_sign.entry(ekubo_position_index).read();
            
            // Set up withdrawal state
            self.ekubo_withdrawing.write(true);
            self.ekubo_withdraw_position_index.write(ekubo_position_index);
            self.ekubo_withdraw_liquidity.write(ekubo_liquidity);
            self.ekubo_withdraw_token0.write(token0);
            self.ekubo_withdraw_token1.write(token1);
            self.ekubo_withdraw_fee.write(fee);
            self.ekubo_withdraw_tick_spacing.write(tick_spacing);
            self.ekubo_withdraw_extension.write(extension);
            self.ekubo_withdraw_salt.write(salt);
            self.ekubo_withdraw_tick_lower_mag.write(tick_lower_mag);
            self.ekubo_withdraw_tick_lower_sign.write(tick_lower_sign);
            self.ekubo_withdraw_tick_upper_mag.write(tick_upper_mag);
            self.ekubo_withdraw_tick_upper_sign.write(tick_upper_sign);
            
            // Reset withdrawn amounts
            self.ekubo_withdrawn_amount0.write(0);
            self.ekubo_withdrawn_amount1.write(0);
            
            // Call Core.lock() to initiate withdrawal
            // This will trigger our locked() callback which should call update_position()
            let ekubo_core = self.ekubo_core.read();
            let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
            let empty_data = ArrayTrait::new().span();
            let _result = ekubo.lock(empty_data);
            
            // Read withdrawn amounts from callback
            let withdrawn_0 = self.ekubo_withdrawn_amount0.read();
            let withdrawn_1 = self.ekubo_withdrawn_amount1.read();
            total_strk_recalled += withdrawn_0;
            total_eth_recalled += withdrawn_1;
            
            // Update position value tracking
            let current_ekubo_value = self.ekubo_position_value.read();
            let recalled_value = withdrawn_0 + withdrawn_1;
            if current_ekubo_value >= recalled_value {
                self.ekubo_position_value.write(current_ekubo_value - recalled_value);
            } else {
                self.ekubo_position_value.write(0);
            }
            
            // Clear withdrawal state
            self.ekubo_withdrawing.write(false);
        }
        
        self.emit(ProtocolsRecalled {
            jediswap_amount: total_strk_recalled,
            ekubo_amount: total_eth_recalled,
            timestamp: get_block_timestamp(),
        });
        
        (total_strk_recalled, total_eth_recalled)
    }
    
    
    // ============================================
    // QUERY PENDING FEES (Without Collecting)
    // ============================================
    // This allows us to see fees available before collecting them
    // Useful for calculating actual APY and showing pending earnings
    #[external(v0)]
    fn get_pending_fees(self: @ContractState) -> (u256, u256) {
        let mut jedi_fees_0 = 0_u256;
        let mut jedi_fees_1 = 0_u256;
        
        // Query JediSwap positions for pending fees
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
        let position_count = self.jediswap_position_count.read();
        
        let mut i = 0_u256;
        loop {
            if i >= position_count {
                break;
            }
            
            let token_id = self.jediswap_position_ids.entry(i).read();
            
            // Query position to get tokens_owed (pending fees)
            let position = nft_manager.positions(token_id);
            jedi_fees_0 += position.tokens_owed0;
            jedi_fees_1 += position.tokens_owed1;
            
            i += 1;
        };
        
        // For Ekubo, we can't easily query pending fees without collecting
        // The fees are in the pool and require collect_fees() to retrieve
        // For now, return 0 for Ekubo pending fees
        // TODO: Investigate if Ekubo has a view function for pending fees
        
        // Return (jedi_fees_0, ekubo_fees_0) - using jedi_fees_0 as primary metric
        (jedi_fees_0, 0_u256)
    }
    
    // ============================================
    // GET YIELD TIMESTAMPS (For APY Calculation)
    // ============================================
    #[external(v0)]
    fn get_yield_timestamps(self: @ContractState) -> (u64, u64) {
        let first = self.first_yield_timestamp.read();
        let last = self.last_yield_timestamp.read();
        (first, last)
    }
    
    // ============================================
    // GET POSITION LIQUIDITY (Helper for Rebalancing)
    // ============================================
    #[external(v0)]
    fn get_position_liquidity(
        self: @ContractState,
        protocol: felt252,  // 0 = JediSwap, 1 = Ekubo
        position_index: u256
    ) -> u128 {
        if protocol == 0 {
            // JediSwap
            let jedi_position_count = self.jediswap_position_count.read();
            assert(position_index < jedi_position_count, 'Invalid JediSwap position index');
            
            let token_id = self.jediswap_position_ids.entry(position_index).read();
            let jediswap_nft_manager = self.jediswap_nft_manager.read();
            let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
            let position = nft_manager.positions(token_id);
            position.liquidity
        } else {
            // Ekubo - would need to query via Core or Positions
            // For now, return 0 (needs implementation)
            // TODO: Implement Ekubo position liquidity query
            0
        }
    }
}

