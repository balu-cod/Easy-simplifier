import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '@/services/auth'
import { User, LoginCredentials, RegisterData } from '@/types/auth'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const userData = await authApi.getCurrentUser()
          setUser(userData)
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('access_token')
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      const response = await authApi.login(credentials)
      localStorage.setItem('access_token', response.access_token)
      setUser(response.user)
    } catch (error) {
      throw error
    }
  }

  const register = async (data: RegisterData): Promise<void> => {
    try {
      const response = await authApi.register(data)
      setUser(response)
      // Note: No token stored yet - user needs to verify email first
    } catch (error) {
      throw error
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await authApi.logout()
    } catch (error) {
      // Even if logout fails on server, clear local state
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }

  const refreshUser = async (): Promise<void> => {
    try {
      const userData = await authApi.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user:', error)
      // Don't logout automatically - let the user stay logged in
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}