"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { MessageSquare, TrendingUp, Lightbulb, BarChart2, Clock, AlertTriangle } from "lucide-react"
import { BACKEND_URL } from "@/lib/config"

interface AnalyticsTabProps {
  category: string
}

interface AnalyticsData {
  channel_analysis: string[]
  content_strategy: string[]
  metadata: {
    analysis_timestamp: string
    data_points_analyzed: number
    time_range: {
      start: string
      end: string
    }
  }
  overview: string
  recommendations: string[]
  trend_analysis: string[]
}

// Custom tooltip for the chart
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-800 p-3 rounded-md shadow-lg border border-indigo-500/20 text-gray-200">
        <p className="text-sm font-medium text-indigo-300">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={`value-${index}`} className="text-sm" style={{ color: entry.color }}>
            Value: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function AnalyticsTab({ category }: AnalyticsTabProps) {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await fetch(`${BACKEND_URL}/api/dashboard/${category}/text-analysis`)
        if (!response.ok) throw new Error("Failed to fetch analytics data")
        const result = await response.json()
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [category])

  if (loading) {
    return (
      <Card className="p-6 bg-gray-800/40 backdrop-blur-sm border border-indigo-500/20 rounded-xl">
        <div className="space-y-6">
          <Skeleton className="h-8 w-1/3 bg-indigo-200/10 rounded-md" />
          <Skeleton className="h-32 w-full bg-indigo-200/10 rounded-md" />
          <Skeleton className="h-24 w-full bg-indigo-200/10 rounded-md" />
          <div className="grid grid-cols-3 gap-4">
            <Skeleton className="h-16 w-full bg-indigo-200/10 rounded-md" />
            <Skeleton className="h-16 w-full bg-indigo-200/10 rounded-md" />
            <Skeleton className="h-16 w-full bg-indigo-200/10 rounded-md" />
          </div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-6 bg-red-900/20 border border-red-500/30 rounded-xl">
        <AlertTriangle className="h-5 w-5 text-red-400" />
        <AlertDescription className="text-red-200">{error}</AlertDescription>
      </Alert>
    )
  }

  if (!data) return null

  const sampleChartData = [
    { month: data.metadata.time_range.start, value: 30 },
    { month: "Mid-point", value: 65 },
    { month: data.metadata.time_range.end, value: 100 },
  ]

  return (
    <Card className="p-6 bg-gray-800/40 backdrop-blur-sm border border-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 ease-in-out rounded-xl">
      <CardHeader className="px-1">
        <CardTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-blue-400 bg-clip-text text-transparent pb-1">
          Text Analytics Dashboard
        </CardTitle>
        <p className="text-gray-300 mt-3 leading-relaxed">{data.overview}</p>
      </CardHeader>

      <CardContent className="px-1">
        <div className="grid gap-6">
          {/* Metadata Section */}
          <div className="bg-indigo-900/20 p-5 rounded-xl border border-indigo-500/20">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-3">
                <div className="bg-indigo-500/20 p-2 rounded-lg">
                  <Clock className="h-5 w-5 text-indigo-300" />
                </div>
                <div>
                  <p className="text-sm font-medium text-indigo-200">Analysis Time</p>
                  <p className="text-sm text-gray-400">
                    {new Date(data.metadata.analysis_timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="bg-indigo-500/20 p-2 rounded-lg">
                  <BarChart2 className="h-5 w-5 text-indigo-300" />
                </div>
                <div>
                  <p className="text-sm font-medium text-indigo-200">Data Points</p>
                  <p className="text-sm text-gray-400">{data.metadata.data_points_analyzed.toLocaleString()}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="bg-indigo-500/20 p-2 rounded-lg">
                  <Clock className="h-5 w-5 text-indigo-300" />
                </div>
                <div>
                  <p className="text-sm font-medium text-indigo-200">Time Range</p>
                  <p className="text-sm text-gray-400">
                    {data.metadata.time_range.start} - {data.metadata.time_range.end}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="trends" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-6 bg-gray-700/30 rounded-xl p-1">
              <TabsTrigger 
                value="trends" 
                className="data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-200 rounded-lg transition-all duration-300"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Trends
              </TabsTrigger>
              <TabsTrigger 
                value="channels" 
                className="data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-200 rounded-lg transition-all duration-300"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Channels
              </TabsTrigger>
              <TabsTrigger 
                value="strategy" 
                className="data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-200 rounded-lg transition-all duration-300"
              >
                <Lightbulb className="h-4 w-4 mr-2" />
                Strategy
              </TabsTrigger>
              <TabsTrigger 
                value="recommendations" 
                className="data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-200 rounded-lg transition-all duration-300"
              >
                <BarChart2 className="h-4 w-4 mr-2" />
                Recommendations
              </TabsTrigger>
            </TabsList>

            <TabsContent value="trends" className="space-y-6">
              <div className="h-72 w-full bg-gray-800/40 rounded-xl p-6 border border-indigo-500/10">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sampleChartData}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#60A5FA" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#60A5FA" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="month" stroke="#A0AEC0" />
                    <YAxis stroke="#A0AEC0" />
                    <Tooltip content={<CustomTooltip />} />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#60A5FA" 
                      strokeWidth={3}
                      activeDot={{ r: 6, strokeWidth: 1, stroke: "#60A5FA", fill: "#1F2937" }}
                      fill="url(#colorValue)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              {data.trend_analysis.map((trend, index) => (
                <div 
                  key={index} 
                  className="bg-indigo-900/10 p-5 rounded-xl border border-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300"
                >
                  <p className="text-gray-300 leading-relaxed">{trend}</p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="channels" className="space-y-6">
              {data.channel_analysis.map((analysis, index) => (
                <div 
                  key={index} 
                  className="bg-indigo-900/10 p-5 rounded-xl border border-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300"
                >
                  <p className="text-gray-300 leading-relaxed">{analysis}</p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="strategy" className="space-y-6">
              {data.content_strategy.map((strategy, index) => (
                <div 
                  key={index} 
                  className="bg-indigo-900/10 p-5 rounded-xl border border-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300"
                >
                  <p className="text-gray-300 leading-relaxed">{strategy}</p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="recommendations" className="space-y-6">
              {data.recommendations.map((recommendation, index) => (
                <div 
                  key={index} 
                  className="bg-indigo-900/10 p-5 rounded-xl border border-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300"
                >
                  <p className="text-gray-300 leading-relaxed">{recommendation}</p>
                </div>
              ))}
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  )
}

export default AnalyticsTab