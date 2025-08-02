import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HomeIcon,
  CloudArrowUpIcon,
  PhotoIcon,
  PuzzlePieceIcon,
  ChatBubbleLeftRightIcon,
  UserIcon,
  Cog6ToothIcon,
  ChatBubbleBottomCenterTextIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
  BellIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/hooks/useTheme'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuth()
  const { theme, toggleTheme } = useTheme()

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon, public: true },
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Upload Image', href: '/upload', icon: CloudArrowUpIcon },
    { name: 'Gallery', href: '/gallery', icon: PhotoIcon },
    { name: 'Games', href: '/games', icon: PuzzlePieceIcon },
    { name: 'AI Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
    { name: 'Profile', href: '/profile', icon: UserIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
    { name: 'Feedback', href: '/feedback', icon: ChatBubbleBottomCenterTextIcon },
  ]

  const filteredNavigation = navigation.filter(item => 
    item.public || isAuthenticated
  )

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="bg-white dark:bg-gray-900">
        {/* Mobile sidebar overlay */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 lg:hidden"
            >
              <div
                className="fixed inset-0 bg-gray-600 bg-opacity-75"
                onClick={() => setSidebarOpen(false)}
              />
              <motion.div
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="relative flex flex-col flex-1 w-64 pt-5 pb-4 bg-white dark:bg-gray-800"
              >
                <div className="absolute top-0 right-0 -mr-12 pt-2">
                  <button
                    type="button"
                    className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                    onClick={() => setSidebarOpen(false)}
                  >
                    <XMarkIcon className="h-6 w-6 text-white" />
                  </button>
                </div>
                <div className="flex-shrink-0 px-4">
                  <Link to="/" className="flex items-center">
                    <div className="h-8 w-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-lg">AI</span>
                    </div>
                    <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
                      ImageProcessor
                    </span>
                  </Link>
                </div>
                <nav className="mt-8 flex-1 px-2 space-y-1">
                  {filteredNavigation.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.href
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`${
                          isActive
                            ? 'bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                        } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
                        onClick={() => setSidebarOpen(false)}
                      >
                        <Icon className="mr-3 flex-shrink-0 h-6 w-6" />
                        {item.name}
                      </Link>
                    )
                  })}
                </nav>
                {isAuthenticated && (
                  <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-2 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white"
                    >
                      <ArrowRightOnRectangleIcon className="mr-3 h-6 w-6" />
                      Sign out
                    </button>
                  </div>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Desktop sidebar */}
        <div className="hidden lg:flex lg:flex-shrink-0">
          <div className="flex flex-col w-64">
            <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
              <div className="flex items-center flex-shrink-0 px-4">
                <Link to="/" className="flex items-center">
                  <div className="h-8 w-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">AI</span>
                  </div>
                  <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
                    ImageProcessor
                  </span>
                </Link>
              </div>
              <nav className="mt-8 flex-1 px-2 space-y-1">
                {filteredNavigation.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`${
                        isActive
                          ? 'bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                      } group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200`}
                    >
                      <Icon className="mr-3 flex-shrink-0 h-6 w-6" />
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
              {isAuthenticated && (
                <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={handleLogout}
                    className="flex items-center w-full px-2 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                  >
                    <ArrowRightOnRectangleIcon className="mr-3 h-6 w-6" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex flex-col w-0 flex-1 lg:ml-64">
          {/* Top navigation */}
          <div className="relative z-10 flex-shrink-0 flex h-16 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
            <button
              type="button"
              className="px-4 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            
            <div className="flex-1 px-4 flex justify-between items-center">
              <div className="flex-1 flex">
                <div className="w-full flex md:ml-0">
                  <div className="relative w-full text-gray-400 focus-within:text-gray-600 dark:focus-within:text-gray-300">
                    <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                      <MagnifyingGlassIcon className="h-5 w-5" />
                    </div>
                    <input
                      className="block w-full h-full pl-8 pr-3 py-2 border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 dark:focus:placeholder-gray-500 focus:ring-0 focus:border-transparent bg-transparent"
                      placeholder="Search images, games, or chat..."
                      type="search"
                    />
                  </div>
                </div>
              </div>
              
              <div className="ml-4 flex items-center md:ml-6 space-x-3">
                {/* Theme toggle */}
                <button
                  onClick={toggleTheme}
                  className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {theme === 'light' ? (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  )}
                </button>

                {/* Notifications */}
                {isAuthenticated && (
                  <button className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <BellIcon className="h-5 w-5" />
                  </button>
                )}

                {/* User menu */}
                {isAuthenticated && user && (
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      <div className="h-8 w-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-medium text-sm">
                          {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
                        </span>
                      </div>
                      <div className="hidden md:block">
                        <div className="text-sm font-medium text-gray-700 dark:text-gray-200">
                          {user.username}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Level {user.level} • {user.total_score} pts
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {!isAuthenticated && (
                  <div className="flex items-center space-x-2">
                    <Link
                      to="/auth/login"
                      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-3 py-2 text-sm font-medium"
                    >
                      Sign in
                    </Link>
                    <Link
                      to="/auth/register"
                      className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200"
                    >
                      Sign up
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Page content */}
          <main className="flex-1 relative overflow-y-auto focus:outline-none">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="py-6"
            >
              {children}
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default Layout