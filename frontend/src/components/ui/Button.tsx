import { ButtonHTMLAttributes, forwardRef } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '../../shared/utils'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'tonal'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled,
      leftIcon,
      rightIcon,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[color:var(--osd-background)] disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none'
    
    const variants = {
      primary: 'bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white hover:opacity-90 hover:shadow-lg hover:shadow-[color:var(--osd-accent)]/30 focus:ring-[color:var(--osd-accent)] active:scale-[0.98]',
      secondary: 'bg-[color:var(--osd-surface)] text-[color:var(--osd-text)] border border-[color:var(--osd-border)] hover:bg-[color:var(--osd-surfaceAlt)] hover:border-[color:var(--osd-accent)]/30 focus:ring-[color:var(--osd-accent)] active:scale-[0.98]',
      outline: 'border-2 border-[color:var(--osd-border)] text-[color:var(--osd-text)] bg-transparent hover:bg-[color:var(--osd-accentSoft)] hover:border-[color:var(--osd-accent)] focus:ring-[color:var(--osd-accent)] active:scale-[0.98]',
      ghost: 'text-[color:var(--osd-text)] hover:bg-[color:var(--osd-accentSoft)] focus:ring-[color:var(--osd-accent)] active:scale-[0.98]',
      danger: 'bg-gradient-to-r from-red-600 to-red-700 text-white hover:opacity-90 hover:shadow-lg hover:shadow-red-500/30 focus:ring-red-500 active:scale-[0.98]',
      tonal: 'bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-accent)] border border-[color:var(--osd-accent)]/20 hover:bg-[color:var(--osd-accentSoft)]/80 hover:border-[color:var(--osd-accent)]/40 focus:ring-[color:var(--osd-accent)] active:scale-[0.98]',
    }
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm rounded-xl',
      md: 'px-4 py-2.5 text-base rounded-xl',
      lg: 'px-6 py-3 text-lg rounded-xl',
    }
    
    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
        {!isLoading && leftIcon && <span className="shrink-0">{leftIcon}</span>}
        {children}
        {!isLoading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
export { Button }


