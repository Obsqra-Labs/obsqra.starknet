const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Stage 3A: enable On-Chain AI section and ModelParamsViewer on landing (override with .env.local if needed)
  env: {
    NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL: process.env.NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL ?? 'true',
  },
  reactStrictMode: false, // Disabled: obsqra.kit has compatibility issues with strict mode in dev
  experimental: {
    // Allow importing the local obsqra.kit package from outside the app directory.
    externalDir: true,
  },
  // Allow dev asset loads from the hosted domain during testing
  allowedDevOrigins: ['https://starknet.obsqra.fi'],
  transpilePackages: ['obsqra.kit'],
  // Proxy API requests to backend
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8002';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/health',
        destination: `${backendUrl}/health`,
      },
    ];
  },
  webpack: (config) => {
    // Ensure modules resolve from this app's node_modules when importing externalDir packages.
    config.resolve.modules = [
      ...(config.resolve.modules || []),
      path.resolve(__dirname, 'node_modules'),
    ];
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    // Allow reading files from docs directory
    config.resolve.alias = {
      ...config.resolve.alias,
    };
    return config;
  },
};

module.exports = nextConfig;
