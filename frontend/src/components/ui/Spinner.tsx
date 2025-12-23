import { Loader2 } from 'lucide-react'
import { cn } from '../../shared/utils'

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  text?: string
}

export default function Spinner({ size = 'md', className, text }: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  }
  
  return (
    <div className={cn('flex flex-col items-center justify-center', className)}>
      <Loader2 className={cn('animate-spin text-blue-600', sizes[size])} />
      {text && <p className="mt-2 text-sm text-gray-600">{text}</p>}
    </div>
  )
}


