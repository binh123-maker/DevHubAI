import { NavigateFunction } from "react-router-dom"

export interface RouteTarget {
  path: string
  sectionId?: string
}

export const TARGET_MAPPINGS: Record<string, RouteTarget> = {
  overview: { path: "/workspaces", sectionId: "overview" },
  statistics: { path: "/workspaces", sectionId: "statistics text-primary" },
  analytics: { path: "/workspaces", sectionId: "analytics" },
  heatmap: { path: "/workspaces", sectionId: "heatmap" },
  activity: { path: "/workspaces", sectionId: "activity" },
  kanban: { path: "/workspaces", sectionId: "kanban" },
  workspaces: { path: "/workspaces", sectionId: "workspaces" },
  chats: { path: "/history" },
  profile: { path: "/profile" },
}

export function handleTargetNavigation(
  targetKey: string,
  navigate: NavigateFunction,
  currentPathname: string,
  scrollToSection: (id: string) => void
) {
  const target = TARGET_MAPPINGS[targetKey] || { path: "/workspaces", sectionId: targetKey }

  const isDashboardPage = currentPathname === "/workspaces" || currentPathname === "/"

  if (target.path === "/workspaces" && isDashboardPage && target.sectionId) {
    scrollToSection(target.sectionId)
  } else {
    navigate(target.path)
    if (target.sectionId) {
      setTimeout(() => {
        const el = document.getElementById(target.sectionId!)
        if (el) {
          el.scrollIntoView({ behavior: "smooth" })
        }
      }, 200)
    }
  }
}
