import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  CloudArrowUpIcon,
  CpuChipIcon,
  PuzzlePieceIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  RocketLaunchIcon,
  StarIcon,
  CheckIcon,
} from '@heroicons/react/24/outline'
import { useAuth } from '@/hooks/useAuth'

const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth()

  const features = [
    {
      name: 'AI-Powered OCR',
      description: 'Extract and understand text from any image with advanced optical character recognition technology.',
      icon: CpuChipIcon,
      color: 'from-blue-400 to-blue-600',
    },
    {
      name: 'Smart Image Analysis',
      description: 'Detect objects, analyze scenes, and get intelligent insights about your uploaded images.',
      icon: CloudArrowUpIcon,
      color: 'from-green-400 to-green-600',
    },
    {
      name: 'Interactive Games',
      description: 'Challenge yourself with pattern recognition, puzzles, and brain-training games.',
      icon: PuzzlePieceIcon,
      color: 'from-purple-400 to-purple-600',
    },
    {
      name: 'AI Chat Assistant',
      description: 'Discuss your images with an intelligent AI that understands context and provides helpful explanations.',
      icon: ChatBubbleLeftRightIcon,
      color: 'from-pink-400 to-pink-600',
    },
    {
      name: 'Secure & Private',
      description: 'Your images and data are protected with enterprise-grade security and privacy controls.',
      icon: ShieldCheckIcon,
      color: 'from-yellow-400 to-yellow-600',
    },
    {
      name: 'Lightning Fast',
      description: 'Get instant results with our optimized AI processing pipeline and modern infrastructure.',
      icon: RocketLaunchIcon,
      color: 'from-red-400 to-red-600',
    },
  ]

  const stats = [
    { name: 'Images Processed', value: '1.2M+' },
    { name: 'Active Users', value: '50K+' },
    { name: 'Games Played', value: '2.5M+' },
    { name: 'AI Accuracy', value: '98.5%' },
  ]

  const testimonials = [
    {
      content: "This app transformed how I handle documents. The OCR is incredibly accurate and the AI explanations are so helpful!",
      author: "Sarah Chen",
      role: "Researcher",
      avatar: "SC"
    },
    {
      content: "The games are addictive and actually help me think better. Plus, the image analysis features are mind-blowing.",
      author: "Alex Rivera",
      role: "Student", 
      avatar: "AR"
    },
    {
      content: "Perfect for my workflow. I can quickly extract text from screenshots and get AI insights instantly.",
      author: "Michael Wong",
      role: "Designer",
      avatar: "MW"
    }
  ]

  return (
    <div className="bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <div className="relative isolate">
        <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
          <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-primary-400 to-secondary-600 opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" />
        </div>

        <div className="mx-auto max-w-7xl px-6 pt-10 sm:pt-16 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl font-display"
            >
              Transform Images with{' '}
              <span className="bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                AI Intelligence
              </span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mt-6 text-lg leading-8 text-gray-600 dark:text-gray-300"
            >
              Upload any image and let our advanced AI extract text, analyze content, and provide intelligent explanations. 
              Plus, challenge yourself with interactive games designed to enhance your cognitive abilities.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mt-10 flex items-center justify-center gap-x-6"
            >
              {isAuthenticated ? (
                <Link
                  to="/upload"
                  className="rounded-md bg-primary-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 transition-all duration-200 transform hover:scale-105"
                >
                  Upload Image
                </Link>
              ) : (
                <Link
                  to="/auth/register"
                  className="rounded-md bg-primary-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 transition-all duration-200 transform hover:scale-105"
                >
                  Get Started Free
                </Link>
              )}
              <Link
                to="#features"
                className="text-sm font-semibold leading-6 text-gray-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-200"
              >
                Learn more <span aria-hidden="true">→</span>
              </Link>
            </motion.div>
          </div>

          {/* Hero Image/Demo */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-16 flow-root sm:mt-24"
          >
            <div className="relative rounded-xl bg-gray-900/5 dark:bg-gray-100/5 p-2 ring-1 ring-inset ring-gray-900/10 dark:ring-gray-100/10 lg:rounded-2xl lg:p-4">
              <div className="aspect-[16/9] rounded-md bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-800 dark:to-gray-700 flex items-center justify-center">
                <div className="text-center">
                  <CloudArrowUpIcon className="h-16 w-16 text-primary-600 mx-auto mb-4" />
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Interactive Demo Coming Soon
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]">
          <div className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-secondary-400 to-primary-600 opacity-20 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]" />
        </div>
      </div>

      {/* Stats Section */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mx-auto max-w-7xl px-6 lg:px-8 mt-32"
      >
        <div className="mx-auto max-w-2xl lg:max-w-none">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Trusted by users worldwide
            </h2>
            <p className="mt-4 text-lg leading-8 text-gray-600 dark:text-gray-300">
              Join thousands of users who are already transforming their productivity with AI
            </p>
          </div>
          <dl className="mt-16 grid grid-cols-1 gap-0.5 overflow-hidden rounded-2xl text-center sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="flex flex-col bg-gray-400/5 dark:bg-gray-600/10 p-8"
              >
                <dt className="text-sm font-semibold leading-6 text-gray-600 dark:text-gray-300">
                  {stat.name}
                </dt>
                <dd className="order-first text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
                  {stat.value}
                </dd>
              </motion.div>
            ))}
          </dl>
        </div>
      </motion.div>

      {/* Features Section */}
      <div id="features" className="mx-auto max-w-7xl px-6 lg:px-8 mt-32">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-base font-semibold leading-7 text-primary-600 dark:text-primary-400">
            Powerful Features
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Everything you need in one platform
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600 dark:text-gray-300">
            Combine the power of AI image processing with engaging interactive experiences
          </p>
        </div>
        
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="flex flex-col"
                >
                  <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900 dark:text-white">
                    <div className={`h-10 w-10 rounded-lg bg-gradient-to-r ${feature.color} p-2 text-white`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    {feature.name}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600 dark:text-gray-300">
                    <p className="flex-auto">{feature.description}</p>
                  </dd>
                </motion.div>
              )
            })}
          </dl>
        </div>
      </div>

      {/* Testimonials Section */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mx-auto max-w-7xl px-6 lg:px-8 mt-32"
      >
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            What our users say
          </h2>
        </div>
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="flex flex-col pb-10 sm:pb-16 lg:pb-0 lg:pr-8 xl:pr-20"
            >
              <div className="mb-4">
                {[...Array(5)].map((_, i) => (
                  <StarIcon key={i} className="h-5 w-5 text-yellow-400 inline" />
                ))}
              </div>
              <blockquote className="text-lg leading-8 text-gray-900 dark:text-white sm:text-xl sm:leading-9">
                <p>"{testimonial.content}"</p>
              </blockquote>
              <div className="mt-8 flex items-center gap-x-4">
                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center">
                  <span className="text-white font-medium text-sm">{testimonial.avatar}</span>
                </div>
                <div>
                  <div className="font-semibold text-gray-900 dark:text-white">{testimonial.author}</div>
                  <div className="text-gray-600 dark:text-gray-300">{testimonial.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mx-auto max-w-7xl px-6 lg:px-8 mt-32 mb-16"
      >
        <div className="relative isolate overflow-hidden bg-gradient-to-r from-primary-600 to-secondary-600 px-6 py-24 text-center shadow-2xl rounded-3xl sm:px-16">
          <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to transform your images?
          </h2>
          <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-gray-100">
            Join thousands of users who are already experiencing the power of AI-driven image analysis and interactive learning.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            {!isAuthenticated && (
              <>
                <Link
                  to="/auth/register"
                  className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200 transform hover:scale-105"
                >
                  Start Free Trial
                </Link>
                <Link
                  to="/auth/login"
                  className="text-sm font-semibold leading-6 text-white hover:text-gray-100 transition-colors duration-200"
                >
                  Sign In <span aria-hidden="true">→</span>
                </Link>
              </>
            )}
            {isAuthenticated && (
              <Link
                to="/dashboard"
                className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200 transform hover:scale-105"
              >
                Go to Dashboard
              </Link>
            )}
          </div>
          <div className="absolute -top-24 right-0 -z-10 transform-gpu blur-3xl">
            <div className="aspect-[1404/767] w-[87.75rem] bg-gradient-to-r from-secondary-400 to-primary-600 opacity-25" />
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default HomePage