import { Card, CardContent, CardHeader } from "@/components/ui/card"


export function AnalyticsSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, idx) => (
        <Card key={idx} className="border border-border/50 bg-card/60 animate-pulse">
          <CardHeader className="pb-2">
            <div className="h-3 bg-muted rounded-md w-1/2" />
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="h-7 bg-muted rounded-md w-1/3" />
            <div className="h-3 bg-muted/60 rounded-md w-3/4" />
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
