import './globals.css';
import { StarknetProvider } from '@/providers/StarknetProvider';
import { AuthProvider } from '@/contexts/AuthContext';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Inter, Space_Grotesk } from 'next/font/google';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'obsqra.fi | Verifiable execution layer on Starknet',
  description:
    'obsqra.fi is a Starknet-native verifiable execution layer for DeFi. Allocation and execution are gated by on-chain proof verification. ' +
    'Proof-gated execution, on-chain model governance, privacy and selected disclosure. No proof, no execution.',
  keywords: [
    'verifiable AI',
    'STARK proofs',
    'Starknet',
    'Cairo',
    'DeFi',
    'risk engine',
    'constraint verification',
    'SHARP',
    'zk-ready',
  ],
};

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-body',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${spaceGrotesk.variable} ${inter.variable} font-sans bg-[#0a0a0b] text-white`}>
        <ErrorBoundary>
          <StarknetProvider>
            <AuthProvider>
              {children}
            </AuthProvider>
          </StarknetProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
