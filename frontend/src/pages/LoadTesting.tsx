import { FeaturePageTemplate } from '../components/templates/FeaturePageTemplate'
import { useIARouteContext } from '../navigation/iaContext'
import { API } from '../api'
import { toast } from '../utils/toast'

/**
 * Operations Load testing - Feature Page
 * Route: /operations/load-testing
 */
export default function OperationsLoadtesting() {
  const routeContext = useIARouteContext()
  
  const handleExecute = async (params: Record<string, any>, config?: string, environment?: string) => {
    try {
      const response = await API.testing.loadTesting({
        ...params,
        config,
        environment,
      })
      toast.success('Load testing completed successfully')
      return response
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to execute load testing'
      toast.error(message)
      throw error
    }
  }
  
  const handleSave = async (params: Record<string, any>, config?: string) => {
    try {
      await API.settings.update({
        loadTesting: { params, config },
      })
      toast.success('Configuration saved successfully')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to save configuration'
      toast.error(message)
    }
  }
  
  const handleExport = async (format: 'json' | 'markdown', data: any) => {
    try {
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `load-testing-${Date.now()}.json`
        a.click()
        URL.revokeObjectURL(url)
        toast.success('Exported as JSON')
      } else {
        const markdown = `# Load Testing Results\n\n${JSON.stringify(data, null, 2)}`
        const blob = new Blob([markdown], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `load-testing-${Date.now()}.md`
        a.click()
        URL.revokeObjectURL(url)
        toast.success('Exported as Markdown')
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to export'
      toast.error(message)
    }
  }
  
  return (
    <FeaturePageTemplate
      title="Operations Load testing"
      description="Feature page for Operations Load testing"
      parameters={[
        { name: 'input1', label: 'Input Parameter 1', type: 'text', required: true },
        { name: 'input2', label: 'Input Parameter 2', type: 'number', required: false },
        { name: 'input3', label: 'Input Parameter 3', type: 'select', options: [
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' }
        ]}
      ]}
      configSelector={
        label: 'Configuration Profile',
        options: [
          { id: 'default', name: 'Default' },
          { id: 'custom', name: 'Custom' },
          { id: 'optimized', name: 'Optimized' }
        ]
      }
      onExecute={handleExecute}
      onSave={handleSave}
      onExport={handleExport}
    />
  )
}
