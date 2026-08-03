import { FormEvent, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Mail, Lock, User, ArrowRight, ShieldCheck } from "lucide-react"

import { getApiErrorMessage } from "@/api/axios"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"

import { authApi } from "@/api/auth.api"

export default function RegisterPage() {
  const { register, isLoading } = useAuth()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [passwordConfirm, setPasswordConfirm] = useState("")
  const [agreeTerms, setAgreeTerms] = useState(false)
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
  const [fieldErrors, setFieldErrors] = useState<{
    fullName?: string
    email?: string
    password?: string
    passwordConfirm?: string
    terms?: string
  }>({})
  const [error, setError] = useState<string | null>(null)

  // Password strength logic
  const calculatePasswordStrength = (pass: string) => {
    if (!pass) return 0
    let score = 0
    if (pass.length >= 8) score += 25
    if (/[A-Z]/.test(pass)) score += 25
    if (/[0-9]/.test(pass)) score += 25
    if (/[^A-Za-z0-9]/.test(pass)) score += 25
    return score
  }

  const strength = calculatePasswordStrength(password)

  function validate() {
    const errors: {
      fullName?: string
      email?: string
      password?: string
      passwordConfirm?: string
      terms?: string
    } = {}

    if (!fullName.trim()) {
      errors.fullName = "Họ tên là bắt buộc"
    }
    if (!email.trim()) {
      errors.email = "Email là bắt buộc"
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = "Email không hợp lệ"
    }
    if (!password) {
      errors.password = "Mật khẩu là bắt buộc"
    } else if (password.length < 8) {
      errors.password = "Mật khẩu phải có ít nhất 8 ký tự"
    }
    if (!passwordConfirm) {
      errors.passwordConfirm = "Xác nhận mật khẩu là bắt buộc"
    } else if (password !== passwordConfirm) {
      errors.passwordConfirm = "Mật khẩu xác nhận không khớp"
    }
    if (!agreeTerms) {
      errors.terms = "Bạn cần đồng ý với Điều khoản dịch vụ"
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
      await register(email.trim(), password, passwordConfirm, fullName.trim())
      navigate("/workspaces", { replace: true })
    } catch (err) {
      setError(getApiErrorMessage(err, "Đăng ký thất bại. Vui lòng thử lại."))
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25 }}
      className="w-full rounded-[28px] border border-border/80 bg-card/75 p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-5"
    >
      {/* Header */}
      <div className="text-center space-y-1.5">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-indigo-600 text-primary-foreground font-extrabold text-2xl shadow-md ring-4 ring-primary/10">
          D
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight text-foreground">Create your Account</h1>
        <p className="text-xs text-muted-foreground">Start building your AI Knowledge Workspace</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
        {/* Full Name */}
        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground">Full Name</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
              <User className="h-4 w-4" />
            </div>
            <input
              id="fullName"
              type="text"
              autoComplete="name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Doe"
              className="flex h-10 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium placeholder:text-muted-foreground/60 focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </div>
          {fieldErrors.fullName && <p className="text-[11px] text-destructive font-semibold">{fieldErrors.fullName}</p>}
        </div>

        {/* Email */}
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
              className="flex h-10 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium placeholder:text-muted-foreground/60 focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </div>
          {fieldErrors.email && <p className="text-[11px] text-destructive font-semibold">{fieldErrors.email}</p>}
        </div>

        {/* Password */}
        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground">Password</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
              <Lock className="h-4 w-4" />
            </div>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="flex h-10 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium placeholder:text-muted-foreground/60 focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </div>
          {/* Password Strength Meter */}
          {password && (
            <div className="space-y-1 pt-1">
              <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${
                    strength < 50 ? "bg-destructive" : strength < 75 ? "bg-amber-500" : "bg-emerald-500"
                  }`}
                  style={{ width: `${strength}%` }}
                />
              </div>
              <p className="text-[10px] text-muted-foreground font-mono">
                Mật khẩu: {strength < 50 ? "Yếu" : strength < 75 ? "Trung bình" : "Mạnh (An toàn)"}
              </p>
            </div>
          )}
          {fieldErrors.password && <p className="text-[11px] text-destructive font-semibold">{fieldErrors.password}</p>}
        </div>

        {/* Confirm Password */}
        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground">Confirm Password</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <input
              id="passwordConfirm"
              type="password"
              autoComplete="new-password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="••••••••"
              className="flex h-10 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium placeholder:text-muted-foreground/60 focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </div>
          {fieldErrors.passwordConfirm && (
            <p className="text-[11px] text-destructive font-semibold">{fieldErrors.passwordConfirm}</p>
          )}
        </div>

        {/* Terms Checkbox */}
        <div className="space-y-1 pt-1">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              className="rounded text-primary focus:ring-primary/30"
            />
            <span className="text-[11px] text-muted-foreground leading-tight">
              Tôi đồng ý với <a href="#" className="text-primary underline">Điều khoản dịch vụ</a> và <a href="#" className="text-primary underline">Chính sách bảo mật</a>
            </span>
          </label>
          {fieldErrors.terms && <p className="text-[11px] text-destructive font-semibold">{fieldErrors.terms}</p>}
        </div>

        {error && <p className="text-xs text-destructive font-bold p-2 bg-destructive/10 rounded-xl">{error}</p>}

        {/* Submit */}
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full h-11 rounded-[16px] bg-gradient-to-r from-primary to-indigo-600 font-bold text-xs shadow-md hover:shadow-lg transition-all click-press text-white mt-2"
        >
          {isLoading ? "Creating Account..." : "Sign Up"}
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </form>

      {/* Google Sign In Button (ADR 9) */}
      <div className="pt-1">
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
      </div>

      {/* Switch to Login */}
      <p className="text-center text-xs text-muted-foreground">
        Already have an account?{" "}
        <Link to="/login" className="font-bold text-primary hover:underline">
          Sign In
        </Link>
      </p>
    </motion.div>
  )
}
