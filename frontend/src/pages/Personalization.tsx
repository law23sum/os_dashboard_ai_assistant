import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Target, Sparkles, TrendingUp } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface PersonalizationRequest {
  recommendation_type: string
  user_preferences: string
  context_data: string
  max_recommendations: number
}

export default function Personalization() {
  const [recType, setRecType] = useState('content_based')
  const [preferences, setPreferences] = useState('')
  const [contextData, setContextData] = useState('')
  const [maxRecs, setMaxRecs] = useState(10)
  const [results, setResults] = useState<string>('')

  const personalizationMutation = useMutation({
    mutationFn: async (data: PersonalizationRequest) => {
      const response = await apiClient.post(apiPath('intelligence/personalization'), data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(JSON.stringify(data, null, 2))
      toast.success('Recommendations generated successfully')
    },
    onError: (error: any) => {
      toast.error(`Personalization failed: ${error.message || 'Unknown error'}`)
      setResults(`Error: ${error.message || 'Unknown error'}`)
    },
  })

  const handleGenerate = () => {
    personalizationMutation.mutate({
      recommendation_type: recType,
      user_preferences: preferences,
      context_data: contextData,
      max_recommendations: maxRecs,
    })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <div className="flex items-center mb-2">
          <Target className="h-8 w-8 mr-3 text-primary-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Personalization & Recommendations
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Generate personalized recommendations using ML-powered engines
        </p>
      </div>

      {/* Status Indicator */}
      <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-center">
          <Sparkles className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-green-800 dark:text-green-200 font-semibold">
            ✅ Personalization Engine Available
          </span>
        </div>
      </div>

      {/* Recommendation Settings */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Recommendation Settings
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Recommendation Type
            </label>
            <select
              value={recType}
              onChange={(e) => setRecType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="content_based">Content-Based</option>
              <option value="collaborative">Collaborative Filtering</option>
              <option value="hybrid">Hybrid</option>
              <option value="contextual">Contextual</option>
              <option value="trend_based">Trend-Based</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              User Preferences
            </label>
            <input
              type="text"
              value={preferences}
              onChange={(e) => setPreferences(e.target.value)}
              placeholder="Enter user preferences (comma-separated)"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Context Data
            </label>
            <input
              type="text"
              value={contextData}
              onChange={(e) => setContextData(e.target.value)}
              placeholder="Enter context information"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Recommendations
            </label>
            <input
              type="number"
              value={maxRecs}
              onChange={(e) => setMaxRecs(parseInt(e.target.value) || 10)}
              min={1}
              max={100}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={personalizationMutation.isPending}
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {personalizationMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating...
              </>
            ) : (
              <>
                <TrendingUp className="h-4 w-4 mr-2" />
                Generate Recommendations
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Area */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Sparkles className="h-5 w-5 mr-2 text-gray-500" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Recommendation Results
          </h3>
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-4">
          <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-96">
            {results || 'Recommendations will appear here after generation...'}
          </pre>
        </div>
      </div>
    </div>
  )
}
