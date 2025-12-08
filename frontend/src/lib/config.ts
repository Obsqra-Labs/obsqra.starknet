/**
 * Frontend configuration validation
 * Ensures all required environment variables are set and valid
 */

interface FrontendConfig {
  rpcUrl: string;
  backendUrl: string;
  strategyRouterAddress: string;
  riskEngineAddress: string;
  networkName: 'sepolia' | 'mainnet';
  docsUrl: string;
  githubUrl: string;
}

const REQUIRED_ENV_VARS = {
  NEXT_PUBLIC_RPC_URL: { default: 'https://starknet-sepolia-rpc.publicnode.com', isDev: true },
  NEXT_PUBLIC_BACKEND_URL: { default: 'http://localhost:8000', isDev: true },
  NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS: { default: '', isDev: true }, // V2 not deployed yet - optional
  NEXT_PUBLIC_RISK_ENGINE_ADDRESS: { default: '', isDev: true }, // Optional for now
  NEXT_PUBLIC_NETWORK: { default: 'sepolia', isDev: true },
};

/**
 * Validate and load configuration
 */
function loadConfig(): FrontendConfig {
  const errors: string[] = [];

  // Validate required variables
  Object.entries(REQUIRED_ENV_VARS).forEach(([key, { isDev }]) => {
    const value = process.env[key];
    
    if (!value) {
      if (!isDev && process.env.NODE_ENV === 'production') {
        errors.push(`Missing required environment variable: ${key}`);
      }
    }
  });

  if (errors.length > 0) {
    console.error('Configuration Errors:', errors);
    console.warn('Some features may not work correctly without proper configuration.');
  }

  const rpcUrl = process.env.NEXT_PUBLIC_RPC_URL || 'https://starknet-sepolia-rpc.publicnode.com';
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  const strategyRouterAddress = process.env.NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS || '';
  const riskEngineAddress = process.env.NEXT_PUBLIC_RISK_ENGINE_ADDRESS || '';
  const networkName = (process.env.NEXT_PUBLIC_NETWORK || 'sepolia') as 'sepolia' | 'mainnet';

  // Validate address format (should be 0x... format)
  const validateAddress = (addr: string, name: string): void => {
    if (addr && !addr.startsWith('0x')) {
      console.warn(`Invalid ${name} format (should start with 0x): ${addr}`);
    }
  };

  validateAddress(strategyRouterAddress, 'Strategy Router Address');
  validateAddress(riskEngineAddress, 'Risk Engine Address');

  return {
    rpcUrl,
    backendUrl,
    strategyRouterAddress: strategyRouterAddress as `0x${string}`,
    riskEngineAddress: riskEngineAddress as `0x${string}`,
    networkName,
    docsUrl: 'https://github.com/obsqra-labs/obsqra.starknet/tree/main/docs',
    githubUrl: 'https://github.com/obsqra-labs/obsqra.starknet',
  };
}

let config: FrontendConfig | null = null;

/**
 * Get configuration (lazy-loaded)
 */
export function getConfig(): FrontendConfig {
  if (!config) {
    config = loadConfig();
  }
  return config;
}

/**
 * Check if a critical contract address is configured
 */
export function isContractConfigured(contractType: 'strategyRouter' | 'riskEngine'): boolean {
  const cfg = getConfig();
  const address = {
    strategyRouter: cfg.strategyRouterAddress,
    riskEngine: cfg.riskEngineAddress,
  }[contractType];

  return !!address && address !== '';
}

/**
 * Get a contract address or null if not configured
 */
export function getContractAddress(contractType: 'strategyRouter' | 'riskEngine'): `0x${string}` | null {
  if (!isContractConfigured(contractType)) {
    return null;
  }

  const cfg = getConfig();
  return {
    strategyRouter: cfg.strategyRouterAddress,
    riskEngine: cfg.riskEngineAddress,
  }[contractType] as `0x${string}`;
}

export type { FrontendConfig };
