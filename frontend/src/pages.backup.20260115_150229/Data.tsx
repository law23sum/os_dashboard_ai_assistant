import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Data Overview",
    "path": "/data"
  },
  {
    "title": "CIR Store",
    "path": "/data/cir"
  },
  {
    "title": "Capsule Store",
    "path": "/data/capsules"
  },
  {
    "title": "Project Ledger",
    "path": "/data/ledger"
  },
  {
    "title": "Binary Artifacts",
    "path": "/data/artifacts"
  },
  {
    "title": "Schema & Ontology",
    "path": "/data/schema"
  },
  {
    "title": "Ingestion Pipelines",
    "path": "/data/ingestion"
  },
  {
    "title": "Data Lineage",
    "path": "/data/lineage"
  }
]

/**
 * Core Data Stores Home
 * Route: /data
 */
export default function Data() {
  return (
    <CategoryHomeTemplate
      title="Core Data Stores"
      description="Category home and dashboard for Core Data Stores."
      features={features}
    />
  )
}
