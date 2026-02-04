import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Get absolute path to docs directory
// process.cwd() in Next.js returns the project root (where next.config.js is)
// So from frontend/, we go up one level to root, then into docs/
const DOCS_DIR = path.resolve(process.cwd(), '../docs');

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const filePath = params.path.join('/');
    const fullPath = path.join(DOCS_DIR, `${filePath}.md`);
    
    // Security: prevent directory traversal
    if (!fullPath.startsWith(DOCS_DIR)) {
      return NextResponse.json({ error: 'Invalid path' }, { status: 400 });
    }
    
    if (!fs.existsSync(fullPath)) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 });
    }
    
    const content = fs.readFileSync(fullPath, 'utf-8');
    return NextResponse.json({ content });
  } catch (error) {
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
