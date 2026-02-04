//! Model Registry Contract
//! Tracks model versions, hashes, and provenance for zkML system

use core::array::{ArrayTrait, SpanTrait};

#[derive(Drop, Serde, starknet::Store)]
struct ModelVersion {
    version: felt252,
    model_hash: felt252,
    deployed_at: u64,
    description: ByteArray,
    is_active: bool,
}

#[derive(Drop, starknet::Event)]
struct ModelRegistered {
    #[key]
    version: felt252,
    #[key]
    model_hash: felt252,
    // Note: description omitted to avoid ByteArray move issues
    // Clients can query the model version to get the description
}

#[starknet::interface]
trait IModelRegistry<TContractState> {
    fn register_model_version(
        ref self: TContractState,
        version: felt252,
        model_hash: felt252,
        description: ByteArray
    ) -> ModelVersion;
    
    fn get_current_model(self: @TContractState) -> ModelVersion;
    fn get_model_version(self: @TContractState, version: felt252) -> Option<ModelVersion>;
    fn get_model_history(self: @TContractState) -> Span<felt252>;  // Returns version numbers only
}

#[starknet::contract]
mod ModelRegistry {
    use starknet::{
        ContractAddress, get_caller_address,
        storage::{
            StoragePointerReadAccess, StoragePointerWriteAccess,
            StorageMapReadAccess, StorageMapWriteAccess,
            Map
        },
    };
    use core::starknet::event::EventEmitter;
    use super::{ModelVersion, ModelRegistered};

    #[storage]
    struct Storage {
        owner: ContractAddress,
        current_version: felt252,
        model_versions: Map<felt252, ModelVersion>,
        version_count: felt252,  // Track number of versions
        versions_by_index: Map<felt252, felt252>,  // index -> version (for history)
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        ModelRegistered: ModelRegistered,
    }

    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
        self.current_version.write(0);
    }

    #[abi(embed_v0)]
    impl ModelRegistryImpl of super::IModelRegistry<ContractState> {
        fn register_model_version(
            ref self: ContractState,
            version: felt252,
            model_hash: felt252,
            description: ByteArray
        ) -> ModelVersion {
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 1);
            
            // Note: We don't update old versions' is_active field to avoid ByteArray copy issues
            // The current_version pointer effectively marks which is active
            let _current = self.current_version.read();
            
            let timestamp = starknet::get_block_timestamp();
            let new_version = ModelVersion {
                version,
                model_hash,
                deployed_at: timestamp,
                description,  // Now we can move description into struct
                is_active: true,
            };
            
            self.model_versions.write(version, new_version);
            self.current_version.write(version);
            
            // Add to version history (using Map instead of Vec for compatibility)
            let count = self.version_count.read();
            self.versions_by_index.write(count, version);
            self.version_count.write(count + 1);
            
            // Emit event after storing (description is in stored struct)
            self.emit(ModelRegistered {
                version,
                model_hash,
            });
            
            // Return the stored version (read back from storage)
            self.model_versions.read(version)
        }
        
        fn get_current_model(self: @ContractState) -> ModelVersion {
            let version = self.current_version.read();
            if version == 0 {
                ModelVersion {
                    version: 0,
                    model_hash: 0,
                    deployed_at: 0,
                    description: "",
                    is_active: false,
                }
            } else {
                self.model_versions.read(version)
            }
        }
        
        fn get_model_version(self: @ContractState, version: felt252) -> Option<ModelVersion> {
            if version == 0 {
                return Option::None;
            }
            let model = self.model_versions.read(version);
            if model.version == 0 && model.model_hash == 0 {
                Option::None
            } else {
                Option::Some(model)
            }
        }
        
        fn get_model_history(self: @ContractState) -> Span<felt252> {
            // Return version numbers only (callers can query full models if needed)
            let count = self.version_count.read();
            let mut history = ArrayTrait::new();
            let mut i: felt252 = 0;
            while i != count {
                let version = self.versions_by_index.read(i);
                history.append(version);
                i += 1;
            };
            history.span()
        }
    }
}
