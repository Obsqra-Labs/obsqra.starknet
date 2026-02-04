/**
 * Feature flags for zkML evolution stages (monorepo)
 */
export const FEATURES = {
  PROOF_GATED_EXECUTION: true,
  PARAMETERIZED_MODEL: process.env.NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL === 'true',
  MODEL_GOVERNANCE: process.env.NEXT_PUBLIC_ENABLE_MODEL_GOVERNANCE === 'true',
  ZKML_INFERENCE: process.env.NEXT_PUBLIC_ENABLE_ZKML === 'true',
  DAO_MODEL_APPROVAL: process.env.NEXT_PUBLIC_ENABLE_DAO_APPROVAL === 'true',
  AGENT_INTENTS: process.env.NEXT_PUBLIC_ENABLE_AGENT_INTENTS === 'true',
};

/**
 * Optional contract addresses per stage
 */
export const CONTRACTS = {
  RISK_ENGINE_V4: process.env.NEXT_PUBLIC_RISK_ENGINE_ADDRESS,
  RISK_ENGINE_V4_5: process.env.NEXT_PUBLIC_RISK_ENGINE_PARAMETERIZED,
  ZKML_VERIFIER: process.env.NEXT_PUBLIC_ZKML_VERIFIER,
  AGENT_ORCHESTRATOR: process.env.NEXT_PUBLIC_AGENT_ORCHESTRATOR,
};

/**
 * Frontend configuration validation
 * Ensures all required environment variables are set and valid
 */

interface FrontendConfig {
  rpcUrl: string;
  backendUrl: string;
  strategyRouterAddress: string;
  riskEngineAddress: string;
  modelRegistryAddress: string;
  networkName: 'sepolia' | 'mainnet';
  docsUrl: string;
  githubUrl: string;
  jediswapFactoryAddress: string;
  jediswapRouterAddress: string;
  mistChamberAddress: string; // NEW: MIST.cash chamber address
}

const REQUIRED_ENV_VARS = {
  NEXT_PUBLIC_RPC_URL: { default: 'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7', isDev: true },
  NEXT_PUBLIC_BACKEND_URL: { default: '', isDev: true }, // Empty = use relative path for Nginx proxy
  NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS: { default: '', isDev: true }, // V3 contract address
  NEXT_PUBLIC_RISK_ENGINE_ADDRESS: { default: '', isDev: true }, // Optional for now
  NEXT_PUBLIC_MODEL_REGISTRY_ADDRESS: { default: '', isDev: true }, // Optional for demo
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

  // Use Alchemy (most reliable) or fallback to publicnode
  const rpcUrl = process.env.NEXT_PUBLIC_RPC_URL || 
                 'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7';
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
  const strategyRouterAddress = process.env.NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS || '';
  const riskEngineAddress = process.env.NEXT_PUBLIC_RISK_ENGINE_ADDRESS || '';
  const modelRegistryAddress = process.env.NEXT_PUBLIC_MODEL_REGISTRY_ADDRESS || '';
  const networkName = (process.env.NEXT_PUBLIC_NETWORK || 'sepolia') as 'sepolia' | 'mainnet';

  // Validate address format (should be 0x... format)
  const validateAddress = (addr: string, name: string): void => {
    if (addr && !addr.startsWith('0x')) {
      console.warn(`Invalid ${name} format (should start with 0x): ${addr}`);
    }
  };

  validateAddress(strategyRouterAddress, 'Strategy Router Address');
  validateAddress(riskEngineAddress, 'Risk Engine Address');
  validateAddress(modelRegistryAddress, 'Model Registry Address');

  // JediSwap Sepolia addresses (from official documentation)
  const jediswapFactoryAddress = '0x050d3df81b920d3e608c4f7aeb67945a830413f618a1cf486bdcce66a395109c';
  const jediswapRouterAddress = '0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21';

  // MIST.cash Chamber address (mainnet - Sepolia not available)
  // Default: mainnet address from @mistcash/config
  const mistChamberAddress = process.env.NEXT_PUBLIC_MIST_CHAMBER_ADDRESS || 
    '0x063eab2f19523fc8578c66a3ddf248d72094c65154b6dd7680b6e05a64845277';

  return {
    rpcUrl,
    backendUrl,
    strategyRouterAddress: strategyRouterAddress as `0x${string}`,
    riskEngineAddress: riskEngineAddress as `0x${string}`,
    modelRegistryAddress: modelRegistryAddress as `0x${string}`,
    networkName,
    docsUrl: 'https://github.com/obsqra-labs/obsqra.starknet/tree/main/docs',
    githubUrl: 'https://github.com/obsqra-labs/obsqra.starknet',
    jediswapFactoryAddress,
    jediswapRouterAddress,
    mistChamberAddress,
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

/**
 * Get JediSwap factory address (Sepolia testnet)
 */
export function getJediSwapFactoryAddress(): string {
  return getConfig().jediswapFactoryAddress;
}

/**
 * Get JediSwap router address (Sepolia testnet, v2)
 */
export function getJediSwapRouterAddress(): string {
  return getConfig().jediswapRouterAddress;
}

export type { FrontendConfig };
