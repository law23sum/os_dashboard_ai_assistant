import { useMutation, useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Search, ShieldCheck, Sparkles, Workflow } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { toolingApi, ToolingTriageRequest } from '../services/api'
import { toast } from '../utils/toast'

const parseNumber = (value: string): number | undefined => {
  const trimmed = value.trim()
  if (!trimmed) return undefined
  const parsed = Number(trimmed)
  return Number.isFinite(parsed) ? parsed : undefined
}

export default function ToolingLab() {
  const [triagePrompt, setTriagePrompt] = useState('Route this prompt to the right agent.')
  const [triageMode, setTriageMode] = useState<ToolingTriageRequest['mode']>('auto')
  const [triageMaxAgents, setTriageMaxAgents] = useState('3')

  const [fileQuery, setFileQuery] = useState('Explain streaming tool calls in our docs.')
  const [vectorStoreIds, setVectorStoreIds] = useState('')
  const [fileMaxResults, setFileMaxResults] = useState('5')

  const [guardrailText, setGuardrailText] = useState('Here is a response draft to evaluate.')
  const [guardrailMaxChars, setGuardrailMaxChars] = useState('')

  const toolExamplesQuery = useQuery({
    queryKey: ['tooling', 'tool-examples'],
    queryFn: toolingApi.getToolExamples,
  })

  const triageMutation = useMutation({
    mutationFn: toolingApi.triage,
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Triage failed')
    },
  })

  const fileSearchMutation = useMutation({
    mutationFn: toolingApi.fileSearch,
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'File search failed')
    },
  })

  const guardrailsMutation = useMutation({
    mutationFn: toolingApi.guardrails,
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Guardrails check failed')
    },
  })

  const vectorStoreList = useMemo(() => {
    return vectorStoreIds
      .split(',')
      .map((entry) => entry.trim())
      .filter(Boolean)
  }, [vectorStoreIds])

  const handleTriage = () => {
    const maxAgents = parseNumber(triageMaxAgents)
    triageMutation.mutate({
      prompt: triagePrompt,
      mode: triageMode || undefined,
      max_agents: maxAgents,
    })
  }

  const handleFileSearch = () => {
    if (vectorStoreList.length === 0) {
      toast.error('Enter at least one vector store id')
      return
    }

    const maxResults = parseNumber(fileMaxResults)
    fileSearchMutation.mutate({
      query: fileQuery,
      vector_store_ids: vectorStoreList,
      max_num_results: maxResults,
    })
  }

  const handleGuardrails = () => {
    const maxChars = parseNumber(guardrailMaxChars)
    guardrailsMutation.mutate({
      response_text: guardrailText,
      max_response_chars: maxChars,
      require_safe_language: true,
    })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tooling Lab"
        description="Experiment with tool calling, agent routing, file search, and guardrails."
        icon={Sparkles}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="bg-white rounded-lg border p-6 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Workflow className="w-4 h-4 text-indigo-500" />
            Tool Calling Examples
          </div>
          {toolExamplesQuery.isLoading ? (
            <p className="text-sm text-gray-500">Loading tool examples...</p>
          ) : toolExamplesQuery.data ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">{toolExamplesQuery.data.openapi_hint}</p>
              <div className="space-y-2">
                {toolExamplesQuery.data.examples.map((example, index) => (
                  <div key={`${example.tool_name}-${index}`} className="rounded-md border bg-gray-50 p-3">
                    <p className="text-xs text-gray-500">Prompt</p>
                    <p className="text-sm text-gray-800">{example.prompt}</p>
                    <p className="mt-2 text-xs text-gray-500">Tool</p>
                    <p className="text-sm font-medium text-gray-900">{example.tool_name}</p>
                  </div>
                ))}
              </div>
              <details className="rounded-md border p-3">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700">
                  View Tool Schemas
                </summary>
                <pre className="mt-3 text-xs text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(toolExamplesQuery.data.tools, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No tool examples available.</p>
          )}
        </section>

        <section className="bg-white rounded-lg border p-6 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Workflow className="w-4 h-4 text-emerald-500" />
            Multi-Agent Triage
          </div>
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700">Prompt</label>
            <textarea
              className="w-full rounded-md border px-3 py-2 text-sm"
              rows={4}
              value={triagePrompt}
              onChange={(event) => setTriagePrompt(event.target.value)}
            />
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="text-sm font-medium text-gray-700">Mode</label>
              <select
                className="w-full rounded-md border px-3 py-2 text-sm"
                value={triageMode}
                onChange={(event) => setTriageMode(event.target.value as ToolingTriageRequest['mode'])}
              >
                <option value="auto">Auto</option>
                <option value="heuristic">Heuristic</option>
                <option value="llm">LLM</option>
              </select>
              <label className="text-sm font-medium text-gray-700">Max Agents</label>
              <input
                className="w-full rounded-md border px-3 py-2 text-sm"
                value={triageMaxAgents}
                onChange={(event) => setTriageMaxAgents(event.target.value)}
                placeholder="3"
              />
            </div>
            <button
              className="inline-flex items-center gap-2 rounded-md bg-black px-4 py-2 text-sm font-semibold text-white"
              onClick={handleTriage}
              type="button"
            >
              Run Triage
            </button>
            {triageMutation.data && (
              <div className="rounded-md border bg-gray-50 p-3 text-sm text-gray-700">
                <div className="flex flex-wrap gap-2">
                  {triageMutation.data.agents.map((agent) => (
                    <span key={agent} className="rounded-full bg-white px-3 py-1 text-xs font-semibold">
                      {agent}
                    </span>
                  ))}
                </div>
                <p className="mt-2 text-xs text-gray-500">Mode: {triageMutation.data.mode}</p>
                <p className="mt-2 text-sm text-gray-700">{triageMutation.data.rationale}</p>
                <p className="mt-2 text-xs text-gray-500">
                  Confidence: {(triageMutation.data.confidence * 100).toFixed(0)}%
                </p>
              </div>
            )}
          </div>
        </section>

        <section className="bg-white rounded-lg border p-6 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Search className="w-4 h-4 text-blue-500" />
            File Search
          </div>
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700">Query</label>
            <textarea
              className="w-full rounded-md border px-3 py-2 text-sm"
              rows={3}
              value={fileQuery}
              onChange={(event) => setFileQuery(event.target.value)}
            />
            <label className="text-sm font-medium text-gray-700">Vector Store IDs</label>
            <input
              className="w-full rounded-md border px-3 py-2 text-sm"
              value={vectorStoreIds}
              onChange={(event) => setVectorStoreIds(event.target.value)}
              placeholder="vs_123, vs_456"
            />
            <label className="text-sm font-medium text-gray-700">Max Results</label>
            <input
              className="w-full rounded-md border px-3 py-2 text-sm"
              value={fileMaxResults}
              onChange={(event) => setFileMaxResults(event.target.value)}
              placeholder="5"
            />
            <button
              className="inline-flex items-center gap-2 rounded-md bg-black px-4 py-2 text-sm font-semibold text-white"
              onClick={handleFileSearch}
              type="button"
            >
              Run File Search
            </button>
            {fileSearchMutation.data && (
              <div className="rounded-md border bg-gray-50 p-3 text-sm text-gray-700">
                <p className="text-xs text-gray-500">
                  Results: {fileSearchMutation.data.results.length}
                </p>
                <p className="mt-2 text-sm text-gray-700">{fileSearchMutation.data.response}</p>
                <details className="mt-3">
                  <summary className="cursor-pointer text-xs font-semibold text-gray-600">
                    View Raw Results
                  </summary>
                  <pre className="mt-2 text-xs whitespace-pre-wrap">
                    {JSON.stringify(fileSearchMutation.data.results, null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </div>
        </section>

        <section className="bg-white rounded-lg border p-6 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
            <ShieldCheck className="w-4 h-4 text-rose-500" />
            Guardrails
          </div>
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700">Response Text</label>
            <textarea
              className="w-full rounded-md border px-3 py-2 text-sm"
              rows={3}
              value={guardrailText}
              onChange={(event) => setGuardrailText(event.target.value)}
            />
            <label className="text-sm font-medium text-gray-700">Max Characters (optional)</label>
            <input
              className="w-full rounded-md border px-3 py-2 text-sm"
              value={guardrailMaxChars}
              onChange={(event) => setGuardrailMaxChars(event.target.value)}
              placeholder="1500"
            />
            <button
              className="inline-flex items-center gap-2 rounded-md bg-black px-4 py-2 text-sm font-semibold text-white"
              onClick={handleGuardrails}
              type="button"
            >
              Check Guardrails
            </button>
            {guardrailsMutation.data && (
              <div className="rounded-md border bg-gray-50 p-3 text-sm text-gray-700">
                <p className="text-xs text-gray-500">
                  Allowed: {guardrailsMutation.data.allowed ? 'Yes' : 'No'} | Score:{' '}
                  {guardrailsMutation.data.score.toFixed(2)}
                </p>
                {guardrailsMutation.data.violations.length > 0 ? (
                  <ul className="mt-2 space-y-1 text-xs text-rose-600">
                    {guardrailsMutation.data.violations.map((violation, index) => (
                      <li key={`${violation.rule}-${index}`}>{violation.detail}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-xs text-emerald-600">No violations detected.</p>
                )}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
