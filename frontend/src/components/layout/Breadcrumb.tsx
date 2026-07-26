import React from "react"
import { Link, useLocation } from "react-router-dom"
import { ChevronRight, Home } from "lucide-react"

interface BreadcrumbItem {
  label: string
  to?: string
}

export function Breadcrumb() {
  const location = useLocation()

  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const path = location.pathname
    if (path === "/" || path === "/workspaces") {
      return [
        { label: "Home", to: "/workspaces" },
        { label: "Knowledge Dashboard" },
      ]
    }
    if (path.startsWith("/workspaces/")) {
      return [
        { label: "Home", to: "/workspaces" },
        { label: "Workspaces", to: "/workspaces" },
        { label: "Chi tiết Workspace" },
      ]
    }
    if (path.startsWith("/documents/")) {
      return [
        { label: "Home", to: "/workspaces" },
        { label: "Tài liệu" },
        { label: "Chi tiết" },
      ]
    }
    if (path.startsWith("/history")) {
      return [
        { label: "Home", to: "/workspaces" },
        { label: "Lịch sử Chat AI" },
      ]
    }
    if (path === "/profile") {
      return [
        { label: "Home", to: "/workspaces" },
        { label: "Hồ sơ cá nhân" },
      ]
    }
    return [{ label: "Home", to: "/workspaces" }]
  }

  const items = getBreadcrumbs()

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs text-muted-foreground">
      <Home className="h-3.5 w-3.5 text-muted-foreground/80" />
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        return (
          <React.Fragment key={index}>
            {index > 0 && <ChevronRight className="h-3 w-3 text-muted-foreground/50" />}
            {item.to && !isLast ? (
              <Link to={item.to} className="hover:text-foreground transition-colors">
                {item.label}
              </Link>
            ) : (
              <span className={`font-semibold ${isLast ? "text-foreground" : ""}`}>{item.label}</span>
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}
