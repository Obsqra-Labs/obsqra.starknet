use starknet::ContractAddress;

#[starknet::interface]
pub trait IPoolFactory<TContractState> {
    // Pool creation
    fn create_pool(
        ref self: TContractState,
        name: ByteArray,
        cap: u256,
        jediswap_pct: felt252,
        ekubo_pct: felt252
    ) -> ContractAddress;
    
    // Pool management
    fn pause_pool(ref self: TContractState, pool_address: ContractAddress);
    fn unpause_pool(ref self: TContractState, pool_address: ContractAddress);
    fn update_pool_cap(ref self: TContractState, pool_address: ContractAddress, new_cap: u256);
    
    // Getters
    fn get_pool_count(self: @TContractState) -> u32;
    fn get_pool_by_index(self: @TContractState, index: u64) -> ContractAddress;
    fn get_pool_by_id(self: @TContractState, pool_id: felt252) -> ContractAddress;
    fn is_pool(self: @TContractState, address: ContractAddress) -> bool;
    fn get_owner(self: @TContractState) -> ContractAddress;
    
    // Owner management
    fn transfer_ownership(ref self: TContractState, new_owner: ContractAddress);
}

#[starknet::contract]
mod PoolFactory {
    use starknet::{
        ContractAddress, ClassHash, get_caller_address, get_block_timestamp,
        syscalls::deploy_syscall,
        storage::{
            Map,
            StoragePointerReadAccess, StoragePointerWriteAccess,
            StoragePathEntry
        }
    };
    use core::poseidon::poseidon_hash_span;
    use super::super::pool::{IPoolDispatcher, IPoolDispatcherTrait};
    
    #[storage]
    struct Storage {
        // Owner (Obsqra multisig, later DAO)
        owner: ContractAddress,
        
        // Pool tracking (Map instead of Vec for Cairo 2.8.5 compatibility)
        pools_by_index: Map<u32, ContractAddress>,
        pool_by_id: Map<felt252, ContractAddress>,
        is_pool_map: Map<ContractAddress, bool>,
        pool_count: u32,
        
        // Pool class hash for deployment
        pool_class_hash: ClassHash,
        
        // Protocol addresses
        jediswap_router: ContractAddress,
        ekubo_core: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        asset_token: ContractAddress,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        PoolCreated: PoolCreated,
        PoolPaused: PoolPaused,
        PoolUnpaused: PoolUnpaused,
        PoolCapUpdated: PoolCapUpdated,
        OwnershipTransferred: OwnershipTransferred,
    }
    
    #[derive(Drop, starknet::Event)]
    struct PoolCreated {
        pool_address: ContractAddress,
        pool_id: felt252,
        name: ByteArray,
        cap: u256,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct PoolPaused {
        pool_address: ContractAddress,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct PoolUnpaused {
        pool_address: ContractAddress,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct PoolCapUpdated {
        pool_address: ContractAddress,
        old_cap: u256,
        new_cap: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct OwnershipTransferred {
        previous_owner: ContractAddress,
        new_owner: ContractAddress,
        timestamp: u64,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        pool_class_hash: ClassHash,
        jediswap_router: ContractAddress,
        ekubo_core: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        asset_token: ContractAddress
    ) {
        self.owner.write(owner);
        self.pool_class_hash.write(pool_class_hash);
        self.jediswap_router.write(jediswap_router);
        self.ekubo_core.write(ekubo_core);
        self.risk_engine.write(risk_engine);
        self.dao_manager.write(dao_manager);
        self.asset_token.write(asset_token);
        self.pool_count.write(0);
    }
    
    #[abi(embed_v0)]
    impl PoolFactoryImpl of super::IPoolFactory<ContractState> {
        fn create_pool(
            ref self: ContractState,
            name: ByteArray,
            cap: u256,
            jediswap_pct: felt252,
            ekubo_pct: felt252
        ) -> ContractAddress {
            // Only owner can create pools
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 'Only owner');
            
            // Verify allocation
            assert(jediswap_pct + ekubo_pct == 10000, 'Allocation must sum to 100%');
            
            // Generate unique pool ID
            let pool_count = self.pool_count.read();
            let timestamp = get_block_timestamp();
            let pool_id = poseidon_hash_span(
                array![pool_count.into(), timestamp.into()].span()
            );
            
            // Prepare constructor calldata
            let mut calldata = ArrayTrait::new();
            Serde::serialize(@pool_id, ref calldata);
            Serde::serialize(@name, ref calldata);
            Serde::serialize(@cap, ref calldata);
            Serde::serialize(@jediswap_pct, ref calldata);
            Serde::serialize(@ekubo_pct, ref calldata);
            Serde::serialize(@get_caller_address(), ref calldata);  // factory
            Serde::serialize(@self.jediswap_router.read(), ref calldata);
            Serde::serialize(@self.ekubo_core.read(), ref calldata);
            Serde::serialize(@self.risk_engine.read(), ref calldata);
            Serde::serialize(@self.dao_manager.read(), ref calldata);
            Serde::serialize(@self.asset_token.read(), ref calldata);
            
            // Deploy pool
            let (pool_address, _) = deploy_syscall(
                self.pool_class_hash.read(),
                pool_id,  // salt
                calldata.span(),
                false
            ).expect('Pool deploy failed');
            
            // Track pool
            self.pools_by_index.entry(pool_count).write(pool_address);
            self.pool_by_id.entry(pool_id).write(pool_address);
            self.is_pool_map.entry(pool_address).write(true);
            self.pool_count.write(pool_count + 1);
            
            self.emit(PoolCreated {
                pool_address,
                pool_id,
                name,
                cap,
                jediswap_pct,
                ekubo_pct,
                timestamp,
            });
            
            pool_address
        }
        
        fn pause_pool(ref self: ContractState, pool_address: ContractAddress) {
            // Only owner can pause
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 'Only owner');
            
            // Verify it's a pool
            assert(self.is_pool_map.entry(pool_address).read(), 'Not a pool');
            
            // Call pause on pool
            let pool = IPoolDispatcher { contract_address: pool_address };
            pool.pause();
            
            self.emit(PoolPaused {
                pool_address,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn unpause_pool(ref self: ContractState, pool_address: ContractAddress) {
            // Only owner can unpause
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 'Only owner');
            
            // Verify it's a pool
            assert(self.is_pool_map.entry(pool_address).read(), 'Not a pool');
            
            // Call unpause on pool
            let pool = IPoolDispatcher { contract_address: pool_address };
            pool.unpause();
            
            self.emit(PoolUnpaused {
                pool_address,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn update_pool_cap(
            ref self: ContractState,
            pool_address: ContractAddress,
            new_cap: u256
        ) {
            // Only owner can update cap
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 'Only owner');
            
            // Verify it's a pool
            assert(self.is_pool_map.entry(pool_address).read(), 'Not a pool');
            
            // Get old cap
            let pool = IPoolDispatcher { contract_address: pool_address };
            let old_cap = pool.get_cap();
            
            // Update cap
            pool.update_cap(new_cap);
            
            self.emit(PoolCapUpdated {
                pool_address,
                old_cap,
                new_cap,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn get_pool_count(self: @ContractState) -> u32 {
            self.pool_count.read()
        }
        
        fn get_pool_by_index(self: @ContractState, index: u64) -> ContractAddress {
            self.pools_by_index.entry(index.try_into().unwrap()).read()
        }
        
        fn get_pool_by_id(self: @ContractState, pool_id: felt252) -> ContractAddress {
            self.pool_by_id.entry(pool_id).read()
        }
        
        fn is_pool(self: @ContractState, address: ContractAddress) -> bool {
            self.is_pool_map.entry(address).read()
        }
        
        fn get_owner(self: @ContractState) -> ContractAddress {
            self.owner.read()
        }
        
        fn transfer_ownership(ref self: ContractState, new_owner: ContractAddress) {
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 'Only owner');
            
            let previous_owner = owner;
            self.owner.write(new_owner);
            
            self.emit(OwnershipTransferred {
                previous_owner,
                new_owner,
                timestamp: get_block_timestamp(),
            });
        }
    }
}

