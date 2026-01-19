import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import PageHeader from '@/components/PageHeader'
import { conceptsApi } from '@/api/concepts'
import { ipmApi } from '@/api/ipm'
import { useActor } from '@/contexts/ActorContext'
import type {
  ConceptEdge,
  ConceptNode,
  ConceptTransition,
  ConceptEventLogEntry,
  ConceptQueueItem,
  ConceptObjectState,
  ConceptQueueResult,
  ConceptSimulationResult,
  ConceptBacklogDelta,
  GuardPredicate,
  GuardPredicateKind,
} from '@/types/concepts'
import type { PmsEpic, PmsProject } from '@/types/pms'

const tabs = [
  { id: 'graph', label: 'Concept Graph Studio' },
  { id: 'transitions', label: 'Transition Table Studio' },
  { id: 'runtime', label: 'Runtime & Simulation' },
  { id: 'publisher', label: 'Publisher' },
  { id: 'ipm', label: 'IPM Integration' },
]

const nodeTypes = [
  'ObjectType',
  'StateType',
  'EventType',
  'BehaviorType',
  'Attribute',
  'Constraint',
  'Invariant',
  'Actor',
  'Context',
  'Interface',
  'Resource',
]

const edgeTypes = [
  'OBJECT_HAS_STATE',
  'EVENT_TRIGGERS_BEHAVIOR',
  'BEHAVIOR_TRANSITIONS_STATE',
  'BEHAVIOR_EMITS_EVENT',
  'ENTITY_HAS_ATTRIBUTE',
  'CONSTRAINT_APPLIES_TO',
  'INVARIANT_GUARDED_BY',
  'EVENT_CAUSED_BY',
  'EVENT_CORRELATES_WITH',
]

const guardPredicateKinds: GuardPredicateKind[] = [
  'always_true',
  'always_false',
  'payload_equals',
  'payload_present',
  'state_equals',
]

type GuardFormState = {
  node_type: 'Constraint' | 'Invariant'
  node_id: string
  name: string
  description: string
  semantics: string
  predicate_kind: GuardPredicateKind
  predicate_path: string
  predicate_value: string
}

export default function ConceptStudio() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('graph')
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null)
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null)
  const [modelName, setModelName] = useState('')
  const [modelDescription, setModelDescription] = useState('')
  const [modelContext, setModelContext] = useState('')

  const [nodeForm, setNodeForm] = useState({
    node_type: 'ObjectType',
    node_id: '',
    name: '',
    description: '',
    semantics: '',
  })
  const [attributeSpec, setAttributeSpec] = useState({
    dtype: 'string',
    required: true,
    default: '',
    provenance: 'assigned',
    constraints: '',
    units: '',
    classification: '',
  })
  const [nodeMetadataJson, setNodeMetadataJson] = useState('{}')
  const [nodeError, setNodeError] = useState<string | null>(null)
  const [editingNodeId, setEditingNodeId] = useState<string | null>(null)

  const [edgeForm, setEdgeForm] = useState({
    edge_type: 'OBJECT_HAS_STATE',
    edge_id: '',
    source_node_id: '',
    target_node_id: '',
    name: '',
    description: '',
    semantics: '',
  })
  const [editingEdgeId, setEditingEdgeId] = useState<string | null>(null)

  const [transitionForm, setTransitionForm] = useState({
    state_type_id: '',
    event_type_id: '',
    behavior_type_id: '',
    next_state_type_id: '',
    emitted_event_type_ids: [] as string[],
    guard_ids: '',
    handling: 'handled',
    description: '',
  })
  const [editingTransitionId, setEditingTransitionId] = useState<string | null>(null)
  const [guardForm, setGuardForm] = useState<GuardFormState>({
    node_type: 'Constraint',
    node_id: '',
    name: '',
    description: '',
    semantics: '',
    predicate_kind: 'always_true',
    predicate_path: '',
    predicate_value: '',
  })
  const [guardError, setGuardError] = useState<string | null>(null)
  const [editingGuardId, setEditingGuardId] = useState<string | null>(null)
  const [initialStateId, setInitialStateId] = useState('')
  const [isDeprecated, setIsDeprecated] = useState(false)
  const [deprecationNote, setDeprecationNote] = useState('')

  const [exportContent, setExportContent] = useState('')
  const [exportFormat, setExportFormat] = useState<
    'json' | 'jsonld' | 'markdown' | 'mermaid' | 'dot' | 'plantuml' | 'schema'
  >('json')

  const [scopeStates, setScopeStates] = useState<string[]>([])
  const [scopeEvents, setScopeEvents] = useState<string[]>([])
  const [scopeBehaviors, setScopeBehaviors] = useState<string[]>([])
  const [scopeObjects, setScopeObjects] = useState<string[]>([])
  const [acceptanceRules, setAcceptanceRules] = useState('')

  const [eventForm, setEventForm] = useState({
    event_type_id: '',
    object_id: '',
    object_type_id: '',
    state_type_id: '',
    payload_json: '{}',
    correlation_id: '',
    causation_id: '',
    actor_id: '',
    source: 'concept_studio',
    enqueue: true,
  })
  const [eventError, setEventError] = useState<string | null>(null)
  const [queueStatus, setQueueStatus] = useState<'pending' | 'handled' | 'failed' | 'all'>('pending')
  const [queueLimit, setQueueLimit] = useState(10)
  const [processResults, setProcessResults] = useState<ConceptQueueResult[]>([])
  const [simulationStartStateId, setSimulationStartStateId] = useState('')
  const [simulationEventsText, setSimulationEventsText] = useState('')
  const [simulationStopOnError, setSimulationStopOnError] = useState(true)
  const [simulationResult, setSimulationResult] = useState<ConceptSimulationResult | null>(null)
  const [simulationError, setSimulationError] = useState<string | null>(null)
  const [guardOverrides, setGuardOverrides] = useState<Record<string, 'default' | 'pass' | 'fail'>>({})
  const [selectedSequenceId, setSelectedSequenceId] = useState('')

  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [selectedEpicId, setSelectedEpicId] = useState<string | null>(null)
  const [backlogPreview, setBacklogPreview] = useState<string[]>([])
  const [backlogDelta, setBacklogDelta] = useState<ConceptBacklogDelta | null>(null)

  const { data: models = [] } = useQuery({
    queryKey: ['concept-models'],
    queryFn: () => conceptsApi.listModels(),
  })

  const { data: versions = [] } = useQuery({
    queryKey: ['concept-versions', selectedModelId],
    queryFn: () => conceptsApi.listVersions(selectedModelId as string),
    enabled: !!selectedModelId,
  })

  const { data: bundle } = useQuery({
    queryKey: ['concept-bundle', selectedVersionId],
    queryFn: () => conceptsApi.getBundle(selectedVersionId as string),
    enabled: !!selectedVersionId,
  })

  const { data: analysis } = useQuery({
    queryKey: ['concept-analysis', selectedVersionId],
    queryFn: () => conceptsApi.getAnalysis(selectedVersionId as string),
    enabled: !!selectedVersionId,
  })

  const { data: projects = [] } = useQuery({
    queryKey: ['ipm-projects', currentActor],
    queryFn: () => ipmApi.listProjects(currentActor),
  })

  const { data: epics = [] } = useQuery({
    queryKey: ['ipm-epics', selectedProjectId, currentActor],
    queryFn: () => ipmApi.listEpics(selectedProjectId as string, currentActor),
    enabled: !!selectedProjectId,
  })

  const { data: links = [] } = useQuery({
    queryKey: ['concept-links', selectedProjectId, selectedEpicId],
    queryFn: () =>
      conceptsApi.listPmsLinks({ project_id: selectedProjectId ?? undefined, epic_id: selectedEpicId ?? undefined }),
    enabled: !!selectedProjectId,
  })

  const { data: coverage } = useQuery({
    queryKey: ['concept-coverage', selectedVersionId, selectedProjectId, selectedEpicId],
    queryFn: () =>
      conceptsApi.getCoverage(selectedVersionId as string, selectedProjectId as string, selectedEpicId),
    enabled: !!selectedVersionId && !!selectedProjectId,
  })

  const { data: eventLog = [] } = useQuery({
    queryKey: ['concept-events', selectedVersionId],
    queryFn: () => conceptsApi.listEvents(selectedVersionId as string, { limit: 100 }),
    enabled: !!selectedVersionId && activeTab === 'runtime',
  })

  const { data: queueItems = [] } = useQuery({
    queryKey: ['concept-queue', selectedVersionId, queueStatus],
    queryFn: () =>
      conceptsApi.listQueue(selectedVersionId as string, { status: queueStatus, limit: Math.max(queueLimit, 10) }),
    enabled: !!selectedVersionId && activeTab === 'runtime',
  })

  const { data: objectStates = [] } = useQuery({
    queryKey: ['concept-object-states', selectedVersionId],
    queryFn: () => conceptsApi.listObjectStates(selectedVersionId as string, { limit: 100 }),
    enabled: !!selectedVersionId && activeTab === 'runtime',
  })

  useEffect(() => {
    if (!selectedModelId && models.length > 0) {
      setSelectedModelId(models[0].model_id)
    }
  }, [models, selectedModelId])

  useEffect(() => {
    if (!selectedVersionId && versions.length > 0) {
      setSelectedVersionId(versions[0].version_id)
    }
  }, [versions, selectedVersionId])

  useEffect(() => {
    if (!selectedProjectId && projects.length > 0) {
      setSelectedProjectId(projects[0].project_id)
    }
  }, [projects, selectedProjectId])

  useEffect(() => {
    if (!selectedEpicId && epics.length > 0) {
      setSelectedEpicId(epics[0].epic_id)
    }
  }, [epics, selectedEpicId])

  useEffect(() => {
    const metadata = (bundle?.version?.metadata as Record<string, unknown>) || {}
    const initial = typeof metadata.initial_state_id === 'string' ? metadata.initial_state_id : ''
    setInitialStateId(initial)
  }, [bundle?.version?.metadata])

  useEffect(() => {
    if (!simulationStartStateId && initialStateId) {
      setSimulationStartStateId(initialStateId)
    }
  }, [initialStateId, simulationStartStateId])

  useEffect(() => {
    if (guardOptions.length === 0) {
      return
    }
    setGuardOverrides((prev) => {
      const next: Record<string, 'default' | 'pass' | 'fail'> = {}
      guardOptions.forEach((guardId) => {
        next[guardId] = prev[guardId] || 'default'
      })
      return next
    })
  }, [guardOptions])

  useEffect(() => {
    if (selectedSequenceId && suggestedSequences.some((sequence) => sequence.id === selectedSequenceId)) {
      return
    }
    setSelectedSequenceId('')
  }, [selectedSequenceId, suggestedSequences])

  useEffect(() => {
    setIsDeprecated(Boolean(bundle?.version?.is_deprecated))
    setDeprecationNote(bundle?.version?.deprecation_note || '')
  }, [bundle?.version?.version_id, bundle?.version?.is_deprecated, bundle?.version?.deprecation_note])

  const createModel = useMutation({
    mutationFn: () =>
      conceptsApi.createModel({
        name: modelName,
        description: modelDescription,
        context: modelContext || null,
      }),
    onSuccess: (data) => {
      setModelName('')
      setModelDescription('')
      setModelContext('')
      queryClient.invalidateQueries({ queryKey: ['concept-models'] })
      setSelectedModelId(data.model.model_id)
      setSelectedVersionId(data.version.version_id)
    },
  })

  const createVersion = useMutation({
    mutationFn: (parentVersionId: string) =>
      conceptsApi.createVersion(selectedModelId as string, {
        parent_version_id: parentVersionId,
        clone_from_parent: true,
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['concept-versions'] })
      setSelectedVersionId(data.version_id)
    },
  })

  const updateVersion = useMutation({
    mutationFn: (payload: Record<string, unknown>) => conceptsApi.updateVersion(selectedVersionId as string, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['concept-bundle'] }),
  })

  const createNode = useMutation({
    mutationFn: (payload: Partial<ConceptNode>) => conceptsApi.createNode(selectedVersionId as string, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      setNodeForm({ node_type: 'ObjectType', node_id: '', name: '', description: '', semantics: '' })
      setAttributeSpec({
        dtype: 'string',
        required: true,
        default: '',
        provenance: 'assigned',
        constraints: '',
        units: '',
        classification: '',
      })
      setNodeMetadataJson('{}')
      setNodeError(null)
      setEditingNodeId(null)
    },
  })

  const updateNode = useMutation({
    mutationFn: (payload: { nodeId: string; patch: Partial<ConceptNode> }) =>
      conceptsApi.updateNode(selectedVersionId as string, payload.nodeId, payload.patch),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      setNodeForm({ node_type: 'ObjectType', node_id: '', name: '', description: '', semantics: '' })
      setAttributeSpec({
        dtype: 'string',
        required: true,
        default: '',
        provenance: 'assigned',
        constraints: '',
        units: '',
        classification: '',
      })
      setNodeMetadataJson('{}')
      setNodeError(null)
      setEditingNodeId(null)
    },
  })

  const createEdge = useMutation({
    mutationFn: (payload: Partial<ConceptEdge>) => conceptsApi.createEdge(selectedVersionId as string, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      setEdgeForm({
        edge_type: 'OBJECT_HAS_STATE',
        edge_id: '',
        source_node_id: '',
        target_node_id: '',
        name: '',
        description: '',
        semantics: '',
      })
      setEditingEdgeId(null)
    },
  })

  const updateEdge = useMutation({
    mutationFn: (payload: { edgeId: string; patch: Partial<ConceptEdge> }) =>
      conceptsApi.updateEdge(selectedVersionId as string, payload.edgeId, payload.patch),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      setEdgeForm({
        edge_type: 'OBJECT_HAS_STATE',
        edge_id: '',
        source_node_id: '',
        target_node_id: '',
        name: '',
        description: '',
        semantics: '',
      })
      setEditingEdgeId(null)
    },
  })

  const upsertTransition = useMutation({
    mutationFn: (payload: Partial<ConceptTransition>) =>
      conceptsApi.upsertTransition(selectedVersionId as string, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      queryClient.invalidateQueries({ queryKey: ['concept-analysis'] })
      setTransitionForm({
        state_type_id: '',
        event_type_id: '',
        behavior_type_id: '',
        next_state_type_id: '',
        emitted_event_type_ids: [],
        guard_ids: '',
        handling: 'handled',
        description: '',
      })
      setEditingTransitionId(null)
    },
  })

  const createGuard = useMutation({
    mutationFn: (payload: Partial<ConceptNode>) => conceptsApi.createNode(selectedVersionId as string, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      setGuardForm({
        node_type: 'Constraint',
        node_id: '',
        name: '',
        description: '',
        semantics: '',
        predicate_kind: 'always_true',
        predicate_path: '',
        predicate_value: '',
      })
      setGuardError(null)
      setEditingGuardId(null)
    },
  })

  const updateGuard = useMutation({
    mutationFn: (payload: { nodeId: string; patch: Partial<ConceptNode> }) =>
      conceptsApi.updateNode(selectedVersionId as string, payload.nodeId, payload.patch),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
      setGuardForm({
        node_type: 'Constraint',
        node_id: '',
        name: '',
        description: '',
        semantics: '',
        predicate_kind: 'always_true',
        predicate_path: '',
        predicate_value: '',
      })
      setGuardError(null)
      setEditingGuardId(null)
    },
  })

  const exportVersion = useMutation({
    mutationFn: (format: 'json' | 'jsonld' | 'markdown' | 'mermaid' | 'dot' | 'plantuml' | 'schema') =>
      conceptsApi.exportVersion(selectedVersionId as string, format),
    onSuccess: (data, format) => {
      setExportFormat(format)
      if (typeof data === 'string') {
        setExportContent(data)
      } else {
        setExportContent(JSON.stringify(data, null, 2))
      }
      queryClient.invalidateQueries({ queryKey: ['concept-bundle'] })
    },
  })

  const createLink = useMutation({
    mutationFn: () =>
      conceptsApi.createPmsLink(selectedVersionId as string, {
        project_id: selectedProjectId as string,
        epic_id: selectedEpicId as string,
        scope:
          scopeStates.length || scopeEvents.length || scopeBehaviors.length || scopeObjects.length
            ? {
                object_types: scopeObjects,
                states: scopeStates,
                event_types: scopeEvents,
                behaviors: scopeBehaviors,
              }
            : undefined,
        acceptance_rules: acceptanceRules || undefined,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['concept-links'] }),
  })

  const generateBacklog = useMutation({
    mutationFn: (dryRun: boolean) =>
      conceptsApi.generateBacklog(selectedVersionId as string, {
        project_id: selectedProjectId as string,
        epic_id: selectedEpicId,
        scope:
          scopeStates.length || scopeEvents.length || scopeBehaviors.length || scopeObjects.length
            ? {
                object_types: scopeObjects,
                states: scopeStates,
                event_types: scopeEvents,
                behaviors: scopeBehaviors,
              }
            : undefined,
        dry_run: dryRun,
      }),
    onSuccess: (items) => {
      setBacklogPreview(items.map((item) => item.title))
      queryClient.invalidateQueries({ queryKey: ['concept-coverage'] })
    },
  })

  const fetchBacklogDelta = useMutation({
    mutationFn: () =>
      conceptsApi.getBacklogDelta(selectedVersionId as string, {
        project_id: selectedProjectId as string,
        epic_id: selectedEpicId,
        scope:
          scopeStates.length || scopeEvents.length || scopeBehaviors.length || scopeObjects.length
            ? {
                object_types: scopeObjects,
                states: scopeStates,
                event_types: scopeEvents,
                behaviors: scopeBehaviors,
              }
            : undefined,
      }),
    onSuccess: (delta) => {
      setBacklogDelta(delta)
    },
  })

  const createEvent = useMutation({
    mutationFn: (payload: {
      event_type_id: string
      object_id: string
      object_type_id: string
      state_type_id?: string | null
      payload?: Record<string, unknown>
      correlation_id?: string | null
      causation_id?: string | null
      actor_id?: string | null
      source?: string | null
      enqueue?: boolean
    }) => conceptsApi.createEvent(selectedVersionId as string, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concept-events'] })
      queryClient.invalidateQueries({ queryKey: ['concept-queue'] })
      setEventError(null)
    },
  })

  const processQueue = useMutation({
    mutationFn: () => conceptsApi.processQueue(selectedVersionId as string, { limit: queueLimit }),
    onSuccess: (items) => {
      setProcessResults(items)
      queryClient.invalidateQueries({ queryKey: ['concept-queue'] })
      queryClient.invalidateQueries({ queryKey: ['concept-object-states'] })
      queryClient.invalidateQueries({ queryKey: ['concept-events'] })
    },
  })

  const simulateSequence = useMutation({
    mutationFn: (payload: { event_type_ids: string[]; start_state_id?: string | null; stop_on_error?: boolean }) =>
      conceptsApi.simulateSequence(selectedVersionId as string, payload),
    onSuccess: (result) => {
      setSimulationResult(result)
      setSimulationError(null)
    },
    onError: (error) => {
      setSimulationError(error instanceof Error ? error.message : 'Simulation failed.')
    },
  })

  const nodes = bundle?.nodes ?? []
  const edges = bundle?.edges ?? []
  const transitions = bundle?.transitions ?? []
  const isFrozen = bundle?.version?.status === 'frozen'
  const versionMetadata = (bundle?.version?.metadata as Record<string, unknown>) || {}

  const stateNodes = useMemo(() => nodes.filter((node) => node.node_type === 'StateType'), [nodes])
  const eventNodes = useMemo(() => nodes.filter((node) => node.node_type === 'EventType'), [nodes])
  const behaviorNodes = useMemo(() => nodes.filter((node) => node.node_type === 'BehaviorType'), [nodes])
  const objectNodes = useMemo(() => nodes.filter((node) => node.node_type === 'ObjectType'), [nodes])
  const guardNodes = useMemo(
    () => nodes.filter((node) => node.node_type === 'Constraint' || node.node_type === 'Invariant'),
    [nodes],
  )
  const guardOptions = useMemo(() => {
    const unique = new Set<string>()
    transitions.forEach((transition) => {
      ;(transition.guard_ids || []).forEach((guardId) => unique.add(guardId))
    })
    return Array.from(unique)
  }, [transitions])
  const nodeNameById = useMemo(() => {
    const mapping: Record<string, string> = {}
    nodes.forEach((node) => {
      mapping[node.node_id] = node.name
    })
    return mapping
  }, [nodes])
  const suggestedSequences = useMemo(() => {
    if (!initialStateId || transitions.length === 0) {
      return []
    }
    const byState: Record<string, ConceptTransition[]> = {}
    transitions.forEach((transition) => {
      if (transition.handling !== 'handled') return
      if (!byState[transition.state_type_id]) {
        byState[transition.state_type_id] = []
      }
      byState[transition.state_type_id].push(transition)
    })
    const maxDepth = 4
    const limit = 6
    const sequences: Array<{
      id: string
      label: string
      eventIds: string[]
      states: string[]
      startStateId: string
    }> = []

    const visit = (stateId: string, eventIds: string[], states: string[], depth: number) => {
      if (sequences.length >= limit) return
      const outgoing = byState[stateId] || []
      if (depth >= maxDepth || outgoing.length === 0) {
        if (eventIds.length > 0) {
          const label = states.map((id) => nodeNameById[id] || id).join(' -> ')
          sequences.push({
            id: eventIds.join('|'),
            label,
            eventIds,
            states,
            startStateId: initialStateId,
          })
        }
        return
      }
      for (const transition of outgoing) {
        if (sequences.length >= limit) return
        if (states.includes(transition.next_state_type_id)) continue
        visit(
          transition.next_state_type_id,
          [...eventIds, transition.event_type_id],
          [...states, transition.next_state_type_id],
          depth + 1,
        )
      }
    }

    visit(initialStateId, [], [initialStateId], 0)
    const unique = new Map<string, typeof sequences[number]>()
    sequences.forEach((sequence) => {
      if (!unique.has(sequence.id)) {
        unique.set(sequence.id, sequence)
      }
    })
    return Array.from(unique.values())
  }, [initialStateId, nodeNameById, transitions])
  const selectedSequence = useMemo(
    () => suggestedSequences.find((sequence) => sequence.id === selectedSequenceId) || null,
    [suggestedSequences, selectedSequenceId],
  )

  const handleCreateNode = () => {
    if (!selectedVersionId) return
    if (!nodeForm.name.trim()) {
      setNodeError('Node name is required.')
      return
    }
    let metadata: Record<string, unknown> = {}
    if (nodeForm.node_type === 'Attribute') {
      metadata = {
        dtype: attributeSpec.dtype,
        required: attributeSpec.required,
        default: attributeSpec.default || null,
        provenance: attributeSpec.provenance,
        constraints: attributeSpec.constraints ? attributeSpec.constraints.split(',').map((item) => item.trim()) : [],
        units: attributeSpec.units || null,
        classification: attributeSpec.classification || null,
      }
    } else if (nodeMetadataJson.trim()) {
      try {
        metadata = JSON.parse(nodeMetadataJson)
      } catch (error) {
        setNodeError('Metadata JSON is invalid.')
        return
      }
    }
    const payload = {
      node_id: nodeForm.node_id || undefined,
      node_type: nodeForm.node_type,
      name: nodeForm.name,
      description: nodeForm.description,
      semantics: nodeForm.semantics,
      metadata,
    }
    if (editingNodeId) {
      updateNode.mutate({ nodeId: editingNodeId, patch: payload })
      return
    }
    createNode.mutate(payload)
  }

  const handleCreateEdge = () => {
    if (!selectedVersionId) return
    if (!edgeForm.source_node_id || !edgeForm.target_node_id) return
    const payload = {
      edge_id: edgeForm.edge_id || undefined,
      edge_type: edgeForm.edge_type,
      source_node_id: edgeForm.source_node_id,
      target_node_id: edgeForm.target_node_id,
      name: edgeForm.name || undefined,
      description: edgeForm.description || undefined,
      semantics: edgeForm.semantics || undefined,
    }
    if (editingEdgeId) {
      updateEdge.mutate({ edgeId: editingEdgeId, patch: payload })
      return
    }
    createEdge.mutate(payload)
  }

  const handleUpsertTransition = () => {
    if (!selectedVersionId) return
    if (
      !transitionForm.state_type_id ||
      !transitionForm.event_type_id ||
      !transitionForm.behavior_type_id ||
      !transitionForm.next_state_type_id
    ) {
      return
    }
    upsertTransition.mutate({
      state_type_id: transitionForm.state_type_id,
      event_type_id: transitionForm.event_type_id,
      behavior_type_id: transitionForm.behavior_type_id,
      next_state_type_id: transitionForm.next_state_type_id,
      emitted_event_type_ids: transitionForm.emitted_event_type_ids,
      guard_ids: transitionForm.guard_ids
        ? transitionForm.guard_ids.split(',').map((item) => item.trim()).filter(Boolean)
        : [],
      handling: transitionForm.handling,
      description: transitionForm.description || undefined,
    })
  }

  const handleSaveGuard = () => {
    if (!selectedVersionId) return
    if (!guardForm.name.trim()) {
      setGuardError('Guard name is required.')
      return
    }
    let predicateValue: unknown
    if (guardForm.predicate_value.trim()) {
      try {
        predicateValue = JSON.parse(guardForm.predicate_value)
      } catch (error) {
        predicateValue = guardForm.predicate_value
      }
    }
    const predicate: GuardPredicate = { kind: guardForm.predicate_kind }
    if (guardForm.predicate_path.trim()) {
      predicate.path = guardForm.predicate_path.trim()
    }
    if (guardForm.predicate_value.trim()) {
      predicate.value = predicateValue
    }
    const metadata = { predicate }

    if (editingGuardId) {
      updateGuard.mutate({
        nodeId: editingGuardId,
        patch: {
          name: guardForm.name,
          description: guardForm.description,
          semantics: guardForm.semantics,
          metadata,
        },
      })
      return
    }

    createGuard.mutate({
      node_id: guardForm.node_id || undefined,
      node_type: guardForm.node_type,
      name: guardForm.name,
      description: guardForm.description,
      semantics: guardForm.semantics,
      metadata,
    })
  }

  const handleCreateEvent = () => {
    if (!selectedVersionId) return
    if (!eventForm.event_type_id || !eventForm.object_id || !eventForm.object_type_id) {
      setEventError('Event type, object ID, and object type are required.')
      return
    }
    let payload: Record<string, unknown> = {}
    if (eventForm.payload_json.trim()) {
      try {
        payload = JSON.parse(eventForm.payload_json)
      } catch (error) {
        setEventError('Payload JSON is invalid.')
        return
      }
    }
    createEvent.mutate({
      event_type_id: eventForm.event_type_id,
      object_id: eventForm.object_id,
      object_type_id: eventForm.object_type_id,
      state_type_id: eventForm.state_type_id || undefined,
      payload,
      correlation_id: eventForm.correlation_id || undefined,
      causation_id: eventForm.causation_id || undefined,
      actor_id: eventForm.actor_id || undefined,
      source: eventForm.source || undefined,
      enqueue: eventForm.enqueue,
    })
    setEventForm((prev) => ({
      ...prev,
      payload_json: '{}',
      correlation_id: '',
      causation_id: '',
      actor_id: '',
    }))
  }

  const handleRunSimulation = () => {
    if (!selectedVersionId) return
    const eventIds = simulationEventsText
      .split(/[\n,]+/g)
      .map((item) => item.trim())
      .filter(Boolean)
    if (eventIds.length === 0) {
      setSimulationError('Provide at least one event type id to simulate.')
      return
    }
    const guardPayload: Record<string, boolean> = {}
    Object.entries(guardOverrides).forEach(([guardId, mode]) => {
      if (mode === 'pass') guardPayload[guardId] = true
      if (mode === 'fail') guardPayload[guardId] = false
    })
    simulateSequence.mutate({
      event_type_ids: eventIds,
      start_state_id: simulationStartStateId || undefined,
      stop_on_error: simulationStopOnError,
      guard_overrides: Object.keys(guardPayload).length ? guardPayload : undefined,
    })
  }

  const handleLoadSequence = () => {
    if (!selectedSequence) {
      setSimulationError('Select a suggested sequence to load.')
      return
    }
    setSimulationEventsText(selectedSequence.eventIds.join('\n'))
    setSimulationStartStateId(selectedSequence.startStateId)
    setSimulationResult(null)
    setSimulationError(null)
  }

  const startEditNode = (node: ConceptNode) => {
    setEditingNodeId(node.node_id)
    setNodeForm({
      node_type: node.node_type,
      node_id: node.node_id,
      name: node.name,
      description: node.description || '',
      semantics: node.semantics || '',
    })
    if (node.node_type === 'Attribute') {
      const metadata = node.metadata as Record<string, unknown> | undefined
      setAttributeSpec({
        dtype: (metadata?.dtype as string) || 'string',
        required: typeof metadata?.required === 'boolean' ? (metadata?.required as boolean) : true,
        default: (metadata?.default as string) || '',
        provenance: (metadata?.provenance as string) || 'assigned',
        constraints: Array.isArray(metadata?.constraints) ? (metadata?.constraints as string[]).join(', ') : '',
        units: (metadata?.units as string) || '',
        classification: (metadata?.classification as string) || '',
      })
      setNodeMetadataJson('{}')
    } else {
      setNodeMetadataJson(JSON.stringify(node.metadata || {}, null, 2))
    }
  }

  const startEditGuard = (node: ConceptNode) => {
    const metadata = (node.metadata as Record<string, unknown>) || {}
    const predicate = (metadata.predicate as GuardPredicate) || { kind: 'always_true' }
    let predicateValue = ''
    if (predicate.value !== undefined) {
      predicateValue = typeof predicate.value === 'string' ? predicate.value : JSON.stringify(predicate.value)
    }
    setEditingGuardId(node.node_id)
    setGuardForm({
      node_type: node.node_type === 'Invariant' ? 'Invariant' : 'Constraint',
      node_id: node.node_id,
      name: node.name,
      description: node.description || '',
      semantics: node.semantics || '',
      predicate_kind: predicate.kind || 'always_true',
      predicate_path: predicate.path || '',
      predicate_value: predicateValue,
    })
    setGuardError(null)
  }

  const startEditEdge = (edge: ConceptEdge) => {
    setEditingEdgeId(edge.edge_id)
    setEdgeForm({
      edge_type: edge.edge_type,
      edge_id: edge.edge_id,
      source_node_id: edge.source_node_id,
      target_node_id: edge.target_node_id,
      name: edge.name || '',
      description: edge.description || '',
      semantics: edge.semantics || '',
    })
  }

  const startEditTransition = (transition: ConceptTransition) => {
    setEditingTransitionId(transition.transition_id)
    setTransitionForm({
      state_type_id: transition.state_type_id,
      event_type_id: transition.event_type_id,
      behavior_type_id: transition.behavior_type_id,
      next_state_type_id: transition.next_state_type_id,
      emitted_event_type_ids: transition.emitted_event_type_ids || [],
      guard_ids: (transition.guard_ids || []).join(', '),
      handling: transition.handling,
      description: transition.description || '',
    })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Concept Systems"
        title="Meta / Concept Studio"
        description="Typed semantic graph, transition rules, and traceable execution plans."
      />

      <section className="glass-card p-5 space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex-1 min-w-[220px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Concept Model</label>
            <select
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={selectedModelId || ''}
              onChange={(event) => {
                setSelectedModelId(event.target.value)
                setSelectedVersionId(null)
              }}
            >
              {models.map((model) => (
                <option key={model.model_id} value={model.model_id}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[220px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Version</label>
            <select
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={selectedVersionId || ''}
              onChange={(event) => setSelectedVersionId(event.target.value)}
            >
              {versions.map((version) => (
                <option key={version.version_id} value={version.version_id}>
                  {version.version_label} · {version.status}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[220px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Initial State</label>
            <div className="mt-2 flex items-center gap-2">
              <select
                className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={initialStateId || ''}
                onChange={(event) => setInitialStateId(event.target.value)}
                disabled={!selectedVersionId || isFrozen}
              >
                <option value="">Select initial state</option>
                {stateNodes.map((node) => (
                  <option key={node.node_id} value={node.node_id}>
                    {node.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={!selectedVersionId || isFrozen}
                onClick={() =>
                  updateVersion.mutate({
                    metadata: { ...versionMetadata, initial_state_id: initialStateId || null },
                  })
                }
              >
                Save
              </button>
            </div>
          </div>
          <div className="flex items-end gap-2">
            <button
              type="button"
              className="btn btn-secondary"
              disabled={!selectedVersionId}
              onClick={() => createVersion.mutate(selectedVersionId as string)}
            >
              Fork Version
            </button>
            <select
              className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
              value={bundle?.version?.status || 'draft'}
              onChange={(event) => updateVersion.mutate({ status: event.target.value })}
              disabled={!selectedVersionId}
            >
              <option value="draft">Draft</option>
              <option value="reviewed">Reviewed</option>
              <option value="frozen">Frozen</option>
            </select>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          <div className="md:col-span-2">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Canonical Link</label>
            <input
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-xs"
              value={bundle?.version?.canonical_link || ''}
              readOnly
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Deprecation</label>
            <div className="mt-2 flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                checked={isDeprecated}
                onChange={(event) => setIsDeprecated(event.target.checked)}
                disabled={!selectedVersionId || isFrozen}
              />
              <span className="text-sm text-[color:var(--osd-text)]">Deprecated</span>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() =>
                  updateVersion.mutate({
                    is_deprecated: isDeprecated,
                    deprecation_note: deprecationNote || null,
                  })
                }
                disabled={!selectedVersionId || isFrozen}
              >
                Save
              </button>
            </div>
          </div>
        </div>

        <div>
          <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Deprecation Note</label>
          <textarea
            className="mt-2 w-full min-h-[80px] rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
            value={deprecationNote}
            onChange={(event) => setDeprecationNote(event.target.value)}
            disabled={!selectedVersionId || isFrozen}
          />
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
            <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Nodes</div>
            <div className="mt-2 text-2xl font-semibold text-[color:var(--osd-text)]">{nodes.length}</div>
          </div>
          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
            <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Edges</div>
            <div className="mt-2 text-2xl font-semibold text-[color:var(--osd-text)]">{edges.length}</div>
          </div>
          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
            <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Transitions</div>
            <div className="mt-2 text-2xl font-semibold text-[color:var(--osd-text)]">{transitions.length}</div>
          </div>
        </div>
      </section>

      <section className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
          >
            {tab.label}
          </button>
        ))}
      </section>

      {activeTab === 'graph' && (
        <div className="grid gap-6 lg:grid-cols-2">
          <section className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">
                {editingNodeId ? 'Edit Node' : 'Create Node'}
              </h2>
              {editingNodeId ? (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setEditingNodeId(null)
                    setNodeForm({ node_type: 'ObjectType', node_id: '', name: '', description: '', semantics: '' })
                    setAttributeSpec({
                      dtype: 'string',
                      required: true,
                      default: '',
                      provenance: 'assigned',
                      constraints: '',
                      units: '',
                      classification: '',
                    })
                    setNodeMetadataJson('{}')
                    setNodeError(null)
                  }}
                  disabled={isFrozen}
                >
                  Cancel
                </button>
              ) : null}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Type</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={nodeForm.node_type}
                  onChange={(event) => setNodeForm((prev) => ({ ...prev, node_type: event.target.value }))}
                  disabled={isFrozen || !!editingNodeId}
                >
                  {nodeTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Stable ID</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={nodeForm.node_id}
                  placeholder="optional"
                  onChange={(event) => setNodeForm((prev) => ({ ...prev, node_id: event.target.value }))}
                  disabled={isFrozen || !!editingNodeId}
                />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Name</label>
              <input
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={nodeForm.name}
                onChange={(event) => setNodeForm((prev) => ({ ...prev, name: event.target.value }))}
                disabled={isFrozen}
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Description</label>
              <input
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={nodeForm.description}
                onChange={(event) => setNodeForm((prev) => ({ ...prev, description: event.target.value }))}
                disabled={isFrozen}
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Semantics</label>
              <input
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={nodeForm.semantics}
                onChange={(event) => setNodeForm((prev) => ({ ...prev, semantics: event.target.value }))}
                disabled={isFrozen}
              />
            </div>

            {nodeForm.node_type === 'Attribute' ? (
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Dtype</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                    value={attributeSpec.dtype}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, dtype: event.target.value }))}
                    disabled={isFrozen}
                  />
                </div>
                <div className="flex items-center gap-2 mt-6">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                    checked={attributeSpec.required}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, required: event.target.checked }))}
                    disabled={isFrozen}
                  />
                  <span className="text-sm text-[color:var(--osd-text)]">Required</span>
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Default</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                    value={attributeSpec.default}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, default: event.target.value }))}
                    disabled={isFrozen}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Provenance</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                    value={attributeSpec.provenance}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, provenance: event.target.value }))}
                    disabled={isFrozen}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Constraints</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                    value={attributeSpec.constraints}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, constraints: event.target.value }))}
                    disabled={isFrozen}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Units</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                    value={attributeSpec.units}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, units: event.target.value }))}
                    disabled={isFrozen}
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Classification</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                    value={attributeSpec.classification}
                    onChange={(event) => setAttributeSpec((prev) => ({ ...prev, classification: event.target.value }))}
                    disabled={isFrozen}
                  />
                </div>
              </div>
            ) : (
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Metadata (JSON)</label>
                <textarea
                  className="mt-2 w-full min-h-[120px] rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 font-mono text-xs"
                  value={nodeMetadataJson}
                  onChange={(event) => setNodeMetadataJson(event.target.value)}
                  disabled={isFrozen}
                />
              </div>
            )}

            {nodeError ? <p className="text-xs text-red-400">{nodeError}</p> : null}
            <button type="button" className="btn btn-primary" onClick={handleCreateNode} disabled={isFrozen}>
              {editingNodeId ? 'Save Node' : 'Add Node'}
            </button>
          </section>

          <section className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">
                {editingEdgeId ? 'Edit Edge' : 'Create Edge'}
              </h2>
              {editingEdgeId ? (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setEditingEdgeId(null)
                    setEdgeForm({
                      edge_type: 'OBJECT_HAS_STATE',
                      edge_id: '',
                      source_node_id: '',
                      target_node_id: '',
                      name: '',
                      description: '',
                      semantics: '',
                    })
                  }}
                  disabled={isFrozen}
                >
                  Cancel
                </button>
              ) : null}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Type</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={edgeForm.edge_type}
                  onChange={(event) => setEdgeForm((prev) => ({ ...prev, edge_type: event.target.value }))}
                  disabled={isFrozen}
                >
                  {edgeTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Stable ID</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={edgeForm.edge_id}
                  placeholder="optional"
                  onChange={(event) => setEdgeForm((prev) => ({ ...prev, edge_id: event.target.value }))}
                  disabled={isFrozen || !!editingEdgeId}
                />
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Source</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={edgeForm.source_node_id}
                  onChange={(event) => setEdgeForm((prev) => ({ ...prev, source_node_id: event.target.value }))}
                  disabled={isFrozen}
                >
                  <option value="">Select node</option>
                  {nodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name} · {node.node_type}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Target</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={edgeForm.target_node_id}
                  onChange={(event) => setEdgeForm((prev) => ({ ...prev, target_node_id: event.target.value }))}
                  disabled={isFrozen}
                >
                  <option value="">Select node</option>
                  {nodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name} · {node.node_type}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Name</label>
              <input
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={edgeForm.name}
                onChange={(event) => setEdgeForm((prev) => ({ ...prev, name: event.target.value }))}
                disabled={isFrozen}
              />
            </div>
            <button type="button" className="btn btn-primary" onClick={handleCreateEdge} disabled={isFrozen}>
              {editingEdgeId ? 'Save Edge' : 'Add Edge'}
            </button>
          </section>

          <section className="glass-card p-5 space-y-3 lg:col-span-2">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Nodes</h2>
            <div className="grid gap-2">
              {nodes.map((node) => {
                const metadata = (node.metadata as Record<string, unknown>) || {}
                const constraints = Array.isArray(metadata.constraints) ? metadata.constraints.join(', ') : ''
                const units = metadata.units ? String(metadata.units) : ''
                const classification = metadata.classification ? String(metadata.classification) : ''
                return (
                  <div key={node.node_id} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <div className="text-sm font-semibold text-[color:var(--osd-text)]">{node.name}</div>
                        <div className="text-xs text-[color:var(--osd-muted)]">{node.node_type}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-xs text-[color:var(--osd-muted)]">{node.node_id}</div>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => startEditNode(node)}
                          disabled={isFrozen}
                        >
                          Edit
                        </button>
                      </div>
                    </div>
                    {node.description ? (
                      <p className="text-xs text-[color:var(--osd-muted)] mt-2">{node.description}</p>
                    ) : null}
                    {node.semantics ? (
                      <p className="text-xs text-[color:var(--osd-muted)] mt-1">Semantics: {node.semantics}</p>
                    ) : null}
                    {node.node_type === 'Attribute' ? (
                      <div className="mt-2 text-xs text-[color:var(--osd-muted)]">
                        dtype: {String(metadata.dtype || '')} · required: {String(metadata.required)} · default:{' '}
                        {String(metadata.default ?? '')} · provenance: {String(metadata.provenance || '')}
                        {constraints ? ` · constraints: ${constraints}` : ''}
                        {units ? ` · units: ${units}` : ''}
                        {classification ? ` · classification: ${classification}` : ''}
                      </div>
                    ) : null}
                  </div>
                )
              })}
            </div>
          </section>

          <section className="glass-card p-5 space-y-3 lg:col-span-2">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Edges</h2>
            <div className="grid gap-2">
              {edges.map((edge) => (
                <div key={edge.edge_id} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <div className="text-sm font-semibold text-[color:var(--osd-text)]">{edge.edge_type}</div>
                      <div className="text-xs text-[color:var(--osd-muted)]">{edge.edge_id}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-xs text-[color:var(--osd-muted)]">
                        {nodeNameById[edge.source_node_id] || edge.source_node_id} →{' '}
                        {nodeNameById[edge.target_node_id] || edge.target_node_id}
                      </div>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => startEditEdge(edge)}
                        disabled={isFrozen}
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                  {edge.description ? (
                    <p className="text-xs text-[color:var(--osd-muted)] mt-2">{edge.description}</p>
                  ) : null}
                  {edge.name ? (
                    <p className="text-xs text-[color:var(--osd-muted)] mt-1">Name: {edge.name}</p>
                  ) : null}
                  {edge.semantics ? (
                    <p className="text-xs text-[color:var(--osd-muted)] mt-1">Semantics: {edge.semantics}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </section>
        </div>
      )}

      {activeTab === 'transitions' && (
        <div className="space-y-6">
          <section className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">
                {editingTransitionId ? 'Edit Transition' : 'Define Transition'}
              </h2>
              {editingTransitionId ? (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setEditingTransitionId(null)
                    setTransitionForm({
                      state_type_id: '',
                      event_type_id: '',
                      behavior_type_id: '',
                      next_state_type_id: '',
                      emitted_event_type_ids: [],
                      guard_ids: '',
                      handling: 'handled',
                      description: '',
                    })
                  }}
                  disabled={isFrozen}
                >
                  Cancel
                </button>
              ) : null}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">State</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={transitionForm.state_type_id}
                  onChange={(event) => setTransitionForm((prev) => ({ ...prev, state_type_id: event.target.value }))}
                  disabled={isFrozen}
                >
                  <option value="">Select state</option>
                  {stateNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Event</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={transitionForm.event_type_id}
                  onChange={(event) => setTransitionForm((prev) => ({ ...prev, event_type_id: event.target.value }))}
                  disabled={isFrozen}
                >
                  <option value="">Select event</option>
                  {eventNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Behavior</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={transitionForm.behavior_type_id}
                  onChange={(event) =>
                    setTransitionForm((prev) => ({ ...prev, behavior_type_id: event.target.value }))
                  }
                  disabled={isFrozen}
                >
                  <option value="">Select behavior</option>
                  {behaviorNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Next State</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={transitionForm.next_state_type_id}
                  onChange={(event) =>
                    setTransitionForm((prev) => ({ ...prev, next_state_type_id: event.target.value }))
                  }
                  disabled={isFrozen}
                >
                  <option value="">Select next state</option>
                  {stateNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Emitted Events</label>
              <div className="mt-2 grid gap-2 md:grid-cols-2">
                {eventNodes.map((node) => {
                  const checked = transitionForm.emitted_event_type_ids.includes(node.node_id)
                  return (
                    <label key={node.node_id} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                        checked={checked}
                        onChange={(event) => {
                          setTransitionForm((prev) => {
                            const next = new Set(prev.emitted_event_type_ids)
                            if (event.target.checked) next.add(node.node_id)
                            else next.delete(node.node_id)
                            return { ...prev, emitted_event_type_ids: Array.from(next) }
                          })
                        }}
                        disabled={isFrozen}
                      />
                      {node.name}
                    </label>
                  )
                })}
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Guard Registry</label>
              <div className="mt-2 grid gap-2 md:grid-cols-2">
                {guardNodes.length === 0 ? (
                  <p className="text-xs text-[color:var(--osd-muted)]">No guards registered.</p>
                ) : (
                  guardNodes.map((node) => {
                    const guardIds = transitionForm.guard_ids
                      ? transitionForm.guard_ids.split(',').map((item) => item.trim()).filter(Boolean)
                      : []
                    const checked = guardIds.includes(node.node_id)
                    return (
                      <label key={node.node_id} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                          checked={checked}
                          onChange={(event) => {
                            setTransitionForm((prev) => {
                              const next = new Set(
                                prev.guard_ids
                                  ? prev.guard_ids.split(',').map((item) => item.trim()).filter(Boolean)
                                  : [],
                              )
                              if (event.target.checked) next.add(node.node_id)
                              else next.delete(node.node_id)
                              return { ...prev, guard_ids: Array.from(next).join(', ') }
                            })
                          }}
                          disabled={isFrozen}
                        />
                        {node.name}
                      </label>
                    )
                  })
                )}
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                  Guard IDs (manual)
                </label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={transitionForm.guard_ids}
                  onChange={(event) => setTransitionForm((prev) => ({ ...prev, guard_ids: event.target.value }))}
                  placeholder="comma-separated"
                  disabled={isFrozen}
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Handling</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={transitionForm.handling}
                  onChange={(event) => setTransitionForm((prev) => ({ ...prev, handling: event.target.value }))}
                  disabled={isFrozen}
                >
                  <option value="handled">Handled</option>
                  <option value="ignored">Ignored</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleUpsertTransition} disabled={isFrozen}>
              {editingTransitionId ? 'Save Transition' : 'Add Transition'}
            </button>
          </section>

          <section className="glass-card p-5 space-y-3">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Transition Table</h2>
            <div className="grid gap-2">
              {transitions.map((transition) => (
                <div key={transition.transition_id} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <div className="text-sm font-semibold text-[color:var(--osd-text)]">
                        {nodeNameById[transition.state_type_id] || transition.state_type_id} +{' '}
                        {nodeNameById[transition.event_type_id] || transition.event_type_id}
                      </div>
                      <div className="text-xs text-[color:var(--osd-muted)]">
                        Behavior: {nodeNameById[transition.behavior_type_id] || transition.behavior_type_id} →{' '}
                        {nodeNameById[transition.next_state_type_id] || transition.next_state_type_id}
                      </div>
                      <div className="text-xs text-[color:var(--osd-muted)]">
                        Emits:{' '}
                        {(transition.emitted_event_type_ids || [])
                          .map((eventId) => nodeNameById[eventId] || eventId)
                          .join(', ') || 'none'}
                      </div>
                      <div className="text-xs text-[color:var(--osd-muted)]">
                        Guards:{' '}
                        {(transition.guard_ids || [])
                          .map((guardId) => nodeNameById[guardId] || guardId)
                          .join(', ') || 'none'}
                      </div>
                      <div className="text-xs text-[color:var(--osd-muted)]">Handling: {transition.handling}</div>
                      {transition.description ? (
                        <div className="text-xs text-[color:var(--osd-muted)]">Notes: {transition.description}</div>
                      ) : null}
                    </div>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => startEditTransition(transition)}
                      disabled={isFrozen}
                    >
                      Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">
                {editingGuardId ? 'Edit Guard Predicate' : 'Guard Registry'}
              </h2>
              {editingGuardId ? (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setEditingGuardId(null)
                    setGuardForm({
                      node_type: 'Constraint',
                      node_id: '',
                      name: '',
                      description: '',
                      semantics: '',
                      predicate_kind: 'always_true',
                      predicate_path: '',
                      predicate_value: '',
                    })
                    setGuardError(null)
                  }}
                  disabled={isFrozen}
                >
                  Cancel
                </button>
              ) : null}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Type</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={guardForm.node_type}
                  onChange={(event) =>
                    setGuardForm((prev) => ({
                      ...prev,
                      node_type: event.target.value === 'Invariant' ? 'Invariant' : 'Constraint',
                    }))
                  }
                  disabled={isFrozen || !!editingGuardId}
                >
                  <option value="Constraint">Constraint</option>
                  <option value="Invariant">Invariant</option>
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Stable ID</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={guardForm.node_id}
                  placeholder="optional"
                  onChange={(event) => setGuardForm((prev) => ({ ...prev, node_id: event.target.value }))}
                  disabled={isFrozen || !!editingGuardId}
                />
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Name</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={guardForm.name}
                  onChange={(event) => setGuardForm((prev) => ({ ...prev, name: event.target.value }))}
                  disabled={isFrozen}
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Description</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={guardForm.description}
                  onChange={(event) => setGuardForm((prev) => ({ ...prev, description: event.target.value }))}
                  disabled={isFrozen}
                />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Semantics</label>
              <input
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={guardForm.semantics}
                onChange={(event) => setGuardForm((prev) => ({ ...prev, semantics: event.target.value }))}
                disabled={isFrozen}
              />
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Predicate Kind</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={guardForm.predicate_kind}
                  onChange={(event) =>
                    setGuardForm((prev) => ({
                      ...prev,
                      predicate_kind: event.target.value as GuardPredicateKind,
                    }))
                  }
                  disabled={isFrozen}
                >
                  {guardPredicateKinds.map((kind) => (
                    <option key={kind} value={kind}>
                      {kind}
                    </option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Predicate Path</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={guardForm.predicate_path}
                  onChange={(event) => setGuardForm((prev) => ({ ...prev, predicate_path: event.target.value }))}
                  placeholder="payload path (e.g., reviewer.present)"
                  disabled={isFrozen}
                />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Predicate Value</label>
              <input
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 font-mono text-xs"
                value={guardForm.predicate_value}
                onChange={(event) => setGuardForm((prev) => ({ ...prev, predicate_value: event.target.value }))}
                placeholder='JSON or raw string (e.g., "approved", true)'
                disabled={isFrozen}
              />
            </div>
            {guardError ? <p className="text-xs text-red-400">{guardError}</p> : null}
            <button type="button" className="btn btn-primary" onClick={handleSaveGuard} disabled={isFrozen}>
              {editingGuardId ? 'Save Guard' : 'Add Guard'}
            </button>
            <div className="grid gap-2">
              {guardNodes.length === 0 ? (
                <p className="text-sm text-[color:var(--osd-muted)]">No guard predicates registered.</p>
              ) : (
                guardNodes.map((node) => {
                  const metadata = (node.metadata as Record<string, unknown>) || {}
                  const predicate = metadata.predicate as GuardPredicate | undefined
                  const predicateLabel = predicate
                    ? `${predicate.kind}${predicate.path ? ` · ${predicate.path}` : ''}`
                    : 'no predicate'
                  return (
                    <div key={node.node_id} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <div className="text-sm font-semibold text-[color:var(--osd-text)]">{node.name}</div>
                          <div className="text-xs text-[color:var(--osd-muted)]">
                            {node.node_type} · {predicateLabel}
                          </div>
                        </div>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => startEditGuard(node)}
                          disabled={isFrozen}
                        >
                          Edit
                        </button>
                      </div>
                      {node.description ? (
                        <p className="text-xs text-[color:var(--osd-muted)] mt-2">{node.description}</p>
                      ) : null}
                    </div>
                  )
                })
              )}
            </div>
          </section>

          <section className="glass-card p-5 space-y-3">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Model Checks</h2>
            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Missing</div>
                <div className="mt-1 text-lg font-semibold">{analysis?.missing_transitions?.length || 0}</div>
              </div>
              <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Unreachable</div>
                <div className="mt-1 text-lg font-semibold">{analysis?.unreachable_states?.length || 0}</div>
              </div>
              <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Invariants</div>
                <div className="mt-1 text-lg font-semibold">{analysis?.invariant_coverage?.length || 0}</div>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Missing Transitions</div>
                <div className="mt-2 space-y-1 text-xs text-[color:var(--osd-muted)]">
                  {(analysis?.missing_transitions || []).length === 0
                    ? 'All state/event pairs handled or ignored.'
                    : (analysis?.missing_transitions || []).map((item, idx) => (
                        <div key={`missing-${idx}`}>
                          {String(item.state_name || item.state_id)} + {String(item.event_name || item.event_id)}
                        </div>
                      ))}
                </div>
              </div>
              <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Unreachable States</div>
                <div className="mt-2 space-y-1 text-xs text-[color:var(--osd-muted)]">
                  {(analysis?.unreachable_states || []).length === 0
                    ? 'All states reachable from the initial state.'
                    : (analysis?.unreachable_states || []).map((item, idx) => (
                        <div key={`unreachable-${idx}`}>{String(item.state_name || item.state_id)}</div>
                      ))}
                </div>
              </div>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
              <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Invariant Coverage</div>
              <div className="mt-2 space-y-1 text-xs text-[color:var(--osd-muted)]">
                {(analysis?.invariant_coverage || []).length === 0
                  ? 'No invariants linked.'
                  : (analysis?.invariant_coverage || []).map((item, idx) => (
                      <div key={`invariant-${idx}`}>
                        {String(item.invariant_name || item.invariant_id)} →{' '}
                        {String(item.behavior_name || item.behavior_id)} ·{' '}
                        {item.has_transition ? 'linked' : 'unlinked'}
                      </div>
                    ))}
              </div>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
              <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Lint Issues</div>
              <div className="mt-2 space-y-1 text-xs text-[color:var(--osd-muted)]">
                {(analysis?.lint_issues || []).length === 0
                  ? 'No lint issues detected.'
                  : (analysis?.lint_issues || []).map((item, idx) => (
                      <div key={`lint-${idx}`}>
                        {String(item.kind || 'issue')} ·{' '}
                        {String(item.edge_type || item.field || item.node_id || item.transition_id || '')}
                      </div>
                    ))}
              </div>
            </div>
          </section>
        </div>
      )}

      {activeTab === 'runtime' && (
        <div className="space-y-6">
          <section className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Enqueue Event</h2>
              <div className="text-xs text-[color:var(--osd-muted)]">
                Initial state: {initialStateId || 'unset'}
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Event Type</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.event_type_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, event_type_id: event.target.value }))}
                >
                  <option value="">Select event</option>
                  {eventNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Object Type</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.object_type_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, object_type_id: event.target.value }))}
                >
                  <option value="">Select object type</option>
                  {objectNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Object ID</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.object_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, object_id: event.target.value }))}
                  placeholder="object-123"
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Current State</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.state_type_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, state_type_id: event.target.value }))}
                >
                  <option value="">Use initial state</option>
                  {stateNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Payload (JSON)</label>
              <textarea
                className="mt-2 w-full min-h-[120px] rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 font-mono text-xs"
                value={eventForm.payload_json}
                onChange={(event) => setEventForm((prev) => ({ ...prev, payload_json: event.target.value }))}
              />
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Correlation ID</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.correlation_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, correlation_id: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Causation ID</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.causation_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, causation_id: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Actor</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.actor_id}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, actor_id: event.target.value }))}
                />
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Source</label>
                <input
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={eventForm.source}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, source: event.target.value }))}
                />
              </div>
              <div className="flex items-center gap-2 mt-6">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                  checked={eventForm.enqueue}
                  onChange={(event) => setEventForm((prev) => ({ ...prev, enqueue: event.target.checked }))}
                />
                <span className="text-sm text-[color:var(--osd-text)]">Enqueue for processing</span>
              </div>
            </div>
            {eventError ? <p className="text-xs text-red-400">{eventError}</p> : null}
            <button type="button" className="btn btn-primary" onClick={handleCreateEvent}>
              Enqueue Event
            </button>
          </section>

          <section className="glass-card p-5 space-y-4">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Process Queue</h2>
            <div className="flex flex-wrap items-center gap-3">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Limit</label>
                <input
                  type="number"
                  min={1}
                  max={100}
                  className="mt-2 w-24 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={queueLimit}
                  onChange={(event) => setQueueLimit(Number(event.target.value) || 1)}
                />
              </div>
              <button type="button" className="btn btn-primary" onClick={() => processQueue.mutate()}>
                Process Pending
              </button>
            </div>
            <div className="grid gap-2">
              {processResults.length === 0 ? (
                <p className="text-sm text-[color:var(--osd-muted)]">Run processing to record results.</p>
              ) : (
                processResults.map((item) => (
                  <div key={item.queue_id} className="rounded-lg border border-[color:var(--osd-border)] p-3 text-sm">
                    {item.queue_id} · {item.status} · next:{' '}
                    {nodeNameById[item.next_state_id || ''] || item.next_state_id || 'n/a'}
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="glass-card p-5 space-y-4">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Simulation</h2>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Start State</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={simulationStartStateId}
                  onChange={(event) => setSimulationStartStateId(event.target.value)}
                >
                  <option value="">Use initial state</option>
                  {stateNodes.map((node) => (
                    <option key={node.node_id} value={node.node_id}>
                      {node.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2 mt-6">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                  checked={simulationStopOnError}
                  onChange={(event) => setSimulationStopOnError(event.target.checked)}
                />
                <span className="text-sm text-[color:var(--osd-text)]">Stop on first error</span>
              </div>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] p-3 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Guard Overrides</div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setGuardOverrides((prev) => {
                      const next: Record<string, 'default' | 'pass' | 'fail'> = {}
                      Object.keys(prev).forEach((guardId) => {
                        next[guardId] = 'default'
                      })
                      return next
                    })
                  }}
                >
                  Clear
                </button>
              </div>
              {guardOptions.length === 0 ? (
                <p className="text-xs text-[color:var(--osd-muted)]">No guards referenced by transitions.</p>
              ) : (
                <div className="grid gap-2 md:grid-cols-2">
                  {guardOptions.map((guardId) => (
                    <label key={guardId} className="flex items-center justify-between gap-3 text-xs">
                      <span className="text-[color:var(--osd-text)]">
                        {nodeNameById[guardId] || guardId}
                      </span>
                      <select
                        className="rounded border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-2 py-1"
                        value={guardOverrides[guardId] || 'default'}
                        onChange={(event) =>
                          setGuardOverrides((prev) => ({
                            ...prev,
                            [guardId]: event.target.value as 'default' | 'pass' | 'fail',
                          }))
                        }
                      >
                        <option value="default">Default</option>
                        <option value="pass">Force pass</option>
                        <option value="fail">Force fail</option>
                      </select>
                    </label>
                  ))}
                </div>
              )}
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] p-3 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                  Suggested Sequences
                </div>
                <button type="button" className="btn btn-secondary" onClick={handleLoadSequence}>
                  Load
                </button>
              </div>
              {suggestedSequences.length === 0 ? (
                <p className="text-xs text-[color:var(--osd-muted)]">No sequences available from the initial state.</p>
              ) : (
                <div className="grid gap-2">
                  <select
                    className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                    value={selectedSequenceId}
                    onChange={(event) => setSelectedSequenceId(event.target.value)}
                  >
                    <option value="">Select a sequence</option>
                    {suggestedSequences.map((sequence) => (
                      <option key={sequence.id} value={sequence.id}>
                        {sequence.label}
                      </option>
                    ))}
                  </select>
                  {selectedSequence ? (
                    <div className="text-xs text-[color:var(--osd-muted)]">
                      Events:{' '}
                      {selectedSequence.eventIds.map((eventId) => nodeNameById[eventId] || eventId).join(', ')}
                    </div>
                  ) : null}
                </div>
              )}
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                Event Sequence (one per line)
              </label>
              <textarea
                className="mt-2 w-full min-h-[120px] rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 font-mono text-xs"
                value={simulationEventsText}
                onChange={(event) => setSimulationEventsText(event.target.value)}
                placeholder="event.submit&#10;event.approve"
              />
            </div>
            {simulationError ? <p className="text-xs text-red-400">{simulationError}</p> : null}
            <button type="button" className="btn btn-primary" onClick={handleRunSimulation}>
              Run Simulation
            </button>
            <div className="space-y-2">
              {!simulationResult ? (
                <p className="text-sm text-[color:var(--osd-muted)]">Run a simulation to see the transition path.</p>
              ) : (
                <>
                  <div className="text-xs text-[color:var(--osd-muted)]">
                    Start: {nodeNameById[simulationResult.start_state_id] || simulationResult.start_state_id} | Final:{' '}
                    {nodeNameById[simulationResult.final_state_id] || simulationResult.final_state_id}
                  </div>
                  {simulationResult.steps.map((step) => (
                    <div
                      key={`${step.index}-${step.event_type_id}`}
                      className="rounded-lg border border-[color:var(--osd-border)] p-3 text-xs"
                    >
                      <div className="text-[color:var(--osd-text)]">
                        Step {step.index + 1} · Event:{' '}
                        {nodeNameById[step.event_type_id] || step.event_type_id}
                      </div>
                      <div className="text-[color:var(--osd-muted)]">
                        State: {nodeNameById[step.state_before] || step.state_before}
                        {' -> '}
                        {step.next_state_id ? nodeNameById[step.next_state_id] || step.next_state_id : 'unchanged'}
                      </div>
                      <div className="text-[color:var(--osd-muted)]">
                        Status: {step.status}
                        {step.behavior_id ? ` · Behavior: ${nodeNameById[step.behavior_id] || step.behavior_id}` : ''}
                      </div>
                      <div className="text-[color:var(--osd-muted)]">
                        Emits:{' '}
                        {(step.emitted_event_type_ids || [])
                          .map((eventId) => nodeNameById[eventId] || eventId)
                          .join(', ') || 'none'}
                      </div>
                      {step.error ? <div className="text-red-400">Error: {step.error}</div> : null}
                    </div>
                  ))}
                </>
              )}
            </div>
          </section>

          <div className="grid gap-6 lg:grid-cols-3">
            <section className="glass-card p-5 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Queue</h2>
                <select
                  className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-2 py-1 text-xs"
                  value={queueStatus}
                  onChange={(event) => setQueueStatus(event.target.value as typeof queueStatus)}
                >
                  <option value="pending">Pending</option>
                  <option value="handled">Handled</option>
                  <option value="failed">Failed</option>
                  <option value="all">All</option>
                </select>
              </div>
              <div className="space-y-2">
                {queueItems.length === 0 ? (
                  <p className="text-xs text-[color:var(--osd-muted)]">No queue entries.</p>
                ) : (
                  queueItems.map((item: ConceptQueueItem) => (
                    <div key={item.queue_id} className="rounded-lg border border-[color:var(--osd-border)] p-2 text-xs">
                      <div className="text-[color:var(--osd-text)]">{item.event_type_id}</div>
                      <div className="text-[color:var(--osd-muted)]">
                        {item.object_id} · {item.status}
                      </div>
                      {item.last_error ? (
                        <div className="text-[color:var(--osd-muted)]">Error: {item.last_error}</div>
                      ) : null}
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="glass-card p-5 space-y-3">
              <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Event Log</h2>
              <div className="space-y-2">
                {eventLog.length === 0 ? (
                  <p className="text-xs text-[color:var(--osd-muted)]">No events recorded.</p>
                ) : (
                  eventLog.slice(0, 20).map((entry: ConceptEventLogEntry) => (
                    <div key={entry.event_id} className="rounded-lg border border-[color:var(--osd-border)] p-2 text-xs">
                      <div className="text-[color:var(--osd-text)]">
                        {nodeNameById[entry.event_type_id] || entry.event_type_id}
                      </div>
                      <div className="text-[color:var(--osd-muted)]">{entry.object_id}</div>
                      <div className="text-[color:var(--osd-muted)]">{entry.occurred_at || entry.created_at}</div>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="glass-card p-5 space-y-3">
              <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Object States</h2>
              <div className="space-y-2">
                {objectStates.length === 0 ? (
                  <p className="text-xs text-[color:var(--osd-muted)]">No object snapshots yet.</p>
                ) : (
                  objectStates.map((state: ConceptObjectState) => (
                    <div key={state.object_id} className="rounded-lg border border-[color:var(--osd-border)] p-2 text-xs">
                      <div className="text-[color:var(--osd-text)]">{state.object_id}</div>
                      <div className="text-[color:var(--osd-muted)]">
                        {nodeNameById[state.state_type_id] || state.state_type_id}
                      </div>
                      <div className="text-[color:var(--osd-muted)]">{state.updated_at}</div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>
        </div>
      )}

      {activeTab === 'publisher' && (
        <section className="glass-card p-5 space-y-4">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Publisher</h2>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('json')}>
              Export JSON
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('schema')}>
              Export Schema
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('jsonld')}>
              Export JSON-LD
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('markdown')}>
              Export Markdown
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('mermaid')}>
              Export Mermaid
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('dot')}>
              Export DOT
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => exportVersion.mutate('plantuml')}>
              Export PlantUML
            </button>
          </div>
          <div>
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
              {exportFormat.toUpperCase()} Output
            </label>
            <pre className="mt-2 max-h-[420px] overflow-auto rounded-lg border border-[color:var(--osd-border)] bg-black/40 p-4 text-xs text-slate-100">
              {exportContent || 'Run an export to populate the spec output.'}
            </pre>
          </div>
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4">
            <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Export History</div>
            <div className="mt-2 space-y-2 text-xs text-[color:var(--osd-muted)]">
              {(bundle?.version?.exports || []).length === 0
                ? 'No exports recorded yet.'
                : (bundle?.version?.exports || []).map((entry, idx) => (
                    <div key={`export-${idx}`}>
                      {String(entry.format || 'export')} · {String(entry.generated_at || '')}
                    </div>
                  ))}
            </div>
          </div>
        </section>
      )}

      {activeTab === 'ipm' && (
        <div className="space-y-6">
          <section className="glass-card p-5 space-y-4">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Link to IPM Epic</h2>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Project</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={selectedProjectId || ''}
                  onChange={(event) => {
                    setSelectedProjectId(event.target.value)
                    setSelectedEpicId(null)
                  }}
                >
                  {projects.map((project: PmsProject) => (
                    <option key={project.project_id} value={project.project_id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Epic</label>
                <select
                  className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                  value={selectedEpicId || ''}
                  onChange={(event) => setSelectedEpicId(event.target.value)}
                >
                  {epics.map((epic: PmsEpic) => (
                    <option key={epic.epic_id} value={epic.epic_id}>
                      {epic.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] p-3 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Scope Filters</div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setScopeObjects([])
                    setScopeStates([])
                    setScopeEvents([])
                    setScopeBehaviors([])
                  }}
                >
                  Clear Scope
                </button>
              </div>
              <div className="grid gap-3 md:grid-cols-4">
                <div className="space-y-2">
                  <div className="text-xs text-[color:var(--osd-muted)]">Objects</div>
                  <div className="grid gap-1">
                    {objectNodes.map((node) => (
                      <label key={node.node_id} className="flex items-center gap-2 text-xs">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                          checked={scopeObjects.includes(node.node_id)}
                          onChange={(event) => {
                            setScopeObjects((prev) => {
                              const next = new Set(prev)
                              if (event.target.checked) next.add(node.node_id)
                              else next.delete(node.node_id)
                              return Array.from(next)
                            })
                          }}
                        />
                        {node.name}
                      </label>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-[color:var(--osd-muted)]">States</div>
                  <div className="grid gap-1">
                    {stateNodes.map((node) => (
                      <label key={node.node_id} className="flex items-center gap-2 text-xs">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                          checked={scopeStates.includes(node.node_id)}
                          onChange={(event) => {
                            setScopeStates((prev) => {
                              const next = new Set(prev)
                              if (event.target.checked) next.add(node.node_id)
                              else next.delete(node.node_id)
                              return Array.from(next)
                            })
                          }}
                        />
                        {node.name}
                      </label>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-[color:var(--osd-muted)]">Events</div>
                  <div className="grid gap-1">
                    {eventNodes.map((node) => (
                      <label key={node.node_id} className="flex items-center gap-2 text-xs">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                          checked={scopeEvents.includes(node.node_id)}
                          onChange={(event) => {
                            setScopeEvents((prev) => {
                              const next = new Set(prev)
                              if (event.target.checked) next.add(node.node_id)
                              else next.delete(node.node_id)
                              return Array.from(next)
                            })
                          }}
                        />
                        {node.name}
                      </label>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-[color:var(--osd-muted)]">Behaviors</div>
                  <div className="grid gap-1">
                    {behaviorNodes.map((node) => (
                      <label key={node.node_id} className="flex items-center gap-2 text-xs">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                          checked={scopeBehaviors.includes(node.node_id)}
                          onChange={(event) => {
                            setScopeBehaviors((prev) => {
                              const next = new Set(prev)
                              if (event.target.checked) next.add(node.node_id)
                              else next.delete(node.node_id)
                              return Array.from(next)
                            })
                          }}
                        />
                        {node.name}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div className="text-xs text-[color:var(--osd-muted)]">
                Scope selected: {scopeObjects.length} objects · {scopeStates.length} states · {scopeEvents.length} events ·{' '}
                {scopeBehaviors.length} behaviors
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Acceptance Rules</label>
              <textarea
                className="mt-2 w-full min-h-[120px] rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
                value={acceptanceRules}
                onChange={(event) => setAcceptanceRules(event.target.value)}
                placeholder="Optional acceptance rules for the concept link."
              />
            </div>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => createLink.mutate()}
              disabled={isFrozen || !selectedProjectId || !selectedEpicId}
            >
              Link Epic
            </button>
            <div className="grid gap-2">
              {links.map((link) => (
                <div key={link.link_id} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                  <div className="text-sm font-semibold text-[color:var(--osd-text)]">
                    Epic {link.epic_id} · Version {link.concept_version_label || link.concept_version_id}
                  </div>
                  <div className="text-xs text-[color:var(--osd-muted)]">
                    Status: {link.status || 'active'} · Concept: {link.concept_status || 'draft'}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="glass-card p-5 space-y-4">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Generate Backlog</h2>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => generateBacklog.mutate(true)}
                disabled={!selectedProjectId || !selectedVersionId}
              >
                Preview
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => generateBacklog.mutate(false)}
                disabled={!selectedProjectId || !selectedEpicId || !selectedVersionId}
              >
                Create Tasks
              </button>
            </div>
            <div className="grid gap-2">
              {backlogPreview.length === 0 ? (
                <p className="text-sm text-[color:var(--osd-muted)]">Run a preview to list derived work items.</p>
              ) : (
                backlogPreview.map((item) => (
                  <div key={item} className="rounded-lg border border-[color:var(--osd-border)] p-3 text-sm">
                    {item}
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="glass-card p-5 space-y-4">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Backlog Delta</h2>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => fetchBacklogDelta.mutate()}
                disabled={!selectedProjectId || !selectedVersionId}
              >
                Analyze Delta
              </button>
            </div>
            {!backlogDelta ? (
              <p className="text-sm text-[color:var(--osd-muted)]">
                Generate a delta report to see added, changed, or removed transitions.
              </p>
            ) : (
              <div className="grid gap-3 text-sm">
                <div className="text-[color:var(--osd-muted)]">
                  Added {backlogDelta.added.length} · Changed {backlogDelta.changed.length} · Removed{' '}
                  {backlogDelta.removed.length}
                </div>
                {backlogDelta.added.length > 0 && (
                  <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                    <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Added</div>
                    <ul className="mt-2 grid gap-1">
                      {backlogDelta.added.slice(0, 5).map((item) => (
                        <li key={item.title}>{item.title}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {backlogDelta.changed.length > 0 && (
                  <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                    <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Changed</div>
                    <ul className="mt-2 grid gap-1">
                      {backlogDelta.changed.slice(0, 5).map((item) => (
                        <li key={`${item.task_id || 'task'}-${item.transition_id || 'transition'}`}>
                          {item.transition_id || item.task_id}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {backlogDelta.removed.length > 0 && (
                  <div className="rounded-lg border border-[color:var(--osd-border)] p-3">
                    <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Removed</div>
                    <ul className="mt-2 grid gap-1">
                      {backlogDelta.removed.slice(0, 5).map((item) => (
                        <li key={`${item.task_id || 'task'}-${item.transition_id || 'transition'}`}>
                          {item.transition_id || item.task_id}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>

          <section className="glass-card p-5 space-y-3">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Coverage View</h2>
            <div className="text-sm text-[color:var(--osd-muted)]">
              Covered {coverage?.covered || 0} of {coverage?.total || 0} transitions.
            </div>
            <div className="grid gap-2">
              {(coverage?.missing || []).map((transition) => (
                <div key={transition.transition_id} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                  <div className="text-sm text-[color:var(--osd-text)]">
                    Missing: {nodeNameById[transition.state_type_id] || transition.state_type_id} +{' '}
                    {nodeNameById[transition.event_type_id] || transition.event_type_id}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}

      <section className="glass-card p-5 space-y-4">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Create New Model</h2>
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Name</label>
            <input
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={modelName}
              onChange={(event) => setModelName(event.target.value)}
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Context</label>
            <input
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={modelContext}
              onChange={(event) => setModelContext(event.target.value)}
            />
          </div>
        </div>
        <div>
          <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Description</label>
          <textarea
            className="mt-2 w-full min-h-[120px] rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
            value={modelDescription}
            onChange={(event) => setModelDescription(event.target.value)}
          />
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => createModel.mutate()}
          disabled={!modelName.trim()}
        >
          Create Model
        </button>
      </section>
    </div>
  )
}
