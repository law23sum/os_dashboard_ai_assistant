import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Vision Deck Hub",
    "path": "/vision/vision-deck-hub/vision"
  },
  {
    "title": "Vision Roadmap",
    "path": "/vision/roadmap"
  },
  {
    "title": "Vision Glossary",
    "path": "/vision/glossary"
  }
]

/**
 * Vision Deck Hub Home
 * Route: /vision (legacy), /vision/vision-deck-hub/vision (canonical)
 */
export default function Vision() {
  return (
    <CategoryHomeTemplate
      title="Vision Deck Hub"
      description="Category home and dashboard for Vision Deck Hub."
      features={features}
    />
  )
}
