"""Knowledge graph utilities for visualizing relationships between tasks, projects, and documents."""

from typing import Dict, List, Set, Optional
from collections import defaultdict
from dataclasses import dataclass

from .db import AssistantState, Task, Project


@dataclass
class GraphNode:
    """A node in the knowledge graph."""
    id: str
    type: str  # "task", "project", "document"
    label: str
    properties: Dict


@dataclass
class GraphEdge:
    """An edge (relationship) in the knowledge graph."""
    source: str
    target: str
    type: str  # "depends_on", "belongs_to", "linked_to", "related_to"
    weight: float = 1.0


class KnowledgeGraph:
    """Knowledge graph representing relationships in the system."""
    
    def __init__(self, state: AssistantState):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._build_graph(state)
    
    def _build_graph(self, state: AssistantState):
        """Build the knowledge graph from state."""
        # Add project nodes
        for project in state.projects:
            node_id = f"project:{project.name}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                type="project",
                label=project.name,
                properties={
                    "status": project.status,
                    "priority": project.priority,
                    "description": project.description
                }
            )
        
        # Add task nodes and edges
        for task in state.tasks:
            node_id = f"task:{task.id}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                type="task",
                label=task.title,
                properties={
                    "status": task.status,
                    "priority": task.priority,
                    "project": task.project,
                    "owner": task.owner,
                    "due_date": task.due_date
                }
            )
            
            # Task -> Project edge
            project_node_id = f"project:{task.project}"
            if project_node_id in self.nodes:
                self.edges.append(GraphEdge(
                    source=node_id,
                    target=project_node_id,
                    type="belongs_to",
                    weight=1.0
                ))
            
            # Task dependency edges
            if task.depends_on:
                dep_node_id = f"task:{task.depends_on}"
                if dep_node_id in self.nodes:
                    self.edges.append(GraphEdge(
                        source=node_id,
                        target=dep_node_id,
                        type="depends_on",
                        weight=2.0  # Dependencies are stronger relationships
                    ))
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[GraphNode]:
        """Get neighboring nodes."""
        neighbors = []
        for edge in self.edges:
            if edge.source == node_id:
                if edge_type is None or edge.type == edge_type:
                    node = self.nodes.get(edge.target)
                    if node:
                        neighbors.append(node)
            elif edge.target == node_id:
                if edge_type is None or edge.type == edge_type:
                    node = self.nodes.get(edge.source)
                    if node:
                        neighbors.append(node)
        return neighbors
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> 'KnowledgeGraph':
        """Get a subgraph around a specific node."""
        subgraph = KnowledgeGraph.__new__(KnowledgeGraph)
        subgraph.nodes = {}
        subgraph.edges = []
        
        visited: Set[str] = set()
        to_visit = [(node_id, 0)]
        
        while to_visit:
            current_id, current_depth = to_visit.pop(0)
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            if current_id in self.nodes:
                subgraph.nodes[current_id] = self.nodes[current_id]
            
            # Add edges and neighbors
            for edge in self.edges:
                if edge.source == current_id and edge.target not in visited:
                    if edge.target in self.nodes:
                        subgraph.nodes[edge.target] = self.nodes[edge.target]
                        subgraph.edges.append(edge)
                        to_visit.append((edge.target, current_depth + 1))
                elif edge.target == current_id and edge.source not in visited:
                    if edge.source in self.nodes:
                        subgraph.nodes[edge.source] = self.nodes[edge.source]
                        # Reverse edge for subgraph
                        reversed_edge = GraphEdge(
                            source=edge.target,
                            target=edge.source,
                            type=edge.type,
                            weight=edge.weight
                        )
                        subgraph.edges.append(reversed_edge)
                        to_visit.append((edge.source, current_depth + 1))
        
        return subgraph
    
    def get_dependency_chain(self, task_id: int) -> List[Task]:
        """Get the full dependency chain for a task."""
        chain = []
        visited: Set[int] = set()
        
        def traverse(current_id: int):
            if current_id in visited:
                return
            visited.add(current_id)
            
            node_id = f"task:{current_id}"
            node = self.nodes.get(node_id)
            if not node:
                return
            
            # Find dependencies (tasks this depends on)
            for edge in self.edges:
                if edge.source == node_id and edge.type == "depends_on":
                    dep_id = int(edge.target.split(":")[1])
                    traverse(dep_id)
            
            chain.append(current_id)
        
        traverse(task_id)
        return chain
    
    def find_critical_path(self) -> List[str]:
        """Find critical path through task dependencies."""
        # Simple implementation: longest dependency chain
        chains = []
        
        # Find all tasks with no dependencies
        task_nodes = [n for n in self.nodes.values() if n.type == "task"]
        root_tasks = []
        
        for node in task_nodes:
            has_deps = any(e.source == node.id and e.type == "depends_on" for e in self.edges)
            if not has_deps:
                root_tasks.append(node.id)
        
        # Build chains from root tasks
        for root_id in root_tasks:
            chain = self._build_chain(root_id, [])
            if chain:
                chains.append(chain)
        
        # Return longest chain
        if chains:
            return max(chains, key=len)
        return []
    
    def _build_chain(self, node_id: str, current_chain: List[str]) -> List[str]:
        """Recursively build a dependency chain."""
        if node_id in current_chain:  # Cycle detection
            return current_chain
        
        current_chain = current_chain + [node_id]
        longest_chain = current_chain
        
        # Find dependent tasks (tasks that depend on this one)
        for edge in self.edges:
            if edge.target == node_id and edge.type == "depends_on":
                dep_chain = self._build_chain(edge.source, current_chain)
                if len(dep_chain) > len(longest_chain):
                    longest_chain = dep_chain
        
        return longest_chain
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary format (for JSON serialization)."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type,
                    "label": node.label,
                    "properties": node.properties
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "weight": edge.weight
                }
                for edge in self.edges
            ]
        }
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        node_types = defaultdict(int)
        edge_types = defaultdict(int)
        
        for node in self.nodes.values():
            node_types[node.type] += 1
        
        for edge in self.edges:
            edge_types[edge.type] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
            "density": len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0
        }


def build_knowledge_graph(state: AssistantState) -> KnowledgeGraph:
    """Build a knowledge graph from the current state."""
    return KnowledgeGraph(state)

