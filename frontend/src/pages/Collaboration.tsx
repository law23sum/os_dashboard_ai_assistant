import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Users, Network, TrendingUp } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface CollaborationRequest {
  action: string
  team_size: number
  communication_patterns: string
  project_complexity: string
}

export default function Collaboration() {
  const [action, setAction] = useState('analyze_team')
  const [teamSize, setTeamSize] = useState(5)
  const [patterns, setPatterns] = useState('')
  const [complexity, setComplexity] = useState('medium')
  const [results, setResults] = useState<string>('')

  const collaborationMutation = useMutation({
    mutationFn: async (data: CollaborationRequest) => {
      const response = await apiClient.post(apiPath('intelligence/collaboration'), data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(JSON.stringify(data, null, 2))
      toast.success('Team analysis completed successfully')
    },
    onError: (error: any) => {
      toast.error(`Collaboration analysis failed: ${error.message || 'Unknown error'}`)
      setResults(`Error: ${error.message || 'Unknown error'}`)
    },
  })

  const handleAnalyze = () => {
    collaborationMutation.mutate({
      action,
      team_size: teamSize,
      communication_patterns: patterns,
      project_complexity: complexity,
    })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <div className="flex items-center mb-2">
          <Users className="h-8 w-8 mr-3 text-primary-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Collaboration Intelligence
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Analyze team collaboration patterns and generate insights
        </p>
      </div>

      {/* Status Indicator */}
      <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-center">
          <Network className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-green-800 dark:text-green-200 font-semibold">
            ✅ Collaboration Intelligence Available
          </span>
        </div>
      </div>

      {/* Team Analysis Settings */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Team Analysis Settings
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Action
            </label>
            <select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="analyze_team">Analyze Team</option>
              <option value="generate_insights">Generate Insights</option>
              <option value="optimize_workflow">Optimize Workflow</option>
              <option value="predict_productivity">Predict Productivity</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Team Size
            </label>
            <input
              type="number"
              value={teamSize}
              onChange={(e) => setTeamSize(parseInt(e.target.value) || 5)}
              min={1}
              max={100}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Communication Patterns
            </label>
            <input
              type="text"
              value={patterns}
              onChange={(e) => setPatterns(e.target.value)}
              placeholder="Describe communication patterns"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Project Complexity
            </label>
            <select
              value={complexity}
              onChange={(e) => setComplexity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="very_high">Very High</option>
            </select>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={collaborationMutation.isPending}
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {collaborationMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <TrendingUp className="h-4 w-4 mr-2" />
                Analyze Team
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Area */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Network className="h-5 w-5 mr-2 text-gray-500" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Collaboration Analysis Results
          </h3>
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-4">
          <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-96">
            {results || 'Analysis results will appear here...'}
          </pre>
        </div>
      </div>
    </div>
  )
}
