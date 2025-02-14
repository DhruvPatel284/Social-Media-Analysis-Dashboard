"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { BarChart2, Layout, MessagesSquare, Moon, Sun } from "lucide-react"
import { DashboardTab } from "@/components/dashboard/dashboard-tab"
import { AnalyticsTab } from "@/components/dashboard/analytics-tab"
import { ChatbotTab } from "@/components/dashboard/chatbot-tab"
import { useTheme } from "next-themes"

export default function DashboardPage() {
  const [category, setCategory] = useState<string>("")
  const [showTabs, setShowTabs] = useState(false)
  const { theme, setTheme } = useTheme();
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
    <div className="flex min-h-screen flex-col space-y-6 p-8 bg-background text-foreground transition-colors duration-300">
      <div className="h-[50px]"></div>
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Social Media Analysis
        </h2>
        <div className="flex items-center space-x-4">
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Smartphones">Smartphones</SelectItem>
              <SelectItem value="Electric Vehicles">Electric Vehicles</SelectItem>
              <SelectItem value="Gaming Consoles">Gaming Consoles</SelectItem>
              <SelectItem value="Motivation">Motivation</SelectItem>
              <SelectItem value="Educational">Educational</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleAnalyze}
            disabled={!category}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
          >
            Analyze
          </Button>
          <Button variant="outline" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? <Sun className="h-[1.2rem] w-[1.2rem]" /> : <Moon className="h-[1.2rem] w-[1.2rem]" />}
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>

      {showTabs && (
        <Tabs defaultValue="dashboard" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3 bg-muted/20 p-1 rounded-lg">
            <TabsTrigger value="dashboard" className="space-x-2 data-[state=active]:bg-background">
              <Layout className="h-4 w-4" />
              <span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="space-x-2 data-[state=active]:bg-background">
              <BarChart2 className="h-4 w-4" />
              <span>Analytics</span>
            </TabsTrigger>
            <TabsTrigger value="chatbot" className="space-x-2 data-[state=active]:bg-background">
              <MessagesSquare className="h-4 w-4" />
              <span>Chatbot</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard">
            <DashboardTab category={category} />
          </TabsContent>

          <TabsContent value="analytics">
            <AnalyticsTab category={category} />
          </TabsContent>

          <TabsContent value="chatbot">
            <ChatbotTab category={category} />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}

