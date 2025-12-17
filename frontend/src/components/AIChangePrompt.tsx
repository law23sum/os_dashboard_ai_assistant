import { X, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

interface AIChangePromptProps {
  isOpen: boolean
  documentTitle: string
  changeSummary: string
  confidence: number
  onAccept: () => void
  onReject: () => void
  onViewChanges: () => void
}

export default function AIChangePrompt({
  isOpen,
  documentTitle,
  changeSummary,
  confidence,
  onAccept,
  onReject,
  onViewChanges,
}: AIChangePromptProps) {
  if (!isOpen) return null

  const getConfidenceColor = () => {
    if (confidence >= 80) return 'text-green-500'
    if (confidence >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getConfidenceLabel = () => {
    if (confidence >= 80) return 'High'
    if (confidence >= 60) return 'Medium'
    return 'Low'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI Change Proposed
          </h3>
          <button
            onClick={onReject}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Document</p>
            <p className="font-medium text-gray-900 dark:text-white">{documentTitle}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Change Summary</p>
            <p className="text-gray-900 dark:text-gray-100">{changeSummary}</p>
          </div>

          <div className="flex items-center gap-2">
            <p className="text-sm text-gray-500 dark:text-gray-400">Confidence:</p>
            <span className={`font-semibold ${getConfidenceColor()}`}>
              {getConfidenceLabel()} ({confidence}%)
            </span>
          </div>

          {confidence < 60 && (
            <div className="flex items-center gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />
              <p className="text-sm text-amber-700 dark:text-amber-300">
                Low confidence detected. Review changes carefully before accepting.
              </p>
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onReject}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center justify-center gap-2"
          >
            <XCircle className="w-4 h-4" />
            Reject
          </button>
          <button
            onClick={onViewChanges}
            className="flex-1 px-4 py-2 border border-primary-500 text-primary-600 dark:text-primary-400 rounded-md hover:bg-primary-50 dark:hover:bg-primary-900/20"
          >
            View Changes
          </button>
          <button
            onClick={onAccept}
            className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 flex items-center justify-center gap-2"
          >
            <CheckCircle className="w-4 h-4" />
            Accept
          </button>
        </div>
      </div>
    </div>
  )
}

