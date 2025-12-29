# IA Relationships - Corrected Model

## Analysis Results

Based on analysis of `gui_nav.latest.json` and the tech spec, here are the **corrected** relationship models:

### ✅ CORRECTED RELATIONSHIPS

1. **Platform → Categories: ONE-TO-MANY** (not one-to-one)
   - One platform contains multiple categories
   - Example: "Mission Control" platform has 3 categories:
     - Core Flight Deck
     - Engagement & Persona Surfaces  
     - Collaboration & Federation

2. **Category ↔ Platforms: MANY-TO-MANY** ✅ (Your intuition was correct!)
   - Categories CAN appear in multiple platforms
   - **18 categories** currently appear in multiple platforms
   - Example: "Dev & DevOps Workspace" appears in:
     - "Workspaces" (Personal Edition)
     - "Workspaces (Enterprise Extensions)" (Enterprise Edition)

3. **Category → Features: ONE-TO-MANY** (not one-to-one)
   - One category contains multiple features
   - Example: "Core Flight Deck" category has 20 features:
     - Dashboard, Projects, Tasks, Task Board, etc.

4. **Feature ↔ Categories: MANY-TO-MANY** ✅ (Your intuition was correct!)
   - Features CAN appear in multiple categories
   - **79 features** currently appear in multiple categories
   - Examples:
     - "Overview" appears in 79 categories
     - "Todos" appears in 64 categories
     - "Capability Matrix" appears in 8 categories

## Current Statistics

### Editions
- **Personal Workstation Edition**: 7 platforms, 43 categories, 460 features
- **Enterprise Control Plane Add-Ons**: 8 platforms, 55 categories, 409 features

### Multi-Platform Categories (18 total)
- Dev & DevOps Workspace
- Research & Simulation Workspace
- Writer Workspace
- Cybersecurity Workspace
- Business & Finance Workspace
- Operator & SRE Workspace
- Archive & Continuity Workspace
- Digital Twin & Enterprise Twin Workspace
- Record Auditor & Logbook Workspace
- User & Tenant Settings
- ... and 8 more

### Multi-Category Features (79 total)
- Overview (79 categories)
- Todos (64 categories)
- Capability Matrix (8 categories)
- Packs (4 categories)
- Collaboration (3 categories)
- Runbooks (3 categories)
- ... and 73 more

## Corrected Model Summary

```
Platform (1) ──→ (N) Categories  [ONE-TO-MANY]
Platform (N) ←── (1) Category    [MANY-TO-MANY - categories can appear in multiple platforms]

Category (1) ──→ (N) Features     [ONE-TO-MANY]
Category (N) ←── (1) Feature     [MANY-TO-MANY - features can appear in multiple categories]
```

## Implications for Navigation

1. **Platform Dropdowns** (Top Nav):
   - Show all platforms for the current edition
   - Each platform dropdown lists its categories
   - Categories that appear in multiple platforms will show in each platform's dropdown

2. **Category Home Pages**:
   - Each category has a home page (first feature in the list)
   - Category home pages can be accessed from multiple platforms if the category appears in multiple platforms

3. **Feature Sidebar** (Left Side):
   - Shows features for the currently selected category
   - Features that appear in multiple categories will show in each category's sidebar

4. **Routing**:
   - Platform routes: `/{platform}`
   - Category routes: `/{platform}/{category}` (or just `/{category}` if category is unique)
   - Feature routes: `/{platform}/{category}/{feature}` (or `/{category}/{feature}` if unique)

## Next Steps for Merge

When merging branches, we need to:
1. Preserve all platforms (maximize platform count)
2. Preserve all categories (maximize category count) 
3. Preserve all features (maximize feature count)
4. Handle many-to-many relationships correctly:
   - If a category appears in multiple platforms, ensure it's present in all relevant platforms
   - If a feature appears in multiple categories, ensure it's present in all relevant categories
5. Resolve path conflicts (134 duplicate paths detected - these need resolution)



