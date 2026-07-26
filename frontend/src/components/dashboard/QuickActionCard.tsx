import { LucideIcon, ArrowRight } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface QuickActionCardProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel: string
  onClick: () => void
  color?: string
  bgColor?: string
}

export function QuickActionCard({
  icon: Icon,
  title,
  description,
  actionLabel,
  onClick,
  color = "text-primary",
  bgColor = "bg-primary/10",
}: QuickActionCardProps) {
  return (
    <Card
      onClick={onClick}
      className="group relative cursor-pointer overflow-hidden border border-border/50 bg-card/60 backdrop-blur-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-md hover:border-primary/40"
    >
      <CardContent className="p-4 flex flex-col justify-between h-full space-y-3">
        <div className="flex items-start gap-3">
          <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${bgColor} ${color}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
              {title}
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
              {description}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-end pt-1">
          <Button variant="ghost" size="sm" className="h-7 px-2 text-xs font-semibold gap-1 text-primary group-hover:translate-x-0.5 transition-transform">
            <span>{actionLabel}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
