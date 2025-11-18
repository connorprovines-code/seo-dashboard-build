import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { backlinksApi } from '../services/api'

interface BacklinksDashboardProps {
  projectId: string
}

interface BacklinkSummary {
  total_backlinks: number
  referring_domains: number
  domain_rank: number
  new_backlinks_30d: number
  lost_backlinks_30d: number
}

interface Backlink {
  id: string
  source_domain: string
  source_url: string
  target_url: string
  anchor_text?: string
  domain_rank?: number
  first_seen: string
  is_active: boolean
}

interface ReferringDomain {
  domain: string
  backlinks_count: number
  domain_rank: number
  first_seen: string
}

export function BacklinksDashboard({ projectId }: BacklinksDashboardProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'list' | 'domains'>('summary')

  // Fetch backlink summary
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['backlinks-summary', projectId],
    queryFn: async () => {
      const response = await backlinksApi.getSummary(projectId)
      return response.data as BacklinkSummary
    }
  })

  // Fetch backlinks list
  const { data: backlinks, isLoading: backlinksLoading } = useQuery({
    queryKey: ['backlinks-list', projectId],
    queryFn: async () => {
      const response = await backlinksApi.getList(projectId, 50, 0)
      return response.data as Backlink[]
    },
    enabled: activeTab === 'list'
  })

  // Fetch referring domains
  const { data: domains, isLoading: domainsLoading } = useQuery({
    queryKey: ['referring-domains', projectId],
    queryFn: async () => {
      const response = await backlinksApi.getReferringDomains(projectId, 50)
      return response.data as ReferringDomain[]
    },
    enabled: activeTab === 'domains'
  })

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <SummaryCard
            title="Total Backlinks"
            value={summary.total_backlinks.toLocaleString()}
            icon="🔗"
            color="blue"
          />
          <SummaryCard
            title="Referring Domains"
            value={summary.referring_domains.toLocaleString()}
            icon="🌐"
            color="green"
          />
          <SummaryCard
            title="Domain Rank"
            value={summary.domain_rank.toString()}
            icon="📊"
            color="purple"
          />
          <SummaryCard
            title="New (30 days)"
            value={`+${summary.new_backlinks_30d}`}
            icon="⬆️"
            color="green"
            trend="up"
          />
          <SummaryCard
            title="Lost (30 days)"
            value={`-${summary.lost_backlinks_30d}`}
            icon="⬇️"
            color="red"
            trend="down"
          />
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <TabButton
              active={activeTab === 'summary'}
              onClick={() => setActiveTab('summary')}
              label="Overview"
            />
            <TabButton
              active={activeTab === 'list'}
              onClick={() => setActiveTab('list')}
              label="All Backlinks"
            />
            <TabButton
              active={activeTab === 'domains'}
              onClick={() => setActiveTab('domains')}
              label="Referring Domains"
            />
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'summary' && <SummaryView summary={summary} loading={summaryLoading} />}
          {activeTab === 'list' && <BacklinksList backlinks={backlinks} loading={backlinksLoading} />}
          {activeTab === 'domains' && <ReferringDomainsList domains={domains} loading={domainsLoading} />}
        </div>
      </div>
    </div>
  )
}

function SummaryCard({
  title,
  value,
  icon,
  color,
  trend
}: {
  title: string
  value: string
  icon: string
  color: 'blue' | 'green' | 'purple' | 'red'
  trend?: 'up' | 'down'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-lg ${colorClasses[color]} flex items-center justify-center text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  label
}: {
  active: boolean
  onClick: () => void
  label: string
}) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
        active
          ? 'border-blue-500 text-blue-600'
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      }`}
    >
      {label}
    </button>
  )
}

function SummaryView({ summary, loading }: { summary?: BacklinkSummary; loading: boolean }) {
  if (loading) {
    return <div className="animate-pulse bg-gray-100 h-64 rounded"></div>
  }

  if (!summary) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No backlink data available yet.</p>
        <p className="text-sm mt-1">Run a backlink analysis to see your profile.</p>
      </div>
    )
  }

  const healthScore = Math.min(100, Math.floor((summary.total_backlinks / 100) * 50 + (summary.domain_rank || 0)))

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Health Score */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Backlink Health Score</h4>
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg className="transform -rotate-90 w-32 h-32">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  className="text-gray-200"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={`${(healthScore / 100) * 351.86} 351.86`}
                  className="text-blue-600"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl font-bold text-gray-900">{healthScore}</span>
              </div>
            </div>
          </div>
          <p className="text-center text-sm text-gray-600 mt-4">
            {healthScore >= 70 ? 'Excellent' : healthScore >= 40 ? 'Good' : 'Needs Improvement'}
          </p>
        </div>

        {/* Recent Activity */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Recent Activity (30 days)</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
              <span className="text-sm text-gray-600">New Backlinks</span>
              <span className="font-semibold text-green-600">+{summary.new_backlinks_30d}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
              <span className="text-sm text-gray-600">Lost Backlinks</span>
              <span className="font-semibold text-red-600">-{summary.lost_backlinks_30d}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
              <span className="text-sm text-gray-600">Net Change</span>
              <span className={`font-semibold ${summary.new_backlinks_30d - summary.lost_backlinks_30d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {summary.new_backlinks_30d - summary.lost_backlinks_30d >= 0 ? '+' : ''}
                {summary.new_backlinks_30d - summary.lost_backlinks_30d}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function BacklinksList({ backlinks, loading }: { backlinks?: Backlink[]; loading: boolean }) {
  if (loading) {
    return <div className="animate-pulse bg-gray-100 h-64 rounded"></div>
  }

  if (!backlinks || backlinks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No backlinks found.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Source Domain
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Anchor Text
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Domain Rank
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              First Seen
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {backlinks.map((backlink) => (
            <tr key={backlink.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <a
                  href={backlink.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800"
                >
                  {backlink.source_domain}
                </a>
              </td>
              <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                {backlink.anchor_text || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {backlink.domain_rank || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(backlink.first_seen).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    backlink.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {backlink.is_active ? 'Active' : 'Lost'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ReferringDomainsList({
  domains,
  loading
}: {
  domains?: ReferringDomain[]
  loading: boolean
}) {
  if (loading) {
    return <div className="animate-pulse bg-gray-100 h-64 rounded"></div>
  }

  if (!domains || domains.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No referring domains found.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Domain
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Backlinks Count
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Domain Rank
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              First Seen
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {domains.map((domain, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {domain.domain}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {domain.backlinks_count} backlinks
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {domain.domain_rank}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(domain.first_seen).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
