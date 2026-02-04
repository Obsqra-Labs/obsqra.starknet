pragma circom 2.1.6;

// Private deposit: prove commitment = hash(amount, nonce) and balance >= amount.
// Public outputs: commitment, amount_public (for contract to credit).
// Use circomlib Poseidon; if not installed, this is a placeholder - replace with actual include.
include "node_modules/circomlib/circuits/comparators.circom";

template PrivateDeposit() {
    signal input amount;
    signal input nonce;
    signal input balance;

    signal output commitment;
    signal output amount_public;

    // Constraint: balance >= amount (user has enough)
    // Use LessThan component from circomlib
    component lt = LessThan(252);
    lt.in[0] <== amount;
    lt.in[1] <== balance + 1;
    lt.out === 1;

    // Commitment = hash(amount, nonce). Minimal: use product for demo; replace with Poseidon in production.
    commitment <== amount * 0x10000 + nonce;
    amount_public <== amount;
}

component main = PrivateDeposit();
