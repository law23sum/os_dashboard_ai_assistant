/**
 * Example: Updated Projects page using new API service and UI components
 * This demonstrates best practices for connecting frontend to backend
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, RefreshCw, Edit, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { toast } from '../utils/toast'
import api from '../services/api'
import PageWrapper from '../components/ui/PageWrapper'
import Button from '../components/ui/Button'
import Card, { CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/Card'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'
import Alert from '../components/ui/Alert'
import type { Project } from '../types'

export default function Projects() {
  const [isCreating, setIsCreating] = useState(false)
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    status: 'ACTIVE',
  })
  const [error, setError] = useState<string | null>(null)

  const queryClient = useQueryClient()

  // Use the new API service
  const { data: projects, isLoading, error: queryError } = useQuery({
    queryKey: ['projects'],
    queryFn: api.projects.list,
    retry: 2,
  })

  const createMutation = useMutation({
    mutationFn: api.projects.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Project created successfully')
      setIsCreating(false)
      setNewProject({ name: '', description: '', status: 'ACTIVE' })
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message)
      toast.error(`Failed to create project: ${err.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: api.projects.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Project deleted successfully')
    },
    onError: (err: Error) => {
      toast.error(`Failed to delete project: ${err.message}`)
    },
  })

  const handleCreate = () => {
    if (!newProject.name.trim()) {
      setError('Project name is required')
      return
    }
    createMutation.mutate(newProject)
  }

  const handleDelete = (name: string) => {
    if (confirm(`Are you sure you want to delete project "${name}"?`)) {
      deleteMutation.mutate(name)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600 mt-1">Manage your projects and track progress</p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Plus />}
          onClick={() => setIsCreating(true)}
        >
          New Project
        </Button>
      </div>

      {error && (
        <Alert variant="error" title="Error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {isCreating && (
        <Card variant="elevated" padding="lg">
          <CardHeader>
            <CardTitle>Create New Project</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Project Name"
              value={newProject.name}
              onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
              placeholder="Enter project name"
              error={error && !newProject.name.trim() ? 'Required' : undefined}
            />
            <Input
              label="Description"
              value={newProject.description}
              onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              placeholder="Enter project description"
            />
          </CardContent>
          <CardFooter className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => {
                setIsCreating(false)
                setError(null)
              }}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              isLoading={createMutation.isPending}
              onClick={handleCreate}
            >
              Create Project
            </Button>
          </CardFooter>
        </Card>
      )}

      <PageWrapper
        isLoading={isLoading}
        error={queryError}
        isEmpty={projects?.length === 0}
        emptyTitle="No projects"
        emptyDescription="Create your first project to get started"
        emptyAction={
          <Button variant="primary" onClick={() => setIsCreating(true)}>
            Create Project
          </Button>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects?.map((project: Project) => (
            <Card key={project.name} variant="elevated" padding="md">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle>{project.name}</CardTitle>
                  <Badge
                    variant={project.status === 'ACTIVE' ? 'success' : 'default'}
                    size="sm"
                  >
                    {project.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {project.description || 'No description'}
                </p>
              </CardContent>
              <CardFooter className="flex justify-end space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={<Edit />}
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={<Trash2 />}
                  onClick={() => handleDelete(project.name)}
                >
                  Delete
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </PageWrapper>
    </div>
  )
}









