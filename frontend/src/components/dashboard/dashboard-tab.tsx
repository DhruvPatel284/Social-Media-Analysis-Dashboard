'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';
import { BACKEND_URL } from '@/lib/config';

interface DashboardTabProps {
  category: string;
}

// Custom color palette for charts
const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))'
];

// Format large numbers with K/M suffix
const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num;
};

export function DashboardTab({ category }: DashboardTabProps) {
  const [overview, setOverview] = useState<any>(null);
  const [channels, setChannels] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [timeline, setTimeline] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [overviewRes, channelsRes, trendsRes, timelineRes] = await Promise.all([
          axios.get(`${BACKEND_URL}/api/dashboard/${category}/overview`),
          axios.get(`${BACKEND_URL}/api/dashboard/${category}/channels`),
          axios.get(`${BACKEND_URL}/api/dashboard/${category}/trends`),
          axios.get(`${BACKEND_URL}/api/dashboard/${category}/timeline`)
        ]);

        setOverview(overviewRes.data);
        setChannels(channelsRes.data);
        setTrends(trendsRes.data);
        setTimeline(timelineRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (category) {
      fetchData();
    }
  }, [category]);

  if (loading) {
    return <div>Loading...</div>;
  }

  // Transform timeline data
  const timelineData = timeline ? Object.entries(timeline).map(([month, data]: [string, any]) => ({
    month,
    views: data.views,
    engagement: data.avg_engagement
  })) : [];

  // Transform trends data for keywords
  const keywordsData = trends ? Object.entries(trends.top_keywords)
    .slice(0, 5)
    .map(([name, value]: [string, any]) => ({
      name,
      value
    })) : [];

  // Transform channels data
  const channelData = channels ? Object.entries(channels.top_channels)
    .map(([name, data]: [string, any]) => ({
      name,
      views: data.total_views,
      engagement: data.avg_engagement
    })) : [];

  // Get engagement metrics from overview
  const engagementData = overview ? {
    likes_per_view: overview.total_likes / overview.total_views,
    comments_per_view: overview.total_comments / overview.total_views,
    comments_per_like: overview.total_comments / overview.total_likes
  } : {
    likes_per_view: 0,
    comments_per_view: 0,
    comments_per_like: 0
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* Views & Engagement Trends */}
      <Card className="p-6 col-span-2">
        <h3 className="text-xl font-semibold mb-4">Views & Engagement Trends</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="views"
                stroke={COLORS[0]}
                name="Views"
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="engagement"
                stroke={COLORS[1]}
                name="Engagement Rate"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Top Keywords */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Top Keywords</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={keywordsData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
                label
              >
                {keywordsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Channel Performance */}
      <Card className="p-6 col-span-2">
        <h3 className="text-xl font-semibold mb-4">Top Channel Performance</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={channelData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="views" fill={COLORS[0]} name="Views" />
              <Bar dataKey="engagement" fill={COLORS[1]} name="Engagement Rate" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Engagement Metrics */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Engagement Metrics</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={[
                { name: 'Likes/View', value: engagementData.likes_per_view },
                { name: 'Comments/View', value: engagementData.comments_per_view },
                { name: 'Comments/Like', value: engagementData.comments_per_like }
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="value"
                stroke={COLORS[0]}
                fill={COLORS[0]}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}