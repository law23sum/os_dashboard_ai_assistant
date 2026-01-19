import { useState, useMemo, ChangeEvent } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { UploadCloud, Image as ImageIcon, ScanLine, Type, Crosshair, Sparkles } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface FilePayload {
  filename: string
  content_type?: string
  data_url?: string | null
}

interface AnalysisResult {
  summary: string
  labels: string[]
  confidence: number
  metadata: Record<string, unknown>
  highlights: string[]
  generated_at: string
}

interface OCRResult {
  text: string
  word_count: number
  language: string
  sections: string[]
}

interface DetectionResult {
  objects: Array<{ label: string; confidence: number; bounding_box: { x: number; y: number; w: number; h: number } }>
  detected_at: string
  model_version: string
}

interface VisionStats {
  documents_processed_today: number
  avg_latency_ms: number
  last_model_update: string
  active_models: string[]
}

const sampleImages = [
  {
    id: 'whiteboard',
    title: 'AI Lab Whiteboard',
    tint: 'from-indigo-500/30 via-purple-500/20 to-sky-500/20',
    description: 'Handwritten workflow sketch with data arrows',
  },
  {
    id: 'diagram',
    title: 'Edge Topology Diagram',
    tint: 'from-emerald-500/20 via-teal-500/10 to-blue-500/10',
    description: 'Vector blueprint exported from Tkinter tab',
  },
  {
    id: 'notes',
    title: 'Research Notes',
    tint: 'from-amber-400/30 via-orange-500/10 to-rose-500/10',
    description: 'OCR friendly screenshot of meta notes',
  },
]

const fetchStats = async (): Promise<VisionStats> => {
  const { data } = await apiClient.get<VisionStats>(apiPath('computer-vision/stats'))
  return data
}

const fileToDataURL = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })

export default function ComputerVision() {
  const [payload, setPayload] = useState<FilePayload | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [ocr, setOcr] = useState<OCRResult | null>(null)
  const [detections, setDetections] = useState<DetectionResult | null>(null)

  const statsQuery = useQuery({
    queryKey: ['cv-stats'],
    queryFn: fetchStats,
    refetchInterval: 60000,
  })

  const analyzeMutation = useMutation({
    mutationFn: async () => {
      if (!payload) throw new Error('Select or upload an image first')
      const { data } = await apiClient.post<AnalysisResult>(apiPath('computer-vision/analyze'), payload)
      return data
    },
    onSuccess: (data) => {
      setAnalysis(data)
      toast.success('Analysis complete')
    },
    onError: (error: any) => {
      toast.error(error?.message ?? 'Unable to analyze image')
    },
  })

  const ocrMutation = useMutation({
    mutationFn: async () => {
      if (!payload) throw new Error('Select or upload an image first')
      const { data } = await apiClient.post<OCRResult>(apiPath('computer-vision/ocr'), payload)
      return data
    },
    onSuccess: (data) => {
      setOcr(data)
      toast.success('OCR finished')
    },
    onError: (error: any) => toast.error(error?.message ?? 'OCR request failed'),
  })

  const detectMutation = useMutation({
    mutationFn: async () => {
      if (!payload) throw new Error('Select or upload an image first')
      const { data } = await apiClient.post<DetectionResult>(apiPath('computer-vision/detect'), payload)
      return data
    },
    onSuccess: (data) => {
      setDetections(data)
      toast.success('Detection complete')
    },
    onError: (error: any) => toast.error(error?.message ?? 'Detection request failed'),
  })

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    const data_url = await fileToDataURL(file)
    setPayload({ filename: file.name, content_type: file.type, data_url })
    setAnalysis(null)
    setOcr(null)
    setDetections(null)
  }

  const handleSample = (sampleId: string) => {
    const sample = sampleImages.find((item) => item.id === sampleId)
    if (!sample) return
    setPayload({
      filename: `${sample.title.replace(/\s+/g, '_').toLowerCase()}.png`,
      content_type: 'image/png',
      data_url: `sample://${sample.id}`,
    })
    setAnalysis(null)
    setOcr(null)
    setDetections(null)
  }

  const busy = analyzeMutation.isPending || ocrMutation.isPending || detectMutation.isPending

  const detectionBadges = useMemo(() => {
    if (!detections) return []
    return detections.objects.map((obj) => ({
      label: obj.label,
      confidence: `${Math.round(obj.confidence * 100)}%`,
    }))
  }, [detections])

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Computer Vision</p>
          <h2 className="text-3xl font-semibold text-white">Multimodal Intelligence Console</h2>
          <p className="text-slate-300 max-w-2xl">
            Shared React/Electron interface for whiteboards, diagrams, and OCR — styled with the Tkinter-inspired neon
            glass aesthetic.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => analyzeMutation.mutate()}
            disabled={busy}
            className="cv-btn cv-btn-primary"
          >
            <ScanLine className="w-4 h-4 mr-2" />
            Analyze Image
          </button>
          <button onClick={() => ocrMutation.mutate()} disabled={busy} className="cv-btn cv-btn-ghost">
            <Type className="w-4 h-4 mr-2" />
            Run OCR
          </button>
          <button onClick={() => detectMutation.mutate()} disabled={busy} className="cv-btn cv-btn-ghost">
            <Crosshair className="w-4 h-4 mr-2" />
            Detect Objects
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 glass-panel p-5">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
            <UploadCloud className="w-5 h-5 text-accent" />
            Input Source
          </h3>
          <label className="theme-upload">
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <span>{payload?.filename ?? 'Drag & drop or browse image'}</span>
          </label>
          <div className="mt-6 space-y-3">
            <p className="text-sm text-slate-300 uppercase tracking-[0.3em]">Samples</p>
            <div className="grid grid-cols-1 gap-3">
              {sampleImages.map((sample) => (
                <button
                  key={sample.id}
                  className={`sample-card bg-gradient-to-r ${sample.tint} ${
                    payload?.filename?.includes(sample.id) ? 'ring-2 ring-accent' : ''
                  }`}
                  onClick={() => handleSample(sample.id)}
                >
                  <div>
                    <p className="font-semibold">{sample.title}</p>
                    <p className="text-xs text-slate-200/80">{sample.description}</p>
                  </div>
                  <ImageIcon className="w-5 h-5 text-white/70" />
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-accent" />
                Analysis
              </h3>
              {analysis && (
                <span className="pill">
                  Confidence {Math.round(analysis.confidence * 100)}% · {analysis.labels.join(', ')}
                </span>
              )}
            </div>
            {analysis ? (
              <div className="space-y-4 text-slate-100">
                <p>{analysis.summary}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.highlights.map((highlight) => (
                    <div key={highlight} className="highlight-card">
                      {highlight}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-400">
                  Generated {new Date(analysis.generated_at).toLocaleString()}
                </p>
              </div>
            ) : (
              <p className="text-slate-400 text-sm">Trigger an analysis to view insights.</p>
            )}
          </div>

          <div className="glass-panel p-5 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                <Type className="w-4 h-4 text-accent" />
                OCR
              </h4>
              {ocr ? (
                <div className="space-y-2 text-slate-100">
                  <pre className="bg-slate-900/60 rounded-lg p-3 text-xs leading-relaxed">{ocr.text}</pre>
                  <p className="text-xs text-slate-400">
                    {ocr.language.toUpperCase()} · {ocr.word_count} words
                  </p>
                </div>
              ) : (
                <p className="text-slate-400 text-sm">Run OCR to extract text.</p>
              )}
            </div>
            <div>
              <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-accent" />
                Detections
              </h4>
              {detectionBadges.length ? (
                <div className="flex flex-wrap gap-2">
                  {detectionBadges.map((badge) => (
                    <span key={badge.label} className="pill">
                      {badge.label} · {badge.confidence}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-slate-400 text-sm">Detect objects to view bounding boxes.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {statsQuery.data && (
        <div className="glass-panel p-5">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-slate-100 text-sm">
            <div>
              <p className="text-slate-400 uppercase tracking-[0.3em] text-xs">Documents</p>
              <p className="text-2xl font-semibold">{statsQuery.data.documents_processed_today}</p>
              <p className="text-slate-500 text-xs">Processed today</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase tracking-[0.3em] text-xs">Latency</p>
              <p className="text-2xl font-semibold">{statsQuery.data.avg_latency_ms} ms</p>
              <p className="text-slate-500 text-xs">Average pipeline latency</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase tracking-[0.3em] text-xs">Models</p>
              <p>{statsQuery.data.active_models.join(', ')}</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase tracking-[0.3em] text-xs">Updated</p>
              <p>{new Date(statsQuery.data.last_model_update).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
