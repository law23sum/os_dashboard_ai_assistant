/**
 * End-to-End Tests: Projects
 * 
 * Regression, Sanity, and Functional Tests
 * Covers all CRUD operations and project management features
 */

import { describe, it, expect, beforeAll, afterAll } from '@jest/globals'
import { getEnvironment } from './test-config'

const env = getEnvironment(process.env.TEST_ENV || 'local')
const API_BASE = env.apiBase

describe('Projects E2E Tests', () => {
  let testProjectId: string | null = null

  beforeAll(async () => {
    // Verify API is accessible
    const healthCheck = await fetch(`${API_BASE.replace('/api', '')}/api/health`)
    expect(healthCheck.ok).toBe(true)
  })

  afterAll(async () => {
    // Cleanup: Delete test project if created
    if (testProjectId) {
      try {
        await fetch(`${API_BASE}/projects/${encodeURIComponent(testProjectId)}`, {
          method: 'DELETE',
        })
      } catch (error) {
        console.warn('Failed to cleanup test project:', error)
      }
    }
  })

  describe('Sanity Tests', () => {
    it('should fetch projects list', async () => {
      const response = await fetch(`${API_BASE}/projects`)
      expect(response.ok).toBe(true)
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    it('should return valid project structure', async () => {
      const response = await fetch(`${API_BASE}/projects`)
      const projects = await response.json()
      if (projects.length > 0) {
        const project = projects[0]
        expect(project).toHaveProperty('name')
        expect(project).toHaveProperty('status')
        expect(project).toHaveProperty('priority')
        expect(project).toHaveProperty('description')
      }
    })
  })

  describe('Functional Tests - CRUD Operations', () => {
    it('should create a new project', async () => {
      const newProject = {
        name: `Test Project ${Date.now()}`,
        description: 'E2E test project',
        status: 'active',
        priority: 'MEDIUM',
        order_num: 0,
      }

      const response = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProject),
      })

      expect(response.ok).toBe(true)
      const created = await response.json()
      expect(created.name).toBe(newProject.name)
      testProjectId = created.name
    })

    it('should update an existing project', async () => {
      if (!testProjectId) {
        // Create project first
        const createResponse = await fetch(`${API_BASE}/projects`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: `Test Update ${Date.now()}`,
            description: 'Test',
            status: 'active',
            priority: 'MEDIUM',
          }),
        })
        testProjectId = (await createResponse.json()).name
      }

      const updateData = {
        description: 'Updated description',
        priority: 'HIGH',
      }

      const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(testProjectId!)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      })

      expect(response.ok).toBe(true)
      const updated = await response.json()
      expect(updated.description).toBe(updateData.description)
      expect(updated.priority).toBe(updateData.priority)
    })

    it('should fetch a single project by name', async () => {
      if (!testProjectId) return

      const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(testProjectId)}`)
      expect(response.ok).toBe(true)
      const project = await response.json()
      expect(project.name).toBe(testProjectId)
    })

    it('should delete a project', async () => {
      // Create a project to delete
      const createResponse = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `Test Delete ${Date.now()}`,
          description: 'To be deleted',
          status: 'active',
          priority: 'LOW',
        }),
      })
      const toDelete = (await createResponse.json()).name

      const deleteResponse = await fetch(`${API_BASE}/projects/${encodeURIComponent(toDelete)}`, {
        method: 'DELETE',
      })

      expect(deleteResponse.status).toBe(204)

      // Verify deletion
      const getResponse = await fetch(`${API_BASE}/projects/${encodeURIComponent(toDelete)}`)
      expect(getResponse.status).toBe(404)
    })
  })

  describe('Functional Tests - Project Features', () => {
    it('should fetch project links', async () => {
      const response = await fetch(`${API_BASE}/projects/links`)
      expect(response.ok).toBe(true)
      const links = await response.json()
      expect(Array.isArray(links)).toBe(true)
    })

    it('should fetch project ledger events', async () => {
      const response = await fetch(`${API_BASE}/projects/ledger?limit=10`)
      expect(response.ok).toBe(true)
      const events = await response.json()
      expect(Array.isArray(events)).toBe(true)
    })

    it('should fetch project intelligence', async () => {
      const response = await fetch(`${API_BASE}/projects/intelligence`)
      expect(response.ok).toBe(true)
      const intelligence = await response.json()
      expect(Array.isArray(intelligence)).toBe(true)
    })

    it('should fetch project insights', async () => {
      // Get first project
      const projectsResponse = await fetch(`${API_BASE}/projects`)
      const projects = await projectsResponse.json()
      if (projects.length > 0) {
        const projectName = projects[0].name
        const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectName)}/insights`)
        expect(response.ok).toBe(true)
        const insights = await response.json()
        expect(insights).toHaveProperty('project')
        expect(insights).toHaveProperty('risk')
        expect(insights).toHaveProperty('forecast')
      }
    })

    it('should fetch project TRF data', async () => {
      const projectsResponse = await fetch(`${API_BASE}/projects`)
      const projects = await projectsResponse.json()
      if (projects.length > 0) {
        const projectName = projects[0].name
        const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectName)}/trf`)
        expect(response.ok).toBe(true)
        const trf = await response.json()
        expect(trf).toHaveProperty('project_id')
        expect(trf).toHaveProperty('entropy')
        expect(trf).toHaveProperty('resonance')
        expect(trf).toHaveProperty('continuity')
      }
    })
  })

  describe('Regression Tests', () => {
    it('should handle invalid project creation', async () => {
      const response = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          // Missing required 'name' field
          description: 'Invalid project',
        }),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })

    it('should handle non-existent project fetch', async () => {
      const response = await fetch(`${API_BASE}/projects/non-existent-project-12345`)
      expect(response.status).toBe(404)
    })

    it('should handle project filtering by status', async () => {
      const response = await fetch(`${API_BASE}/projects?status=active`)
      expect(response.ok).toBe(true)
      const projects = await response.json()
      projects.forEach((project: any) => {
        expect(project.status).toBe('active')
      })
    })
  })
})
