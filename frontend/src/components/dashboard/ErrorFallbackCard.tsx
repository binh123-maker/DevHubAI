import { AlertTriangle, RotateCcw } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface ErrorFallbackCardProps {
  title?: string
  message?: string
  onRetry?: () => void
}

export function ErrorFallbackCard({
  title = "Không thể tải widget này",
  message = "Đã xảy ra lỗi khi truy xuất dữ liệu. Các widget khác vẫn hoạt động bình thường.",
  onRetry,
}: ErrorFallbackCardProps) {
  return (
    <Card className="border border-destructive/30 bg-destructive/5 backdrop-blur-xs shadow-xs">
      <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <AlertTriangle className="h-5 w-5" />
        </div>
        <h4 className="text-sm font-bold text-foreground">{title}</h4>
        <p className="text-xs text-muted-foreground max-w-sm">{message}</p>
        {onRetry && (
          <Button variant="outline" size="sm" onClick={onRetry} className="gap-1.5 text-xs mt-1 border-destructive/30 hover:bg-destructive/10">
            <RotateCcw className="h-3.5 w-3.5" />
            Thử lại
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
