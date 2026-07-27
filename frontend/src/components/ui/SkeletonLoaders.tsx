export function SkeletonBox({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-muted/60 rounded-xl ${className}`} />
}

export function ProfilePageSkeleton() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Hero Banner Skeleton */}
      <SkeletonBox className="h-44 w-full rounded-2xl" />

      {/* Grid skeleton */}
      <div className="grid gap-6 md:grid-cols-3">
        <SkeletonBox className="h-64 rounded-2xl md:col-span-2" />
        <SkeletonBox className="h-64 rounded-2xl md:col-span-1" />
      </div>

      <SkeletonBox className="h-72 w-full rounded-2xl" />
    </div>
  )
}

export function ChatListSkeleton() {
  return (
    <div className="space-y-4 p-4 animate-in fade-in duration-300 max-w-4xl mx-auto">
      <div className="flex gap-3 justify-start">
        <SkeletonBox className="h-8 w-8 rounded-xl shrink-0" />
        <SkeletonBox className="h-20 w-3/4 rounded-2xl" />
      </div>
      <div className="flex gap-3 justify-end">
        <SkeletonBox className="h-12 w-1/2 rounded-2xl" />
        <SkeletonBox className="h-8 w-8 rounded-xl shrink-0" />
      </div>
      <div className="flex gap-3 justify-start">
        <SkeletonBox className="h-8 w-8 rounded-xl shrink-0" />
        <SkeletonBox className="h-32 w-4/5 rounded-2xl" />
      </div>
    </div>
  )
}

export function WorkspaceGridSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-in fade-in duration-300">
      {[1, 2, 3, 4, 5, 6].map((idx) => (
        <SkeletonBox key={idx} className="h-40 rounded-2xl" />
      ))}
    </div>
  )
}

export function DocumentListSkeleton() {
  return (
    <div className="space-y-3 animate-in fade-in duration-300">
      {[1, 2, 3, 4].map((idx) => (
        <SkeletonBox key={idx} className="h-16 w-full rounded-xl" />
      ))}
    </div>
  )
}
