export interface UserProfile {
  id: string
  email: string
  role: string
  full_name: string
  avatar_url: string | null
  gender: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

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
