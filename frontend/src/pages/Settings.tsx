import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  Bell,
  CheckSquare,
  Database,
  FolderKanban,
  LayoutDashboard,
  Monitor,
  Save,
  ShieldCheck,
  SlidersHorizontal,
} from 'lucide-react'
import type { ReactNode } from 'react'
import { useMemo, useState } from 'react'
import { toast } from '../utils/toast'
import type {
  ChangePermissionMode,
  ContinuityMode,
  RiskAppetite,
  Settings as SettingsType,
} from '../types'
import { updateSettings as updateSettingsRequest } from '../api/settings'
import { useAppSettings } from '../hooks/useSettings'
import { availableThemes, describeTheme } from '../theme'

const viewOptions = [
  {
    value: 'dashboard',
    label: 'Mission Control',
    description: 'Cross-plane telemetry, health, and Capsules at a glance.',
    icon: LayoutDashboard,
  },
  {
    value: 'tasks',
    label: 'Task Flow',
    description: 'Prioritize execution sequences and dependency chains.',
    icon: CheckSquare,
  },
  {
    value: 'projects',
    label: 'Master Stack',
    description: 'Roadmaps, milestones, and Capsule phase gates.',
    icon: FolderKanban,
  },
]

const fontScaleOptions = [
  { value: 'small', label: 'Dense Grid', description: 'Compact typography for dashboards and planners.' },
  { value: 'medium', label: 'Balanced', description: 'Default scale tuned for both desktop and browser.' },
  { value: 'large', label: 'Reading Mode', description: 'Comfort-first scale for reports and docs.' },
]

const permissionModes: Array<{
  value: ChangePermissionMode
  label: string
  description: string
  emphasis: string
}> = [
  {
    value: 'auto',
    label: 'Auto · Trusted',
    description: 'Allow Capsules to self-heal and remediate without extra prompts.',
    emphasis: 'bg-emerald-500/15 text-emerald-200',
  },
  {
    value: 'ask',
    label: 'Always Ask',
    description: 'Require explicit confirmation before altering external systems.',
    emphasis: 'bg-amber-500/15 text-amber-200',
  },
  {
    value: 'ask_when_unsure',
    label: 'Ask When Unsure',
    description: 'Default guardrail — automation proceeds when evidence quality is high.',
    emphasis: 'bg-indigo-500/15 text-indigo-200',
  },
]

const continuityModes: Array<{
  value: ContinuityMode
  label: string
  description: string
  tone: string
}> = [
  {
    value: 'full',
    label: 'Full Continuity',
    description: 'Normal operating conditions with automation and write paths enabled.',
    tone: 'from-sky-500/90 via-indigo-500/80 to-purple-500/80',
  },
  {
    value: 'automation-off',
    label: 'Automation-Off',
    description: 'Suggest and plan only; drivers remain read-only pending review.',
    tone: 'from-amber-500/80 via-orange-500/70 to-rose-500/70',
  },
  {
    value: 'read-only',
    label: 'Read-Only',
    description: 'Ledger + CIR stay visible while containment or recovery is underway.',
    tone: 'from-slate-600/70 via-slate-700/70 to-slate-800/70',
  },
]

const riskAppetiteOptions: Array<{
  value: RiskAppetite
  label: string
  detail: string
}> = [
  { value: 'conservative', label: 'Conservative', detail: 'Maximum approvals, smallest automation radius.' },
  { value: 'balanced', label: 'Balanced', detail: 'Default profile; bounded risk aligned with Section 14.' },
  { value: 'progressive', label: 'Progressive', detail: 'Fewer prompts for trusted tenants & Capsules.' },
]

const preferenceMetadata: Record<
  string,
  { title: string; description: string; icon: typeof Database | typeof Bell | typeof Activity | typeof Monitor }
> = {
  notes: {
    title: 'Notes / Memory',
    description: 'Capture Notebook capsules and keep Ledger context warm.',
    icon: Monitor,
  },
  calendar: {
    title: 'Calendar / Cadence',
    description: 'Sync meetings to drive Capsule planning and resourcing.',
    icon: Activity,
  },
  mail: {
    title: 'Mail / Signals',
    description: 'Enable inbox parsing for incidents and regulator escalations.',
    icon: Bell,
  },
  files: {
    title: 'Files / Artifacts',
    description: 'Watch file systems for Capsule-ready source documents.',
    icon: Database,
  },
}

const resiliencePrinciples = [
  {
    title: 'Fail visibly',
    detail: 'System status banners stay latched to the chrome when telemetry is enabled.',
  },
  {
    title: 'Fail bounded',
    detail: 'Continuity modes scope automation per tenant, per workspace, per Capsule.',
  },
  {
    title: 'Fail explainably',
    detail: 'Evidence Packs stitch Ledger, Logbook, and Capsule provenance automatically.',
  },
  {
    title: 'Fail forward',
    detail: 'HyperDaemon ingests every incident to improve guardrails and Capsule criteria.',
  },
]

const quickActions = [
  {
    label: 'Temporal Backtest',
    description: 'Replay last incident with updated policies to validate fixes.',
    tone: 'from-sky-400/80 to-indigo-500/80',
  },
  {
    label: 'Generate Evidence Pack',
    description: 'Compile Ledger slices + telemetry for regulators or AI Court.',
    tone: 'from-emerald-400/80 to-cyan-400/80',
  },
  {
    label: 'Risk Re-Score',
    description: 'Refresh workspace risk posture against current failures + drift.',
    tone: 'from-amber-400/80 to-orange-500/80',
  },
  {
    label: 'Chaos Drill',
    description: 'Simulate driver outage and capture Capsule-specific runbooks.',
    tone: 'from-rose-400/80 to-red-500/80',
  },
]

interface SettingPanelProps {
  title: string
  description: string
  icon?: ReactNode
  children: ReactNode
}

function SettingPanel({ title, description, icon, children }: SettingPanelProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/85 p-6 shadow-2xl shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 dark:border-white/5 dark:bg-slate-900/70">
      <div className="mb-4 flex items-center gap-3">
        {icon && <div className="text-indigo-300">{icon}</div>}
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">{description}</p>
        </div>
      </div>
      {children}
    </section>
  )
}

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const { data: settings, isLoading } = useAppSettings()
  const [localSettings, setLocalSettings] = useState<SettingsType | null>(null)

  const updateMutation = useMutation({
    mutationFn: updateSettingsRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      toast.success('Settings saved successfully')
      setLocalSettings(null)
    },
    onError: (error) => {
      toast.error(`Failed to save settings: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  if (isLoading || !settings) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-indigo-400" />
      </div>
    )
  }

  const currentSettings = localSettings || settings
  const defaultView = viewOptions.find((option) => option.value === currentSettings.default_view) ?? viewOptions[0]
  const policyMode =
    permissionModes.find((option) => option.value === (currentSettings.change_permission_mode ?? 'ask_when_unsure')) ??
    permissionModes[2]
  const continuityMode: ContinuityMode = currentSettings.continuity_mode && continuityModes.some((mode) => mode.value === currentSettings.continuity_mode)
    ? (currentSettings.continuity_mode as ContinuityMode)
    : 'full'
  const riskAppetite: RiskAppetite =
    currentSettings.risk_appetite && riskAppetiteOptions.some((option) => option.value === currentSettings.risk_appetite)
      ? (currentSettings.risk_appetite as RiskAppetite)
      : 'balanced'

  const heroStats = useMemo(
    () => [
      {
        label: 'Experience Layer',
        value: describeTheme(currentSettings.theme),
        detail: 'Shared gradients for browser + desktop packaging.',
      },
      {
        label: 'Default View',
        value: defaultView.label,
        detail: defaultView.description,
      },
      {
        label: 'Telemetry',
        value: currentSettings.show_system_status ? 'Visible' : 'Muted',
        detail: currentSettings.show_system_status
          ? 'Section 14 principle satisfied — fail visibly.'
          : 'Enable sensors to surface health + risk banners.',
      },
      {
        label: 'Policy Mode',
        value: policyMode.label,
        detail: policyMode.description,
      },
    ],
    [currentSettings.show_system_status, currentSettings.theme, defaultView, policyMode],
  )

  const handleChange = (key: keyof SettingsType, value: unknown) => {
    setLocalSettings((prev) => ({
      ...(prev || settings),
      [key]: value,
    }))
  }

  const handleDataPreferenceChange = (key: string, checked: boolean) => {
    handleChange('data_preferences', {
      ...currentSettings.data_preferences,
      [key]: checked,
    })
  }

  const handleQuickAction = (label: string) => {
    toast.info(`${label} scheduled — check Ledger for the Evidence Pack once it completes.`)
  }

  const hasPendingChanges = Boolean(localSettings)

  return (
    <div className="space-y-8 px-4 py-8 text-slate-900 dark:text-slate-100">
      <header className="rounded-3xl bg-gradient-to-r from-indigo-500 via-purple-500 to-sky-500 p-8 text-white shadow-2xl shadow-indigo-500/25">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-white/70">Policy · Controls · Preferences</p>
            <h1 className="mt-2 text-3xl font-bold">Operating Envelope Settings</h1>
            <p className="mt-2 max-w-3xl text-sm text-white/80">
              Tune how the OS Dashboard AI Assistant behaves across desktop and browser launches — enforce continuity
              modes, theme parity, Capsule permissions, and data feeds without fragmenting the code path.
            </p>
          </div>
          {hasPendingChanges && (
            <button
              onClick={() => localSettings && updateMutation.mutate(localSettings)}
              disabled={updateMutation.isPending}
              className="inline-flex items-center rounded-full bg-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/25 disabled:opacity-50"
            >
              <Save className="mr-2 h-4 w-4" />
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          )}
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {heroStats.map((stat) => (
            <div key={stat.label} className="rounded-2xl bg-white/10 p-4 backdrop-blur">
              <p className="text-xs uppercase tracking-wide text-white/70">{stat.label}</p>
              <p className="mt-2 text-xl font-semibold">{stat.value}</p>
              <p className="mt-2 text-xs text-white/80">{stat.detail}</p>
            </div>
          ))}
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <SettingPanel
          title="Experience & Presentation"
          description="Align theme, typography, and landing surfaces so web + desktop stay visually consistent."
          icon={<Monitor className="h-5 w-5" />}
        >
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Theme tokens</p>
            <div className="mt-3 grid gap-3 sm:grid-cols-3">
              {availableThemes.map((themeName) => {
                const active = currentSettings.theme === themeName
                return (
                  <button
                    type="button"
                    key={themeName}
                    onClick={() => handleChange('theme', themeName)}
                    className={`rounded-2xl border p-4 text-left shadow-sm transition ${
                      active
                        ? 'border-indigo-400 bg-gradient-to-r from-indigo-500/90 to-sky-500/80 text-white'
                        : 'border-slate-200 bg-white/70 text-slate-800 hover:border-indigo-200 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-100'
                    }`}
                  >
                    <p className="text-sm font-semibold">{describeTheme(themeName)}</p>
                    <p className={`mt-1 text-xs ${active ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'}`}>
                      Mirrors Tkinter palettes · {themeName}
                    </p>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Default view</p>
              <div className="mt-3 space-y-3">
                {viewOptions.map((option) => {
                  const Icon = option.icon
                  const active = currentSettings.default_view === option.value
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => handleChange('default_view', option.value)}
                      className={`flex w-full items-start gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                        active
                          ? 'border-indigo-400 bg-gradient-to-r from-indigo-500/90 to-purple-500/70 text-white'
                          : 'border-slate-200 bg-white/60 hover:border-indigo-200 dark:border-slate-800 dark:bg-slate-900/60'
                      }`}
                    >
                      <span
                        className={`rounded-full p-2 ${
                          active ? 'bg-white/20 text-white' : 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-200'
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                      </span>
                      <div>
                        <p className="text-sm font-semibold">{option.label}</p>
                        <p className={`text-xs ${active ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'}`}>
                          {option.description}
                        </p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Font scale</p>
              <div className="mt-3 grid gap-3">
                {fontScaleOptions.map((option) => {
                  const active = currentSettings.font_scale === option.value
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => handleChange('font_scale', option.value)}
                      className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                        active
                          ? 'border-indigo-400 bg-gradient-to-r from-sky-500/80 to-indigo-500/80 text-white'
                          : 'border-slate-200 bg-white/70 hover:border-indigo-200 dark:border-slate-800 dark:bg-slate-900/60'
                      }`}
                    >
                      <p className="text-sm font-semibold capitalize">{option.label}</p>
                      <p className={`text-xs ${active ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'}`}>
                        {option.description}
                      </p>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        </SettingPanel>

        <SettingPanel
          title="Policy Engine & Automation"
          description="Govern Capsule automation depth, telemetry visibility, and approvals per Section 14."
          icon={<ShieldCheck className="h-5 w-5" />}
        >
          <div className="grid gap-3 lg:grid-cols-3">
            {permissionModes.map((mode) => {
              const active = (currentSettings.change_permission_mode ?? 'ask_when_unsure') === mode.value
              return (
                <button
                  key={mode.value}
                  type="button"
                  onClick={() => handleChange('change_permission_mode', mode.value)}
                  className={`flex h-full flex-col rounded-2xl border p-4 text-left transition ${
                    active
                      ? 'border-emerald-300 bg-slate-900 text-white'
                      : 'border-slate-200 bg-white/80 hover:border-emerald-200 dark:border-slate-800 dark:bg-slate-900/60'
                  }`}
                >
                  <span className={`inline-flex w-fit rounded-full px-3 py-1 text-xs ${mode.emphasis}`}>
                    {mode.label}
                  </span>
                  <p className={`mt-2 text-sm ${active ? 'text-slate-100' : 'text-slate-600 dark:text-slate-300'}`}>
                    {mode.description}
                  </p>
                </button>
              )
            })}
          </div>

          <div className="mt-6 rounded-2xl border border-indigo-100 bg-indigo-50/70 p-4 dark:border-indigo-800/60 dark:bg-indigo-950/40">
            <label className="flex items-start gap-3">
              <span className="mt-1">
                <input
                  type="checkbox"
                  checked={currentSettings.show_system_status}
                  onChange={(e) => handleChange('show_system_status', e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
              </span>
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">Show System Status Banner</p>
                <p className="text-xs text-slate-600 dark:text-slate-300">
                  Keeps the failure-detection strip pinned so every incident is visible to operators and regulators.
                </p>
              </div>
            </label>
          </div>
        </SettingPanel>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SettingPanel
          title="Continuity Modes & Risk Appetite"
          description="Express how aggressive the assistant can be when recovering, containing, or simulating failures."
          icon={<SlidersHorizontal className="h-5 w-5" />}
        >
          <div className="grid gap-3 sm:grid-cols-3">
            {continuityModes.map((mode) => {
              const active = continuityMode === mode.value
              return (
                <button
                  key={mode.value}
                  type="button"
                  onClick={() => handleChange('continuity_mode', mode.value)}
                  className={`rounded-2xl border p-4 text-left transition ${
                    active
                      ? `border-transparent bg-gradient-to-r ${mode.tone} text-white`
                      : 'border-slate-200 bg-white/70 hover:border-indigo-200 dark:border-slate-800 dark:bg-slate-900/60'
                  }`}
                >
                  <p className="text-sm font-semibold">{mode.label}</p>
                  <p className={`text-xs ${active ? 'text-white/80' : 'text-slate-500 dark:text-slate-400'}`}>
                    {mode.description}
                  </p>
                </button>
              )
            })}
          </div>

          <div className="mt-6">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Risk appetite</p>
            <div className="mt-3 flex flex-wrap gap-3">
              {riskAppetiteOptions.map((option) => {
                const active = riskAppetite === option.value
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleChange('risk_appetite', option.value)}
                    className={`rounded-full px-4 py-2 text-sm transition ${
                      active
                        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                        : 'bg-slate-200/70 text-slate-600 hover:bg-slate-300 dark:bg-slate-800 dark:text-slate-200'
                    }`}
                  >
                    {option.label}
                  </button>
                )
              })}
            </div>
            <p className="mt-2 text-xs text-slate-500 dark:text-slate-300">
              {riskAppetiteOptions.find((option) => option.value === riskAppetite)?.detail}
            </p>
          </div>

          <ul className="mt-6 space-y-3 rounded-2xl border border-slate-200 bg-white/60 p-4 text-sm dark:border-slate-800 dark:bg-slate-900/60">
            {resiliencePrinciples.map((principle) => (
              <li key={principle.title} className="flex items-start gap-3">
                <ShieldCheck className="mt-1 h-4 w-4 text-indigo-500" />
                <div>
                  <p className="font-semibold">{principle.title}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-300">{principle.detail}</p>
                </div>
              </li>
            ))}
          </ul>
        </SettingPanel>

        <SettingPanel
          title="Data Preferences & Evidence"
          description="Control which data sources feed Capsules, Ledger, and HyperDaemon."
          icon={<Database className="h-5 w-5" />}
        >
          <div className="space-y-4">
            {Object.entries(currentSettings.data_preferences || {}).map(([key, value]) => {
              const metadata = preferenceMetadata[key] ?? {
                title: key,
                description: 'Data stream toggle',
                icon: Database,
              }
              const Icon = metadata.icon
              return (
                <div
                  key={key}
                  className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white/70 px-4 py-3 dark:border-slate-800 dark:bg-slate-900/60"
                >
                  <div className="flex items-center gap-3">
                    <span className="rounded-full bg-indigo-100/80 p-2 text-indigo-600 dark:bg-slate-800 dark:text-indigo-300">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div>
                      <p className="text-sm font-semibold capitalize">{metadata.title}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-300">{metadata.description}</p>
                    </div>
                  </div>
                  <label className="inline-flex cursor-pointer items-center gap-2 text-xs font-semibold uppercase tracking-wide">
                    <span className="text-slate-400 dark:text-slate-500">Off</span>
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => handleDataPreferenceChange(key, e.target.checked)}
                      className="peer sr-only"
                    />
                    <span className="relative inline-flex h-6 w-11 items-center rounded-full bg-slate-300 transition peer-checked:bg-indigo-500">
                      <span className="inline-block h-4 w-4 rounded-full bg-white transition peer-checked:translate-x-5" />
                    </span>
                    <span className="text-indigo-500">On</span>
                  </label>
                </div>
              )
            })}
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50/70 p-4 text-sm text-emerald-900 dark:border-emerald-700/50 dark:bg-emerald-900/30 dark:text-emerald-200">
              <p className="font-semibold">Ledger Integrity</p>
              <p className="mt-1 text-xs">
                Hash-chain verification + Merkle anchoring keep every Capsule change provable for regulators.
              </p>
            </div>
            <div className="rounded-2xl border border-rose-200 bg-rose-50/70 p-4 text-sm text-rose-900 dark:border-rose-700/50 dark:bg-rose-900/30 dark:text-rose-200">
              <p className="font-semibold">Corruption Playbooks</p>
              <p className="mt-1 text-xs">
                On detection, segments are quarantined, tagged, and reconstructed with Evidence Packs automatically.
              </p>
            </div>
          </div>
        </SettingPanel>
      </div>

      <SettingPanel
        title="Resilience Capsules & Quick Actions"
        description="Kick off continuity drills, evidence packs, or risk scoring runs directly from settings."
        icon={<Activity className="h-5 w-5" />}
      >
        <div className="grid gap-4 md:grid-cols-2">
          {quickActions.map((action) => (
            <button
              key={action.label}
              type="button"
              onClick={() => handleQuickAction(action.label)}
              className={`rounded-2xl border border-white/30 bg-gradient-to-r ${action.tone} p-5 text-left text-white shadow-lg shadow-slate-900/15 transition hover:-translate-y-0.5`}
            >
              <p className="text-sm font-semibold">{action.label}</p>
              <p className="text-xs text-white/80">{action.description}</p>
            </button>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3 text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
          <span className="rounded-full bg-slate-200/70 px-3 py-1 dark:bg-slate-800">observability</span>
          <span className="rounded-full bg-slate-200/70 px-3 py-1 dark:bg-slate-800">policy</span>
          <span className="rounded-full bg-slate-200/70 px-3 py-1 dark:bg-slate-800">ledger</span>
          <span className="rounded-full bg-slate-200/70 px-3 py-1 dark:bg-slate-800">hyperdaemon</span>
        </div>
      </SettingPanel>
    </div>
  )
}
