'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeMermaid from 'rehype-mermaid';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Link from 'next/link';
import { docsStructure, type DocItem } from '@/lib/docs';
import { usePathname } from 'next/navigation';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { MermaidDiagram } from './MermaidDiagram';

interface MarkdownRendererProps {
  content: string;
}

function getNextDoc(path: string): DocItem | null {
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
  
  const currentIndex = allDocs.findIndex((doc) => doc.path === path);
  if (currentIndex >= 0 && currentIndex < allDocs.length - 1) {
    return allDocs[currentIndex + 1];
  }
  return null;
}

function getPrevDoc(path: string): DocItem | null {
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
  
  const currentIndex = allDocs.findIndex((doc) => doc.path === path);
  if (currentIndex > 0) {
    return allDocs[currentIndex - 1];
  }
  return null;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const pathname = usePathname();
  const currentPath = (pathname || '').replace('/docs/', '');
  const nextDoc = getNextDoc(currentPath);
  const prevDoc = getPrevDoc(currentPath);
  const { theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const isDark = resolvedTheme === 'dark' || (!resolvedTheme && theme === 'dark');

  useEffect(() => {
    setMounted(true);
  }, []);

  // Process internal links
  const processedContent = content.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    (match, text, href) => {
      if (href.startsWith('http')) {
        return match; // External link, keep as is
      }
      // Internal link - convert to /docs path
      if (href.startsWith('../')) {
        const parts = currentPath.split('/');
        const levels = (href.match(/\.\.\//g) || []).length;
        const newPath = parts.slice(0, -levels - 1).join('/') + '/' + href.replace(/\.\.\//g, '');
        return `[${text}](/docs/${newPath})`;
      }
      if (href.startsWith('./') || !href.startsWith('/')) {
        const basePath = currentPath.split('/').slice(0, -1).join('/');
        const newPath = basePath ? `${basePath}/${href.replace('./', '')}` : href.replace('./', '');
        return `[${text}](/docs/${newPath})`;
      }
      return match;
    }
  );

  return (
    <div className="docs-content">
      <article className="prose prose-invert prose-lg max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ node, ...props }) => (
              <h1 className="font-display text-5xl md:text-6xl leading-[1.05] mb-6 mt-12 text-white border-b border-white/10 pb-4" {...props} />
            ),
            h2: ({ node, ...props }) => (
              <h2 className="font-display text-3xl md:text-4xl leading-tight mb-4 mt-10 text-white border-b border-white/10 pb-2" {...props} />
            ),
            h3: ({ node, ...props }) => (
              <h3 className="font-display text-2xl md:text-3xl leading-tight mb-3 mt-8 text-white" {...props} />
            ),
            h4: ({ node, ...props }) => (
              <h4 className="font-display text-xl md:text-2xl leading-tight mb-2 mt-6 text-white/90" {...props} />
            ),
            p: ({ node, ...props }) => (
              <p className="text-lg text-white/70 leading-relaxed mb-6" {...props} />
            ),
            a: ({ node, href, ...props }) => {
              if (href?.startsWith('/docs/')) {
                return (
                  <Link
                    href={href}
                    className="text-emerald-400 hover:text-cyan-400 underline underline-offset-2 transition-colors"
                    {...props}
                  />
                );
              }
              return (
                <a
                  href={href}
                  target={href?.startsWith('http') ? '_blank' : undefined}
                  rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
                  className="text-emerald-400 hover:text-cyan-400 underline underline-offset-2 transition-colors"
                  {...props}
                />
              );
            },
            code: ({ node, className, children, ...props }: any) => {
              const match = /language-(\w+)/.exec(className || '');
              const language = match ? match[1] : '';
              const inline = !className || !match;
              
              if (language === 'mermaid') {
                return <MermaidDiagram chart={String(children).replace(/\n$/, '')} isDark={isDark} />;
              }
              
              if (!inline && language) {
                return (
                  <div className="my-6 rounded-lg overflow-hidden border border-white/10">
                    <SyntaxHighlighter
                      style={isDark ? vscDarkPlus : oneLight}
                      language={language}
                      PreTag="div"
                      className="!bg-[#0a0a0b] !text-sm"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  </div>
                );
              }
              
              return (
                <code
                  className="bg-white/10 text-emerald-300 px-2 py-1 rounded text-sm font-mono border border-white/10"
                  {...props}
                >
                  {children}
                </code>
              );
            },
            ul: ({ node, ...props }) => (
              <ul className="list-disc list-inside mb-6 text-white/70 space-y-2 ml-4" {...props} />
            ),
            ol: ({ node, ...props }) => (
              <ol className="list-decimal list-inside mb-6 text-white/70 space-y-2 ml-4" {...props} />
            ),
            li: ({ node, ...props }) => (
              <li className="ml-2" {...props} />
            ),
            blockquote: ({ node, ...props }) => (
              <blockquote className="border-l-4 border-emerald-400/50 pl-6 italic text-white/60 my-6 bg-white/5 py-4 rounded-r-lg" {...props} />
            ),
            table: ({ node, ...props }) => (
              <div className="overflow-x-auto my-6 rounded-lg border border-white/10">
                <table className="min-w-full" {...props} />
              </div>
            ),
            thead: ({ node, ...props }) => (
              <thead className="bg-white/5" {...props} />
            ),
            th: ({ node, ...props }) => (
              <th className="border border-white/10 px-4 py-3 text-left font-semibold text-white" {...props} />
            ),
            td: ({ node, ...props }) => (
              <td className="border border-white/10 px-4 py-3 text-white/70" {...props} />
            ),
            hr: ({ node, ...props }) => (
              <hr className="my-12 border-white/10" {...props} />
            ),
            strong: ({ node, ...props }) => (
              <strong className="font-semibold text-white" {...props} />
            ),
          }}
        >
          {processedContent}
        </ReactMarkdown>
      </article>
      
      <div className="mt-16 pt-8 border-t border-white/10 flex justify-between items-center">
        {prevDoc ? (
          <Link
            href={`/docs/${prevDoc.path}`}
            className="flex items-center gap-3 text-white/60 hover:text-emerald-400 transition-colors group"
          >
            <span className="text-2xl group-hover:-translate-x-1 transition-transform">←</span>
            <div>
              <div className="text-xs text-white/40 uppercase tracking-wider">Previous</div>
              <div className="font-medium">{prevDoc.title}</div>
            </div>
          </Link>
        ) : (
          <div />
        )}
        {nextDoc ? (
          <Link
            href={`/docs/${nextDoc.path}`}
            className="flex items-center gap-3 text-white/60 hover:text-emerald-400 transition-colors group text-right"
          >
            <div>
              <div className="text-xs text-white/40 uppercase tracking-wider">Next</div>
              <div className="font-medium">{nextDoc.title}</div>
            </div>
            <span className="text-2xl group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        ) : (
          <div />
        )}
      </div>
    </div>
  );
}
