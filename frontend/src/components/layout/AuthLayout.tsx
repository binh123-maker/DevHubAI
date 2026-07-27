import { Outlet } from "react-router-dom"

export function AuthLayout() {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background p-4 sm:p-6">
      {/* Dynamic Animated Ambient Mesh Gradient Background */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40 dark:opacity-30">
        <div className="absolute -top-[20%] -left-[10%] h-[500px] w-[500px] rounded-full bg-gradient-to-tr from-primary via-indigo-500 to-purple-600 blur-[120px] animate-pulse" />
        <div className="absolute -bottom-[20%] -right-[10%] h-[600px] w-[600px] rounded-full bg-gradient-to-br from-blue-600 via-cyan-400 to-emerald-400 blur-[140px] animate-pulse" />
      </div>

      {/* Main Glass Card Wrapper (420px max width) */}
      <div className="relative z-10 w-full max-w-[420px]">
        <Outlet />
      </div>
    </div>
  )
}
