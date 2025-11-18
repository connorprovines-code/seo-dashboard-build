import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, keywordsApi, credentialsApi, rankTrackingApi } from '../services/api'
import APISetupModal from '../components/APISetupModal'
import RankHistoryChart from '../components/RankHistoryChart'
import { DashboardOverview } from '../components/DashboardOverview'
import { CompetitorManager } from '../components/CompetitorManager'
import { CompetitorAnalysis } from '../components/CompetitorAnalysis'
import { AIChat } from '../components/AIChat'
import { AIPermissions } from '../components/AIPermissions'
import { BacklinksDashboard } from '../components/BacklinksDashboard'

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [activeTab, setActiveTab] = useState('overview')
  const [showAPISetup, setShowAPISetup] = useState(false)
  const [showAddKeyword, setShowAddKeyword] = useState(false)
  const [showBulkAdd, setShowBulkAdd] = useState(false)
  const [showEnableTracking, setShowEnableTracking] = useState(false)
  const [selectedKeyword, setSelectedKeyword] = useState<any>(null)
  const [trackedUrl, setTrackedUrl] = useState('')
  const [newKeyword, setNewKeyword] = useState('')
  const [bulkKeywords, setBulkKeywords] = useState('')
  const queryClient = useQueryClient()

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await projectsApi.get(projectId!)
      return response.data
    },
    enabled: !!projectId,
  })

  const { data: keywords, isLoading: keywordsLoading } = useQuery({
    queryKey: ['keywords', projectId],
    queryFn: async () => {
      const response = await keywordsApi.list(projectId!)
      return response.data
    },
    enabled: !!projectId && activeTab === 'keywords',
  })

  const { data: trackedKeywords, isLoading: trackingLoading } = useQuery({
    queryKey: ['rank-tracking', projectId],
    queryFn: async () => {
      const response = await rankTrackingApi.list(projectId!)
      return response.data
    },
    enabled: !!projectId && activeTab === 'rankings',
  })

  const { data: rankStats } = useQuery({
    queryKey: ['rank-stats', projectId],
    queryFn: async () => {
      const response = await rankTrackingApi.getStats(projectId!)
      return response.data
    },
    enabled: !!projectId && activeTab === 'rankings',
  })

  const { data: credCheck } = useQuery({
    queryKey: ['credentials', 'dataforseo'],
    queryFn: async () => {
      const response = await credentialsApi.check('dataforseo')
      return response.data
    },
  })

  const addKeywordMutation = useMutation({
    mutationFn: () => keywordsApi.add(projectId!, newKeyword),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords', projectId] })
      setNewKeyword('')
      setShowAddKeyword(false)
    },
  })

  const bulkAddMutation = useMutation({
    mutationFn: (keywords: string[]) => keywordsApi.bulkAdd(projectId!, keywords),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords', projectId] })
      setBulkKeywords('')
      setShowBulkAdd(false)
    },
  })

  const refreshAllMutation = useMutation({
    mutationFn: () => keywordsApi.refreshAll(projectId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords', projectId] })
    },
  })

  const deleteKeywordMutation = useMutation({
    mutationFn: (keywordId: string) => keywordsApi.delete(projectId!, keywordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords', projectId] })
    },
  })

  const enableTrackingMutation = useMutation({
    mutationFn: () => rankTrackingApi.enable(projectId!, {
      keyword_id: selectedKeyword.id,
      tracked_url: trackedUrl,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rank-tracking', projectId] })
      queryClient.invalidateQueries({ queryKey: ['rank-stats', projectId] })
      setShowEnableTracking(false)
      setTrackedUrl('')
      setSelectedKeyword(null)
    },
  })

  const checkNowMutation = useMutation({
    mutationFn: (keywordId: string) => rankTrackingApi.checkNow(projectId!, keywordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rank-tracking', projectId] })
    },
  })

  const stopTrackingMutation = useMutation({
    mutationFn: (keywordId: string) => rankTrackingApi.stop(projectId!, keywordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rank-tracking', projectId] })
      queryClient.invalidateQueries({ queryKey: ['rank-stats', projectId] })
    },
  })

  const handleAddKeyword = () => {
    if (credCheck?.exists) {
      setShowAddKeyword(true)
    } else {
      setShowAPISetup(true)
    }
  }

  const handleBulkAdd = () => {
    const keywordsList = bulkKeywords
      .split('\n')
      .map(k => k.trim())
      .filter(k => k.length > 0)

    if (keywordsList.length > 0) {
      bulkAddMutation.mutate(keywordsList)
    }
  }

  const handleRefreshAll = () => {
    if (credCheck?.exists) {
      if (confirm('This will fetch data for all keywords. Continue?')) {
        refreshAllMutation.mutate()
      }
    } else {
      setShowAPISetup(true)
    }
  }

  const handleEnableTracking = (keyword: any) => {
    if (credCheck?.exists) {
      setSelectedKeyword(keyword)
      setTrackedUrl(project?.domain || '')
      setShowEnableTracking(true)
    } else {
      setShowAPISetup(true)
    }
  }

  if (projectLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{project?.name}</h1>
        <p className="text-gray-600 mt-1">{project?.domain}</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`${
              activeTab === 'overview'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('keywords')}
            className={`${
              activeTab === 'keywords'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Keywords
          </button>
          <button
            onClick={() => setActiveTab('rankings')}
            className={`${
              activeTab === 'rankings'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Rankings
          </button>
          <button
            onClick={() => setActiveTab('competitors')}
            className={`${
              activeTab === 'competitors'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Competitors
          </button>
          <button
            onClick={() => setActiveTab('ai-assistant')}
            className={`${
              activeTab === 'ai-assistant'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            AI Assistant
          </button>
          <button
            onClick={() => setActiveTab('backlinks')}
            className={`${
              activeTab === 'backlinks'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Backlinks
          </button>
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && projectId && (
        <DashboardOverview projectId={projectId} />
      )}

      {/* Keywords Tab */}
      {activeTab === 'keywords' && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Keywords</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowBulkAdd(true)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Bulk Add
              </button>
              <button
                onClick={handleAddKeyword}
                className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
              >
                Add Keyword
              </button>
              {keywords && keywords.length > 0 && (
                <button
                  onClick={handleRefreshAll}
                  disabled={refreshAllMutation.isPending}
                  className="px-4 py-2 border border-primary-600 rounded-md text-sm font-medium text-primary-600 hover:bg-primary-50 disabled:opacity-50"
                >
                  {refreshAllMutation.isPending ? 'Refreshing...' : 'Refresh All Data'}
                </button>
              )}
            </div>
          </div>

          {keywordsLoading ? (
            <div className="text-center py-8">Loading keywords...</div>
          ) : keywords && keywords.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Keyword
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Volume
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Difficulty
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CPC
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {keywords.map((keyword: any) => (
                    <tr key={keyword.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {keyword.keyword_text}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {keyword.search_volume?.toLocaleString() || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {keyword.keyword_difficulty || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {keyword.cpc ? `$${keyword.cpc}` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <button
                          onClick={() => handleEnableTracking(keyword)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          Track
                        </button>
                        <button
                          onClick={() => deleteKeywordMutation.mutate(keyword.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No keywords yet. Add your first keyword to get started!
            </div>
          )}
        </div>
      )}

      {/* Rankings Tab */}
      {activeTab === 'rankings' && (
        <div className="space-y-6">
          {/* Stats Overview */}
          {rankStats && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Ranking Overview</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Top 3</h3>
                  <p className="mt-2 text-2xl font-semibold text-green-600">{rankStats.distribution?.top_3 || 0}</p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Top 10</h3>
                  <p className="mt-2 text-2xl font-semibold text-blue-600">{rankStats.distribution?.top_10 || 0}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Top 20</h3>
                  <p className="mt-2 text-2xl font-semibold text-yellow-600">{rankStats.distribution?.top_20 || 0}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">Below 20</h3>
                  <p className="mt-2 text-2xl font-semibold text-gray-600">{rankStats.distribution?.below_20 || 0}</p>
                </div>
              </div>
            </div>
          )}

          {/* Tracked Keywords Table */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Tracked Keywords</h2>

            {trackingLoading ? (
              <div className="text-center py-8">Loading rankings...</div>
            ) : trackedKeywords && trackedKeywords.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Keyword
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Position
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        URL
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Checked
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {trackedKeywords.map((tracked: any) => (
                      <tr key={tracked.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {tracked.keyword_text}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {tracked.rank_position ? (
                            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
                              tracked.rank_position <= 3 ? 'bg-green-100 text-green-800' :
                              tracked.rank_position <= 10 ? 'bg-blue-100 text-blue-800' :
                              tracked.rank_position <= 20 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              #{tracked.rank_position}
                            </span>
                          ) : (
                            <span className="text-gray-400">Not ranked</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {tracked.tracked_url}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(tracked.checked_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                          <button
                            onClick={() => checkNowMutation.mutate(tracked.keyword_id)}
                            disabled={checkNowMutation.isPending}
                            className="text-primary-600 hover:text-primary-900 disabled:opacity-50"
                          >
                            Check Now
                          </button>
                          <button
                            onClick={() => {
                              if (confirm(`Stop tracking "${tracked.keyword_text}"?`)) {
                                stopTrackingMutation.mutate(tracked.keyword_id)
                              }
                            }}
                            className="text-red-600 hover:text-red-900"
                          >
                            Stop
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No keywords being tracked yet. Go to Keywords tab to enable tracking!
              </div>
            )}
          </div>
        </div>
      )}

      {/* Competitors Tab */}
      {activeTab === 'competitors' && projectId && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Competitor Manager */}
            <CompetitorManager projectId={projectId} />

            {/* Competitor Analysis */}
            <div className="lg:col-span-2">
              <CompetitorAnalysis projectId={projectId} />
            </div>
          </div>
        </div>
      )}

      {/* AI Assistant Tab */}
      {activeTab === 'ai-assistant' && projectId && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AIChat projectId={projectId} />
          </div>
          <div>
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                About AI Assistant
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Your AI-powered SEO assistant can analyze data, find opportunities, and provide insights.
              </p>
              <button
                onClick={() => window.open('/ai-permissions', '_blank')}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Manage Permissions →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Backlinks Tab */}
      {activeTab === 'backlinks' && projectId && (
        <BacklinksDashboard projectId={projectId} />
      )}

      {/* Modals... (keeping existing modals) */}
      {showAddKeyword && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddKeyword(false)}></div>

            <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add Keyword</h3>
              <form onSubmit={(e) => { e.preventDefault(); addKeywordMutation.mutate() }}>
                <div className="mb-4">
                  <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-1">
                    Keyword
                  </label>
                  <input
                    type="text"
                    id="keyword"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    placeholder="seo tools"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowAddKeyword(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={addKeywordMutation.isPending}
                    className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                  >
                    {addKeywordMutation.isPending ? 'Adding...' : 'Add Keyword'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showBulkAdd && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowBulkAdd(false)}></div>

            <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Bulk Add Keywords</h3>
              <form onSubmit={(e) => { e.preventDefault(); handleBulkAdd() }}>
                <div className="mb-4">
                  <label htmlFor="bulk-keywords" className="block text-sm font-medium text-gray-700 mb-1">
                    Keywords (one per line)
                  </label>
                  <textarea
                    id="bulk-keywords"
                    rows={10}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    value={bulkKeywords}
                    onChange={(e) => setBulkKeywords(e.target.value)}
                    placeholder="seo tools&#10;keyword research&#10;rank tracking"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowBulkAdd(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={bulkAddMutation.isPending}
                    className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                  >
                    {bulkAddMutation.isPending ? 'Adding...' : 'Add Keywords'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showEnableTracking && selectedKeyword && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowEnableTracking(false)}></div>

            <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Enable Rank Tracking</h3>
              <form onSubmit={(e) => { e.preventDefault(); enableTrackingMutation.mutate() }}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Keyword
                  </label>
                  <input
                    type="text"
                    disabled
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                    value={selectedKeyword.keyword_text}
                  />
                </div>
                <div className="mb-4">
                  <label htmlFor="tracked-url" className="block text-sm font-medium text-gray-700 mb-1">
                    URL to Track
                  </label>
                  <input
                    type="text"
                    id="tracked-url"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    value={trackedUrl}
                    onChange={(e) => setTrackedUrl(e.target.value)}
                    placeholder="https://example.com/page"
                  />
                  <p className="mt-1 text-xs text-gray-500">Enter the URL you want to track rankings for</p>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowEnableTracking(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={enableTrackingMutation.isPending}
                    className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                  >
                    {enableTrackingMutation.isPending ? 'Enabling...' : 'Enable Tracking'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showAPISetup && (
        <APISetupModal
          provider="dataforseo"
          feature="keyword research"
          onComplete={() => {
            setShowAPISetup(false)
            setShowAddKeyword(true)
          }}
          onSkip={() => setShowAPISetup(false)}
        />
      )}
    </div>
  )
}
