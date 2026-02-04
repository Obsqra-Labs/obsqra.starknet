'use client';

import { useState, useEffect } from 'react';
import { ThemeProvider } from 'next-themes';
import { DocsSidebar } from '@/components/docs/DocsSidebar';
import { DocsHeader } from '@/components/docs/DocsHeader';
import { usePathname } from 'next/navigation';

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-[#0a0a0b] text-white flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-emerald-400/30 border-t-emerald-400 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <div className="min-h-screen bg-[#0a0a0b] dark:bg-[#0a0a0b] bg-white text-white dark:text-white">
        <DocsHeader onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <div className="flex">
          <DocsSidebar isOpen={sidebarOpen} currentPath={pathname || ''} />
          <main
            className={`flex-1 transition-all duration-300 ${
              sidebarOpen ? 'lg:ml-64' : 'lg:ml-0'
            }`}
          >
            <div className="max-w-4xl mx-auto px-6 py-12">
              {children}
            </div>
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}
