# IA Structure Clarification - Based on Tech Spec v6

## Structure Hierarchy

```
Edition (Personal/Enterprise) → Platform → Category → Feature
```

## Relationship Model

### ✅ CORRECT Relationships (Enforced):

1. **Platform → Category: ONE-TO-MANY**
   - One platform has many categories
   - Example: "Workspaces" platform has categories: "Dev & DevOps", "Research & Simulation", "Writer", etc.
   - ✅ **This is correct and enforced**

2. **Category → Feature: ONE-TO-MANY**
   - One category has many features
   - Example: "Dev & DevOps Workspace" category has features: "Code Merge Advisor", "Commit → Task Generator", "CI/CD Integration", etc.
   - ✅ **This is correct and enforced**

3. **Category → Platform: MANY-TO-ONE**
   - Each category belongs to exactly ONE platform
   - A category cannot appear in multiple platforms
   - ✅ **This is enforced by structure**

4. **Feature → Category: MANY-TO-ONE**
   - Each feature belongs to exactly ONE category
   - A feature cannot appear in multiple categories
   - ✅ **This is enforced for IA compliance**

### ❌ INCORRECT Assumptions (To Clarify):

**Your question: "does a category have multiple platforms (i think so)"**
- ❌ **NO** - A category belongs to exactly ONE platform
- However, similar categories may exist in different platforms (e.g., "Dev Tools" category in Mission Control vs "Dev Workspace" category in Workspaces)
- These are DIFFERENT categories, not the same category in multiple places

**Your question: "does a feature have multiple categories (i think so)"**
- ❌ **NO** - A feature belongs to exactly ONE category
- However, similar features may exist in different categories (e.g., "Code Review" feature in Dev category vs "Security Review" feature in Cyber category)
- These are DIFFERENT features, not the same feature in multiple places

## Edition (Personal vs Enterprise)

**Edition is NOT a structural element** - it's a **visibility/capability gate**:
- Same IA structure for both editions
- Personal edition: Some features/categories hidden or simplified
- Enterprise edition: All features/categories visible + additional enterprise-only features
- Edition switching changes visibility, not structure

## Example Structure

```
Personal Workstation Edition
└── Mission Control (Platform)
    ├── Core Flight Deck (Category)
    │   ├── Dashboard (Feature)
    │   ├── Projects (Feature)
    │   └── Tasks (Feature)
    └── Engagement & Persona Surfaces (Category)
        ├── Chat (Feature)
        └── Voice (Feature)

└── Workspaces (Platform)
    ├── Dev & DevOps Workspace (Category)
    │   ├── Code Merge Advisor (Feature)
    │   ├── Commit → Task Generator (Feature)
    │   └── CI/CD Integration (Feature)
    └── Research & Simulation Workspace (Category)
        ├── Unified Research Lab (Feature)
        └── Simulation Workbench (Feature)
```

## IA Compliance Rules

1. **Platforms** = Top navigation dropdown TAB TITLES only
2. **Categories** = Dropdown LIST ITEMS (category home pages)
3. **Features** = Left sidebar items ONLY (never in dropdowns)
4. **One-to-One Enforcement:**
   - Category → Platform: one-to-one (each category belongs to one platform)
   - Feature → Category: one-to-one (each feature belongs to one category)
5. **One-to-Many Allowed:**
   - Platform → Category: one-to-many (one platform has many categories)
   - Category → Feature: one-to-many (one category has many features)

## From Tech Spec v6

Based on Section 7 (Workspaces) and other sections:

### Platforms (Top Nav):
1. Mission & Architecture (`/mission`)
2. Mission Control (`/dashboard`)
3. Workspaces (`/workspaces`)
4. Drivers & Integrations (`/drivers`)
5. Governance & Security (`/governance`)
6. Observability & Evidence (`/observability`)
7. Operations & Infrastructure (`/operations`)
8. Data & Knowledge (`/data`)
9. AI & Automation (`/ai`)
10. Roadmap & Planning (`/roadmap`)
11. Settings & Admin (`/settings`)
12. Documentation (`/docs`)
13. Future Capabilities (`/future`)
14. (Additional platforms from spec)

### Categories Example (Workspaces Platform):
- Dev & DevOps Workspace (Section 7.3)
- Research & Simulation Workspace (Section 7.4)
- Writer Workspace (Section 7.5)
- Archive, Continuity & Resonance Workspace (Section 7.6)
- Cybersecurity Workspace (Section 7.7)
- Business / Finance Workspace (Section 7.8)
- Record Auditor & Logbook Workspace (Section 7.9)
- Operator & SRE Workspace (Section 7.10)
- Digital Twin & Enterprise Twin Workspace (Section 7.11)

### Features Example (Dev & DevOps Workspace Category):
- Code Merge Advisor (7.3.1)
- Commit → Task Generator (7.3.2)
- Dev Environment Automation (7.3.3)
- CI/CD & Pipeline Integration (7.3.4)
- Developer Tools Panel (7.3.5)

## Summary

**Your corrected logic:**
- ✅ Platform → Category: **ONE-TO-MANY** (one platform has many categories)
- ✅ Category → Feature: **ONE-TO-MANY** (one category has many features)
- ✅ Category → Platform: **MANY-TO-ONE** (each category belongs to one platform)
- ✅ Feature → Category: **MANY-TO-ONE** (each feature belongs to one category)

**This structure ensures:**
- No duplication in navigation
- Clear ownership of pages
- Predictable routing patterns
- IA compliance


