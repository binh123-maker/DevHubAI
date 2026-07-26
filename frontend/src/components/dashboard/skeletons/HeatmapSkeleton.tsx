import { Card, CardContent, CardHeader } from "@/components/ui/card"


export function HeatmapSkeleton() {
  return (
    <Card className="border border-border/50 bg-card/60 animate-pulse">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="space-y-2 w-1/3">
          <div className="h-4 bg-muted rounded-md w-3/4" />
          <div className="h-3 bg-muted/60 rounded-md w-1/2" />
        </div>
        <div className="h-4 bg-muted rounded-md w-24" />
      </CardHeader>
      <CardContent className="pt-2 space-y-4">
        <div className="h-28 bg-muted/40 rounded-lg w-full" />
        <div className="h-3 bg-muted/60 rounded-md w-1/2" />
      </CardContent>
    </Card>
  )
}
