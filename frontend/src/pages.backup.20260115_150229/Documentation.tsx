import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowUpRight, ExternalLink } from 'lucide-react'
import { getDocEntry, parityMeta, sourceLabel } from '../data/docManifest'

interface DocumentationPageProps {
  page?: string
}

const resolveHtmlHref = (slug: string, explicit?: string) => {
  if (explicit) return explicit
  if (slug.includes('.')) return `/docs/${slug}`
  return `/docs/${slug}.html`
}

const escapeHtml = (value: string) =>
  value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const escapeAttribute = (value: string) => escapeHtml(value).replace(/"/g, '&quot;')

const formatInline = (value: string) => {
  let output = escapeHtml(value)
  output = output.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, url) => {
    return `<a href="${escapeAttribute(url)}" target="_blank" rel="noreferrer">${label}</a>`
  })
  output = output.replace(/`([^`]+)`/g, (_, code) => `<code>${code}</code>`)
  output = output.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  output = output.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  return output
}

const renderMarkdownTable = (rows: string[]) => {
  const cleanRow = (line: string) =>
    line
      .trim()
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map((cell) => formatInline(cell.trim()))

  if (rows.length < 2) {
    return `<p>${formatInline(rows.join(' '))}</p>`
  }
  const header = cleanRow(rows[0])
  const body = rows.slice(2).map(cleanRow)

  const headerHtml = header.map((cell) => `<th class="px-3 py-2 text-left font-semibold">${cell}</th>`).join('')
  const bodyHtml = body
    .map(
      (row) =>
        `<tr class="border-t border-white/10">${row
          .map((cell) => `<td class="px-3 py-2 align-top">${cell}</td>`)
          .join('')}</tr>`,
    )
    .join('')
  return `<table class="w-full text-sm text-slate-200 border border-white/10 rounded-xl overflow-hidden my-4"><thead class="bg-white/5"><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table>`
}

const markdownToHtml = (markdown: string): string => {
  const lines = markdown.split(/\r?\n/)
  const html: string[] = []
  let inList = false
  let listType: 'ul' | 'ol' = 'ul'
  let inCode = false
  let codeLang = ''
  const codeBuffer: string[] = []

  const closeList = () => {
    if (inList) {
      html.push(`</${listType}>`)
      inList = false
    }
  }

  const closeCode = () => {
    if (inCode) {
      const langAttr = codeLang ? ` class="language-${codeLang}"` : ''
      html.push(`<pre><code${langAttr}>${escapeHtml(codeBuffer.join('\n'))}</code></pre>`)
      inCode = false
      codeLang = ''
      codeBuffer.length = 0
    }
  }

  for (let i = 0; i < lines.length; i += 1) {
    const raw = lines[i]
    const line = raw.trim()

    if (line.startsWith('```')) {
      if (inCode) {
        closeCode()
      } else {
        closeList()
        inCode = true
        codeLang = line.replace(/```/, '').trim()
      }
      continue
    }

    if (inCode) {
      codeBuffer.push(raw)
      continue
    }

    if (!line) {
      closeList()
      continue
    }

    if (/^\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
      const tableLines = [lines[i]]
      i += 1
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i])
        i += 1
      }
      i -= 1
      closeList()
      html.push(renderMarkdownTable(tableLines))
      continue
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/)
    if (headingMatch) {
      closeList()
      const level = Math.min(6, headingMatch[1].length)
      html.push(`<h${level}>${formatInline(headingMatch[2])}</h${level}>`)
      continue
    }

    if (/^>/.test(line)) {
      closeList()
      html.push(`<blockquote>${formatInline(line.replace(/^>\s?/, ''))}</blockquote>`)
      continue
    }

    if (/^(-{3,}|_{3,}|\*{3,})$/.test(line)) {
      closeList()
      html.push('<hr />')
      continue
    }

    const listMatch = line.match(/^(\*|-|\d+\.)\s+(.*)/)
    if (listMatch) {
      const nextType: 'ul' | 'ol' = /\d+\./.test(listMatch[1]) ? 'ol' : 'ul'
      if (!inList || nextType !== listType) {
        closeList()
        inList = true
        listType = nextType
        html.push(`<${listType}>`)
      }
      html.push(`<li>${formatInline(listMatch[2])}</li>`)
      continue
    }

    closeList()
    html.push(`<p>${formatInline(line)}</p>`)
  }

  closeList()
  closeCode()
  return html.join('\n')
}

export default function Documentation({ page: propPage }: DocumentationPageProps) {
  const { page: paramPage } = useParams<{ page?: string }>()
  const pageName = propPage || paramPage || 'index'
  const entry = getDocEntry(pageName)
  const htmlHref = resolveHtmlHref(pageName, entry?.href)
  const isMarkdown = htmlHref.endsWith('.md') || (entry?.path?.endsWith('.md') ?? false)

  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadPage = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(htmlHref)
        if (!response.ok) {
          throw new Error(`Failed to load ${htmlHref}`)
        }
        const text = await response.text()
        setContent(isMarkdown ? markdownToHtml(text) : text)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load documentation')
      } finally {
        setLoading(false)
      }
    }
    loadPage()
  }, [htmlHref, isMarkdown])

  const parity = entry ? parityMeta[entry.parity] : null

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="eyebrow-text">Documentation</p>
            <h1 className="text-3xl font-semibold text-white">{entry?.title ?? pageName}</h1>
            <p className="mt-2 text-sm text-slate-300">
              {entry?.description ?? 'Legacy HTML preserved from the Tkinter era.'}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            {entry && (
              <span className="rounded-full border border-white/20 px-3 py-1 text-slate-200">
                {sourceLabel[entry.source]}
              </span>
            )}
            {parity && (
              <span className={`rounded-full border px-3 py-1 text-slate-100 ${parity.chipClass}`}>
                {parity.label}
              </span>
            )}
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <Link
            to="/docs"
            className="inline-flex items-center rounded-xl border border-white/10 px-4 py-2 text-white hover:border-white/30"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to list
          </Link>
          <a
            href={htmlHref}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center rounded-xl border border-white/10 px-4 py-2 text-white hover:border-white/30"
          >
            <ExternalLink className="mr-2 h-4 w-4" />
            Open HTML
          </a>
          {entry?.reactRoute && (
            <Link
              to={entry.reactRoute}
              className="inline-flex items-center rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/20"
            >
              <ArrowUpRight className="mr-2 h-4 w-4" />
              {entry.reactLabel || 'Open React Surface'}
            </Link>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white">Legacy HTML</h2>
          <p className="text-sm text-slate-300">Direct render of {htmlHref}.</p>
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
            {loading && <p className="text-sm text-slate-400">Loading legacy HTML…</p>}
            {error && (
              <p className="text-sm text-rose-300">
                {error}. Confirm the file exists under <code>/docs/</code>.
              </p>
            )}
            {!loading && !error && (
              <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: content }} />
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white">React Equivalent</h2>
          <p className="text-sm text-slate-300">Embeds the modern route so you can confirm parity at a glance.</p>
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/30">
            {entry?.reactRoute ? (
              <iframe src={entry.reactRoute} title="React Preview" className="h-[600px] w-full rounded-2xl border-0" />
            ) : (
              <div className="p-6 text-sm text-slate-300">
                No React route wired yet. Track this item in <Link className="text-blue-300 underline" to="/docs/tk_to_react_mapping.md">Tk → React Mapping</Link>.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
