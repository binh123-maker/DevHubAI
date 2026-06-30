import { Link, Outlet, useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"

const navItems = [
  { to: "/workspaces", label: "Workspaces" },
  { to: "/chat", label: "Chat" },
  { to: "/profile", label: "Profile" },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate("/login", { replace: true })
  }

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-muted/30 p-4">
        <div className="mb-2 text-xl font-bold text-primary">DevHub AI</div>
        {user && <p className="mb-6 text-sm text-muted-foreground">{user.full_name || user.email}</p>}
        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="block rounded-md px-3 py-2 text-sm hover:bg-accent"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <Button variant="outline" className="mt-8 w-full" onClick={() => void handleLogout()}>
          Logout
        </Button>
      </aside>
      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  )
}
