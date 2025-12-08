import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  clean: true,
  treeshake: true,
  external: ['react', '@starknet-react/core', '@starknet-react/chains', 'starknet'],
  minify: false,
  sourcemap: true,
  target: 'es2020',
});
