use starknet::ContractAddress;

// MIST Chamber interface (based on read_tx pattern)
#[starknet::interface]
pub trait IMistChamber<TContractState> {
    fn read_tx(self: @TContractState, secret: felt252) -> (ContractAddress, u256);
    // Returns: (token_address, amount)
}

