import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

export async function GET() {
  try {
    // Path to dev_log.md from project root
    // process.cwd() in Next.js API routes is the project root (frontend/)
    // So we need to go up one level to get to obsqra.starknet root
    const devLogPath = join(process.cwd(), '..', 'integration_tests', 'dev_log.md');
    
    const content = await readFile(devLogPath, 'utf-8');
    
    return NextResponse.json({
      success: true,
      content: content,
      lastUpdated: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('Error reading dev log:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to read dev log',
        content: '# Integration Tests Development Log\n\nError loading log file.'
      },
      { status: 500 }
    );
  }
}
