import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { credentialsApi } from '../services/api'

interface APISetupModalProps {
  provider: 'dataforseo' | 'google' | 'anthropic'
  feature: string
  onComplete: () => void
  onSkip?: () => void
}

const apiInfo = {
  dataforseo: {
    name: 'DataForSEO',
    cost: '$0.07 per 1,000 keywords',
    signupUrl: 'https://app.dataforseo.com/register',
    docsUrl: 'https://docs.dataforseo.com/v3/',
    fields: [
      { name: 'login', label: 'Login/Email', type: 'text', placeholder: 'your-email@example.com' },
      { name: 'password', label: 'API Password', type: 'password', placeholder: 'Your API password' }
    ],
    instructions: [
      'Go to https://app.dataforseo.com/register',
      'Sign up (get $1 free credits)',
      'Go to Dashboard > API Access',
      'Copy your Login and Password'
    ]
  },
  google: {
    name: 'Google Search Console',
    cost: 'Free!',
    signupUrl: 'https://search.google.com/search-console',
    docsUrl: 'https://developers.google.com/webmaster-tools',
    fields: [],
    instructions: [
      'Click "Connect with Google" below',
      'Authorize access to your Search Console data',
      'Select which site to connect'
    ]
  },
  anthropic: {
    name: 'Claude AI (Anthropic)',
    cost: '~$0.003 per message',
    signupUrl: 'https://console.anthropic.com/',
    docsUrl: 'https://docs.anthropic.com/',
    fields: [
      { name: 'api_key', label: 'API Key', type: 'password', placeholder: 'sk-ant-...' }
    ],
    instructions: [
      'Go to https://console.anthropic.com/',
      'Sign up for an account',
      'Get API key from Settings > API Keys',
      'Note: This may be admin-provided in self-hosted setups'
    ]
  }
}

export default function APISetupModal({ provider, feature, onComplete, onSkip }: APISetupModalProps) {
  const info = apiInfo[provider]
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const setupMutation = useMutation({
    mutationFn: () => credentialsApi.setup(provider, formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credentials', provider] })
      onComplete()
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to save credentials')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setupMutation.mutate()
  }

  const handleChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  return (
    <div className="fixed z-50 inset-0 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Setup {info.name} API</h3>

          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-md">
              <p className="font-semibold text-sm">Why do we need this?</p>
              <p className="text-sm text-gray-700 mt-1">
                To use {feature}, we need access to {info.name}.
              </p>
              <p className="text-sm font-bold mt-2 text-primary-600">Cost: {info.cost}</p>
            </div>

            <div className="space-y-2">
              <p className="font-semibold text-sm">How to get your API key:</p>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                {info.instructions.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
              <a
                href={info.signupUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 text-sm inline-flex items-center mt-2"
              >
                → Open {info.name} signup page
                <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>

            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {info.fields.map(field => (
                <div key={field.name} className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {field.label}
                  </label>
                  <input
                    type={field.type}
                    name={field.name}
                    placeholder={field.placeholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    required
                    onChange={(e) => handleChange(field.name, e.target.value)}
                  />
                </div>
              ))}

              <div className="flex justify-end space-x-3 mt-6">
                {onSkip && (
                  <button
                    type="button"
                    onClick={onSkip}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Skip for Now
                  </button>
                )}
                <button
                  type="submit"
                  disabled={setupMutation.isPending}
                  className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                >
                  {setupMutation.isPending ? 'Testing & Saving...' : 'Test & Save Credentials'}
                </button>
              </div>
            </form>

            <div className="text-xs text-gray-500 mt-4">
              🔒 Your API credentials are encrypted and never shared. You can update or remove them anytime from Settings.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
