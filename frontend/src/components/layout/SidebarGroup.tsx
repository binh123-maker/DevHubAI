import { useState } from "react"

import { ChevronDown } from "lucide-react"

interface SidebarGroupProps {
  title: string
  isCollapsed?: boolean
  children: React.ReactNode
  collapsible?: boolean
}

export function SidebarGroup({ title, isCollapsed = false, children, collapsible = true }: SidebarGroupProps) {
  const [isOpen, setIsOpen] = useState(true)

  if (isCollapsed) {
    return <div className="space-y-1 py-2">{children}</div>
  }

  return (
    <div className="py-2">
      <div
        onClick={() => collapsible && setIsOpen((prev) => !prev)}
        className="flex items-center justify-between px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-muted-foreground/80 cursor-pointer select-none hover:text-foreground transition-colors"
      >
        <span>{title}</span>
        {collapsible && (
          <ChevronDown
            className={`h-3 w-3 transition-transform duration-200 ${isOpen ? "" : "-rotate-90"}`}
          />
        )}
      </div>
      {isOpen && <div className="mt-1 space-y-0.5">{children}</div>}
    </div>
  )
}
