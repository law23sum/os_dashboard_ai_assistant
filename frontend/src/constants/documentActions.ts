import {
  FileText,
  ClipboardList,
  Table,
  Wand2,
  type LucideIcon,
} from 'lucide-react'

export interface QuickAction {
  id: string
  label: string
  description: string
  prompt: string
  icon: LucideIcon
}

export const QUICK_ACTIONS: QuickAction[] = [
  {
    id: 'summary',
    label: 'Executive summary',
    description: '3-sentence overview focusing on decisions, risks, and owners.',
    prompt:
      'Summarize the document in three concise sentences that highlight the decision, owner, and any risks.',
    icon: FileText,
  },
  {
    id: 'actions',
    label: 'Action checklist',
    description: 'List the top tasks with owners and suggested deadlines.',
    prompt:
      'Identify up to three concrete action items from this document. Include the owner, desired outcome, and a reasonable due date.',
    icon: ClipboardList,
  },
  {
    id: 'metrics',
    label: 'Key metrics',
    description: 'Surface KPIs or numbers worth tracking in chat.',
    prompt:
      'Extract any metrics, KPIs, or quantified statements from the document and format them as a short bulleted list.',
    icon: Table,
  },
  {
    id: 'brief',
    label: 'Meeting brief',
    description: 'Draft a short update Chris can drop into chat.',
    prompt:
      'Write a short (under 120 words) meeting brief that includes context, current status, blockers, and a clear ask.',
    icon: Wand2,
  },
]








