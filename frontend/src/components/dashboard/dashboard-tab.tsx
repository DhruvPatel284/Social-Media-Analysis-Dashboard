'use client';

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

export function DashboardTab({  category }: DashboardTabProps) {
  // Sample data transformation for timeline chart
  const timelineData = [
    { month: 'Feb 24', views: 36315953, engagement: 2.23 },
    { month: 'Mar 24', views: 11370211, engagement: 2.42 },
    { month: 'Apr 24', views: 18833077, engagement: 2.42 },
    { month: 'May 24', views: 35314402, engagement: 2.26 },
    { month: 'Jun 24', views: 42781609, engagement: 2.05 },
    { month: 'Jul 24', views: 7757180, engagement: 2.08 },
    { month: 'Aug 24', views: 55700993, engagement: 2.43 },
    { month: 'Sep 24', views: 61553522, engagement: 2.22 },
    { month: 'Oct 24', views: 39900177, engagement: 2.47 },
    { month: 'Nov 24', views: 16702594, engagement: 2.79 },
    { month: 'Dec 24', views: 12236396, engagement: 3.36 },
    { month: 'Jan 25', views: 14023234, engagement: 2.41 }
  ];

  // Top keywords data
  const keywordsData = [
    { name: 'pixel', value: 721 },
    { name: 'iphone', value: 558 },
    { name: 'oneplus', value: 520 },
    { name: 'galaxy', value: 510 },
    { name: 'samsung', value: 421 }
  ];

  // Channel performance data
  const channelData = [
    { name: 'Marques Brownlee', views: 34518186, engagement: 3.32 },
    { name: 'MobilePapa', views: 22939066, engagement: 3.17 },
    { name: 'Mrwhosetheboss', views: 18084687, engagement: 4.35 },
    { name: 'TechDroider', views: 15328476, engagement: 4.05 },
    { name: 'Danny Winget', views: 16176909, engagement: 4.01 }
  ];

  // Engagement metrics
  const engagementData = {
    likes_per_view: 0.033,
    comments_per_view: 0.00076,
    comments_per_like: 0.023
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