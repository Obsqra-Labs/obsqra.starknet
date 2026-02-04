'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { docsStructure, type DocItem } from '@/lib/docs';

interface DocsSidebarProps {
  isOpen: boolean;
  currentPath: string | null;
}

export function DocsSidebar({ isOpen, currentPath }: DocsSidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['01-introduction', '02-user-guides'])
  );

  const toggleSection = (path: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedSections(newExpanded);
  };

  const isActive = (path: string) => {
    return currentPath === `/docs/${path}` || (currentPath || '') === `/docs/${path}`;
  };

  const renderItem = (item: DocItem, level: number = 0) => {
    if (item.children) {
      const isExpanded = expandedSections.has(item.path);
      return (
        <div key={item.path}>
          <button
            onClick={() => toggleSection(item.path)}
            className={`w-full text-left px-4 py-2.5 text-sm font-medium transition-colors ${
              level === 0
                ? 'text-white/70 hover:text-white border-b border-white/5'
                : 'text-white/50 hover:text-white/70'
            }`}
            style={{ paddingLeft: `${level * 16 + 16}px` }}
          >
            <span className="flex items-center justify-between">
              <span>{item.title}</span>
              <span className={`transition-transform ${isExpanded ? 'rotate-90' : ''}`}>›</span>
            </span>
          </button>
          {isExpanded && (
            <div className="ml-2">
              {item.children.map((child) => renderItem(child, level + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <Link
        key={item.path}
        href={`/docs/${item.path}`}
        className={`block px-4 py-2.5 text-sm transition-colors ${
          isActive(item.path)
            ? 'text-emerald-400 bg-emerald-400/10 border-l-2 border-emerald-400'
            : 'text-white/50 hover:text-white/80 hover:bg-white/5'
        }`}
        style={{ paddingLeft: `${level * 16 + 16}px` }}
      >
        {item.title}
      </Link>
    );
  };

  return (
    <aside
      className={`fixed left-0 top-14 h-[calc(100vh-3.5rem)] bg-[#0a0a0b] dark:bg-[#0a0a0b] bg-white border-r border-white/5 dark:border-white/5 border-gray-200 dark:border-white/5 overflow-y-auto transition-transform duration-300 z-40 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 w-64`}
    >
      <div className="p-4">
        <div className="mb-6">
          <Link href="/docs" className="flex items-center gap-2 group">
            <div className="w-5 h-5 rounded bg-gradient-to-br from-emerald-400 to-cyan-400" />
            <span className="font-display text-lg font-semibold text-white group-hover:text-emerald-400 transition-colors">
              Obsqra Docs
            </span>
          </Link>
        </div>
        <nav className="space-y-1">
          {docsStructure.map((section) => renderItem(section))}
        </nav>
      </div>
    </aside>
  );
}
