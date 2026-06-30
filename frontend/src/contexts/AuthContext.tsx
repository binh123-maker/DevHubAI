import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"

import { authApi, type UserProfile } from "@/api/auth.api"
import { clearTokens } from "@/api/axios"

interface AuthContextValue {
  user: UserProfile | null
  isAuthenticated: boolean
  isLoading: boolean
  isInitializing: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, passwordConfirm: string, fullName: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function storeTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem("access_token", accessToken)
  localStorage.setItem("refresh_token", refreshToken)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)

  const fetchCurrentUser = useCallback(async () => {
    const { data } = await authApi.me()
    setUser(data)
    setIsAuthenticated(true)
  }, [])

  useEffect(() => {
    async function bootstrap() {
      const accessToken = localStorage.getItem("access_token")
      if (!accessToken) {
        setIsInitializing(false)
        return
      }

      try {
        await fetchCurrentUser()
      } catch {
        clearTokens()
        setUser(null)
        setIsAuthenticated(false)
      } finally {
        setIsInitializing(false)
      }
    }

    void bootstrap()
  }, [fetchCurrentUser])

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true)
      try {
        const { data } = await authApi.login({ email, password })
        storeTokens(data.access_token, data.refresh_token)
        await fetchCurrentUser()
      } finally {
        setIsLoading(false)
      }
    },
    [fetchCurrentUser],
  )

  const register = useCallback(
    async (email: string, password: string, passwordConfirm: string, fullName: string) => {
      setIsLoading(true)
      try {
        const { data } = await authApi.register({
          email,
          password,
          password_confirm: passwordConfirm,
          full_name: fullName,
        })
        storeTokens(data.access_token, data.refresh_token)
        await fetchCurrentUser()
      } finally {
        setIsLoading(false)
      }
    },
    [fetchCurrentUser],
  )

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem("refresh_token")
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken)
      }
    } catch {
      // Clear local session even if server logout fails
    } finally {
      clearTokens()
      setUser(null)
      setIsAuthenticated(false)
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      isInitializing,
      login,
      register,
      logout,
    }),
    [user, isAuthenticated, isLoading, isInitializing, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
