import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { attachRuntimeDiagnostics, recordRuntimeDiagnostic } from './utils/runtimeDiagnostics'
import './index.css'

attachRuntimeDiagnostics()
recordRuntimeDiagnostic('Bootstrapping React tree', 'main.tsx')

const rootElement = document.getElementById('root')
if (!rootElement) {
  recordRuntimeDiagnostic('Root element #root not found', 'main.tsx')
  throw new Error('Root element #root not found')
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

recordRuntimeDiagnostic('React tree mounted', 'main.tsx')
