use starknet::ContractAddress;
use starknet::get_caller_address;
use starknet::get_contract_address;

#[starknet::interface]
pub trait IMocksqraToken<TContractState> {
    fn name(self: @TContractState) -> ByteArray;
    fn symbol(self: @TContractState) -> ByteArray;
    fn decimals(self: @TContractState) -> u8;
    fn total_supply(self: @TContractState) -> u256;
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
    fn transfer(ref self: TContractState, recipient: ContractAddress, amount: u256) -> bool;
    fn transfer_from(
        ref self: TContractState,
        sender: ContractAddress,
        recipient: ContractAddress,
        amount: u256
    ) -> bool;
    fn approve(ref self: TContractState, spender: ContractAddress, amount: u256) -> bool;
    fn allowance(
        self: @TContractState,
        owner: ContractAddress,
        spender: ContractAddress
    ) -> u256;
    
    // Mint function for testing (not standard ERC20)
    fn mint(ref self: TContractState, to: ContractAddress, amount: u256);
}

#[starknet::contract]
mod MocksqraToken {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address,
        storage::Map
    };
    use core::num::traits::Zero;

    #[storage]
    struct Storage {
        name: ByteArray,
        symbol: ByteArray,
        decimals: u8,
        total_supply: u256,
        balances: Map<ContractAddress, u256>,
        allowances: Map<(ContractAddress, ContractAddress), u256>,
        minter: ContractAddress,  // Address that can mint
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        name: ByteArray,
        symbol: ByteArray,
        decimals: u8,
        initial_supply: u256,
        initial_recipient: ContractAddress
    ) {
        self.name.write(name);
        self.symbol.write(symbol);
        self.decimals.write(decimals);
        self.total_supply.write(initial_supply);
        self.balances.write(initial_recipient, initial_supply);
        self.minter.write(get_caller_address());
    }

    #[abi(embed_v0)]
    impl IMocksqraTokenImpl of super::IMocksqraToken<ContractState> {
        fn name(self: @ContractState) -> ByteArray {
            self.name.read()
        }

        fn symbol(self: @ContractState) -> ByteArray {
            self.symbol.read()
        }

        fn decimals(self: @ContractState) -> u8 {
            self.decimals.read()
        }

        fn total_supply(self: @ContractState) -> u256 {
            self.total_supply.read()
        }

        fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
            self.balances.read(account)
        }

        fn transfer(ref self: ContractState, recipient: ContractAddress, amount: u256) -> bool {
            let caller = get_caller_address();
            let caller_balance = self.balances.read(caller);
            assert(caller_balance >= amount, 'Insufficient balance');
            
            self.balances.write(caller, caller_balance - amount);
            let recipient_balance = self.balances.read(recipient);
            self.balances.write(recipient, recipient_balance + amount);
            
            true
        }

        fn transfer_from(
            ref self: ContractState,
            sender: ContractAddress,
            recipient: ContractAddress,
            amount: u256
        ) -> bool {
            let caller = get_caller_address();
            let allowance_key = (sender, caller);
            let allowance = self.allowances.read(allowance_key);
            assert(allowance >= amount, 'Insufficient allowance');
            
            let sender_balance = self.balances.read(sender);
            assert(sender_balance >= amount, 'Insufficient balance');
            
            self.allowances.write(allowance_key, allowance - amount);
            self.balances.write(sender, sender_balance - amount);
            let recipient_balance = self.balances.read(recipient);
            self.balances.write(recipient, recipient_balance + amount);
            
            true
        }

        fn approve(ref self: ContractState, spender: ContractAddress, amount: u256) -> bool {
            let owner = get_caller_address();
            let allowance_key = (owner, spender);
            self.allowances.write(allowance_key, amount);
            true
        }

        fn allowance(
            self: @ContractState,
            owner: ContractAddress,
            spender: ContractAddress
        ) -> u256 {
            self.allowances.read((owner, spender))
        }

        fn mint(ref self: ContractState, to: ContractAddress, amount: u256) {
            let caller = get_caller_address();
            assert(caller == self.minter.read(), 'Only minter can mint');
            
            let current_supply = self.total_supply.read();
            self.total_supply.write(current_supply + amount);
            
            let to_balance = self.balances.read(to);
            self.balances.write(to, to_balance + amount);
        }
    }
}



