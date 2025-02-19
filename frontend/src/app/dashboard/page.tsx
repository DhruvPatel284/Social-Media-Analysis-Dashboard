"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { BarChart2, Layout, MessagesSquare } from "lucide-react"
import { DashboardTab } from "@/components/dashboard/dashboard-tab"
import { AnalyticsTab } from "@/components/dashboard/analytics-tab"
import { ChatbotTab } from "@/components/dashboard/chatbot-tab"

export default function DashboardPage() {
  const [category, setCategory] = useState<string>("")
  const [showTabs, setShowTabs] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  const handleAnalyze = () => {
    if (!category) {
      return
    }
    setShowTabs(true)
  }

  if (!mounted) return null

  return (
    <div className="flex min-h-screen flex-col space-y-6 p-4 sm:p-8  bg-gradient-to-br from-gray-900 to-gray-950 text-gray-100 transition-all duration-300 ease-in-out">
      <div className="h-[10px]"></div>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 className="text-3xl text-center mx-auto  sm:text-4xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent transition-all duration-300 ease-in-out hover:from-indigo-500 hover:to-purple-600">
          Social Media Analysis
        </h2>
        <div className="flex items-center space-x-4 w-full sm:w-auto">
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="w-full sm:w-[200px] bg-gray-800/50 backdrop-blur-sm border-indigo-500/20 text-gray-200">
              <SelectValue placeholder="Select Category" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 border-indigo-500/20 text-gray-200">
              <SelectItem value="Informative Content">Informative Content</SelectItem>
              <SelectItem value="Motivational">Motivational</SelectItem>
              <SelectItem value="Tech Reviews">Tech Reviews</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleAnalyze}
            disabled={!category}
            className="bg-gradient-to-r from-indigo-600 to-purple-700 hover:from-indigo-700 hover:to-purple-800 text-white transition-all duration-300 ease-in-out shadow-lg shadow-indigo-500/20"
          >
            Analyze
          </Button>
        </div>
      </div>

      {showTabs && (
        <Tabs defaultValue="dashboard" className="space-y-4">
          <div className="relative">
            <TabsList className="w-full grid grid-cols-3 bg-[#131d38] backdrop-blur-sm rounded-lg border border-indigo-500/10 overflow-hidden">
              <TabsTrigger
                value="dashboard"
                className="flex items-center justify-center space-x-2 rounded-md py-3 px-3 text-sm font-medium transition-all duration-300 ease-in-out text-gray-300 hover:text-white data-[state=active]:bg-[#1e2d5e] data-[state=active]:text-white relative"
              >
                <Layout className="h-4 w-4 mr-2" />
                <span>Dashboard</span>
                <div className="absolute bottom-0 inset-x-0 h-0.5 bg-indigo-500 transform scale-x-0 transition-transform duration-300 data-[state=active]:scale-x-100"></div>
              </TabsTrigger>
              <TabsTrigger
                value="analytics"
                className="flex items-center justify-center space-x-2 rounded-md py-3 px-3 text-sm font-medium transition-all duration-300 ease-in-out text-gray-300 hover:text-white data-[state=active]:bg-[#1e2d5e] data-[state=active]:text-white relative"
              >
                <BarChart2 className="h-4 w-4 mr-2" />
                <span>Analytics</span>
                <div className="absolute bottom-0 inset-x-0 h-0.5 bg-indigo-500 transform scale-x-0 transition-transform duration-300 data-[state=active]:scale-x-100"></div>
              </TabsTrigger>
              <TabsTrigger
                value="chatbot"
                className="flex items-center justify-center space-x-2 rounded-md py-3 px-3 text-sm font-medium transition-all duration-300 ease-in-out text-gray-300 hover:text-white data-[state=active]:bg-[#1e2d5e] data-[state=active]:text-white relative"
              >
                <MessagesSquare className="h-4 w-4 mr-2" />
                <span>Chatbot</span>
                <div className="absolute bottom-0 inset-x-0 h-0.5 bg-indigo-500 transform scale-x-0 transition-transform duration-300 data-[state=active]:scale-x-100"></div>
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="dashboard">
            <div className="bg-gray-800/30 backdrop-blur-sm rounded-lg border border-indigo-500/10 p-4 sm:p-6 shadow-xl">
              <DashboardTab category={category} />
            </div>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="bg-gray-800/30 backdrop-blur-sm rounded-lg border border-indigo-500/10 p-4 sm:p-6 shadow-xl">
              <AnalyticsTab category={category} />
            </div>
          </TabsContent>

          <TabsContent value="chatbot">
            <div className="bg-gray-800/30 backdrop-blur-sm rounded-lg border border-indigo-500/10 p-4 sm:p-6 shadow-xl">
              <ChatbotTab category={category} />
            </div>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}