import { useEffect, useState } from "react";
import axios from "axios";
import { Card } from "@/components/ui/card";
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
  Area,
} from "recharts";
import { BACKEND_URL } from "@/lib/config";

interface DashboardTabProps {
  category: string;
}

// Refined elegant color palette for dark mode
const COLORS = [
  "#60A5FA", // Blue 400 - Primary
  "#93C5FD", // Blue 300 - Secondary
  "#3B82F6", // Blue 500 - Accent
  "#2563EB", // Blue 600 - Highlight
  "#1D4ED8", // Blue 700 - Deep accent
];

// Format large numbers with K/M suffix
// const formatNumber = (num: number) => {
//   if (num >= 1000000) {
//     return `${(num / 1000000).toFixed(1)}M`;
//   }
//   if (num >= 1000) {
//     return `${(num / 1000).toFixed(1)}K`;
//   }
//   return num;
// };

// Custom tooltip styles
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-800 p-3 rounded-md shadow-lg border border-indigo-500/20 backdrop-blur-sm">
        <p className="text-gray-300 font-medium">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={`item-${index}`} className="text-sm" style={{ color: entry.color }}>
            {`${entry.name}: ${entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
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
          axios.get(`${BACKEND_URL}/api/dashboard/${category}/timeline`),
        ]);

        setOverview(overviewRes.data);
        setChannels(channelsRes.data);
        setTrends(trendsRes.data);
        setTimeline(timelineRes.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    if (category) {
      fetchData();
    }
  }, [category]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-indigo-400 text-lg font-medium">
          Loading dashboard data...
        </div>
      </div>
    );
  }

  // Transform timeline data
  const timelineData = timeline
    ? Object.entries(timeline).map(([month, data]: [string, any]) => ({
        month,
        views: data.views,
        engagement: data.avg_engagement,
      }))
    : [];

  // Transform trends data for keywords
  const keywordsData = trends
    ? Object.entries(trends.top_keywords)
        .slice(0, 5)
        .map(([name, value]: [string, any]) => ({
          name,
          value,
        }))
    : [];

  // Transform channels data
  const channelData = channels
    ? Object.entries(channels.top_channels).map(([name, data]: [string, any]) => ({
        name,
        views: data.total_views,
        engagement: data.avg_engagement,
      }))
    : [];

  // Get engagement metrics from overview
  const engagementData = overview
    ? {
        likes_per_view: overview.total_likes / overview.total_views,
        comments_per_view: overview.total_comments / overview.total_views,
        comments_per_like: overview.total_comments / overview.total_likes,
      }
    : { likes_per_view: 0, comments_per_view: 0, comments_per_like: 0 };

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {/* Views & Engagement Trends */}
      <Card className="p-6 col-span-2 bg-gray-800/40 backdrop-blur-sm border border-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 ease-in-out rounded-xl">
        <h3 className="text-xl font-semibold mb-6 text-indigo-400">Views & Engagement Trends</h3>
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
              <XAxis dataKey="month" stroke="#A0AEC0" />
              <YAxis yAxisId="left" stroke="#A0AEC0" />
              <YAxis yAxisId="right" orientation="right" stroke="#A0AEC0" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: 10 }} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="views"
                stroke={COLORS[0]}
                name="Views"
                dot={false}
                strokeWidth={3}
                activeDot={{ r: 6, stroke: COLORS[0], strokeWidth: 1, fill: "#1F2937" }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="engagement"
                stroke={COLORS[2]}
                name="Engagement Rate"
                dot={false}
                strokeWidth={3}
                activeDot={{ r: 6, stroke: COLORS[2], strokeWidth: 1, fill: "#1F2937" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Top Keywords */}
      <Card className="p-6 bg-gray-800/40 backdrop-blur-sm border border-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 ease-in-out rounded-xl">
        <h3 className="text-xl font-semibold mb-6 text-indigo-400">Top Keywords</h3>
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={keywordsData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={90}
                fill="#8884d8"
                paddingAngle={4}
                dataKey="value"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {keywordsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Channel Performance */}
      <Card className="p-6 col-span-2 bg-gray-800/40 backdrop-blur-sm border border-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 ease-in-out rounded-xl">
        <h3 className="text-xl font-semibold mb-6 text-indigo-400">Top Channel Performance</h3>
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={channelData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
              <XAxis dataKey="name" stroke="#A0AEC0" />
              <YAxis stroke="#A0AEC0" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: 10 }} />
              <Bar dataKey="views" fill={COLORS[0]} name="Views" radius={[4, 4, 0, 0]} barSize={30} />
              <Bar dataKey="engagement" fill={COLORS[2]} name="Engagement Rate" radius={[4, 4, 0, 0]} barSize={30} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Engagement Metrics */}
      <Card className="p-6 bg-gray-800/40 backdrop-blur-sm border border-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 ease-in-out rounded-xl">
        <h3 className="text-xl font-semibold mb-6 text-indigo-400">Engagement Metrics</h3>
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={[
                { name: "Likes/View", value: engagementData.likes_per_view },
                { name: "Comments/View", value: engagementData.comments_per_view },
                { name: "Comments/Like", value: engagementData.comments_per_like },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
              <XAxis dataKey="name" stroke="#A0AEC0" />
              <YAxis stroke="#A0AEC0" />
              <Tooltip content={<CustomTooltip />} />
              <defs>
                <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS[0]} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={COLORS[0]} stopOpacity={0.2} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke={COLORS[0]}
                fill="url(#colorGradient)"
                strokeWidth={3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
