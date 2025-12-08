# 🔐 Frontend Authentication & Signup Implementation

## Current Status

### ✅ What's Built (Backend)
- User registration endpoint (`POST /api/v1/auth/register`)
- User login endpoint (`POST /api/v1/auth/login`)
- JWT token generation
- Password hashing (bcrypt)
- User profile endpoints
- Session management

### ❌ What's Missing (Frontend)
- Email signup page/form
- Login page/form
- Authentication state management
- Protected routes
- Token storage
- Session persistence

---

## 🎯 The Gap

### Current Frontend Flow
```
User visits http://localhost:3003
    ↓
Sees landing page with "Launch" button
    ↓
Must connect Starknet wallet
    ↓
Sees Dashboard (DEMO MODE)
    ↓
Can see fake data/history
```

### What We Planned
```
User visits http://localhost:3003
    ↓
Sees landing page with signup/login options
    ↓
User can:
  A) Sign up with email (no wallet needed)
  B) Login with existing email
    ↓
User can explore dashboard (real data from backend)
    ↓
Later: Connect wallet to execute transactions
```

### Reality
The **frontend landing page currently skips signup entirely** and goes straight to wallet connection.

---

## 🚀 What Needs to Be Built (Frontend Only)

### 1. Authentication UI Components

```typescript
// NOT YET BUILT
components/Auth/SignupForm.tsx         (Email signup form)
components/Auth/LoginForm.tsx          (Email login form)
components/Auth/AuthModal.tsx          (Modal wrapper)
components/Auth/WalletConnectModal.tsx (Later step)
```

### 2. Authentication State Management

```typescript
// NOT YET BUILT
hooks/useAuth.ts                       (Auth context hook)
contexts/AuthContext.tsx               (Auth state)
utils/authStorage.ts                   (Token storage)
```

### 3. Protected Routes

```typescript
// NOT YET BUILT
components/ProtectedRoute.tsx          (Route guard)
middleware/auth.ts                     (Middleware)
```

### 4. Updated Landing Page

```typescript
// NEEDS UPDATE
app/page.tsx                           (Show signup/login instead of wallet-only)
```

---

## 📝 Implementation Plan (Estimated 2-3 hours)

### Step 1: Create Auth Forms (1 hour)

**SignupForm.tsx**
```typescript
export function SignupForm({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/register`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            password,
            full_name: name,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Signup failed');
      }

      const data = await response.json();
      
      // Save token
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_email', email);
      
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSignup} className="space-y-4">
      <input
        type="text"
        placeholder="Full Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="w-full p-3 border rounded"
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full p-3 border rounded"
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full p-3 border rounded"
        required
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full p-3 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {isLoading ? 'Signing up...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

**LoginForm.tsx** (similar structure)

### Step 2: Create Auth Context (30 minutes)

```typescript
// contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  email: string | null;
  login: (email: string) => void;
  logout: () => void;
  token: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('access_token');
    const savedEmail = localStorage.getItem('user_email');
    if (savedToken && savedEmail) {
      setToken(savedToken);
      setEmail(savedEmail);
    }
  }, []);

  const login = (userEmail: string) => {
    setEmail(userEmail);
  };

  const logout = () => {
    setToken(null);
    setEmail(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
  };

  return (
    <AuthContext.Provider value={{
      isAuthenticated: !!token,
      email,
      login,
      logout,
      token,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Step 3: Update Landing Page (45 minutes)

```typescript
// app/page.tsx - Add signup/login section

function Landing() {
  const [showSignup, setShowSignup] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  if (authenticated) {
    return <Dashboard />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full p-8 rounded-lg border">
        <h1 className="text-2xl font-bold mb-6">
          {showSignup ? 'Sign Up' : 'Log In'}
        </h1>
        
        {showSignup ? (
          <SignupForm 
            onSuccess={() => setAuthenticated(true)}
          />
        ) : (
          <LoginForm 
            onSuccess={() => setAuthenticated(true)}
          />
        )}

        <button
          onClick={() => setShowSignup(!showSignup)}
          className="mt-4 text-sm text-blue-500"
        >
          {showSignup ? 'Already have an account? Log in' : 'No account? Sign up'}
        </button>

        <hr className="my-6" />

        <button
          className="w-full p-3 bg-purple-500 text-white rounded"
        >
          Connect Starknet Wallet
        </button>
        <p className="text-xs text-gray-500 mt-2">
          Connect your wallet to execute transactions later
        </p>
      </div>
    </div>
  );
}
```

### Step 4: Protect Routes (30 minutes)

```typescript
// components/ProtectedRoute.tsx
import { useAuth } from '@/contexts/AuthContext';
import { redirect } from 'next/navigation';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    redirect('/');
  }

  return children;
}
```

### Step 5: Update Environment Config (5 minutes)

```env
# frontend/.env.local - Add if missing
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎯 What This Enables

### Signup Flow
```
User visits http://localhost:3003
    ↓
Clicks "Sign Up"
    ↓
Enters: Email, Password, Full Name
    ↓
Backend creates user in PostgreSQL
    ↓
JWT token returned
    ↓
Token stored in localStorage
    ↓
Dashboard shows REAL data from database
    ↓
User can explore analytics
    ↓
Later: Connect wallet to transact
```

### Login Flow
```
User visits http://localhost:3003
    ↓
Clicks "Log In"
    ↓
Enters: Email, Password
    ↓
Backend validates credentials
    ↓
JWT token returned
    ↓
Dashboard loads with user's real data
```

### Dashboard Features (When Authenticated)
- Real user data from database (not demo mode)
- Risk history (queries `risk_history` table)
- Allocation history (queries `allocation_history` table)
- Actual API calls to backend
- User profile/preferences

---

## 📊 Current vs. After Implementation

### BEFORE (Current)
```
Landing Page
    ↓
"Launch" button → Wallet connection
    ↓
Dashboard (DEMO MODE - fake data)
    ↓
Can't save anything
    ↓
No user accounts
```

### AFTER (With Signup)
```
Landing Page
    ↓
"Sign Up" / "Log In" buttons
    ↓
Email-based authentication
    ↓
Dashboard (REAL MODE - user data from DB)
    ↓
All data persists
    ↓
User accounts in PostgreSQL
    ↓
Later: Can connect wallet to transact
```

---

## 🔧 Integration with Existing Backend

The backend is **100% ready**. These frontend changes just wire it up:

### Backend Endpoints Ready
```
POST   /api/v1/auth/register          ✅ Ready
POST   /api/v1/auth/login             ✅ Ready
GET    /api/v1/auth/me                ✅ Ready
GET    /api/v1/analytics/dashboard    ✅ Ready
GET    /api/v1/analytics/risk-history ✅ Ready
```

### Database Ready
```
users table                 ✅ Created
risk_history table          ✅ Created
allocation_history table    ✅ Created
```

### All you need to do is:
1. Build signup/login UI forms
2. Create auth context
3. Update landing page
4. Protect routes
5. Wire to existing backend

---

## ⏱️ Time Estimate

| Task | Time | Difficulty |
|------|------|-----------|
| Auth Forms | 1 hour | Easy |
| Auth Context | 30 min | Easy |
| Update Landing Page | 45 min | Easy |
| Protected Routes | 30 min | Easy |
| Testing | 30 min | Easy |
| **TOTAL** | **3 hours** | **Easy** |

---

## 🚀 Why This Matters

Right now:
- ❌ No user signup
- ❌ No persistent data
- ❌ Demo mode only
- ❌ Backend auth unused

After 3 hours:
- ✅ Full email signup
- ✅ Persistent user data
- ✅ Real database queries
- ✅ Backend fully utilized
- ✅ Ready for real users

---

## 📝 Summary

**Good news:** Your backend is 100% ready for this!  
**Missing piece:** Frontend signup/login UI (3 hours to build)

The infrastructure exists:
- ✅ Authentication endpoints
- ✅ Database tables
- ✅ API layer
- ✅ JWT handling

You just need to:
- Build the signup form
- Build the login form
- Wire them to the backend
- Add state management
- Protect routes

Then you'll have a **fully functional user signup system** that persists data in PostgreSQL and returns real analytics!

---

## 💡 Recommendation

**This is a critical feature to build next.** Right now your app is in "demo mode" and nothing persists. Building signup/login:

1. Turns the MVP into a real product
2. Gets real user data flowing
3. Lets you test the analytics
4. Enables user feedback
5. Prepares for production

**Estimated effort: 3 hours**  
**Value: Unlocks the entire product**

Would you like me to create these components for you?

