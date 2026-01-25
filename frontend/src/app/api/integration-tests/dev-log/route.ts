'use server';

import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET() {
  try {
    const cwd = process.cwd();
    const candidatePaths = [
      path.join(cwd, 'docs', 'DEV_LOG.md'),
      path.join(cwd, '..', 'docs', 'DEV_LOG.md'),
      path.join(cwd, '..', '..', 'docs', 'DEV_LOG.md'),
    ];

    let logPath = '';
    for (const p of candidatePaths) {
      try {
        await fs.access(p);
        logPath = p;
        break;
      } catch {
        // continue
      }
    }

    if (!logPath) {
      return new NextResponse(
        JSON.stringify({ error: 'DEV_LOG.md not found' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } },
      );
    }

    const content = await fs.readFile(logPath, 'utf-8');
    return new NextResponse(content, {
      status: 200,
      headers: {
        'Content-Type': 'text/markdown; charset=utf-8',
        'Cache-Control': 'no-store',
      },
    });
  } catch (err: any) {
    const status = err?.code === 'ENOENT' ? 404 : 500;
    const message =
      status === 404
        ? 'DEV_LOG.md not found'
        : 'Failed to read DEV_LOG.md';
    return new NextResponse(
      JSON.stringify({ error: message }),
      { status, headers: { 'Content-Type': 'application/json' } },
    );
  }
}


