import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../services/api'

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await projectsApi.get(projectId!)
      return response.data
    },
    enabled: !!projectId,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{project?.name}</h1>
        <p className="text-gray-600 mt-1">{project?.domain}</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Project Overview</h2>
        <p className="text-gray-600">
          This is where you'll manage keywords, track rankings, and analyze competitors for this project.
        </p>
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500">Keywords</h3>
            <p className="mt-2 text-2xl font-semibold text-gray-900">0</p>
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
    </div>
  )
}
