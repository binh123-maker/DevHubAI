import { Link } from "react-router-dom"
import { LucideIcon } from "lucide-react"

interface SidebarItemProps {
  icon: LucideIcon
  label: string
  to?: string
  isActive?: boolean
  isCollapsed?: boolean
  isDisabled?: boolean
  badge?: string | number
  onClick?: () => void
}

export function SidebarItem({
  icon: Icon,
  label,
  to,
  isActive = false,
  isCollapsed = false,
  isDisabled = false,
  badge,
  onClick,
}: SidebarItemProps) {

  const content = (
    <div
      onClick={isDisabled ? undefined : onClick}
      tabIndex={isDisabled ? -1 : 0}
      role="button"
      aria-disabled={isDisabled}
      aria-label={label}
      className={`group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
        isDisabled
          ? "opacity-40 cursor-not-allowed"
          : "cursor-pointer active:scale-[0.98]"
      } ${
        isActive
          ? "bg-primary/10 text-primary font-semibold"
          : "text-muted-foreground hover:bg-accent/80 hover:text-foreground"
      }`}
    >
      {/* Active Left Indicator Bar */}
      {isActive && (
        <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-primary transition-all duration-200" />
      )}

      {/* Icon */}
      <Icon
        className={`h-4 w-4 shrink-0 transition-colors duration-200 ${
          isActive ? "text-primary scale-110" : "text-muted-foreground group-hover:text-foreground"
        }`}
      />

      {/* Label */}
      {!isCollapsed && <span className="truncate">{label}</span>}

      {/* Badge */}
      {!isCollapsed && badge !== undefined && (
        <span className="ml-auto rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-bold text-primary">
          {badge}
        </span>
      )}
    </div>
  )

  if (to && !isDisabled && !onClick) {
    return <Link to={to}>{content}</Link>
  }

  return content
}
