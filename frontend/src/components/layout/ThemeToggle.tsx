import { Sun, Moon, Monitor } from "lucide-react"

import { useTheme } from "@/contexts/ThemeContext"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-9 w-9 text-muted-foreground hover:text-foreground">
          {resolvedTheme === "dark" ? (
            <Moon className="h-4 w-4 text-purple-400" />
          ) : (
            <Sun className="h-4 w-4 text-amber-500" />
          )}
          <span className="sr-only">Chuyển đổi giao diện</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")} className="gap-2 cursor-pointer text-xs">
          <Sun className="h-4 w-4 text-amber-500" />
          <span>Giao diện Sáng (Light)</span>
          {theme === "light" && <span className="ml-auto font-bold text-primary">✓</span>}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")} className="gap-2 cursor-pointer text-xs">
          <Moon className="h-4 w-4 text-purple-400" />
          <span>Giao diện Tối (Dark)</span>
          {theme === "dark" && <span className="ml-auto font-bold text-primary">✓</span>}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")} className="gap-2 cursor-pointer text-xs">
          <Monitor className="h-4 w-4 text-blue-500" />
          <span>Theo hệ thống (System)</span>
          {theme === "system" && <span className="ml-auto font-bold text-primary">✓</span>}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
