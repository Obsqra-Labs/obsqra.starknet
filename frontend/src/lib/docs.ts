export interface DocItem {
  title: string;
  path: string;
  children?: DocItem[];
}

export const docsStructure: DocItem[] = [
  {
    title: 'Introduction & Overview',
    path: '01-introduction',
    children: [
      { title: 'Overview', path: '01-introduction/01-overview' },
      { title: 'What is zkML?', path: '01-introduction/02-what-is-zkml' },
      { title: 'System Architecture Overview', path: '01-introduction/03-system-architecture-overview' },
    ],
  },
  {
    title: 'User Guides',
    path: '02-user-guides',
    children: [
      { title: 'Getting Started', path: '02-user-guides/01-getting-started' },
      { title: 'Executing Allocations', path: '02-user-guides/02-executing-allocations' },
      { title: 'Viewing Transparency', path: '02-user-guides/03-viewing-transparency' },
      { title: 'Troubleshooting', path: '02-user-guides/04-troubleshooting' },
    ],
  },
  {
    title: 'Architecture Deep Dive',
    path: '03-architecture',
    children: [
      { title: 'System Overview', path: '03-architecture/01-system-overview' },
      { title: 'Smart Contracts', path: '03-architecture/02-smart-contracts' },
      { title: 'Backend Services', path: '03-architecture/03-backend-services' },
      { title: 'Proof Generation', path: '03-architecture/04-proof-generation' },
      { title: 'On-Chain Verification', path: '03-architecture/05-on-chain-verification' },
      { title: 'Data Flow', path: '03-architecture/06-data-flow' },
    ],
  },
  {
    title: 'Novel Features',
    path: '04-novel-features',
    children: [
      { title: 'On-Chain zkML Verification', path: '04-novel-features/01-on-chain-zkml-verification' },
      { title: 'Model Provenance', path: '04-novel-features/02-model-provenance' },
      { title: 'Transparency Dashboard', path: '04-novel-features/03-transparency-dashboard' },
      { title: 'Multi-Prover Support', path: '04-novel-features/04-multi-prover-support' },
      { title: 'DAO Governance Integration', path: '04-novel-features/05-dao-governance-integration' },
    ],
  },
  {
    title: 'Developer Guides',
    path: '05-developer-guides',
    children: [
      { title: 'Setup', path: '05-developer-guides/01-setup' },
      { title: 'Contract Development', path: '05-developer-guides/02-contract-development' },
      { title: 'Backend Development', path: '05-developer-guides/03-backend-development' },
      { title: 'Frontend Development', path: '05-developer-guides/04-frontend-development' },
      { title: 'Integrating New Provers', path: '05-developer-guides/05-integrating-new-provers' },
    ],
  },
  {
    title: 'API Reference',
    path: '06-api-reference',
    children: [
      { title: 'API Overview', path: '06-api-reference/01-overview' },
      { title: 'Risk Engine Endpoints', path: '06-api-reference/02-risk-engine-endpoints' },
      { title: 'Verification Endpoints', path: '06-api-reference/03-verification-endpoints' },
      { title: 'Model Registry Endpoints', path: '06-api-reference/04-model-registry-endpoints' },
    ],
  },
  {
    title: 'Contract Reference',
    path: '07-contract-reference',
    children: [
      { title: 'RiskEngine', path: '07-contract-reference/01-risk-engine' },
      { title: 'StrategyRouter', path: '07-contract-reference/02-strategy-router' },
      { title: 'ModelRegistry', path: '07-contract-reference/03-model-registry' },
      { title: 'DAO Constraint Manager', path: '07-contract-reference/04-dao-constraint-manager' },
      { title: 'Fact Registry', path: '07-contract-reference/05-fact-registry' },
    ],
  },
];

export async function getDocContent(docPath: string): Promise<string> {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'}/api/docs/${docPath}`,
      { cache: 'no-store' }
    );
    
    if (!response.ok) {
      // Fallback: try direct file read in server component
      const fs = await import('fs');
      const path = await import('path');
      const DOCS_DIR = path.join(process.cwd(), '../../docs');
      const filePath = path.join(DOCS_DIR, `${docPath}.md`);
      const content = fs.readFileSync(filePath, 'utf-8');
      return content;
    }
    
    const data = await response.json();
    return data.content;
  } catch (error) {
    // Fallback for server-side rendering
    const fs = await import('fs');
    const path = await import('path');
    const DOCS_DIR = path.join(process.cwd(), '../../docs');
    const filePath = path.join(DOCS_DIR, `${docPath}.md`);
    const content = fs.readFileSync(filePath, 'utf-8');
    return content;
  }
}

export async function getDocPaths(): Promise<string[]> {
  const paths: string[] = [];
  
  function traverse(items: DocItem[]) {
    for (const item of items) {
      if (item.children) {
        traverse(item.children);
      } else {
        paths.push(item.path);
      }
    }
  }
  
  traverse(docsStructure);
  return paths;
}

export function getDocByPath(path: string): DocItem | null {
  function findInItems(items: DocItem[]): DocItem | null {
    for (const item of items) {
      if (item.path === path) {
        return item;
      }
      if (item.children) {
        const found = findInItems(item.children);
        if (found) return found;
      }
    }
    return null;
  }
  
  return findInItems(docsStructure);
}

export function getNextDoc(path: string): DocItem | null {
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

export function getPrevDoc(path: string): DocItem | null {
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
