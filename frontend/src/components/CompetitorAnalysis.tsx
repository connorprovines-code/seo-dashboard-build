import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { competitorsApi } from '../services/api'

interface CompetitorAnalysisProps {
  projectId: string
}

interface KeywordOverlap {
  keyword: string
  your_position: number | null
  competitor_positions: Record<string, number>
  opportunity_score: number
}

interface GapAnalysis {
  keyword: string
  competitor_domain: string
  competitor_position: number
  search_volume: number
  difficulty: number
  gap_score: number
}

export function CompetitorAnalysis({ projectId }: CompetitorAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'overlap' | 'gaps'>('overlap')

  // Fetch keyword overlap data
  const { data: overlapData, isLoading: overlapLoading } = useQuery({
    queryKey: ['competitor-overlap', projectId],
    queryFn: async () => {
      const response = await competitorsApi.getKeywordOverlap(projectId)
      return response.data as KeywordOverlap[]
    },
    enabled: activeTab === 'overlap'
  })

  // Fetch gap analysis data
  const { data: gapData, isLoading: gapLoading } = useQuery({
    queryKey: ['competitor-gaps', projectId],
    queryFn: async () => {
      // Note: This would need competitor_id parameter in real implementation
      // For now, showing the structure
      const response = await competitorsApi.getKeywordOverlap(projectId)
      return response.data as GapAnalysis[]
    },
    enabled: activeTab === 'gaps'
  })

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('overlap')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
                activeTab === 'overlap'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Keyword Overlap
            </button>
            <button
              onClick={() => setActiveTab('gaps')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
                activeTab === 'gaps'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Opportunity Gaps
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overlap' && (
            <KeywordOverlapTable data={overlapData} isLoading={overlapLoading} />
          )}
          {activeTab === 'gaps' && (
            <OpportunityGapsTable data={gapData} isLoading={gapLoading} />
          )}
        </div>
      </div>
    </div>
  )
}

function KeywordOverlapTable({
  data,
  isLoading
}: {
  data?: KeywordOverlap[]
  isLoading: boolean
}) {
  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-64 rounded"></div>
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No keyword overlap data available.</p>
        <p className="text-sm mt-1">
          Add competitors and keywords to see overlap analysis.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Keyword
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Your Position
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Competitors
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Opportunity Score
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {item.keyword}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {item.your_position ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    #{item.your_position}
                  </span>
                ) : (
                  <span className="text-gray-400">Not ranking</span>
                )}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                <div className="flex flex-wrap gap-2">
                  {Object.entries(item.competitor_positions).map(
                    ([domain, position]) => (
                      <span
                        key={domain}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 text-xs"
                      >
                        <span className="text-gray-600">{domain}:</span>
                        <span className="font-medium">#{position}</span>
                      </span>
                    )
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div className="flex items-center">
                  <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${item.opportunity_score}%` }}
                    ></div>
                  </div>
                  <span className="text-xs font-medium">
                    {item.opportunity_score}%
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function OpportunityGapsTable({
  data,
  isLoading
}: {
  data?: GapAnalysis[]
  isLoading: boolean
}) {
  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-64 rounded"></div>
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No gap opportunities found.</p>
        <p className="text-sm mt-1">
          These are keywords your competitors rank for but you don't.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Keyword
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Competitor
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Their Position
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Search Volume
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Difficulty
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Gap Score
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                {item.keyword}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {item.competitor_domain}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  #{item.competitor_position}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {item.search_volume?.toLocaleString() || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <DifficultyBadge difficulty={item.difficulty} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {item.gap_score}/100
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function DifficultyBadge({ difficulty }: { difficulty: number }) {
  const getColor = (diff: number) => {
    if (diff < 30) return 'bg-green-100 text-green-800'
    if (diff < 60) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getColor(
        difficulty
      )}`}
    >
      {difficulty}
    </span>
  )
}
