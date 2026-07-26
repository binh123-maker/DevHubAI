import { Card } from "@/components/ui/card"


export function KanbanSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, colIdx) => (
        <div key={colIdx} className="rounded-xl border border-border/60 bg-muted/20 p-3 space-y-3 animate-pulse">
          <div className="h-5 bg-muted rounded-md w-1/2" />
          {Array.from({ length: 2 }).map((_, cardIdx) => (
            <Card key={cardIdx} className="h-24 bg-card/60 p-3 space-y-2 border-border/40">
              <div className="h-4 bg-muted rounded-md w-3/4" />
              <div className="h-3 bg-muted/60 rounded-md w-1/2" />
            </Card>
          ))}
        </div>
      ))}
    </div>
  )
}
