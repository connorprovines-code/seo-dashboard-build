import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

interface Permission {
  id: string
  title: string
  description: string
  required?: boolean
  recommended?: boolean
  dangerous?: boolean
  icon: string
}

const PERMISSIONS: Permission[] = [
  {
    id: 'read_data',
    title: 'Read SEO Data',
    description: 'Allow AI to query your keywords, rankings, and analytics',
    required: true,
    icon: '📊'
  },
  {
    id: 'write_data',
    title: 'Modify SEO Data',
    description: 'Allow AI to add keywords, update tracking, and manage projects',
    recommended: true,
    icon: '✏️'
  },
  {
    id: 'send_emails',
    title: 'Send Emails',
    description: 'Allow AI to send outreach emails on your behalf via webhooks',
    dangerous: true,
    icon: '📧'
  },
  {
    id: 'manage_apis',
    title: 'Manage Integrations',
    description: 'Allow AI to add/remove API connectors and webhooks',
    dangerous: true,
    icon: '🔌'
  }
]

export function AIPermissions() {
  const queryClient = useQueryClient()
  const [permissions, setPermissions] = useState<Record<string, boolean>>({
    read_data: true, // Always true by default
    write_data: false,
    send_emails: false,
    manage_apis: false
  })

  // Fetch current permissions
  const { isLoading } = useQuery({
    queryKey: ['ai-permissions'],
    queryFn: async () => {
      // This would call the API to get current permissions
      // For now, using local state
      return permissions
    }
  })

  // Grant permission mutation
  const grantMutation = useMutation({
    mutationFn: async (_permissionId: string) => {
      // This would call the API to grant permission
      // await aiApi.grantPermission(permissionId)
      return { success: true }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-permissions'] })
    }
  })

  // Revoke permission mutation
  const revokeMutation = useMutation({
    mutationFn: async (_permissionId: string) => {
      // This would call the API to revoke permission
      // await aiApi.revokePermission(permissionId)
      return { success: true }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-permissions'] })
    }
  })

  const handleToggle = (permissionId: string, currentValue: boolean) => {
    if (permissionId === 'read_data') return // Can't disable required permission

    const newValue = !currentValue
    setPermissions(prev => ({ ...prev, [permissionId]: newValue }))

    if (newValue) {
      grantMutation.mutate(permissionId)
    } else {
      revokeMutation.mutate(permissionId)
    }
  }

  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-96 rounded-lg"></div>
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI Assistant Permissions
        </h2>
        <p className="text-gray-600">
          Control what actions the AI assistant can perform on your behalf. You can change
          these at any time.
        </p>
      </div>

      {/* Permissions List */}
      <div className="space-y-4">
        {PERMISSIONS.map((perm) => {
          const isEnabled = permissions[perm.id]

          return (
            <div
              key={perm.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{perm.icon}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {perm.title}
                      </h3>
                      {perm.required && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 ml-2">
                          Required
                        </span>
                      )}
                      {perm.recommended && !perm.required && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 ml-2">
                          Recommended
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 ml-11">
                    {perm.description}
                  </p>

                  {perm.dangerous && (
                    <div className="mt-3 ml-11 flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                      <span className="text-red-600 text-sm">⚠️</span>
                      <p className="text-xs text-red-700">
                        <strong>Caution:</strong> This permission allows significant
                        actions. Only enable if you trust the AI to act on your behalf.
                      </p>
                    </div>
                  )}
                </div>

                {/* Toggle Switch */}
                <div className="ml-6">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={isEnabled}
                      onChange={() => handleToggle(perm.id, isEnabled)}
                      disabled={perm.required}
                    />
                    <div
                      className={`w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600 ${
                        perm.required ? 'cursor-not-allowed opacity-60' : ''
                      }`}
                    ></div>
                  </label>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Security Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <span className="text-blue-600 text-xl">🔒</span>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Security & Privacy</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• All AI actions are logged and can be reviewed in Settings</li>
              <li>
                • Your API credentials are encrypted and never shared with the AI
              </li>
              <li>
                • You can revoke any permission immediately if you're not comfortable
              </li>
              <li>• The AI will always ask for confirmation before major actions</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <button
          onClick={() =>
            setPermissions({
              read_data: true,
              write_data: false,
              send_emails: false,
              manage_apis: false
            })
          }
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition"
        >
          Reset to Defaults
        </button>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
          Save Changes
        </button>
      </div>
    </div>
  )
}
