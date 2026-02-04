'use client';

import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
  isDark: boolean;
}

export function MermaidDiagram({ chart, isDark }: MermaidDiagramProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [rendered, setRendered] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    mermaid.initialize({ 
      startOnLoad: false,
      theme: isDark ? 'dark' : 'default',
      securityLevel: 'loose',
    });
  }, [isDark]);

  useEffect(() => {
    if (ref.current && !rendered) {
      const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
      ref.current.id = id;
      
      mermaid.render(id, chart.trim())
        .then((result) => {
          if (ref.current) {
            ref.current.innerHTML = result.svg;
            setRendered(true);
          }
        })
        .catch((err) => {
          setError(err.message);
          console.error('Mermaid render error:', err);
        });
    }
  }, [chart, rendered]);

  if (error) {
    return (
      <div className="my-8 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
        <p className="font-semibold mb-2">Diagram Error</p>
        <p>{error}</p>
        <pre className="mt-2 text-xs opacity-75 overflow-x-auto">{chart}</pre>
      </div>
    );
  }

  return (
    <div className="my-8 bg-white/5 border border-white/10 rounded-xl p-6 overflow-x-auto">
      <div ref={ref} className="mermaid" />
    </div>
  );
}
