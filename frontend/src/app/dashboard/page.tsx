'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { MessagesSquare, BarChart2, Layout, History } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { DashboardTab } from '@/components/dashboard/dashboard-tab';
import { AnalyticsTab } from '@/components/dashboard/analytics-tab';
import { ChatbotTab } from '@/components/dashboard/chatbot-tab';
import { ChatHistoryTab } from '@/components/dashboard/chat-history-tab';

export default function DashboardPage() {
  const [category, setCategory] = useState<string>('');

  const handleAnalyze = () => {
    if ( !category) {
      setCategory(category);
      return;
    }
  };

  return (
    <div className="flex min-h-screen flex-col space-y-6 p-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Social Media Analysis</h2>
        <div className="flex items-center space-x-4">
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="technology">Smartphones</SelectItem>
              <SelectItem value="business">Business</SelectItem>
              <SelectItem value="entertainment">Entertainment</SelectItem>
              <SelectItem value="sports">Sports</SelectItem>
              <SelectItem value="politics">Politics</SelectItem>
            </SelectContent>
          </Select>
          <Button 
            onClick={handleAnalyze}
            disabled={ !category}
          >
            Analyze
          </Button>
        </div>
      </div>

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard" className="space-x-2">
            <Layout className="h-4 w-4" />
            <span>Dashboard</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="space-x-2">
            <BarChart2 className="h-4 w-4" />
            <span>Analytics</span>
          </TabsTrigger>
          <TabsTrigger value="chatbot" className="space-x-2">
            <MessagesSquare className="h-4 w-4" />
            <span>Chatbot</span>
          </TabsTrigger>
          <TabsTrigger value="history" className="space-x-2">
            <History className="h-4 w-4" />
            <span>Chat History</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard">
          <DashboardTab category={category} />
        </TabsContent>

        <TabsContent value="analytics">
          <AnalyticsTab category={category} />
        </TabsContent>

        <TabsContent value="chatbot">
          <ChatbotTab />
        </TabsContent>

        <TabsContent value="history">
          <ChatHistoryTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}