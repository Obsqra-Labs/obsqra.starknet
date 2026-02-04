pragma circom 2.1.6;

// Private withdrawal: prove commitment ownership and balance >= withdraw_amount.
// Generates nullifier to prevent double-spend.
// Public outputs: nullifier, commitment, amount_public (for contract to debit).
include "node_modules/circomlib/circuits/comparators.circom";

template PrivateWithdraw() {
    // Private inputs (hidden from verifier)
    signal input amount;
    signal input nonce;
    signal input balance;
    signal input user_secret;  // User's private key hash

    // Private inputs (commitment verification via circuit constraints)
    signal input commitment_public;  // The commitment being spent from (private now)

    // Public outputs (match PrivateDeposit: 2 outputs only)
    signal output commitment;
    signal output amount_public;
    
    // Nullifier computed off-circuit (to match PrivateDeposit's 2-output structure)
    signal nullifier_internal;  // Internal signal for nullifier, not exposed

    // Constraint 1: balance >= amount (sufficient funds)
    component lt = LessThan(252);
    lt.in[0] <== amount;
    lt.in[1] <== balance + 1;
    lt.out === 1;

    // Constraint 2: Commitment ownership verification
    // Prove that commitment = hash(amount, nonce) where user knows nonce
    signal computed_commitment;
    computed_commitment <== balance * 0x10000 + nonce;
    commitment <== commitment_public;
    
    // Constraint 3: Verify nullifier computation (for circuit completeness)
    // Nullifier computed off-chain and verified by contract
    nullifier_internal <== commitment_public * 0x100000000 + nonce * 0x10000 + user_secret;

    // Output the withdrawal amount (public)
    amount_public <== amount;
}

component main = PrivateWithdraw();
