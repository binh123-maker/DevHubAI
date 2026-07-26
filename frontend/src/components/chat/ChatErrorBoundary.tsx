import { Component, ErrorInfo, ReactNode } from "react"
import { AlertTriangle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Props {
  children: ReactNode
  fallbackText?: string
}

interface State {
  hasError: boolean
  error?: Error
}

export class ChatErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ChatErrorBoundary caught error:", error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 rounded-2xl border border-destructive/40 bg-destructive/5 text-destructive space-y-3 max-w-xl mx-auto my-4 text-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-destructive/10 text-destructive mx-auto">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <h3 className="text-sm font-bold">
            {this.props.fallbackText || "Đã xảy ra lỗi khi hiển thị cuộc trò chuyện."}
          </h3>
          <p className="text-xs text-muted-foreground font-mono">
            {this.state.error?.message || "Lỗi giao diện không xác định."}
          </p>
          <Button
            size="sm"
            variant="outline"
            onClick={this.handleReset}
            className="h-8 text-xs gap-1.5 border-destructive/30 text-destructive hover:bg-destructive/10"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Thử lại giao diện</span>
          </Button>
        </div>
      )
    }

    return this.props.children
  }
}
