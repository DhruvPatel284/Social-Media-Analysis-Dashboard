'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MessageSquare, TrendingUp, Lightbulb, BarChart2, Clock } from 'lucide-react';
import { BACKEND_URL } from '@/lib/config';

interface AnalyticsTabProps {
  category: string;
}

interface AnalyticsData {
  channel_analysis: string[];
  content_strategy: string[];
  metadata: {
    analysis_timestamp: string;
    data_points_analyzed: number;
    time_range: {
      start: string;
      end: string;
    };
  };
  overview: string;
  recommendations: string[];
  trend_analysis: string[];
}

export function AnalyticsTab({ category }: AnalyticsTabProps) {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${BACKEND_URL}/api/dashboard/${category}/text-analysis`);
        if (!response.ok) throw new Error('Failed to fetch analytics data');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [category]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="space-y-4">
          <Skeleton className="h-8 w-1/3" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!data) return null;

  const sampleChartData = [
    { month: data.metadata.time_range.start, value: 30 },
    { month: data.metadata.time_range.end, value: 100 }
  ];

  return (
    <Card className="p-6">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">Text Analytics Dashboard</CardTitle>
        <p className="text-muted-foreground mt-2">{data.overview}</p>
      </CardHeader>
      
      <CardContent>
        <div className="grid gap-6">
          {/* Metadata Section */}
          <div className="bg-muted/50 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm font-medium">Analysis Time</p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(data.metadata.analysis_timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <BarChart2 className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm font-medium">Data Points</p>
                  <p className="text-sm text-muted-foreground">
                    {data.metadata.data_points_analyzed.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm font-medium">Time Range</p>
                  <p className="text-sm text-muted-foreground">
                    {data.metadata.time_range.start} - {data.metadata.time_range.end}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="trends" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-6">
              <TabsTrigger value="trends">
                <TrendingUp className="h-4 w-4 mr-2" />
                Trends
              </TabsTrigger>
              <TabsTrigger value="channels">
                <MessageSquare className="h-4 w-4 mr-2" />
                Channels
              </TabsTrigger>
              <TabsTrigger value="strategy">
                <Lightbulb className="h-4 w-4 mr-2" />
                Strategy
              </TabsTrigger>
              <TabsTrigger value="recommendations">
                <BarChart2 className="h-4 w-4 mr-2" />
                Recommendations
              </TabsTrigger>
            </TabsList>

            <TabsContent value="trends" className="space-y-4">
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sampleChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="#2563eb" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              {data.trend_analysis.map((trend, index) => (
                <div key={index} className="bg-muted/30 p-4 rounded-lg">
                  <p>{trend}</p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="channels" className="space-y-4">
              {data.channel_analysis.map((analysis, index) => (
                <div key={index} className="bg-muted/30 p-4 rounded-lg">
                  <p>{analysis}</p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="strategy" className="space-y-4">
              {data.content_strategy.map((strategy, index) => (
                <div key={index} className="bg-muted/30 p-4 rounded-lg">
                  <p>{strategy}</p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="recommendations" className="space-y-4">
              {data.recommendations.map((recommendation, index) => (
                <div key={index} className="bg-muted/30 p-4 rounded-lg">
                  <p>{recommendation}</p>
                </div>
              ))}
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  );
}

export default AnalyticsTab;