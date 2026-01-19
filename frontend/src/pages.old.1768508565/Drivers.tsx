import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Marketplace",
    "path": "/drivers/marketplace"
  },
  {
    "title": "Reviews & Ratings",
    "path": "/drivers/marketplace/reviews"
  },
  {
    "title": "Security Review Pipeline",
    "path": "/drivers/marketplace/security-review"
  },
  {
    "title": "Driver Packs",
    "path": "/drivers/packs"
  },
  {
    "title": "Pack Builder",
    "path": "/drivers/packs/builder"
  },
  {
    "title": "Vertical Editions",
    "path": "/drivers/vertical-editions"
  },
  {
    "title": "Enterprise App Store",
    "path": "/drivers/enterprise-store"
  },
  {
    "title": "Licensing & Entitlements",
    "path": "/drivers/licensing"
  }
]

/**
 * Driver Packs & Marketplace Home
 * Route: /drivers
 */
export default function Drivers() {
  return (
    <CategoryHomeTemplate
      title="Driver Packs & Marketplace"
      description="Category home and dashboard for Driver Packs & Marketplace."
      features={features}
    />
  )
}
