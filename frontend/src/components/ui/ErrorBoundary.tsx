import { Component, ErrorInfo, ReactNode } from "react"

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught runtime error caught by ErrorBoundary:", error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center p-6 text-center bg-background text-foreground">
          <div className="w-full max-w-md space-y-4 rounded-3xl border border-destructive/30 bg-card p-8 shadow-2xl backdrop-blur-xl">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive font-extrabold text-2xl">
              !
            </div>
            <h1 className="text-xl font-bold text-foreground">Đã xảy ra lỗi giao diện</h1>
            <p className="text-xs text-muted-foreground">
              Ứng dụng gặp sự cố ngoài dự kiến. Chi tiết lỗi:
            </p>
            <div className="p-3 rounded-xl bg-destructive/10 text-destructive font-mono text-[11px] text-left overflow-auto max-h-32">
              {this.state.error?.message || "Unknown rendering exception"}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => window.location.assign("/workspaces")}
                className="flex-1 rounded-2xl bg-primary py-2.5 text-xs font-bold text-primary-foreground hover:bg-primary/90 transition-all"
              >
                Về Workspaces
              </button>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="flex-1 rounded-2xl border border-input bg-background py-2.5 text-xs font-bold hover:bg-accent transition-all"
              >
                Tải lại trang
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
