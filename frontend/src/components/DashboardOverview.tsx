import { useQuery } from '@tanstack/react-query'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { rankTrackingApi } from '../services/api'

interface DashboardOverviewProps {
  projectId: string
}

interface RankStats {
  total_keywords: number
  average_position: number
  top_3: number
  top_10: number
  top_20: number
  top_50: number
  not_ranking: number
}

interface KeywordMover {
  keyword: string
  current_position: number
  previous_position: number
  change: number
}

export function DashboardOverview({ projectId }: DashboardOverviewProps) {
  // Fetch rank statistics
  const { data: rankStats, isLoading: statsLoading } = useQuery({
    queryKey: ['rank-stats', projectId],
    queryFn: async () => {
      const response = await rankTrackingApi.getStats(projectId)
      return response.data as RankStats
    }
  })

  if (statsLoading) {
    return <div className="animate-pulse bg-gray-100 h-96 rounded-lg"></div>
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Keywords"
          value={rankStats?.total_keywords.toString() || '0'}
          icon="🔑"
          color="blue"
        />
        <MetricCard
          title="Avg. Position"
          value={rankStats?.average_position.toFixed(1) || '0'}
          icon="📊"
          color="green"
        />
        <MetricCard
          title="Top 3 Rankings"
          value={rankStats?.top_3.toString() || '0'}
          icon="🏆"
          color="yellow"
        />
        <MetricCard
          title="Top 10 Rankings"
          value={rankStats?.top_10.toString() || '0'}
          icon="⭐"
          color="purple"
        />
      </div>

      {/* Charts and Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rank Distribution Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Rank Distribution
          </h3>
          {rankStats && <RankDistributionChart stats={rankStats} />}
        </div>

        {/* Biggest Movers */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Biggest Movers (7 days)
          </h3>
          <KeywordMoversTable projectId={projectId} />
        </div>
      </div>

      {/* API Usage Tracker */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          API Usage This Month
        </h3>
        <ApiUsageTracker projectId={projectId} />
      </div>
    </div>
  )
}

function MetricCard({
  title,
  value,
  icon,
  color
}: {
  title: string
  value: string
  icon: string
  color: 'blue' | 'green' | 'yellow' | 'purple'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div
          className={`w-14 h-14 rounded-lg ${colorClasses[color]} flex items-center justify-center text-3xl`}
        >
          {icon}
        </div>
      </div>
    </div>
  )
}

function RankDistributionChart({ stats }: { stats: RankStats }) {
  const data = [
    { name: 'Top 3 (1-3)', value: stats.top_3, color: '#10b981' },
    {
      name: 'Top 10 (4-10)',
      value: stats.top_10 - stats.top_3,
      color: '#3b82f6'
    },
    {
      name: 'Top 20 (11-20)',
      value: stats.top_20 - stats.top_10,
      color: '#f59e0b'
    },
    {
      name: 'Top 50 (21-50)',
      value: stats.top_50 - stats.top_20,
      color: '#ef4444'
    },
    { name: 'Below 50', value: stats.not_ranking, color: '#6b7280' }
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) =>
            `${name}: ${(percent * 100).toFixed(0)}%`
          }
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}

function KeywordMoversTable({ projectId }: { projectId: string }) {
  const { data: movers, isLoading } = useQuery({
    queryKey: ['keyword-movers', projectId],
    queryFn: async () => {
      // This would fetch from an actual endpoint
      // For now, returning mock data structure
      return [] as KeywordMover[]
    }
  })

  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-48 rounded"></div>
  }

  if (!movers || movers.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 text-sm">
        <p>No significant rank changes this week.</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {movers.slice(0, 5).map((mover, idx) => {
        const isGainer = mover.change > 0
        return (
          <div
            key={idx}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div className="flex-1">
              <p className="font-medium text-sm text-gray-900">
                {mover.keyword}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">
                Position: #{mover.current_position}
              </p>
            </div>
            <div
              className={`flex items-center gap-1 px-3 py-1 rounded-full ${
                isGainer
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700'
              }`}
            >
              <span className="font-semibold">
                {isGainer ? '↑' : '↓'} {Math.abs(mover.change)}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ApiUsageTracker({ projectId }: { projectId: string }) {
  const { data: usage, isLoading } = useQuery({
    queryKey: ['api-usage', projectId],
    queryFn: async () => {
      // This would fetch from API usage logs endpoint
      // For now, returning mock data structure
      return {
        total_cost: 12.45,
        providers: [
          { name: 'DataForSEO - Keywords', cost: 2.5, calls: 3500 },
          { name: 'DataForSEO - SERP', cost: 8.95, calls: 4800 },
          { name: 'Claude AI', cost: 1.0, calls: 350 }
        ]
      }
    }
  })

  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-32 rounded"></div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-gray-900">
          ${usage?.total_cost.toFixed(2)}
        </span>
        <span className="text-sm text-gray-500">
          vs. $129/mo for Ahrefs 💰
        </span>
      </div>

      <div className="space-y-2">
        {usage?.providers.map((provider, idx) => (
          <div key={idx} className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">
                  {provider.name}
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  ${provider.cost.toFixed(2)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{
                    width: `${(provider.cost / usage.total_cost) * 100}%`
                  }}
                ></div>
              </div>
              <span className="text-xs text-gray-500 mt-0.5">
                {provider.calls.toLocaleString()} calls
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          💡 You're saving ~${(129 - (usage?.total_cost || 0)).toFixed(2)}/month
          compared to traditional SEO tools!
        </p>
      </div>
    </div>
  )
}
