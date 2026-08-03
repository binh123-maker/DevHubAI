import { apiClient } from "./axios"

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  password_confirm: string
  full_name: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserProfile {
  id: string
  email: string
  role: string
  full_name: string
  avatar_url: string | null
  gender: string
}

export interface GoogleOAuthLoginUrlResponse {
  url: string
  state: string
  provider: string
}

export interface GoogleOAuthStatusResponse {
  connected: boolean
  email?: string | null
  display_name?: string | null
  avatar_url?: string | null
  linked_at?: string | null
  last_login_at?: string | null
  can_disconnect: boolean
}

export const authApi = {
  login: (payload: LoginPayload) => apiClient.post<TokenResponse>("/auth/login", payload),
  register: (payload: RegisterPayload) => apiClient.post<TokenResponse>("/auth/register", payload),
  logout: (refresh_token: string) => apiClient.post("/auth/logout", { refresh_token }),
  refresh: (refresh_token: string) => apiClient.post<TokenResponse>("/auth/refresh", { refresh_token }),
  me: () => apiClient.get<UserProfile>("/auth/me"),

  // Google OAuth Methods (ADR 4 & ADR 5)
  getGoogleOAuthUrl: (redirectUri: string) =>
    apiClient.get<GoogleOAuthLoginUrlResponse>("/auth/oauth/google/login", {
      params: { redirect_uri: redirectUri },
    }),
  handleGoogleCallback: (code: string, redirectUri: string) =>
    apiClient.get<TokenResponse>("/auth/oauth/google/callback", {
      params: { code, redirect_uri: redirectUri },
    }),
  getGoogleStatus: () => apiClient.get<GoogleOAuthStatusResponse>("/auth/oauth/google/status"),
  disconnectGoogle: () => apiClient.post("/auth/oauth/google/disconnect"),
}
