# Frontend Development Guide

This guide covers frontend structure, component development, API integration, state management, and styling guidelines.

## Frontend Structure

### Next.js App Router Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router
│   │   ├── page.tsx     # Home page
│   │   └── layout.tsx   # Root layout
│   ├── components/       # React components
│   │   ├── Dashboard.tsx
│   │   └── ...
│   ├── lib/             # Utilities
│   │   ├── config.ts
│   │   └── ...
│   └── hooks/           # Custom hooks
│       └── useStarknet.ts
└── package.json
```

## Component Development

### Component Template

```typescript
'use client';

import { useState } from 'react';

interface ComponentProps {
  prop1: string;
  prop2?: number;
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  const [state, setState] = useState<string>('');
  
  const handleAction = async () => {
    // Component logic
  };
  
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
}
```

### Component Patterns

**1. Server Components:**
- Default in Next.js 14
- No 'use client' directive
- Can fetch data directly

**2. Client Components:**
- Use 'use client' directive
- Interactive components
- State management

## API Integration

### API Client

**Create client:**
```typescript
const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';

export async function apiCall(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}
```

### Using API

```typescript
const data = await apiCall('/api/v1/risk-engine/decisions');
```

## State Management

### React Context

**Create context:**
```typescript
import { createContext, useContext, useState } from 'react';

interface AppContextType {
  state: string;
  setState: (value: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<string>('');
  
  return (
    <AppContext.Provider value={{ state, setState }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
```

### Custom Hooks

```typescript
export function useAllocations() {
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const fetchAllocations = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/api/v1/risk-engine/decisions');
      setAllocations(data);
    } finally {
      setLoading(false);
    }
  };
  
  return { allocations, loading, fetchAllocations };
}
```

## Styling Guidelines

### Tailwind CSS

**Usage:**
```typescript
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h1 className="text-2xl font-bold">Title</h1>
</div>
```

### Component Styling

**Consistent Patterns:**
- Use Tailwind utility classes
- Follow design system
- Responsive design
- Dark mode support (if applicable)

## Next Steps

- **[Integrating New Provers](05-integrating-new-provers.md)** - Prover integration
- **[Backend Development](03-backend-development.md)** - Python services
- **[Setup](01-setup.md)** - Development environment

---

**Frontend Development Summary:** Complete guide for Next.js frontend development with components, API integration, and state management.
