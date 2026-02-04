import { notFound } from 'next/navigation';
import { MarkdownRenderer } from '@/components/docs/MarkdownRenderer';
import fs from 'fs';
import path from 'path';

interface DocsPageProps {
  params: Promise<{
    slug: string;
  }>;
}

const DOCS_DIR = path.resolve(process.cwd(), '../docs');

export const dynamic = 'force-dynamic';

export default async function DocsPage({ params }: DocsPageProps) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug || '';
  
  if (!slug) {
    const { redirect } = await import('next/navigation');
    redirect('/docs/01-introduction/01-overview');
  }
  
  try {
    const filePath = path.join(DOCS_DIR, `${slug}.md`);
    
    if (!fs.existsSync(filePath)) {
      notFound();
    }
    
    const content = fs.readFileSync(filePath, 'utf-8');
    
    if (!content || content.trim().length === 0) {
      notFound();
    }
    
    return <MarkdownRenderer content={content} />;
  } catch (error: any) {
    console.error('[Docs] Error:', error);
    notFound();
  }
}

export async function generateMetadata({ params }: DocsPageProps) {
  try {
    const resolvedParams = await params;
    const slug = resolvedParams.slug || '';
    const title = slug.split('/').pop()?.replace(/-/g, ' ') || 'Documentation';
    
    return {
      title: `${title} | Obsqra Documentation`,
      description: 'Obsqra zkML Risk Engine Documentation',
    };
  } catch {
    return {
      title: 'Documentation | Obsqra',
      description: 'Obsqra zkML Risk Engine Documentation',
    };
  }
}
