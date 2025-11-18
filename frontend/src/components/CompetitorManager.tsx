import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { competitorsApi } from '../services/api'

interface CompetitorManagerProps {
  projectId: string
}

interface Competitor {
  id: string
  domain: string
  notes?: string
  created_at: string
}

export function CompetitorManager({ projectId }: CompetitorManagerProps) {
  const [newDomain, setNewDomain] = useState('')
  const [notes, setNotes] = useState('')
  const queryClient = useQueryClient()

  // Fetch competitors
  const { data: competitors, isLoading } = useQuery<Competitor[]>({
    queryKey: ['competitors', projectId],
    queryFn: async () => {
      const response = await competitorsApi.list(projectId)
      return response.data
    }
  })

  // Add competitor mutation
  const addMutation = useMutation({
    mutationFn: (data: { domain: string; notes?: string }) =>
      competitorsApi.add(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors', projectId] })
      setNewDomain('')
      setNotes('')
    }
  })

  // Delete competitor mutation
  const deleteMutation = useMutation({
    mutationFn: (competitorId: string) =>
      competitorsApi.delete(projectId, competitorId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors', projectId] })
    }
  })

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newDomain.trim()) return

    addMutation.mutate({
      domain: newDomain.trim(),
      notes: notes.trim() || undefined
    })
  }

  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-64 rounded-lg"></div>
  }

  return (
    <div className="space-y-6">
      {/* Add Competitor Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Add Competitor Domain</h3>
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Competitor Domain
            </label>
            <input
              type="text"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              placeholder="competitor.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={addMutation.isPending}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Main competitor, similar niche, etc."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={addMutation.isPending}
            />
          </div>

          <button
            type="submit"
            disabled={addMutation.isPending || !newDomain.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
          >
            {addMutation.isPending ? 'Adding...' : 'Add Competitor'}
          </button>
        </form>
      </div>

      {/* Competitors List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">
            Tracked Competitors ({competitors?.length || 0})
          </h3>
        </div>

        {competitors && competitors.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {competitors.map((competitor) => (
              <div
                key={competitor.id}
                className="p-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-gray-900">
                        {competitor.domain}
                      </h4>
                      <span className="text-xs text-gray-500">
                        Added {new Date(competitor.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {competitor.notes && (
                      <p className="text-sm text-gray-600 mt-1">
                        {competitor.notes}
                      </p>
                    )}
                  </div>

                  <button
                    onClick={() => deleteMutation.mutate(competitor.id)}
                    disabled={deleteMutation.isPending}
                    className="ml-4 text-red-600 hover:text-red-800 text-sm font-medium disabled:text-gray-400"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <p>No competitors added yet.</p>
            <p className="text-sm mt-1">
              Add competitor domains to track their rankings and find opportunities.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
