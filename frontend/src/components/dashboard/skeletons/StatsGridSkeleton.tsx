import { Card, CardContent } from "@/components/ui/card"


export function StatsGridSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, idx) => (
        <Card key={idx} className="border border-border/50 bg-card/60 animate-pulse">
          <CardContent className="p-5 flex items-center justify-between">
            <div className="space-y-2 w-2/3">
              <div className="h-3 bg-muted rounded-md w-1/2" />
              <div className="h-6 bg-muted rounded-md w-3/4" />
              <div className="h-2.5 bg-muted/60 rounded-md w-full" />
            </div>
            <div className="h-11 w-11 rounded-xl bg-muted" />
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
