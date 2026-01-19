import { useState } from 'react'

const environmentOptions = [
  {
    id: 'local',
    label: 'Local',
    detail: 'Developer workstation or container.',
  },
  {
    id: 'sandbox',
    label: 'Sandbox',
    detail: 'Shared staging environment for validation.',
  },
  {
    id: 'enterprise',
    label: 'Enterprise',
    detail: 'Production-grade controls and governance.',
  },
]

export default function EnvironmentSection() {
  const [environment, setEnvironment] = useState('sandbox')
  const active = environmentOptions.find((option) => option.id === environment)

  return (
    <div className="section" data-page-section="environment">
      <div className="section-header">
        <div>
          <h2>Environment</h2>
          <p className="text-muted">
            Choose where this workspace runs and review the guardrails in effect.
          </p>
        </div>
        <span className="badge">Active: {active?.label ?? 'Sandbox'}</span>
      </div>
      <div className="environment-grid">
        {environmentOptions.map((option) => (
          <label
            key={option.id}
            className={`environment-option${environment === option.id ? ' is-active' : ''}`}
          >
            <input
              type="radio"
              name="environment"
              checked={environment === option.id}
              onChange={() => setEnvironment(option.id)}
            />
            <div className="environment-meta">
              <span className="environment-title">{option.label}</span>
              <span className="text-muted">{option.detail}</span>
            </div>
          </label>
        ))}
      </div>
      <div className="text-muted">
        Selected scope inherits data residency, auth, and observability defaults.
      </div>
    </div>
  )
}
