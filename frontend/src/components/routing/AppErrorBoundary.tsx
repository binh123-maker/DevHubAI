import { Component, ErrorInfo, ReactNode } from "react"
import { AlertOctagon, ArrowLeft, Bug, RefreshCw, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class AppErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[AppErrorBoundary] UI Error caught:", error, errorInfo)
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined })
  }

  private handleBack = () => {
    window.history.back()
    setTimeout(() => this.setState({ hasError: false, error: undefined }), 300)
  }

  private handleReload = () => {
    window.location.reload()
  }

  private handleReportBug = () => {
    const errorDetails = encodeURIComponent(this.state.error?.stack || this.state.error?.message || "Unknown error")
    window.open(`mailto:support@devhub.ai?subject=UI%20Bug%20Report&body=${errorDetails}`, "_blank")
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[60vh] w-full items-center justify-center p-4">
          <Card className="max-w-md w-full border-destructive/30 bg-card/90 shadow-xl backdrop-blur-md">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
                <AlertOctagon className="h-6 w-6" />
              </div>
              <CardTitle className="text-lg font-extrabold text-foreground">Đã xảy ra sự cố giao diện</CardTitle>
              <p className="text-xs text-muted-foreground mt-1">
                Ứng dụng ant-crash đã khôi phục lại trang để tránh gây gián đoạn hệ thống.
              </p>
            </CardHeader>
            <CardContent className="space-y-3 text-center">
              <div className="rounded-xl bg-muted/60 p-3 text-left font-mono text-[11px] text-destructive overflow-x-auto max-h-32 border border-border/40">
                {this.state.error?.message || "Internal Rendering Error"}
              </div>

              <div className="flex flex-col gap-2 pt-2">
                <div className="grid grid-cols-2 gap-2 w-full">
                  <Button variant="default" size="sm" onClick={this.handleRetry} className="gap-1.5 font-bold">
                    <RefreshCw className="h-3.5 w-3.5" />
                    <span>Thử lại</span>
                  </Button>
                  <Button variant="outline" size="sm" onClick={this.handleBack} className="gap-1.5">
                    <ArrowLeft className="h-3.5 w-3.5" />
                    <span>Quay lại</span>
                  </Button>
                </div>
                <div className="grid grid-cols-2 gap-2 w-full">
                  <Button variant="secondary" size="sm" onClick={this.handleReload} className="gap-1.5 text-xs">
                    <RotateCcw className="h-3.5 w-3.5" />
                    <span>Tải lại trang</span>
                  </Button>
                  <Button variant="ghost" size="sm" onClick={this.handleReportBug} className="gap-1.5 text-xs text-muted-foreground hover:text-foreground">
                    <Bug className="h-3.5 w-3.5" />
                    <span>Báo lỗi</span>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
