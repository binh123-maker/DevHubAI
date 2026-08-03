import { useEffect, useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"

import { authApi } from "@/api/auth.api"
import { getApiErrorMessage } from "@/api/axios"
import { tokenStorage } from "@/auth/utils/tokenStorage"

export default function OAuthCallbackPage() {
  const { provider = "google" } = useParams<{ provider: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    async function processCallback() {
      const code = searchParams.get("code")
      const state = searchParams.get("state")
      const storedState = sessionStorage.getItem("oauth_state")

      console.log("[OAuth Callback] Start processing:", { provider, code: code ? "RECEIVED" : "MISSING", state, storedState })

      if (!code) {
        console.error("[OAuth Callback] Missing authorization code")
        setError("Không nhận được mã xác thực từ Google.")
        setIsProcessing(false)
        return
      }

      // CSRF State parameter validation
      if (!state || !storedState || state !== storedState) {
        console.error("[OAuth Callback] CSRF State mismatch:", { state, storedState })
        setError("Mã trạng thái bảo mật (CSRF state) không hợp lệ hoặc đã hết hạn.")
        setIsProcessing(false)
        return
      }

      const redirectUri = `${window.location.origin}/auth/callback/google`

      try {
        console.log("[OAuth Callback] Exchanging code via API with redirectUri:", redirectUri)
        const { data } = await authApi.handleGoogleCallback(code, redirectUri)
        console.log("[OAuth Callback] API Response received successfully:", data)

        tokenStorage.setTokens(data.access_token, data.refresh_token)
        console.log("[OAuth Callback] Tokens saved to localStorage")
        sessionStorage.removeItem("oauth_state")
        
        console.log("[OAuth Callback] Navigating to /workspaces")
        window.location.href = "/workspaces"
      } catch (err) {
        console.error("[OAuth Callback] Error during callback handling:", err)
        setError(getApiErrorMessage(err, "Xác thực Google OAuth thất bại. Vui lòng thử lại."))
        setIsProcessing(false)
      }
    }

    void processCallback()
  }, [provider, searchParams, navigate])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4 text-center">
      <div className="w-full max-w-md space-y-4 rounded-3xl border border-border/80 bg-card p-8 shadow-2xl backdrop-blur-xl">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary font-extrabold text-2xl">
          D
        </div>

        {isProcessing ? (
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-foreground">Đang xác thực với {provider.toUpperCase()}...</h2>
            <p className="text-xs text-muted-foreground">Vui lòng chờ trong giây lát.</p>
            <div className="pt-4 flex justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-destructive">Đăng nhập thất bại</h2>
            <p className="text-xs text-destructive bg-destructive/10 p-3 rounded-xl font-medium">{error}</p>
            <button
              type="button"
              onClick={() => navigate("/login", { replace: true })}
              className="w-full rounded-2xl bg-primary py-2.5 text-xs font-bold text-primary-foreground hover:bg-primary/90 transition-all"
            >
              Quay lại trang Đăng Nhập
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

