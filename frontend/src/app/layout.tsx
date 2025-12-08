import './globals.css';
import { StarknetProvider } from '@/providers/StarknetProvider';
import { AuthProvider } from '@/contexts/AuthContext';
import { Inter, Space_Grotesk } from 'next/font/google';

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
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${inter.variable} font-sans bg-sand text-ink`}>
        <StarknetProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </StarknetProvider>
      </body>
    </html>
  );
}

