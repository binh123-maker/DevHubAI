import { FormEvent, useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Mail, Lock, ArrowRight, Check, ShieldCheck, RefreshCw, KeyRound } from "lucide-react"

import { authApi } from "@/api/auth.api"
import { getApiErrorMessage } from "@/api/axios"
import { Button } from "@/components/ui/button"
import { OtpInput } from "@/components/ui/OtpInput"

export default function ForgotPasswordPage() {
  const navigate = useNavigate()

  // Steps: 1 = Email, 2 = OTP, 3 = New Password, 4 = Complete
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1)

  const [email, setEmail] = useState("")
  const [otpCode, setOtpCode] = useState("")
  const [resetToken, setResetToken] = useState("")

  const [newPassword, setNewPassword] = useState("")
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("")

  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const [isLoading, setIsLoading] = useState(false)
  const [cooldown, setCooldown] = useState(0)

  // Cooldown countdown timer
  useEffect(() => {
    if (cooldown <= 0) return
    const timer = setInterval(() => {
      setCooldown((prev) => prev - 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [cooldown])

  // Live password requirements validation
  const requirements = {
    minLength: newPassword.length >= 8,
    hasUpper: /[A-Z]/.test(newPassword),
    hasLower: /[a-z]/.test(newPassword),
    hasNumber: /[0-9]/.test(newPassword),
    hasSpecial: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(newPassword),
    passwordsMatch: newPassword.length >= 8 && newPassword === newPasswordConfirm,
  }

  const isPasswordValid =
    requirements.minLength &&
    requirements.hasUpper &&
    requirements.hasLower &&
    requirements.hasNumber &&
    requirements.hasSpecial &&
    requirements.passwordsMatch

  // Step 1: Request OTP
  async function handleSendOtp(e?: FormEvent) {
    if (e) e.preventDefault()
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("Vui lòng nhập địa chỉ email hợp lệ.")
      return
    }

    setError(null)
    setIsLoading(true)
    try {
      const { data } = await authApi.forgotPassword(email.trim())
      setMessage(data.message)
      setCooldown(data.cooldown_seconds || 60)
      setStep(2)
    } catch (err) {
      setError(getApiErrorMessage(err, "Không thể gửi mã OTP. Vui lòng thử lại."))
    } finally {
      setIsLoading(false)
    }
  }

  // Step 2: Verify OTP
  async function handleVerifyOtp(code: string) {
    setError(null)
    setIsLoading(true)
    try {
      const { data } = await authApi.verifyOtp(email.trim(), code)
      setResetToken(data.reset_token)
      setStep(3)
    } catch (err) {
      setError(getApiErrorMessage(err, "Xác thực mã OTP thất bại. Vui lòng kiểm tra lại."))
    } finally {
      setIsLoading(false)
    }
  }

  // Step 3: Reset Password
  async function handleResetPassword(e: FormEvent) {
    e.preventDefault()
    if (!isPasswordValid) return

    setError(null)
    setIsLoading(true)
    try {
      await authApi.resetPassword({
        email: email.trim(),
        reset_token: resetToken,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      })
      setStep(4)
    } catch (err) {
      setError(getApiErrorMessage(err, "Đặt lại mật khẩu thất bại. Vui lòng thử lại."))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25 }}
      className="w-full max-w-md mx-auto rounded-[28px] border border-border/80 bg-card/75 p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6"
    >
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-indigo-600 text-primary-foreground font-extrabold text-2xl shadow-md ring-4 ring-primary/10">
          <KeyRound className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight text-foreground">Khôi phục mật khẩu</h1>
        <p className="text-xs text-muted-foreground">Bảo mật hệ thống DevHub AI Knowledge Workspace</p>
      </div>

      {/* Step Progress Indicator (Part 21) */}
      <div className="flex items-center justify-between px-2">
        {[
          { number: 1, label: "Email" },
          { number: 2, label: "Mã OTP" },
          { number: 3, label: "Mật khẩu" },
          { number: 4, label: "Hoàn tất" },
        ].map((s) => (
          <div key={s.number} className="flex items-center gap-1.5">
            <div
              className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-all ${
                step >= s.number
                  ? "bg-primary text-primary-foreground shadow-sm ring-2 ring-primary/20"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {step > s.number ? <Check className="h-3.5 w-3.5" /> : s.number}
            </div>
            <span
              className={`text-[11px] font-semibold hidden sm:inline ${
                step >= s.number ? "text-foreground" : "text-muted-foreground"
              }`}
            >
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {error && (
        <p className="text-xs text-destructive font-semibold p-3 bg-destructive/10 rounded-2xl border border-destructive/20">
          {error}
        </p>
      )}

      {/* STEP 1: Enter Email */}
      {step === 1 && (
        <form onSubmit={handleSendOtp} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Nhập email đăng ký tài khoản</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
                <Mail className="h-4 w-4" />
              </div>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="flex h-11 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-primary/40 transition-all"
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !email.trim()}
            className="w-full h-11 rounded-[16px] bg-gradient-to-r from-primary to-indigo-600 font-bold text-xs shadow-md hover:shadow-lg transition-all click-press text-white"
          >
            {isLoading ? "Đang gửi..." : "Gửi mã xác thực OTP"}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </form>
      )}

      {/* STEP 2: 6-Box OTP Input (Part 22) */}
      {step === 2 && (
        <div className="space-y-5 text-center">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-foreground">
              Mã xác thực OTP đã được gửi đến:
            </p>
            <p className="text-xs font-bold text-primary font-mono">{email}</p>
          </div>

          {/* 6 Separate OTP Boxes */}
          <OtpInput length={6} onComplete={handleVerifyOtp} isDisabled={isLoading} />

          {/* Resend Cooldown Timer */}
          <div className="pt-2 flex flex-col items-center gap-2">
            <Button
              variant="outline"
              type="button"
              disabled={cooldown > 0 || isLoading}
              onClick={() => handleSendOtp()}
              className="h-9 rounded-2xl text-xs font-semibold gap-2 border-border/80"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${cooldown > 0 ? "animate-spin" : ""}`} />
              {cooldown > 0 ? `Thử lại sau (${cooldown}s)` : "Gửi lại mã OTP"}
            </Button>
          </div>
        </div>
      )}

      {/* STEP 3: Enter New Password with Policy Checklist (Part 21) */}
      {step === 3 && (
        <form onSubmit={handleResetPassword} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Mật khẩu mới</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
                <Lock className="h-4 w-4" />
              </div>
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                className="flex h-10 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-primary/40 transition-all"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Xác nhận mật khẩu mới</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-muted-foreground">
                <ShieldCheck className="h-4 w-4" />
              </div>
              <input
                id="newPasswordConfirm"
                type="password"
                value={newPasswordConfirm}
                onChange={(e) => setNewPasswordConfirm(e.target.value)}
                placeholder="••••••••"
                className="flex h-10 w-full rounded-[16px] border border-input bg-background/80 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-primary/40 transition-all"
              />
            </div>
          </div>

          {/* Password Policy Requirements Checklist (Part 21) */}
          <div className="p-3.5 rounded-2xl bg-card border border-border/60 space-y-1.5 text-[11px]">
            <p className="font-bold text-foreground">Yêu cầu bảo mật mật khẩu:</p>
            <div className="grid grid-cols-2 gap-1 font-medium">
              <span className={requirements.minLength ? "text-emerald-500 font-bold" : "text-muted-foreground"}>
                {requirements.minLength ? "✓" : "○"} Tối thiểu 8 ký tự
              </span>
              <span className={requirements.hasUpper ? "text-emerald-500 font-bold" : "text-muted-foreground"}>
                {requirements.hasUpper ? "✓" : "○"} Chữ hoa (A-Z)
              </span>
              <span className={requirements.hasLower ? "text-emerald-500 font-bold" : "text-muted-foreground"}>
                {requirements.hasLower ? "✓" : "○"} Chữ thường (a-z)
              </span>
              <span className={requirements.hasNumber ? "text-emerald-500 font-bold" : "text-muted-foreground"}>
                {requirements.hasNumber ? "✓" : "○"} Chữ số (0-9)
              </span>
              <span className={requirements.hasSpecial ? "text-emerald-500 font-bold" : "text-muted-foreground"}>
                {requirements.hasSpecial ? "✓" : "○"} Ký tự đặc biệt
              </span>
              <span className={requirements.passwordsMatch ? "text-emerald-500 font-bold" : "text-muted-foreground"}>
                {requirements.passwordsMatch ? "✓" : "○"} Mật khẩu trùng khớp
              </span>
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !isPasswordValid}
            className="w-full h-11 rounded-[16px] bg-gradient-to-r from-primary to-indigo-600 font-bold text-xs shadow-md hover:shadow-lg transition-all click-press text-white"
          >
            {isLoading ? "Đang cập nhật..." : "Xác nhận đổi mật khẩu"}
          </Button>
        </form>
      )}

      {/* STEP 4: Success Complete */}
      {step === 4 && (
        <div className="space-y-4 text-center py-2">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500 font-extrabold ring-4 ring-emerald-500/20">
            <Check className="h-7 w-7" />
          </div>
          <h2 className="text-lg font-bold text-foreground">Đặt lại mật khẩu thành công!</h2>
          <p className="text-xs text-muted-foreground">
            Mật khẩu của bạn đã được cập nhật an toàn. Tất cả phiên đăng nhập cũ trên thiết bị khác đã được ngắt kết nối.
          </p>
          <Button
            onClick={() => navigate("/login", { replace: true })}
            className="w-full h-11 rounded-[16px] bg-primary font-bold text-xs text-primary-foreground shadow-md hover:bg-primary/90 transition-all"
          >
            Đăng nhập ngay
          </Button>
        </div>
      )}

      {/* Footer Back Link */}
      {step !== 4 && (
        <p className="text-center text-xs text-muted-foreground">
          Quay lại{" "}
          <Link to="/login" className="font-bold text-primary hover:underline">
            Trang Đăng Nhập
          </Link>
        </p>
      )}
    </motion.div>
  )
}
