// Confidential transfer: Garaga Groth16 verifier + real ERC20 token. No mocks.
use starknet::ContractAddress;

#[starknet::interface]
pub trait IGaragaVerifier<TContractState> {
    fn verify_groth16_proof_bn254(
        self: @TContractState,
        full_proof_with_hints: Span<felt252>
    ) -> Result<Span<u256>, felt252>;
}

#[starknet::interface]
pub trait IConfidentialTransfer<TContractState> {
    fn private_deposit(
        ref self: TContractState,
        commitment: felt252,
        amount_public: u256,
        proof_calldata: Span<felt252>
    );
    fn private_withdraw(
        ref self: TContractState,
        nullifier: felt252,
        commitment: felt252,
        amount_public: u256,
        proof_calldata: Span<felt252>,
        recipient: ContractAddress
    );
    fn get_commitment_balance(self: @TContractState, commitment: felt252) -> u256;
    fn get_garaga_verifier_deposit(self: @TContractState) -> ContractAddress;
    fn get_garaga_verifier_withdraw(self: @TContractState) -> ContractAddress;
    fn get_token(self: @TContractState) -> ContractAddress;
}

#[starknet::contract]
mod ConfidentialTransfer {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address,
        storage::{Map, StoragePointerReadAccess, StoragePointerWriteAccess,
                  StorageMapReadAccess, StorageMapWriteAccess}
    };

    use super::IGaragaVerifierDispatcher;
    use super::IGaragaVerifierDispatcherTrait;
    use crate::erc20_interface::IERC20Dispatcher;
    use crate::erc20_interface::IERC20DispatcherTrait;

    #[storage]
    struct Storage {
        garaga_verifier_deposit: ContractAddress,
        garaga_verifier_withdraw: ContractAddress,
        token: ContractAddress,
        commitment_balance: Map<felt252, u256>,
        nullifiers: Map<felt252, bool>,
        admin: ContractAddress,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        garaga_verifier_deposit: ContractAddress,
        garaga_verifier_withdraw: ContractAddress,
        token: ContractAddress,
        admin: ContractAddress
    ) {
        self.garaga_verifier_deposit.write(garaga_verifier_deposit);
        self.garaga_verifier_withdraw.write(garaga_verifier_withdraw);
        self.token.write(token);
        self.admin.write(admin);
    }

    #[abi(embed_v0)]
    impl ConfidentialTransferImpl of super::IConfidentialTransfer<ContractState> {
        fn private_deposit(
            ref self: ContractState,
            commitment: felt252,
            amount_public: u256,
            proof_calldata: Span<felt252>
        ) {
            assert(amount_public > 0, 'Amount must be positive');
            let caller = get_caller_address();

            let verifier = IGaragaVerifierDispatcher { contract_address: self.garaga_verifier_deposit.read() };
            let result = verifier.verify_groth16_proof_bn254(proof_calldata);
            assert(result.is_ok(), 'Invalid proof');

            let token = IERC20Dispatcher { contract_address: self.token.read() };
            let ok = token.transfer_from(caller, get_contract_address(), amount_public);
            assert(ok, 'Transfer failed');

            let current = self.commitment_balance.read(commitment);
            self.commitment_balance.write(commitment, current + amount_public);
        }

        fn private_withdraw(
            ref self: ContractState,
            nullifier: felt252,
            commitment: felt252,
            amount_public: u256,
            proof_calldata: Span<felt252>,
            recipient: ContractAddress
        ) {
            assert(amount_public > 0, 'Amount must be positive');
            assert(!self.nullifiers.read(nullifier), 'Nullifier already used');

            let verifier = IGaragaVerifierDispatcher { contract_address: self.garaga_verifier_withdraw.read() };
            let result = verifier.verify_groth16_proof_bn254(proof_calldata);
            assert(result.is_ok(), 'Invalid proof');

            self.nullifiers.write(nullifier, true);

            let current = self.commitment_balance.read(commitment);
            assert(current >= amount_public, 'Insufficient commitment balance');
            self.commitment_balance.write(commitment, current - amount_public);

            let token = IERC20Dispatcher { contract_address: self.token.read() };
            let ok = token.transfer(recipient, amount_public);
            assert(ok, 'Transfer to recipient failed');
        }

        fn get_commitment_balance(self: @ContractState, commitment: felt252) -> u256 {
            self.commitment_balance.read(commitment)
        }

        fn get_garaga_verifier_deposit(self: @ContractState) -> ContractAddress {
            self.garaga_verifier_deposit.read()
        }

        fn get_garaga_verifier_withdraw(self: @ContractState) -> ContractAddress {
            self.garaga_verifier_withdraw.read()
        }

        fn get_token(self: @ContractState) -> ContractAddress {
            self.token.read()
        }
    }
}
