import { useState } from 'react'
import { Settings, ChevronDown, ChevronUp, Info, Sparkles } from 'lucide-react'

interface GPT52SettingsProps {
  reasoningEffort: string
  verbosity: string
  enablePreambles: boolean
  enableApplyPatch: boolean
  allowedTools: string[]
  onReasoningEffortChange: (value: string) => void
  onVerbosityChange: (value: string) => void
  onPreamblesChange: (value: boolean) => void
  onApplyPatchChange: (value: boolean) => void
  onAllowedToolsChange: (tools: string[]) => void
}

const REASONING_EFFORTS = [
  { value: 'none', label: 'None', description: 'Lower latency, minimal reasoning' },
  { value: 'low', label: 'Low', description: 'Light reasoning for faster responses' },
  { value: 'medium', label: 'Medium', description: 'Balanced reasoning (recommended)' },
  { value: 'high', label: 'High', description: 'Thorough reasoning for complex problems' },
  { value: 'xhigh', label: 'X-High', description: 'Maximum reasoning effort' },
]

const VERBOSITY_LEVELS = [
  { value: 'low', label: 'Low', description: 'Concise answers, minimal commentary' },
  { value: 'medium', label: 'Medium', description: 'Balanced output (recommended)' },
  { value: 'high', label: 'High', description: 'Thorough explanations with inline comments' },
]

const AVAILABLE_TOOLS = [
  { id: 'execute_command', label: 'Execute Command', description: 'Run shell commands' },
  { id: 'read_file', label: 'Read File', description: 'Read file contents' },
  { id: 'apply_patch', label: 'Apply Patch', description: 'Code editing with structured diffs' },
]

export default function GPT52Settings({
  reasoningEffort,
  verbosity,
  enablePreambles,
  enableApplyPatch,
  allowedTools,
  onReasoningEffortChange,
  onVerbosityChange,
  onPreamblesChange,
  onApplyPatchChange,
  onAllowedToolsChange,
}: GPT52SettingsProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [showToolSelector, setShowToolSelector] = useState(false)

  const toggleTool = (toolId: string) => {
    if (allowedTools.includes(toolId)) {
      onAllowedToolsChange(allowedTools.filter(t => t !== toolId))
    } else {
      onAllowedToolsChange([...allowedTools, toolId])
    }
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden backdrop-blur-sm">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-700/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30">
            <Sparkles className="w-4 h-4 text-primary-400" />
          </div>
          <div className="text-left">
            <div className="text-sm font-semibold text-white">GPT-5.2 Settings</div>
            <div className="text-xs text-slate-400">
              {reasoningEffort} reasoning • {verbosity} verbosity
              {enablePreambles && ' • Preambles'}
              {enableApplyPatch && ' • Apply Patch'}
            </div>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 py-4 space-y-4 border-t border-slate-700/50">
          {/* Reasoning Effort */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Reasoning Effort
            </label>
            <div className="grid grid-cols-5 gap-2">
              {REASONING_EFFORTS.map((effort) => (
                <button
                  key={effort.value}
                  onClick={() => onReasoningEffortChange(effort.value)}
                  className={`
                    px-3 py-2 rounded-lg text-xs font-medium transition-all
                    ${
                      reasoningEffort === effort.value
                        ? 'bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/20'
                        : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-600/50'
                    }
                  `}
                  title={effort.description}
                >
                  {effort.label}
                </button>
              ))}
            </div>
            <p className="mt-1.5 text-xs text-slate-400">
              {REASONING_EFFORTS.find(e => e.value === reasoningEffort)?.description}
            </p>
          </div>

          {/* Verbosity */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Verbosity
            </label>
            <div className="grid grid-cols-3 gap-2">
              {VERBOSITY_LEVELS.map((level) => (
                <button
                  key={level.value}
                  onClick={() => onVerbosityChange(level.value)}
                  className={`
                    px-3 py-2 rounded-lg text-xs font-medium transition-all
                    ${
                      verbosity === level.value
                        ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-lg shadow-emerald-500/20'
                        : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-600/50'
                    }
                  `}
                  title={level.description}
                >
                  {level.label}
                </button>
              ))}
            </div>
            <p className="mt-1.5 text-xs text-slate-400">
              {VERBOSITY_LEVELS.find(v => v.value === verbosity)?.description}
            </p>
          </div>

          {/* Advanced Features */}
          <div className="space-y-3">
            <label className="block text-xs font-semibold text-slate-300">
              Advanced Features
            </label>
            
            {/* Preambles */}
            <label className="flex items-center gap-3 p-3 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 transition-colors cursor-pointer border border-slate-600/30">
              <input
                type="checkbox"
                checked={enablePreambles}
                onChange={(e) => onPreamblesChange(e.target.checked)}
                className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-primary-500 focus:ring-primary-500 focus:ring-offset-slate-900"
              />
              <div className="flex-1">
                <div className="text-sm font-medium text-white">Tool Call Preambles</div>
                <div className="text-xs text-slate-400">
                  Explain tool calls before execution for better transparency
                </div>
              </div>
            </label>

            {/* Apply Patch */}
            <label className="flex items-center gap-3 p-3 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 transition-colors cursor-pointer border border-slate-600/30">
              <input
                type="checkbox"
                checked={enableApplyPatch}
                onChange={(e) => onApplyPatchChange(e.target.checked)}
                className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-primary-500 focus:ring-primary-500 focus:ring-offset-slate-900"
              />
              <div className="flex-1">
                <div className="text-sm font-medium text-white">Apply Patch Tool</div>
                <div className="text-xs text-slate-400">
                  Enable structured code editing with diffs
                </div>
              </div>
            </label>
          </div>

          {/* Allowed Tools */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-semibold text-slate-300">
                Allowed Tools
              </label>
              <button
                onClick={() => setShowToolSelector(!showToolSelector)}
                className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
              >
                {showToolSelector ? 'Hide' : 'Configure'}
              </button>
            </div>
            {showToolSelector && (
              <div className="space-y-2 p-3 rounded-lg bg-slate-700/30 border border-slate-600/30">
                {AVAILABLE_TOOLS.map((tool) => (
                  <label
                    key={tool.id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/50 transition-colors cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={allowedTools.includes(tool.id)}
                      onChange={() => toggleTool(tool.id)}
                      className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-primary-500 focus:ring-primary-500"
                    />
                    <div className="flex-1">
                      <div className="text-xs font-medium text-white">{tool.label}</div>
                      <div className="text-xs text-slate-400">{tool.description}</div>
                    </div>
                  </label>
                ))}
                {allowedTools.length === 0 && (
                  <p className="text-xs text-slate-400 italic">
                    No tools selected. All tools will be available.
                  </p>
                )}
              </div>
            )}
            {!showToolSelector && allowedTools.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {allowedTools.map((toolId) => {
                  const tool = AVAILABLE_TOOLS.find(t => t.id === toolId)
                  return tool ? (
                    <span
                      key={toolId}
                      className="px-2 py-1 text-xs font-medium bg-primary-500/20 text-primary-300 rounded-lg border border-primary-500/30"
                    >
                      {tool.label}
                    </span>
                  ) : null
                })}
              </div>
            )}
          </div>

          {/* Info Note */}
          <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-blue-300">
              <strong className="font-semibold">GPT-5.2 Features:</strong> These settings control
              how the model reasons and responds. Higher reasoning effort improves accuracy but
              increases latency. Verbosity controls output length and detail.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}



