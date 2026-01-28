import { ReactNode } from 'react'
import { FileX } from 'lucide-react'
import Spinner from './Spinner'
import Alert from './Alert'
import EmptyState from '../EmptyState'

export interface PageWrapperProps {
  isLoading?: boolean
  error?: Error | string | null
  isEmpty?: boolean
  emptyTitle?: string
  emptyDescription?: string
  emptyAction?: ReactNode
  children: ReactNode
  loadingText?: string
}

/**
 * PageWrapper - Unified wrapper for pages with loading, error, and empty states
 * Improves UX by providing consistent states across all pages
 */
export default function PageWrapper({
  isLoading = false,
  error = null,
  isEmpty = false,
  emptyTitle = 'No data available',
  emptyDescription = 'There is no data to display at this time.',
  emptyAction,
  children,
  loadingText = 'Loading...',
}: PageWrapperProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size="lg" text={loadingText} />
      </div>
    )
  }

  if (error) {
    const errorMessage = typeof error === 'string' ? error : error?.message || 'An error occurred'
    return (
      <div className="p-4">
        <Alert variant="error" title="Error">
          {errorMessage}
        </Alert>
      </div>
    )
  }

  if (isEmpty) {
    return (
      <EmptyState
        icon={FileX}
        title={emptyTitle}
        description={emptyDescription}
        action={emptyAction}
      />
    )
  }

  return <>{children}</>
}

