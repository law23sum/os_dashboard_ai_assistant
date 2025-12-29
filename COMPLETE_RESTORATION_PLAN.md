# Complete Page Restoration Plan

## Current Status

✅ **Route Inventory Built**
- 48 pages found in source commits
- Best commit matrix created (`route_inventory.json`)
- Most pages prefer 'stable' commit (3a154a6)

✅ **Navigation Structure Found**
- `frontend/src/data/navigationStructure.ts` has 190+ routes
- Current structure: Categories → Platforms → Features
- Need to reorganize to: Platforms → Categories → Features

## IA Structure Requirements

### Current Structure (WRONG for IA)
```
Category (top tabs)
  └─ Platform (dropdowns)
      └─ Feature (sidebar)
```

### Required IA Structure
```
Platform (top nav dropdown triggers)
  └─ Category (dropdown items - category home pages)
      └─ Feature (sidebar items)
```

## Next Steps

1. **Parse navigationStructure.ts** and reorganize to IA format
2. **Generate IA manifest** with all ~444 pages
3. **Restore pages** from best commits using `git restore`
4. **Create navigation components** using IA manifest
5. **Add actor switch** for Personal/Enterprise filtering
6. **Add guardrails** to prevent IA violations

## Implementation

The navigationStructure.ts file contains the complete structure but needs reorganization. Each "Platform" in the current structure should become a top-level Platform in IA structure. Each "Category" should become a Category within its Platform. Features remain as Features.





