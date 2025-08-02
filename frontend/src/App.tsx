import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

// Layout Components
import Layout from '@/components/layout/Layout'
import AuthLayout from '@/components/layout/AuthLayout'

// Pages
import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import ImageUploadPage from '@/pages/ImageUploadPage'
import ImageGalleryPage from '@/pages/ImageGalleryPage'
import ImageDetailPage from '@/pages/ImageDetailPage'
import GamesPage from '@/pages/games/GamesPage'
import GamePage from '@/pages/games/GamePage'
import ChatPage from '@/pages/ChatPage'
import ProfilePage from '@/pages/ProfilePage'
import SettingsPage from '@/pages/SettingsPage'
import FeedbackPage from '@/pages/FeedbackPage'
import NotFoundPage from '@/pages/NotFoundPage'

// Context and Hooks
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { useAuth } from '@/hooks/useAuth'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />
  }

  return <>{children}</>
}

// Public Route Component (redirect if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Layout><HomePage /></Layout>} />
                
                {/* Auth Routes */}
                <Route path="/auth/login" element={
                  <PublicRoute>
                    <AuthLayout><LoginPage /></AuthLayout>
                  </PublicRoute>
                } />
                
                <Route path="/auth/register" element={
                  <PublicRoute>
                    <AuthLayout><RegisterPage /></AuthLayout>
                  </PublicRoute>
                } />

                {/* Protected Routes */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Layout><DashboardPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/upload" element={
                  <ProtectedRoute>
                    <Layout><ImageUploadPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/gallery" element={
                  <ProtectedRoute>
                    <Layout><ImageGalleryPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/images/:imageId" element={
                  <ProtectedRoute>
                    <Layout><ImageDetailPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/games" element={
                  <ProtectedRoute>
                    <Layout><GamesPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/games/:gameType" element={
                  <ProtectedRoute>
                    <Layout><GamePage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/chat" element={
                  <ProtectedRoute>
                    <Layout><ChatPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/profile" element={
                  <ProtectedRoute>
                    <Layout><ProfilePage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/settings" element={
                  <ProtectedRoute>
                    <Layout><SettingsPage /></Layout>
                  </ProtectedRoute>
                } />

                <Route path="/feedback" element={
                  <ProtectedRoute>
                    <Layout><FeedbackPage /></Layout>
                  </ProtectedRoute>
                } />

                {/* 404 Route */}
                <Route path="*" element={<Layout><NotFoundPage /></Layout>} />
              </Routes>

              {/* Toast Notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    duration: 3000,
                    iconTheme: {
                      primary: '#22c55e',
                      secondary: '#fff',
                    },
                  },
                  error: {
                    duration: 5000,
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App