import { Component, ErrorInfo, ReactNode } from "react"

import { ErrorFallbackCard } from "./ErrorFallbackCard"

interface Props {
  children: ReactNode
  title?: string
}

interface State {
  hasError: boolean
  error?: Error
}

export class DashboardWidget extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("DashboardWidget Error Boundary caught an error:", error, errorInfo)
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined })
  }

  public render() {
    if (this.state.hasError) {
      return (
        <ErrorFallbackCard
          title={`Lỗi hiển thị: ${this.props.title || "Widget"}`}
          message={this.state.error?.message || "Không thể tải widget này."}
          onRetry={this.handleRetry}
        />
      )
    }

    return this.props.children
  }
}
