'use client';

export function CardSkeleton() {
  return (
    <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 animate-pulse">
      <div className="h-4 bg-white/10 rounded w-1/3 mb-3"></div>
      <div className="h-10 bg-white/10 rounded w-2/3"></div>
    </div>
  );
}

export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
    </div>
  );
}

export function TableSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="h-16 bg-white/5 rounded-lg animate-pulse"></div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 animate-pulse">
      <div className="h-6 bg-white/10 rounded w-1/4 mb-4"></div>
      <div className="h-48 bg-white/10 rounded"></div>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="container mx-auto p-4 max-w-6xl space-y-6">
      {/* Header Skeleton */}
      <div className="animate-pulse">
        <div className="h-8 bg-white/10 rounded w-1/3 mb-2"></div>
        <div className="h-4 bg-white/10 rounded w-1/4"></div>
      </div>

      {/* Stats Skeleton */}
      <StatsSkeleton />

      {/* Chart Skeleton */}
      <ChartSkeleton />

      {/* Table Skeleton */}
      <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6">
        <div className="h-6 bg-white/10 rounded w-1/4 mb-4 animate-pulse"></div>
        <TableSkeleton rows={5} />
      </div>
    </div>
  );
}

