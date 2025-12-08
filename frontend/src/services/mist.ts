import type { ProviderInterface, AccountInterface } from 'starknet';
import { getChamber, fetchTxAssets, checkTxExists } from '@mistcash/sdk';
import { txSecret, txHash } from '@mistcash/crypto';

export interface MistAsset {
  token: string;
  amount: bigint;
  decimals: number;
}

export interface MistTransaction {
  hash: string;
  isPending: boolean;
  error?: string;
}

/**
 * Service for interacting with MIST.cash privacy protocol on Starknet
 * Handles private deposits and withdrawals with claiming key management
 */
export class MistCashService {
  private provider: ProviderInterface;
  private account?: AccountInterface;
  private chamberAddress: string;
  
  constructor(provider: ProviderInterface, chamberAddress: string, account?: AccountInterface) {
    this.provider = provider;
    this.chamberAddress = chamberAddress;
    this.account = account;
  }
  
  /**
   * Get the MIST Chamber contract instance
   */
  async getChamber() {
    try {
      // MIST Chamber is accessed through the provider
      // The chamber address is set in the constructor
      console.log('MIST Chamber address:', this.chamberAddress);
      return { provider: this.provider, address: this.chamberAddress };
    } catch (error) {
      console.error('Failed to initialize MIST Chamber:', error);
      throw new Error('Failed to initialize MIST Chamber contract');
    }
  }
  
  /**
   * Deposit funds into MIST privacy pool
   * Generates a claiming key that must be securely shared with recipient
   */
  async deposit(amount: bigint, recipientAddress: string, claimingKey: string): Promise<string> {
    if (!this.account) {
      throw new Error('Account not connected. Cannot execute deposit transaction.');
    }

    try {
      const chamber = await this.getChamber();
      
      // Generate transaction secret from claiming key and recipient
      const secret = await txSecret(claimingKey, recipientAddress);
      
      console.log('Initiating MIST deposit:', {
        amount: amount.toString(),
        recipient: recipientAddress,
        chamber: this.chamberAddress,
        secretHash: secret,
      });

      // Execute deposit transaction through the account
      // The account must have STRK tokens to approve and deposit
      const tx = await this.account.execute([
        {
          contractAddress: this.chamberAddress,
          entrypoint: 'deposit',
          calldata: [recipientAddress, amount.toString(), secret],
        },
      ]);

      console.log('MIST deposit transaction submitted:', tx.transaction_hash);
      return tx.transaction_hash;
    } catch (error) {
      console.error('MIST deposit failed:', error);
      throw error instanceof Error 
        ? error 
        : new Error(`Deposit failed: ${String(error)}`);
    }
  }
  
  /**
   * Withdraw funds from MIST privacy pool using claiming secret
   * The secret must match the one provided during deposit
   */
  async withdraw(secret: string, recipientAddress: string, amount: bigint): Promise<string> {
    if (!this.account) {
      throw new Error('Account not connected. Cannot execute withdrawal transaction.');
    }

    try {
      const chamber = await this.getChamber();
      
      console.log('Initiating MIST withdrawal:', {
        amount: amount.toString(),
        recipient: recipientAddress,
        chamber: this.chamberAddress,
      });

      // Execute withdrawal transaction
      // The secret is used to verify the user has rights to claim this transaction
      const tx = await this.account.execute([
        {
          contractAddress: this.chamberAddress,
          entrypoint: 'withdraw',
          calldata: [secret, recipientAddress, amount.toString()],
        },
      ]);

      console.log('MIST withdrawal transaction submitted:', tx.transaction_hash);
      return tx.transaction_hash;
    } catch (error) {
      console.error('MIST withdrawal failed:', error);
      throw error instanceof Error 
        ? error 
        : new Error(`Withdrawal failed: ${String(error)}`);
    }
  }
  
  /**
   * Fetch available assets for a specific transaction
   * Returns list of assets that were sent in the private transaction
   */
  async fetchAssets(claimingKey: string, recipientAddress: string): Promise<MistAsset[]> {
    try {
      // TODO: Implement asset fetching with updated MIST SDK
      // const chamber = await this.getChamber();
      // const assets = await fetchTxAssets(chamber, claimingKey, recipientAddress);
      
      console.log('MIST asset fetching not yet implemented');
      return [];
    } catch (error) {
      console.error('Failed to fetch MIST assets:', error);
      return [];
    }
  }
  
  /**
   * Check if a transaction exists with specified parameters
   * Useful for verifying a transaction was created before attempting to claim
   */
  async checkTransactionExists(
    claimingKey: string,
    recipientAddress: string,
    tokenAddress: string,
    amount: bigint
  ): Promise<boolean> {
    try {
      // TODO: Implement transaction existence check with updated MIST SDK
      // const chamber = await this.getChamber();
      // const exists = await checkTxExists(chamber, claimingKey, recipientAddress, tokenAddress, amount.toString());
      
      console.log('Transaction existence check not yet implemented');
      return false;
    } catch (error) {
      console.error('Failed to check transaction existence:', error);
      return false;
    }
  }
  
  /**
   * Compute transaction hash for verification purposes
   * Can be used to verify transaction integrity
   */
  async computeTransactionHash(
    claimingKey: string,
    recipientAddress: string,
    tokenAddress: string,
    amount: bigint
  ): Promise<string> {
    try {
      const hash = await txHash(claimingKey, recipientAddress, tokenAddress, amount.toString());
      return String(hash);
    } catch (error) {
      console.error('Failed to compute transaction hash:', error);
      throw error instanceof Error 
        ? error 
        : new Error('Failed to compute transaction hash');
    }
  }
}
