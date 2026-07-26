import { Card } from "@/components/ui/card"

export function ConversationSkeleton() {
  return (
    <div className="space-y-2 p-2 animate-pulse">
      {Array.from({ length: 6 }).map((_, idx) => (
        <Card key={idx} className="p-3 border-border/40 bg-muted/20 space-y-2">
          <div className="flex items-center justify-between">
            <div className="h-3.5 bg-muted rounded-md w-1/3" />
            <div className="h-3 bg-muted/60 rounded-md w-12" />
          </div>
          <div className="h-4 bg-muted rounded-md w-3/4" />
          <div className="h-3 bg-muted/40 rounded-md w-1/2" />
        </Card>
      ))}
    </div>
  )
}

export function MessageSkeleton() {
  return (
    <div className="space-y-4 p-4 animate-pulse">
      <div className="flex gap-3 items-start">
        <div className="h-8 w-8 rounded-full bg-muted shrink-0" />
        <div className="space-y-2 flex-1 max-w-lg">
          <div className="h-4 bg-muted rounded-md w-1/4" />
          <div className="h-16 bg-muted/40 rounded-xl w-full" />
        </div>
      </div>
      <div className="flex gap-3 items-start justify-end">
        <div className="space-y-2 flex-1 max-w-lg">
          <div className="h-4 bg-primary/20 rounded-md w-1/4 ml-auto" />
          <div className="h-12 bg-primary/10 rounded-xl w-full" />
        </div>
        <div className="h-8 w-8 rounded-full bg-primary/30 shrink-0" />
      </div>
    </div>
  )
}
