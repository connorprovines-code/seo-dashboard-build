import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, keywordsApi, credentialsApi } from '../services/api'
import APISetupModal from '../components/APISetupModal'

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [activeTab, setActiveTab] = useState('overview')
  const [showAPISetup, setShowAPISetup] = useState(false)
  const [showAddKeyword, setShowAddKeyword] = useState(false)
  const [showBulkAdd, setShowBulkAdd] = useState(false)
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
        <nav className="-mb-px flex space-x-8">
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
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Project Overview</h2>
          <p className="text-gray-600 mb-6">
            Track keywords, rankings, and analyze competitors for this project.
          </p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Keywords</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900">{keywords?.length || 0}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Tracked Rankings</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900">0</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Competitors</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900">0</p>
            </div>
          </div>
        </div>
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
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
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

      {/* Add Keyword Modal */}
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

      {/* Bulk Add Modal */}
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

      {/* API Setup Modal */}
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
