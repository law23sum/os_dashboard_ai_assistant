import { useState, useEffect } from 'react'
import { X, AlertCircle, CheckCircle, Info } from 'lucide-react'

export interface AIPermissionSettings {
  mode: 'auto' | 'permission'
  confidenceThreshold: number // 0-100
}

interface AIPermissionModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (settings: AIPermissionSettings) => void
  initialSettings?: AIPermissionSettings
}

export default function AIPermissionModal({
  isOpen,
  onClose,
  onSave,
  initialSettings,
}: AIPermissionModalProps) {
  const [mode, setMode] = useState<AIPermissionSettings['mode']>(
    initialSettings?.mode || 'permission'
  )
  const [confidenceThreshold, setConfidenceThreshold] = useState(
    initialSettings?.confidenceThreshold || 80
  )

  useEffect(() => {
    if (initialSettings) {
      setMode(initialSettings.mode)
      setConfidenceThreshold(initialSettings.confidenceThreshold)
    }
  }, [initialSettings])

  if (!isOpen) return null

  const handleSave = () => {
    onSave({ mode, confidenceThreshold })
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI Document Update Settings
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Update Mode
            </label>
            <div className="space-y-2">
              <label className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
                <input
                  type="radio"
                  name="mode"
                  value="auto"
                  checked={mode === 'auto'}
                  onChange={(e) => setMode(e.target.value as 'auto')}
                  className="mt-1 mr-3"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="font-medium text-gray-900 dark:text-white">Auto-Update</span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    AI changes are applied automatically when confidence is above threshold
                  </p>
                </div>
              </label>

              <label className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
                <input
                  type="radio"
                  name="mode"
                  value="permission"
                  checked={mode === 'permission'}
                  onChange={(e) => setMode(e.target.value as 'permission')}
                  className="mt-1 mr-3"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-500" />
                    <span className="font-medium text-gray-900 dark:text-white">Require Permission</span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Prompt before applying each AI change, regardless of confidence
                  </p>
                </div>
              </label>
            </div>
          </div>

          {mode === 'auto' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Confidence Threshold: {confidenceThreshold}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>Low (0%)</span>
                <span>Medium (50%)</span>
                <span>High (100%)</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Changes with confidence above {confidenceThreshold}% will be applied automatically
              </p>
            </div>
          )}

          <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <Info className="w-4 h-4 text-blue-500 flex-shrink-0" />
            <p className="text-sm text-blue-700 dark:text-blue-300">
              These settings apply to the current session. You'll be prompted again when starting a new session.
            </p>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}

