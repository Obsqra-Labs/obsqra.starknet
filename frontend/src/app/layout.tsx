import './globals.css';
import { StarknetProvider } from '@/providers/StarknetProvider';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <StarknetProvider>
          {children}
        </StarknetProvider>
      </body>
    </html>
  );
}


