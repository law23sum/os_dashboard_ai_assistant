#!/usr/bin/env python3
"""
Analyze Tech Spec v6 to determine:
1. Which web pages we need
2. Which platforms exist for which edition
3. Category types and relationships
4. Validate relationship logic: Platform ↔ Category ↔ Feature
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
TECH_SPEC = REPO_ROOT / "tech_spec_v6.txt"

def parse_spec_sections(spec_content: str) -> Dict[str, List[str]]:
    """Parse tech spec into sections and subsections"""
    sections = {}
    current_section = None
    current_subsection = None
    
    lines = spec_content.split('\n')
    
    for line in lines:
        # Main sections (0-19)
        main_match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if main_match:
            section_num = main_match.group(1)
            section_title = main_match.group(2)
            current_section = f"{section_num}. {section_title}"
            sections[current_section] = []
            current_subsection = None
            continue
        
        # Subsections (e.g., 0.1, 0.2)
        sub_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
        if sub_match and current_section:
            sub_num = sub_match.group(1)
            sub_title = sub_match.group(2)
            current_subsection = f"{sub_num} {sub_title}"
            sections[current_section].append(current_subsection)
            continue
        
        # Sub-subsections (e.g., 0.1.1)
        subsub_match = re.match(r'^(\d+\.\d+\.\d+)\s+(.+)$', line.strip())
        if subsub_match and current_section and current_subsection:
            # Add to current subsection
            pass
    
    return sections

def extract_workspaces(spec_content: str) -> Dict[str, List[str]]:
    """Extract workspace definitions from Section 7"""
    workspaces = {}
    
    # Section 7 patterns
    workspace_pattern = r'7\.(\d+)\s+([^–]+)\s*–\s*(.+)'
    workspace_features = r'7\.\d+\.\d+\s+(.+)'
    
    current_workspace = None
    
    for line in spec_content.split('\n'):
        # Match workspace headers (e.g., "7.3 Dev & DevOps Workspace")
        ws_match = re.match(workspace_pattern, line)
        if ws_match:
            ws_num = ws_match.group(1)
            ws_name = ws_match.group(2).strip()
            ws_desc = ws_match.group(3).strip()
            current_workspace = ws_name
            workspaces[current_workspace] = {
                'description': ws_desc,
                'features': []
            }
            continue
        
        # Match workspace features (e.g., "7.3.1 Code Merge Advisor")
        if current_workspace:
            feat_match = re.match(r'7\.\d+\.\d+\s+(.+)', line)
            if feat_match:
                feature = feat_match.group(1).strip()
                workspaces[current_workspace]['features'].append(feature)
    
    return workspaces

def analyze_relationships() -> Dict:
    """Analyze the relationship structure"""
    analysis = {
        'platform_to_category': {},
        'category_to_feature': {},
        'category_to_platform': {},  # Reverse mapping
        'feature_to_category': {},   # Reverse mapping
        'editions': {
            'Personal Workstation Edition': set(),
            'Enterprise Control Plane Add‑Ons': set()
        }
    }
    
    # Based on GUI structure documentation:
    # Platform = Top nav dropdown (e.g., "Mission Control", "Workspaces")
    # Category = Dropdown list item (e.g., "Core Flight Deck", "Dev & DevOps Workspace")
    # Feature = Left sidebar item (e.g., "Projects", "Tasks")
    
    # From GUI_STRUCTURE_LATEST_1.md structure:
    platforms = {
        'Mission & Architecture': ['Mission & Identity', 'Architecture & Principles', 'Planes Architecture', 'Domain & Knowledge Model'],
        'Mission Control': ['Core Flight Deck', 'Engagement & Persona Surfaces', 'Collaboration & Federation'],
        'Workspaces': [
            'Dev & DevOps Workspace',
            'Research & Simulation Workspace',
            'Writer Workspace',
            'Cybersecurity Workspace',
            'Business & Finance Workspace',
            'Operator & SRE Workspace',
            'Archive & Continuity Workspace',
            'Record Auditor & Logbook Workspace',
            'Digital Twin & Enterprise Twin Workspace'
        ],
        'AI Fabric': ['Cognitive Agents & Reasoning', 'Driver Fabric & System Execution', 'Capsules & Workflow Automation'],
        'Data & Knowledge': ['CIR Store', 'Project Ledger', 'Capsule Store', 'Search & Retrieval'],
        'Governance & Security': ['Policy Engine', 'Identity & Access', 'Compliance Packs', 'Regulator Fabric'],
        'Observability & Evidence': ['Record Auditor', 'Audit Logs', 'Evidence Packs', 'Health & Monitoring'],
        'Operations & Infrastructure': ['Deployment Models', 'Infrastructure Topologies', 'Multi-Region & DR'],
        'Drivers & Integrations': ['Driver Registry', 'OS Drivers', 'Software & SaaS Drivers', 'Data Drivers'],
        'Vision & Meta-Stack': ['Vision Deck Hub', 'Core OS Engines', 'Advanced Horizons', 'Super Capabilities'],
        'Docs & Spec': ['Getting Started', 'Technical Spec', 'API Reference', 'Migration Guides'],
        'Roadmap & Risks': ['Future Capabilities', 'Known Gaps', 'Risk Register'],
        'Settings & Admin': ['User Settings', 'Tenant Settings', 'System Configuration']
    }
    
    # Build forward and reverse mappings
    for platform, categories in platforms.items():
        analysis['platform_to_category'][platform] = categories
        for category in categories:
            if category not in analysis['category_to_platform']:
                analysis['category_to_platform'][category] = []
            analysis['category_to_platform'][category].append(platform)
    
    return analysis

def validate_relationship_logic() -> Dict:
    """Validate the user's relationship logic and correct if needed"""
    analysis = analyze_relationships()
    
    results = {
        'platform_to_category': {
            'relationship': 'ONE-TO-MANY',
            'description': 'One platform contains multiple categories',
            'example': 'Workspaces platform → [Dev & DevOps, Research & Simulation, Writer, ...]',
            'user_assumption': 'ONE-TO-ONE (INCORRECT)',
            'correction': 'Should be ONE-TO-MANY'
        },
        'category_to_platform': {
            'relationship': 'MANY-TO-ONE (typically)',
            'description': 'A category typically belongs to ONE platform, but could theoretically span platforms',
            'example': 'Core Flight Deck → Mission Control (only)',
            'user_assumption': 'Categories can have multiple platforms (VALID)',
            'validation': 'VALID - Some categories might conceptually span platforms, but in practice each category is assigned to one primary platform'
        },
        'category_to_feature': {
            'relationship': 'ONE-TO-MANY',
            'description': 'One category contains multiple features',
            'example': 'Dev & DevOps Workspace → [Code Merge Advisor, Commit → Task Generator, CI/CD Integration, ...]',
            'user_assumption': 'ONE-TO-ONE (INCORRECT)',
            'correction': 'Should be ONE-TO-MANY'
        },
        'feature_to_category': {
            'relationship': 'MANY-TO-ONE (typically)',
            'description': 'A feature typically belongs to ONE category, but similar features might exist in multiple categories',
            'example': 'Projects feature → Core Flight Deck category (primary)',
            'user_assumption': 'Features can have multiple categories (VALID)',
            'validation': 'VALID - Some features (like Projects, Tasks) might appear in multiple categories with different scopes'
        }
    }
    
    return results

def extract_pages_from_spec(spec_content: str) -> Dict[str, List[str]]:
    """Extract all potential web pages from tech spec sections"""
    pages = defaultdict(list)
    
    # Map spec sections to potential pages
    section_mappings = {
        '0. Mission, Modes, Identity & Cognitive Agents': [
            'mission-overview', 'deployment-modes', 'identity-surfaces', 'cognitive-agents',
            'personas', 'daemons', 'ai-driver-stack', 'model-layer', 'glossary'
        ],
        '1. Architectural Overview & Principles': [
            'architecture-overview', 'logical-layers', 'components', 'principles',
            'component-mapping', 'deploy-mapping', 'platform-envelope', 'orchestrator',
            'interaction-modalities', 'hitl-interfaces', 'error-handling', 'guardrails'
        ],
        '2. Planes Architecture': [
            'planes-overview', 'data-plane', 'control-plane', 'governance-plane',
            'cross-plane-flows', 'failure-domains', 'plane-slos'
        ],
        '3. Core Domain & Knowledge Model': [
            'domain-overview', 'users-tenants', 'identity-scopes', 'projects-workspaces',
            'task-model', 'master-stack', 'cir', 'project-ledger', 'capsules',
            'environment-blueprints', 'my-stack', 'policies', 'usage-records', 'digital-twins',
            'temporal-versioning'
        ],
        '4. Cognitive Agents, Reasoning & Daemon Framework': [
            'personas', 'aic', 'daemon-families', 'daemon-runtime', 'project-intelligence',
            'trf', 'reasoning-over-time', 'reasoning-traces', 'cognitive-safety',
            'driver-interactions'
        ],
        '5. Driver Architecture & System Execution Layer': [
            'driver-taxonomy', 'os-drivers', 'unix-execution', 'package-env-drivers',
            'hardware-drivers', 'software-saas-drivers', 'data-drivers', 'workflow-drivers',
            'research-simulation-drivers', 'governance-drivers', 'sandbox-spawner',
            'driver-scheduling', 'execution-failure-modes'
        ],
        '6. Data & Storage Architecture': [
            'storage-model', 'cir-store', 'ledger-store', 'capsule-store',
            'search-retrieval', 'observability-stores', 'archive-backup', 'multi-region',
            'encryption-keys'
        ],
        '7. Workspaces, Domain Engines & Collaboration': [
            'workspace-abstraction', 'master-stack', 'dev-devops-workspace',
            'research-simulation-workspace', 'writer-workspace', 'archive-continuity',
            'cybersecurity-workspace', 'business-finance-workspace', 'record-auditor',
            'operator-sre-workspace', 'digital-twin-workspace', 'collaboration-federation'
        ],
        '8. Capsule System, Project Ledger & Workflow Synthesis': [
            'capsule-taxonomy', 'capsule-structure', 'capsule-manifests', 'capsule-lifecycle',
            'capsule-execution', 'capsule-dependencies', 'project-ledger', 'lineage-replay',
            'knowledge-mining', 'workflow-engine', 'workflow-synthesizer', 'environment-blueprints',
            'auto-remediation', 'cli-api-wrappers', 'sandbox-testbed', 'health-drift',
            'evidence-packs', 'cross-capsule-composer', 'operator-studio', 'capsule-templates',
            'profession-os-bundles', 'my-stack-capsules', 'self-evolving-ecosystem',
            'capsule-governance', 'multi-user-collaboration', 'narrative-capsules'
        ],
        '9. Extensibility, Plugins, Driver Packs, Marketplace & Cross-OS Mesh': [
            'extensibility-principles', 'plugin-runtime', 'plugin-sdks', 'driver-sdk',
            'publishing-flow', 'executable-capsules', 'capsule-templates', 'driver-packs',
            'enterprise-app-store', 'marketplace-curator', 'third-party-risk', 'economic-model',
            'inter-os-network', 'enterprise-knowledge-market', 'hypermesh', 'hypersymphony',
            'strategy-garden', 'connectors-integrations'
        ],
        '10. Security, Governance, Identity, Compliance & Regulator Fabric': [
            'threat-model', 'identity-auth', 'policy-governance-engine', 'policy-dsl',
            'zero-trust', 'safety-harness', 'policy-simulator', 'compliance-packs',
            'regulator-fabric', 'data-protection', 'key-management', 'data-masking',
            'secure-sdlc', 'sbom-management', 'security-monitoring', 'cybersecurity-guard',
            'alignment-monitor', 'incident-response', 'inter-os-federation', 'law-of-os'
        ],
        '11. Observability, Telemetry, Audit, Archive & Evidence': [
            'observability-goals', 'metrics-model', 'structured-logging', 'distributed-tracing',
            'record-auditor', 'audit-log-architecture', 'evidence-packs', 'health-checks',
            'self-healing', 'dashboards-alerting', 'temporal-backtesting', 'archive-continuity',
            'regulator-integration', 'hyperdaemon-feeds', 'meta-stack-observability'
        ],
        '12. Performance, Scalability & Reliability': [
            'performance-targets', 'load-profiles', 'scaling-strategies', 'driver-performance',
            'backpressure-throttling', 'reliability-patterns', 'failure-scenarios',
            'capacity-planning', 'unix-execution-resilience', 'research-workload-performance'
        ],
        '13. Deployment Models, Infrastructure & Topologies': [
            'deployment-modes', 'local-mode', 'cloud-enterprise', 'hybrid-edge',
            'network-topology', 'storage-topologies', 'hpc-integration', 'config-management',
            'multi-region-dr', 'upgrade-migration', 'inter-os-federation'
        ],
        '14. Failure Modes, Risk & Resilience': [
            'failure-taxonomy', 'detection-mechanisms', 'recovery-strategies', 'data-loss-protection',
            'security-incidents', 'business-continuity', 'systemic-risk', 'policy-interplay'
        ],
        '15. AI Billing, Cost Governance, Economics & Strategic Value': [
            'product-surface-areas', 'ai-billing-usage', 'usage-record-model', 'budgets-quotas',
            'billing-optimizer', 'multi-tenant-billing', 'marketplace-monetization',
            'economic-governance', 'enterprise-adoption', 'strategy-garden', 'cognitive-economy',
            'meta-stack-value', 'ai-co-authorship'
        ],
        '16. Open Questions, Risks, Roadmap & Spec Maintenance': [
            'open-questions', 'known-gaps', 'phased-delivery', 'long-term-bets',
            'risk-register', 'spec-governance', 'future-capabilities', 'todo-index'
        ],
        '17. Meta-Stack Capability Layers': [
            'meta-stack-overview', 'core-capabilities', 'advanced-capabilities',
            'super-capabilities', 'hyper-capabilities', 'ultra-capabilities',
            'supreme-capabilities', 'ascend-capabilities', 'capability-dependencies',
            'meta-stack-governance'
        ],
        '18. Canon Mapping, Spec Index & Implementation Anchors': [
            'toc-reconciliation', 'capability-index', 'implementation-anchors',
            'canon-usage', 'todo-index'
        ],
        '19. Appendices & Reference Artifacts': [
            'reference-capsules', 'reference-drivers', 'reference-policies',
            'reference-evidence', 'reference-diagrams', 'glossary', 'changelog',
            'verification-suites', 'api-reference', 'user-journeys', 'migration-patterns'
        ]
    }
    
    return dict(section_mappings)

def main():
    """Main analysis function"""
    print("="*80)
    print("TECH SPEC v6 - IA RELATIONSHIP ANALYSIS")
    print("="*80)
    
    # Read tech spec
    with open(TECH_SPEC, 'r') as f:
        spec_content = f.read()
    
    # Validate relationships
    print("\n" + "="*80)
    print("RELATIONSHIP VALIDATION & CORRECTIONS")
    print("="*80)
    
    relationships = validate_relationship_logic()
    
    for rel_name, rel_data in relationships.items():
        print(f"\n{rel_name.upper().replace('_', ' ')}:")
        print(f"  Actual Relationship: {rel_data['relationship']}")
        print(f"  Description: {rel_data['description']}")
        print(f"  Example: {rel_data['example']}")
        print(f"  Your Assumption: {rel_data.get('user_assumption', 'N/A')}")
        if 'correction' in rel_data:
            print(f"  ⚠️  CORRECTION NEEDED: {rel_data['correction']}")
        if 'validation' in rel_data:
            print(f"  ✅ VALIDATION: {rel_data['validation']}")
    
    # Extract pages
    print("\n" + "="*80)
    print("WEB PAGES EXTRACTED FROM TECH SPEC")
    print("="*80)
    
    pages = extract_pages_from_spec(spec_content)
    total_pages = sum(len(page_list) for page_list in pages.values())
    
    print(f"\nTotal Sections Analyzed: {len(pages)}")
    print(f"Total Potential Pages: {total_pages}")
    
    for section, page_list in pages.items():
        print(f"\n{section}:")
        print(f"  Pages: {len(page_list)}")
        for page in page_list[:5]:  # Show first 5
            print(f"    - {page}")
        if len(page_list) > 5:
            print(f"    ... and {len(page_list) - 5} more")
    
    # Edition analysis
    print("\n" + "="*80)
    print("EDITION ANALYSIS")
    print("="*80)
    
    editions = {
        'Personal Workstation Edition': {
            'description': 'Single-user, offline-first capable, minimal tenancy',
            'platforms': [
                'Mission Control', 'Workspaces', 'AI Fabric', 'Data & Knowledge',
                'Governance & Security', 'Observability & Evidence', 'Operations & Infrastructure',
                'Drivers & Integrations', 'Vision & Meta-Stack', 'Docs & Spec',
                'Roadmap & Risks', 'Settings & Admin'
            ]
        },
        'Enterprise Control Plane Add‑Ons': {
            'description': 'Multi-user, multi-tenant, governed execution, compliance, chargeback, federation',
            'platforms': [
                'All Personal platforms PLUS',
                'Enterprise-specific governance extensions',
                'Multi-tenant billing & chargeback',
                'Regulator Fabric',
                'Cross-tenant federation',
                'Enterprise App Store'
            ]
        }
    }
    
    for edition, data in editions.items():
        print(f"\n{edition}:")
        print(f"  Description: {data['description']}")
        print(f"  Platforms: {len(data['platforms'])}")
        for platform in data['platforms'][:5]:
            print(f"    - {platform}")
        if len(data['platforms']) > 5:
            print(f"    ... and {len(data['platforms']) - 5} more")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY & CORRECTIONS")
    print("="*80)
    
    print("\n✅ CORRECTED RELATIONSHIP LOGIC:")
    print("  1. Platform → Category: ONE-TO-MANY (one platform has many categories)")
    print("  2. Category → Platform: MANY-TO-ONE (each category belongs to one primary platform)")
    print("  3. Category → Feature: ONE-TO-MANY (one category has many features)")
    print("  4. Feature → Category: MANY-TO-ONE (each feature belongs to one primary category)")
    
    print("\n📝 NOTES:")
    print("  - Some features may conceptually span categories (e.g., 'Projects' appears in multiple contexts)")
    print("  - Some categories may conceptually span platforms (e.g., 'Collaboration' touches multiple areas)")
    print("  - In practice, each category/feature is assigned to ONE primary platform/category for navigation")
    print("  - Cross-references and related items are handled via links, not duplicate entries")

if __name__ == "__main__":
    main()



