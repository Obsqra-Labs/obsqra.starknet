import type { Metadata } from "next";
import "./globals.css";
import { StarknetProvider } from "@/components/zkdefi/StarknetProvider";
import { AppProvider } from "@/lib/AppContext";
import { ToastContainer } from "@/components/zkdefi/Toast";

export const metadata: Metadata = {
  title: "zkde.fi by Obsqra Labs | zkDE + AEGIS",
  description: "zkde.fi — First AEGIS-compatible app. Zero-Knowledge Deterministic Environment (zkDE) + Autonomous Execution Gated Intent Standard (AEGIS). Trustless AI execution on Starknet. Proof-gated autonomous agent for private DeFi. Starknet Re{define} Hackathon (Privacy track). Open source.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased" suppressHydrationWarning>
      <body
        className="min-h-screen bg-zinc-950 text-zinc-100"
        style={{
          backgroundColor: "#09090b",
          color: "#f4f4f5",
          minHeight: "100vh",
          WebkitFontSmoothing: "antialiased",
        }}
      >
        <StarknetProvider>
          <AppProvider>
            {children}
            <ToastContainer />
          </AppProvider>
        </StarknetProvider>
      </body>
    </html>
  );
}
