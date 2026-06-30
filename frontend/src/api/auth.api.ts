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

export const authApi = {
  login: (payload: LoginPayload) => apiClient.post<TokenResponse>("/auth/login", payload),
  register: (payload: RegisterPayload) => apiClient.post<TokenResponse>("/auth/register", payload),
  logout: (refresh_token: string) => apiClient.post("/auth/logout", { refresh_token }),
  refresh: (refresh_token: string) => apiClient.post<TokenResponse>("/auth/refresh", { refresh_token }),
  me: () => apiClient.get<UserProfile>("/auth/me"),
}
