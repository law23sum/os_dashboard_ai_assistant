import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Bot, Play, FileCode, Activity } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface MLOpsRequest {
  action: string
  model_type: string
  dataset_path: string
  hyperparameters: Record<string, unknown>
}

export default function MLOps() {
  const [action, setAction] = useState('train_model')
  const [modelType, setModelType] = useState('classification')
  const [datasetPath, setDatasetPath] = useState('')
  const [hyperparameters, setHyperparameters] = useState('{"learning_rate": 0.001, "epochs": 100}')
  const [results, setResults] = useState<string>('')

  const mlopsMutation = useMutation({
    mutationFn: async (data: MLOpsRequest) => {
      const response = await apiClient.post(apiPath('intelligence/mlops'), data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(JSON.stringify(data, null, 2))
      toast.success('MLOps operation completed successfully')
    },
    onError: (error: any) => {
      toast.error(`MLOps operation failed: ${error.message || 'Unknown error'}`)
      setResults(`Error: ${error.message || 'Unknown error'}`)
    },
  })

  const handleExecute = () => {
    let hparams: Record<string, unknown>
    try {
      hparams = JSON.parse(hyperparameters)
      if (typeof hparams !== 'object' || hparams === null) {
        throw new Error('Hyperparameters must be a JSON object')
      }
    } catch (error) {
      toast.error('Invalid hyperparameters JSON')
      return
    }

    mlopsMutation.mutate({
      action,
      model_type: modelType,
      dataset_path: datasetPath,
      hyperparameters: hparams,
    })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <div className="flex items-center mb-2">
          <Bot className="h-8 w-8 mr-3 text-primary-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">MLOps Platform</h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Manage ML models, pipelines, deployments, and monitoring
        </p>
      </div>

      {/* Status Indicator */}
      <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-center">
          <Activity className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-green-800 dark:text-green-200 font-semibold">
            ✅ MLOps Platform Available
          </span>
        </div>
      </div>

      {/* Model Management Form */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Model Management</h3>
        
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
              <option value="train_model">Train Model</option>
              <option value="evaluate_model">Evaluate Model</option>
              <option value="deploy_model">Deploy Model</option>
              <option value="monitor_model">Monitor Model</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Model Type
            </label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="classification">Classification</option>
              <option value="regression">Regression</option>
              <option value="clustering">Clustering</option>
              <option value="nlp">NLP</option>
              <option value="computer_vision">Computer Vision</option>
              <option value="time_series">Time Series</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Dataset Path
            </label>
            <input
              type="text"
              value={datasetPath}
              onChange={(e) => setDatasetPath(e.target.value)}
              placeholder="Enter dataset path or URL"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Hyperparameters (JSON)
            </label>
            <textarea
              value={hyperparameters}
              onChange={(e) => setHyperparameters(e.target.value)}
              rows={3}
              placeholder='{"learning_rate": 0.001, "epochs": 100}'
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            />
          </div>

          <button
            onClick={handleExecute}
            disabled={mlopsMutation.isPending}
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {mlopsMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Executing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Execute MLOps Operation
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Area */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <FileCode className="h-5 w-5 mr-2 text-gray-500" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">MLOps Results</h3>
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-4">
          <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-96">
            {results || 'Results will appear here after execution...'}
          </pre>
        </div>
      </div>
    </div>
  )
}