'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { docsStructure, type DocItem } from '@/lib/docs';
import { useRouter } from 'next/navigation';

interface DocsHeaderProps {
  onMenuClick: () => void;
}

function getAllDocs(): DocItem[] {
  const allDocs: DocItem[] = [];
  
  function flatten(items: DocItem[]) {
    for (const item of items) {
      if (item.children) {
        flatten(item.children);
      } else {
        allDocs.push(item);
      }
    }
  }
  
  flatten(docsStructure);
  return allDocs;
}

export function DocsHeader({ onMenuClick }: DocsHeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<DocItem[]>([]);
  const [showResults, setShowResults] = useState(false);
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const isDark = resolvedTheme === 'dark' || (!resolvedTheme && theme === 'dark');

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const query = searchQuery.toLowerCase();
    const allDocs = getAllDocs();
    const results = allDocs.filter(
      (doc) =>
        doc.title.toLowerCase().includes(query) ||
        doc.path.toLowerCase().includes(query)
    );
    
    setSearchResults(results.slice(0, 5));
    setShowResults(results.length > 0);
  }, [searchQuery]);

  const handleSearchSelect = (path: string) => {
    router.push(`/docs/${path}`);
    setSearchQuery('');
    setShowResults(false);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-white/5 dark:border-white/5 border-gray-200 dark:border-white/5 bg-[#0a0a0b]/80 dark:bg-[#0a0a0b]/80 bg-white/80 dark:bg-[#0a0a0b]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="lg:hidden text-white/50 hover:text-white transition-colors"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-emerald-400 to-cyan-400" />
            <span className="font-display text-base text-white group-hover:text-emerald-400 transition-colors">obsqra</span>
          </Link>
          <span className="text-white/30">/</span>
          <Link href="/docs" className="font-display text-base text-white/70 hover:text-white transition-colors">
            docs
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:block relative">
            <input
              type="text"
              placeholder="Search docs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchResults.length > 0 && setShowResults(true)}
              onBlur={() => setTimeout(() => setShowResults(false), 200)}
              className="w-64 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-emerald-400/50 focus:bg-white/10 transition-colors text-sm"
            />
            <svg
              className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/40"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {showResults && searchResults.length > 0 && (
              <div className="absolute top-full mt-2 w-64 bg-[#0a0a0b] border border-white/10 rounded-lg shadow-xl overflow-hidden z-50">
                {searchResults.map((doc) => (
                  <button
                    key={doc.path}
                    onClick={() => handleSearchSelect(doc.path)}
                    className="w-full text-left px-4 py-3 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors border-b border-white/5 last:border-0"
                  >
                    <div className="font-medium">{doc.title}</div>
                    <div className="text-xs text-white/40 font-mono mt-1">{doc.path}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
          {mounted && (
            <button
              onClick={() => setTheme(isDark ? 'light' : 'dark')}
              className="text-white/50 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5"
              aria-label="Toggle theme"
            >
              {isDark ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          )}
          <Link
            href="https://github.com/Obsqra-Labs/obsqra.starknet"
            target="_blank"
            rel="noopener noreferrer"
            className="text-white/50 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5"
            aria-label="GitHub"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
          </Link>
        </div>
      </div>
    </header>
  );
}
