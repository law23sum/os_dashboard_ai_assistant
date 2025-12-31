import { Building2, User } from 'lucide-react'
import { useActor } from '../contexts/ActorContext'
import type { ActorType } from '../types/actor'

interface ActorSwitchProps {
  compact?: boolean
}

const options: Array<{
  id: ActorType
  label: string
  description: string
  Icon: typeof User
}> = [
  {
    id: 'personal',
    label: 'Personal',
    description: 'Private memory space',
    Icon: User,
  },
  {
    id: 'enterprise',
    label: 'Enterprise',
    description: 'Shared workspace scope',
    Icon: Building2,
  },
]

export default function ActorSwitch({ compact = false }: ActorSwitchProps) {
  const { currentActor, setCurrentActor } = useActor()

  return (
    <div
      className={`inline-flex items-center gap-1 rounded-full border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/70 p-1 ${
        compact ? 'text-xs' : 'text-sm'
      }`}
      role="tablist"
      aria-label="Scope selector"
    >
      {options.map(({ id, label, description, Icon }) => {
        const active = currentActor === id
        return (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={active}
            className={`flex items-center gap-2 rounded-full px-3 py-1.5 transition-all ${
              active
                ? 'bg-[color:var(--osd-accent)] text-white shadow-sm'
                : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]'
            }`}
            onClick={() => setCurrentActor(id)}
            title={description}
          >
            <Icon className="w-4 h-4" />
            <span className="font-medium">{label}</span>
          </button>
        )
      })}
    </div>
  )
}
