import { getChamber, fetchTxAssets } from '@mistcash/sdk';
import { txSecret, txHash } from '@mistcash/crypto';
import { Provider } from 'starknet';

export class MistCashService {
  private provider: Provider;
  private chamberAddress: string;
  
  constructor(provider: Provider, chamberAddress: string) {
    this.provider = provider;
    this.chamberAddress = chamberAddress;
  }
  
  async getChamber() {
    return await getChamber(this.provider, this.chamberAddress);
  }
  
  async deposit(amount: bigint, recipientAddress: string, claimingKey: string) {
    const chamber = await this.getChamber();
    const secret = await txSecret(claimingKey, recipientAddress);
    
    const tx = await chamber.deposit(amount, secret);
    await tx.wait();
    
    return tx.hash;
  }
  
  async withdraw(secret: string, recipientAddress: string, amount: bigint) {
    const chamber = await this.getChamber();
    
    const tx = await chamber.withdraw(secret, recipientAddress, amount);
    await tx.wait();
    
    return tx.hash;
  }
  
  async fetchAssets() {
    return await fetchTxAssets(this.provider, this.chamberAddress);
  }
}

