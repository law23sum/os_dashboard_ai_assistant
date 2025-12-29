import { Bot } from 'lucide-react'
import { NavLink } from 'react-router-dom'

/**
 * Navigation link for Master Orchestrator
 * Add this to the main navigation menu
 */
export function OrchestratorNavLink() {
  return (
    <NavLink
      to="/ai/orchestrator"
      className={({ isActive }) =>
        `flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
          isActive
            ? 'bg-blue-50 text-blue-700 font-medium'
            : 'text-gray-700 hover:bg-gray-100'
        }`
      }
    >
      <Bot className="w-5 h-5" />
      <span>Master Orchestrator</span>
    </NavLink>
  )
}

export default OrchestratorNavLink
