#!/usr/bin/env python3
"""
Consolidate all .md and .txt files in chronological order with executive summary
"""

import os
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Exclude patterns
EXCLUDE_PATTERNS = [
    'node_modules',
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'target',
    'build',
    'cairo-vm',
    'match_ai_for_agents',
    '.cursor',
    'dist',
    '*.egg-info'
]

def should_exclude(filepath):
    """Check if file should be excluded"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in filepath:
            return True
    return False

def get_file_info(filepath):
    """Get file modification time and size"""
    try:
        stat = os.stat(filepath)
        return {
            'path': filepath,
            'mtime': stat.st_mtime,
            'size': stat.st_size,
            'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    except:
        return None

def find_all_docs(root_dir='.'):
    """Find all .md and .txt files"""
    files = []
    
    for ext in ['*.md', '*.txt']:
        for filepath in glob.glob(f'{root_dir}/**/{ext}', recursive=True):
            if not should_exclude(filepath):
                info = get_file_info(filepath)
                if info:
                    files.append(info)
    
    # Sort by modification time (most recent first for priority, then include older)
    # Prioritize recent files but include older ones too
    files.sort(key=lambda x: x['mtime'], reverse=True)  # Most recent first
    
    return files

def read_file_safely(filepath, max_size=200000):
    """Read file with size limit"""
    try:
        size = os.path.getsize(filepath)
        if size > max_size:
            # Read first and last portion
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_size // 2)
                f.seek(max(0, size - max_size // 2))
                content += "\n\n[... FILE TRUNCATED - MIDDLE PORTION REMOVED ...]\n\n"
                content += f.read()
            return content
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]\n"

def create_executive_summary(files):
    """Create executive summary"""
    summary = []
    summary.append("=" * 80)
    summary.append("OBSQRA LABS - ZKML RISK ENGINE PROJECT")
    summary.append("COMPLETE DOCUMENTATION CONSOLIDATION")
    summary.append("=" * 80)
    summary.append("")
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append(f"Total Files: {len(files)}")
    summary.append("")
    
    # Group by category
    categories = defaultdict(list)
    for f in files:
        path = f['path']
        if 'research_notes' in path:
            categories['Research Notes'].append(f)
        elif 'docs/' in path:
            categories['Documentation'].append(f)
        elif 'tests/' in path:
            categories['Tests'].append(f)
        elif 'integration_tests' in path:
            categories['Integration Tests'].append(f)
        elif path.startswith('./'):
            categories['Root Documentation'].append(f)
        else:
            categories['Other'].append(f)
    
    summary.append("FILE CATEGORIES:")
    summary.append("-" * 80)
    for category, cat_files in sorted(categories.items()):
        summary.append(f"{category}: {len(cat_files)} files")
    summary.append("")
    
    # Key milestones
    summary.append("KEY MILESTONES (Recent First):")
    summary.append("-" * 80)
    recent_files = sorted(files, key=lambda x: x['mtime'], reverse=True)[:20]
    for f in recent_files:
        rel_path = f['path'].replace('./', '')
        summary.append(f"  {f['date']}: {rel_path}")
    summary.append("")
    
    summary.append("=" * 80)
    summary.append("")
    
    return "\n".join(summary)

def consolidate_docs(output_file='OBSQRA_COMPLETE_DOCUMENTATION.md', max_total_size=2000000):
    """Consolidate all documentation files"""
    print("Finding all .md and .txt files...")
    files = find_all_docs()
    print(f"Found {len(files)} files")
    
    # Create executive summary
    executive_summary = create_executive_summary(files)
    
    # Calculate total size
    total_size = len(executive_summary)
    included_files = []
    
    print("\nProcessing files in chronological order...")
    for i, file_info in enumerate(files):
        filepath = file_info['path']
        file_size = file_info['size']
        
        # Skip if adding this file would exceed limit (with buffer)
        if total_size + file_size > max_total_size * 0.95:  # Use 95% of limit to ensure we don't exceed
            print(f"  [Skipping {filepath} - would exceed size limit]")
            continue
        
        print(f"  [{i+1}/{len(files)}] {filepath} ({file_size} bytes)")
        
        # Read file
        content = read_file_safely(filepath, max_size=100000)
        
        # Add file header
        file_header = []
        file_header.append("")
        file_header.append("=" * 80)
        file_header.append(f"FILE: {filepath}")
        file_header.append(f"DATE: {file_info['date']}")
        file_header.append(f"SIZE: {file_size} bytes")
        file_header.append("=" * 80)
        file_header.append("")
        
        file_content = "\n".join(file_header) + content
        
        included_files.append({
            'path': filepath,
            'content': file_content,
            'size': len(file_content)
        })
        
        total_size += len(file_content)
    
    # Write consolidated file
    print(f"\nWriting consolidated file: {output_file}")
    print(f"Total size: {total_size:,} characters")
    print(f"Files included: {len(included_files)}/{len(files)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(executive_summary)
        f.write("\n")
        f.write("=" * 80)
        f.write("\n")
        f.write("DOCUMENTATION CONTENT (Chronological Order)")
        f.write("\n")
        f.write("=" * 80)
        f.write("\n")
        
        for file_info in included_files:
            f.write(file_info['content'])
            f.write("\n\n")
    
    print(f"\n✅ Consolidated documentation written to: {output_file}")
    print(f"   Total size: {total_size:,} characters")
    print(f"   Files included: {len(included_files)}/{len(files)}")
    
    return output_file

if __name__ == "__main__":
    output = consolidate_docs()
    print(f"\n📄 File ready for notebook AI: {output}")
