/**
 * Block Explorer URL utilities for Starknet
 * Provides helper functions to generate links to Starkscan for contracts, transactions, and fact registry queries
 */

export function getBlockExplorerUrl(network: string): string {
  if (network === 'sepolia') {
    return 'https://sepolia.starkscan.co';
  }
  return 'https://starkscan.co';
}

export function getContractUrl(address: string, network: string): string {
  if (!address || !address.startsWith('0x')) {
    return '';
  }
  return `${getBlockExplorerUrl(network)}/contract/${address}`;
}

export function getTransactionUrl(txHash: string, network: string): string {
  if (!txHash || !txHash.startsWith('0x')) {
    return '';
  }
  return `${getBlockExplorerUrl(network)}/tx/${txHash}`;
}

export function getFactRegistryQueryUrl(factHash: string, network: string): string {
  if (!factHash || !factHash.startsWith('0x')) {
    return '';
  }
  // Public FactRegistry address on Sepolia
  const registryAddress = '0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c';
  return `${getBlockExplorerUrl(network)}/contract/${registryAddress}#readContract`;
}

/**
 * Get a search URL for a hash (will search transactions, contracts, etc.)
 */
export function getSearchUrl(hash: string, network: string): string {
  if (!hash || !hash.startsWith('0x')) {
    return '';
  }
  return `${getBlockExplorerUrl(network)}/search?q=${hash}`;
}
