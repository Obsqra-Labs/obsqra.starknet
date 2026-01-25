import type { StarknetWindowObject } from '@starknet-io/types-js';
import {
  ConnectorNotConnectedError,
  InjectedConnector,
  type InjectedConnectorOptions,
} from '@starknet-react/core';
import type { AccountInterface, ProviderInterface, ProviderOptions } from 'starknet';
import { WalletAccount } from 'starknet';

const getWalletProvider = (id: string): StarknetWindowObject | undefined => {
  const globalObject = globalThis as unknown as Record<string, StarknetWindowObject | undefined>;
  return globalObject?.[`starknet_${id}`];
};

class PatchedInjectedConnector extends InjectedConnector {
  private readonly connectorId: string;

  constructor(options: InjectedConnectorOptions) {
    super({ options });
    this.connectorId = options.id;
  }

  async account(provider: ProviderOptions | ProviderInterface): Promise<AccountInterface> {
    const wallet = getWalletProvider(this.connectorId);
    if (!wallet) {
      throw new ConnectorNotConnectedError();
    }

    try {
      const accounts = await wallet.request({
        type: 'wallet_requestAccounts',
        params: { silent_mode: true },
      });

      if (!accounts || accounts.length === 0) {
        throw new ConnectorNotConnectedError();
      }
    } catch (error) {
      throw new ConnectorNotConnectedError();
    }

    return WalletAccount.connectSilent(provider as ProviderInterface, wallet);
  }
}

export const argentPatched = () =>
  new PatchedInjectedConnector({
    id: 'argentX',
    name: 'Argent X',
  });

export const braavosPatched = () =>
  new PatchedInjectedConnector({
    id: 'braavos',
    name: 'Braavos',
  });
