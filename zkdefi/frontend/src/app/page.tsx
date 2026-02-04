"use client";

import Link from "next/link";
import { Shield, Lock, Eye, ArrowRight, CheckCircle2, ExternalLink } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-surface-0 text-white">
      {/* Header */}
      <header className="border-b border-zinc-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg">zkde.fi</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/agent" className="text-sm text-zinc-400 hover:text-white transition-colors">Dashboard</Link>
            <Link href="/profile" className="text-sm text-zinc-400 hover:text-white transition-colors">Profile</Link>
            <Link
              href="/agent"
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-medium transition-all hover:shadow-lg hover:shadow-emerald-500/20 flex items-center gap-2"
            >
              Launch App
              <ArrowRight className="w-4 h-4" />
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-20 relative overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-950/20 via-transparent to-violet-950/20" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.1),transparent_50%)]" />

        <div className="max-w-4xl mx-auto text-center relative z-10 animate-fade-in">
          <div>
            <p className="text-xs font-mono text-zinc-500 tracking-wider mb-6 uppercase">
              Starknet Re{"{define}"} Hackathon · Privacy track · Obsqra Labs
            </p>
            <p className="text-sm font-mono text-emerald-400/90 mb-4">
              zkDE · Zero-Knowledge Deterministic Environment · AEGIS · Autonomous Execution Gated Intent Standard
            </p>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6 tracking-tight bg-gradient-to-r from-white via-emerald-100 to-violet-100 bg-clip-text text-transparent">
              Your DeFi. Invisible. Verifiable.
            </h1>
            <p className="text-xl text-zinc-300 mb-10 leading-relaxed max-w-2xl mx-auto">
              First app in a new class: trustless AI execution on Starknet. Proof-gated autonomous agent for private DeFi — delegate once via session keys; every action verified on-chain. No proof, no execution. Built on zkDE; implements AEGIS.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/agent"
                className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-semibold text-white transition-all hover:shadow-lg hover:shadow-emerald-500/20 flex items-center gap-2"
              >
                Launch App
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="https://github.com/obsqra-labs/zkdefi"
                target="_blank"
                rel="noopener noreferrer"
                className="px-8 py-4 border border-zinc-700 hover:border-zinc-600 rounded-lg font-medium transition-all flex items-center gap-2"
              >
                View on GitHub
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props Section */}
      <section className="px-6 py-20 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Privacy by Design</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              Three pillars of privacy that make zkde.fi the most secure DeFi agent on Starknet
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: "Intent Hiding",
                description: "Agent decisions stay hidden until execution. Proof-gated, no broadcast until verified. MEV and front-running protection.",
                color: "emerald",
              },
              {
                icon: Lock,
                title: "Confidential Transactions",
                description: "Amount-hiding transfers using Garaga Groth16 on Sepolia. Only commitments visible on-chain.",
                color: "violet",
              },
              {
                icon: Eye,
                title: "Selective Disclosure",
                description: "Prove compliance without revealing strategy or full history. Perfect for KYC and regulatory requirements.",
                color: "cyan",
              },
            ].map((prop, i) => {
              const Icon = prop.icon;
              return (
                <div
                  key={prop.title}
                  className="glass rounded-2xl border border-zinc-800 p-8 hover:border-zinc-700 transition-all group"
                >
                  <div className={`w-16 h-16 rounded-xl bg-${prop.color}-600/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                    <Icon className={`w-8 h-8 text-${prop.color}-400`} />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{prop.title}</h3>
                  <p className="text-zinc-400 leading-relaxed">{prop.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="px-6 py-20 border-t border-zinc-800 bg-zinc-950/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-zinc-400">In the zkDE (Zero-Knowledge Deterministic Environment), AEGIS defines how agents run: proof-gated execution that unlocks trustless AI, autonomous agents, and conditional execution.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Set Constraints", desc: "Define your risk parameters and limits" },
              { step: "2", title: "Generate Proof", desc: "Zero-knowledge proof verifies your constraints" },
              { step: "3", title: "Execute", desc: "Contract only executes if proof is valid" },
            ].map((item, i) => (
              <div key={item.step} className="relative">
                <div className="glass rounded-2xl border border-zinc-800 p-8 text-center">
                  <div className="w-12 h-12 rounded-full bg-emerald-600 flex items-center justify-center mx-auto mb-4">
                    <span className="text-xl font-bold">{item.step}</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-400">{item.desc}</p>
                </div>
                {i < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="w-8 h-8 text-zinc-600" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="px-6 py-12 border-t border-zinc-800">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-zinc-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Starknet Re{"{define}"} Hackathon · Privacy track</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Contracts verified on Sepolia</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Open source</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Powered by Integrity + Garaga</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Obsqra Labs · Infrastructure for trustless AI</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800 px-6 py-8">
        <div className="max-w-7xl mx-auto text-center space-y-2">
          <p className="text-xs text-zinc-500">
            zkde.fi by Obsqra Labs · open source ·{" "}
            <a href="https://obsqra.fi" target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:text-emerald-300">
              obsqra.fi
            </a>
          </p>
          <p className="text-xs text-zinc-600 max-w-xl mx-auto">
            zkDE (Zero-Knowledge Deterministic Environment) is the framework; AEGIS (Autonomous Execution Gated Intent Standard) is the standard for agents in that environment. Obsqra Labs builds infrastructure for trustless AI execution on Starknet — zkde.fi is the first AEGIS-compatible app.
          </p>
        </div>
      </footer>
    </main>
  );
}
