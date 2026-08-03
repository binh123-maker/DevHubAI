import { FormEvent, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Mail, Lock, ArrowRight } from "lucide-react"

import { getApiErrorMessage } from "@/api/axios"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"

import { authApi } from "@/api/auth.api"
import { sanitizeRedirectPath } from "@/auth/utils/pathSanitizer"

export default function LoginPage() {
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const rawFrom = (location.state as { from?: { pathname: string } } | null)?.from?.pathname
  const from = sanitizeRedirectPath(rawFrom, "/workspaces")

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({})
  const [error, setError] = useState<string | null>(null)
  const [isOAuthLoading, setIsOAuthLoading] = useState(false)

  async function handleGoogleLogin() {
    setError(null)
    setIsOAuthLoading(true)
    try {
      const redirectUri = `${window.location.origin}/auth/callback/google`
      const { data } = await authApi.getGoogleOAuthUrl(redirectUri)
      sessionStorage.setItem("oauth_state", data.state)
      window.location.href = data.url
    } catch (err) {
      setError(getApiErrorMessage(err, "Không thể khởi tạo đăng nhập với Google."))
      setIsOAuthLoading(false)
    }
  }

  function validate() {
    const errors: { email?: string; password?: string } = {}
    if (!email.trim()) {
      errors.email = "Email là bắt buộc"
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = "Email không hợp lệ"
    }
    if (!password) {
      errors.password = "Mật khẩu là bắt buộc"
    }
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    if (!validate()) {
      return
    }

    try {
      await login(email.trim(), password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(getApiErrorMessage(err, "Đăng nhập thất bại. Kiểm tra email và mật khẩu."))
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25 }}
      className="w-full rounded-[28px] border border-border/80 bg-card/75 p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6"
    >
      {/* Brand Logo & Slogan Header */}
      <div className="text-center space-y-2">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-indigo-600 text-primary-foreground font-extrabold text-2xl shadow-md ring-4 ring-primary/10">
          D
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight text-foreground">Welcome to DevHub AI</h1>
        <p className="text-xs text-muted-foreground">Build your AI Knowledge Workspace</p>
      </div>

      {/* Login Form */}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        {/* Email Field with Prefix Icon & 16px Radius */}
        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground">Email address</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
              <Mail className="h-4 w-4" />
            </div>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="flex h-11 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium placeholder:text-muted-foreground/60 focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </div>
          {fieldErrors.email && <p className="text-[11px] text-destructive font-semibold">{fieldErrors.email}</p>}
        </div>

        {/* Password Field with Prefix Icon */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-muted-foreground">Password</label>
            <Link to="/forgot-password" className="text-[11px] font-semibold text-primary hover:underline">
              Forgot Password?
            </Link>
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
              <Lock className="h-4 w-4" />
            </div>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="flex h-11 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium placeholder:text-muted-foreground/60 focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </div>
          {fieldErrors.password && <p className="text-[11px] text-destructive font-semibold">{fieldErrors.password}</p>}
        </div>

        {error && <p className="text-xs text-destructive font-bold p-2 bg-destructive/10 rounded-xl">{error}</p>}

        {/* Submit Gradient Button */}
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full h-11 rounded-[16px] bg-gradient-to-r from-primary to-indigo-600 font-bold text-xs shadow-md hover:shadow-lg transition-all click-press text-white"
        >
          {isLoading ? "Signing in..." : "Sign In"}
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </form>

      {/* Social Logins Divider */}
      <div className="relative flex items-center justify-center">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border/60" />
        </div>
        <span className="relative bg-card px-3 text-[11px] font-semibold text-muted-foreground uppercase">Or</span>
      </div>

      {/* Google Sign In Button (ADR 9) */}
      <Button
        variant="outline"
        type="button"
        onClick={handleGoogleLogin}
        disabled={isLoading || isOAuthLoading}
        className="w-full h-11 rounded-[16px] text-xs font-bold gap-2.5 hover:bg-accent/60 transition-all"
      >
        <svg className="h-4 w-4" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
          />
        </svg>
        {isOAuthLoading ? "Connecting..." : "Continue with Google"}
      </Button>

      {/* Switch to Register */}
      <p className="text-center text-xs text-muted-foreground">
        Don't have an account?{" "}
        <Link to="/register" className="font-bold text-primary hover:underline">
          Sign Up
        </Link>
      </p>
    </motion.div>
  )
}
