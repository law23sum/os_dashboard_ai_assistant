"""Knowledge graph visualization for tasks, projects, and relationships."""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

from .db import AssistantState, Task, Project


@dataclass
class GraphNode:
    """A node in the knowledge graph."""
    id: str
    node_type: str  # "task", "project", "document"
    label: str
    data: Dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    """An edge in the knowledge graph."""
    source: str
    target: str
    relationship_type: str  # "depends_on", "belongs_to", "linked_to"
    weight: float = 1.0


@dataclass
class KnowledgeGraph:
    """Knowledge graph representing relationships between entities."""
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)
    
    def add_node(self, node: GraphNode):
        """Add a node to the graph."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: GraphEdge):
        """Add an edge to the graph."""
        self.edges.append(edge)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbor node IDs."""
        neighbors = set()
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.add(edge.target)
            elif edge.target == node_id:
                neighbors.add(edge.source)
        return list(neighbors)
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> 'KnowledgeGraph':
        """Get a subgraph around a specific node."""
        subgraph = KnowledgeGraph()
        
        # Add the starting node
        if node_id in self.nodes:
            subgraph.add_node(self.nodes[node_id])
        
        # BFS to collect nodes and edges
        visited = {node_id}
        queue = [(node_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            # Get neighbors
            for edge in self.edges:
                neighbor_id = None
                if edge.source == current_id:
                    neighbor_id = edge.target
                elif edge.target == current_id:
                    neighbor_id = edge.source
                
                if neighbor_id and neighbor_id not in visited:
                    visited.add(neighbor_id)
                    if neighbor_id in self.nodes:
                        subgraph.add_node(self.nodes[neighbor_id])
                        subgraph.add_edge(edge)
                        queue.append((neighbor_id, current_depth + 1))
        
        return subgraph
    
    def find_critical_path(self) -> List[str]:
        """Find the longest dependency path (critical path)."""
        # Build adjacency list for dependencies
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        
        for edge in self.edges:
            if edge.relationship_type == "depends_on":
                adj[edge.source].append(edge.target)
                in_degree[edge.target] += 1
        
        # Find nodes with no incoming dependencies (start nodes)
        start_nodes = [node_id for node_id in self.nodes.keys() if in_degree[node_id] == 0]
        
        if not start_nodes:
            return []
        
        # DFS to find longest path
        longest_path = []
        
        def dfs(node_id: str, path: List[str]):
            nonlocal longest_path
            if len(path) > len(longest_path):
                longest_path = path.copy()
            
            for neighbor in adj.get(node_id, []):
                if neighbor not in path:  # Avoid cycles
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()
        
        for start in start_nodes:
            dfs(start, [start])
        
        return longest_path
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        node_types = defaultdict(int)
        edge_types = defaultdict(int)
        
        for node in self.nodes.values():
            node_types[node.node_type] += 1
        
        for edge in self.edges:
            edge_types[edge.relationship_type] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
            "density": len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0.0
        }
    
    def to_json(self) -> Dict:
        """Serialize graph to JSON format for visualization."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "type": node.node_type,
                    "label": node.label,
                    "data": node.data
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.relationship_type,
                    "weight": edge.weight
                }
                for edge in self.edges
            ]
        }


def build_knowledge_graph(state: AssistantState) -> KnowledgeGraph:
    """Build a knowledge graph from the assistant state.
    
    Args:
        state: AssistantState with tasks and projects
    
    Returns:
        KnowledgeGraph object
    """
    graph = KnowledgeGraph()
    
    # Add project nodes
    for project in state.projects:
        node_id = f"project:{project.name}"
        graph.add_node(GraphNode(
            id=node_id,
            node_type="project",
            label=project.name,
            data={
                "priority": project.priority,
                "status": project.status,
                "description": project.description
            }
        ))
    
    # Add task nodes and edges
    for task in state.tasks:
        node_id = f"task:{task.id}"
        graph.add_node(GraphNode(
            id=node_id,
            node_type="task",
            label=task.title,
            data={
                "priority": task.priority,
                "status": task.status,
                "project": task.project,
                "due_date": task.due_date,
                "owner": task.owner
            }
        ))
        
        # Add "belongs_to" edge from task to project
        project_node_id = f"project:{task.project}"
        if project_node_id in graph.nodes:
            graph.add_edge(GraphEdge(
                source=node_id,
                target=project_node_id,
                relationship_type="belongs_to",
                weight=1.0
            ))
        
        # Add "depends_on" edge if task has dependency
        if task.depends_on:
            dep_node_id = f"task:{task.depends_on}"
            if dep_node_id in graph.nodes:
                graph.add_edge(GraphEdge(
                    source=node_id,
                    target=dep_node_id,
                    relationship_type="depends_on",
                    weight=1.0
                ))
    
    return graph


def get_dependency_chain(graph: KnowledgeGraph, task_id: str) -> List[str]:
    """Get the full dependency chain for a task (all tasks it depends on)."""
    chain = []
    visited = set()
    
    def traverse(node_id: str):
        if node_id in visited:
            return
        visited.add(node_id)
        
        # Find all dependencies
        for edge in graph.edges:
            if edge.source == node_id and edge.relationship_type == "depends_on":
                chain.append(edge.target)
                traverse(edge.target)
    
    task_node_id = f"task:{task_id}"
    traverse(task_node_id)
    
    return chain


def get_dependent_tasks(graph: KnowledgeGraph, task_id: str) -> List[str]:
    """Get all tasks that depend on the given task."""
    task_node_id = f"task:{task_id}"
    dependents = []
    
    for edge in graph.edges:
        if edge.target == task_node_id and edge.relationship_type == "depends_on":
            dependents.append(edge.source)
    
    return dependents



