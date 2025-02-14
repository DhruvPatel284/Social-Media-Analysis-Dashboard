import Spline from "@splinetool/react-spline/next"
import { Button } from "@/components/ui/button"
import { ArrowRight, BarChart2, Brain, Zap } from "lucide-react"
export default function HomePage() {
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">

      {/* Hero Section with Spline */}
      <div className="relative h-screen">
        <div className="absolute inset-0 z-10">
          <Spline scene="https://prod.spline.design/HRZ-rjp918E7Mow7/scene.splinecode" />
        </div>

        {/* Hero Content */}
        <div className="relative z-20 container mx-auto px-4 pt-20 lg:pt-28">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
              <span className="inline-block bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-violet-400 to-purple-400 animate-gradient-slow pb-2">
                Transform Your Social Media
              </span>
              <br />
              <span className="inline-block text-white/90 mt-2">with AI Analytics</span>
            </h1>

            <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
              Harness the power of artificial intelligence to unlock deeper insights and drive exceptional social media
              performance
            </p>

            {/* Enhanced CTA Button */}
            <div className="pt-8">
              <Button
                size="lg"
                className="group relative px-6 py-3 text-base bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 border border-blue-400/30 shadow-lg shadow-blue-500/20 transition-all duration-300 hover:scale-105"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                <div className="absolute inset-0 rounded-lg overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 animate-pulse-slow"></div>
                </div>
              </Button>
            </div>
          </div>
        </div>

        {/* Enhanced Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-transparent z-10" />
      </div>

      {/* Features Overview - Adjusted Positioning */}
      <div className="relative z-20 container mx-auto px-4 -mt-48 mb-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Enhanced Feature Cards */}
          <FeatureCard
            icon={<Brain className="h-6 w-6 text-blue-400" />}
            title="AI-Powered Insights"
            description="Advanced analytics and predictive insights powered by cutting-edge artificial intelligence"
            gradient="from-blue-900/50 to-blue-800/50"
            borderColor="border-blue-700/50"
            hoverBorderColor="hover:border-blue-500/50"
          />
          <FeatureCard
            icon={<BarChart2 className="h-6 w-6 text-violet-400" />}
            title="Real-time Analytics"
            description="Monitor your social media performance with live data and instant updates"
            gradient="from-violet-900/50 to-violet-800/50"
            borderColor="border-violet-700/50"
            hoverBorderColor="hover:border-violet-500/50"
          />
          <FeatureCard
            icon={<Zap className="h-6 w-6 text-purple-400" />}
            title="Automated Reporting"
            description="Generate comprehensive reports and insights with just a few clicks"
            gradient="from-purple-900/50 to-purple-800/50"
            borderColor="border-purple-700/50"
            hoverBorderColor="hover:border-purple-500/50"
          />
        </div>

        {/* Stats Section */}
        <div className="mt-24 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            Trusted by Industry Leaders
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatCard number="500K+" label="Active Users" color="text-blue-400" />
            <StatCard number="98%" label="Satisfaction Rate" color="text-violet-400" />
            <StatCard number="10M+" label="Posts Analyzed" color="text-purple-400" />
            <StatCard number="50+" label="Integrations" color="text-blue-400" />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative">
        <div className="container mx-auto px-4 py-24">
          <div className="relative p-8 md:p-12 rounded-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-900/30 via-violet-900/30 to-purple-900/30 backdrop-blur-sm border border-blue-500/20 rounded-2xl" />
            <div className="relative z-10 max-w-2xl mx-auto text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                Ready to Transform Your Social Media Strategy?
              </h2>
              <p className="text-lg text-gray-300 mb-8 leading-relaxed">
                Join thousands of marketers and social media managers who are already leveraging our AI-powered
                analytics platform.
              </p>
              <Button
                size="lg"
                className="group relative px-6 py-3 text-base bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 border border-blue-400/30 shadow-lg shadow-blue-500/20 transition-all duration-300 hover:scale-105"
              >
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description, gradient, borderColor, hoverBorderColor }:any) {
  return (
    <div
      className={`group p-6 rounded-xl bg-gradient-to-br ${gradient} border ${borderColor} ${hoverBorderColor} backdrop-blur-sm transition-all duration-300 hover:transform hover:scale-105`}
    >
      <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-gray-100 mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  )
}

function StatCard({ number, label, color }:any) {
  return (
    <div className="group p-4 rounded-xl bg-gradient-to-br from-gray-900/50 to-gray-800/50 border border-gray-700/50 hover:border-gray-500/50 transition-all duration-300">
      <p className={`text-3xl font-bold ${color} mb-1 group-hover:scale-110 transition-transform`}>{number}</p>
      <p className="text-gray-400 text-sm">{label}</p>
    </div>
  )
}