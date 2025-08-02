export interface User {
  id: number
  uuid: string
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  bio?: string
  location?: string
  website?: string
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  total_score: number
  games_played: number
  level: number
  experience_points: number
  language: string
  theme: string
  notifications_enabled: boolean
  created_at: string
  updated_at: string
  last_login?: string
  two_factor_enabled: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface AuthError {
  detail: string
  status_code?: number
}

export interface PasswordReset {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  new_password: string
}

export interface TwoFactorSetup {
  secret: string
  qr_code: string
}

export interface TwoFactorVerify {
  token: string
}

export interface SocialAuthRequest {
  provider: string
  code: string
  redirect_uri: string
}