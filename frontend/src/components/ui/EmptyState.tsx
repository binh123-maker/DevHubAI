import { LucideIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  actionLink?: string
  secondaryActionLabel?: string
  onSecondaryAction?: () => void
  className?: string
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  actionLink,
  secondaryActionLabel,
  onSecondaryAction,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-dashed border-border/80 bg-card/40 backdrop-blur-xs max-w-md mx-auto my-6 space-y-4 animate-in fade-in duration-300 ${className}`}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary shadow-xs ring-4 ring-primary/5">
        <Icon className="h-7 w-7" />
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold tracking-tight text-foreground">{title}</h3>
        <p className="text-xs text-muted-foreground leading-relaxed">{description}</p>
      </div>

      {(actionLabel || secondaryActionLabel) && (
        <div className="flex items-center gap-2 pt-2">
          {actionLabel && actionLink && (
            <Button size="sm" asChild className="rounded-xl px-4 text-xs font-semibold shadow-xs">
              <Link to={actionLink}>{actionLabel}</Link>
            </Button>
          )}

          {actionLabel && !actionLink && onAction && (
            <Button size="sm" onClick={onAction} className="rounded-xl px-4 text-xs font-semibold shadow-xs">
              {actionLabel}
            </Button>
          )}

          {secondaryActionLabel && onSecondaryAction && (
            <Button size="sm" variant="outline" onClick={onSecondaryAction} className="rounded-xl px-4 text-xs font-medium">
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
