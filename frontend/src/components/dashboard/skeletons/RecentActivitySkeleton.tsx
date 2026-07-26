import { Card, CardContent, CardHeader } from "@/components/ui/card"


export function RecentActivitySkeleton() {
  return (
    <Card className="border border-border/50 bg-card/60 animate-pulse">
      <CardHeader className="pb-3">
        <div className="h-4 bg-muted rounded-md w-1/3" />
      </CardHeader>
      <CardContent className="space-y-4">
        {Array.from({ length: 4 }).map((_, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-muted shrink-0" />
            <div className="space-y-1.5 flex-1">
              <div className="h-3.5 bg-muted rounded-md w-3/4" />
              <div className="h-2.5 bg-muted/60 rounded-md w-1/2" />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
