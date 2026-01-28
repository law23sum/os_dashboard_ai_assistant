# Information Architecture Relationship Clarification

## Correct Relationship Model

Based on the Technical Spec v6 and GUI Structure documentation:

### Hierarchy Structure
```
Edition (Personal/Enterprise)
  └── Platform (Top Nav Dropdown Title)
      └── Category (Dropdown List Item → Category Home Page)
          └── Feature (Left Sidebar Item → Feature Page)
```

### Relationship Cardinalities

#### ✅ CORRECT Relationships:

1. **Platform → Category: ONE-TO-MANY**
   - One Platform can have multiple Categories
   - Example: "Mission Control" platform has:
     - "Core Flight Deck" category
     - "Engagement & Persona Surfaces" category
     - "Collaboration & Federation" category

2. **Category → Feature: ONE-TO-MANY**
   - One Category can have multiple Features
   - Example: "Core Flight Deck" category has:
     - "Dashboard" feature
     - "Projects" feature
     - "Tasks" feature
     - "Task Board (Kanban)" feature
     - etc.

3. **Category → Platform: MANY-TO-ONE**
   - Each Category belongs to exactly ONE Platform
   - Example: "Core Flight Deck" belongs ONLY to "Mission Control"

4. **Feature → Category: MANY-TO-ONE**
   - Each Feature belongs to exactly ONE Category
   - Example: "Projects" feature belongs ONLY to "Core Flight Deck"

### ❌ INCORRECT Assumptions (from user query):

1. **"Category can have multiple platforms"** - WRONG
   - A category belongs to ONE platform only
   - Reason: Categories are dropdown items under a specific platform
   - If a category appears in multiple platforms, it's actually a different category with the same name (should be disambiguated)

2. **"Feature can have multiple categories"** - WRONG
   - A feature belongs to ONE category only
   - Reason: Features are left sidebar items within a specific category page
   - If a feature appears in multiple categories, it's actually a different feature (should be disambiguated or consolidated)

3. **"Category to feature is one-to-one"** - WRONG
   - A category can have MANY features
   - Reason: Categories are containers for related features
   - Example: "Core Flight Deck" has 15+ features

4. **"Platform to category is one-to-one"** - WRONG
   - A platform can have MANY categories
   - Reason: Platforms are containers for related categories
   - Example: "Workspaces" platform has 8+ categories

### Valid Use Cases for Similar Names:

While the relationships are strict, similar functionality can exist in different contexts:

1. **Similar Categories in Different Platforms:**
   - "Core Flight Deck" (Mission Control platform)
   - "Dev & DevOps Workspace" (Workspaces platform)
   - Both might have "Projects" features, but they're different features in different contexts

2. **Similar Features in Different Categories:**
   - "Projects" in "Core Flight Deck" (general project management)
   - "Repos" in "Dev & DevOps Workspace" (code repository management)
   - These serve different purposes even if conceptually related

### Edition Visibility:

- **Personal Workstation Edition**: Contains platforms/categories/features for individual use
- **Enterprise Control Plane Add‑Ons**: Contains additional platforms/categories/features for multi-tenant, governed execution
- Some platforms/categories/features may appear in BOTH editions (marked as `"actorScope": "both"`)

### Navigation Rules (IA Invariants):

1. **Platforms** = Top nav dropdown TAB TITLES only
2. **Categories** = Dropdown LIST ITEMS (category home pages)
3. **Features** = Left sidebar ONLY (never in dropdowns)
4. **No Duplication**: A route must exist in exactly ONE place (dropdown OR sidebar, never both)
5. **No Features in Dropdowns**: Features must NEVER appear in platform dropdowns

### Example Structure:

```
Personal Workstation Edition
  └── Mission Control (Platform)
      ├── Core Flight Deck (Category)
      │   ├── Core Flight Deck (Category Home - first item)
      │   ├── Dashboard (Feature)
      │   ├── Projects (Feature)
      │   ├── Tasks (Feature)
      │   └── ... (more features)
      ├── Engagement & Persona Surfaces (Category)
      │   ├── Engagement & Persona Surfaces (Category Home)
      │   ├── Chat (Feature)
      │   ├── Search & Discovery (Feature)
      │   └── ... (more features)
      └── ... (more categories)
  
  └── Workspaces (Platform)
      ├── Dev & DevOps Workspace (Category)
      │   ├── Dev & DevOps Workspace (Category Home)
      │   ├── Repos (Feature)
      │   ├── CI/CD Integration (Feature)
      │   └── ... (more features)
      └── ... (more categories)
```

### Summary:

- **Platform → Category**: ONE-TO-MANY ✅
- **Category → Feature**: ONE-TO-MANY ✅
- **Category → Platform**: MANY-TO-ONE ✅
- **Feature → Category**: MANY-TO-ONE ✅
- **Category ↔ Platform**: NO many-to-many ❌
- **Feature ↔ Category**: NO many-to-many ❌



