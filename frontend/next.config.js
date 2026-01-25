const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Disabled: obsqra.kit has compatibility issues with strict mode in dev
  experimental: {
    // Allow importing the local obsqra.kit package from outside the app directory.
    externalDir: true,
  },
  // Allow dev asset loads from the hosted domain during testing
  allowedDevOrigins: ['https://starknet.obsqra.fi'],
  transpilePackages: ['obsqra.kit'],
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
    return config;
  },
};

module.exports = nextConfig;
