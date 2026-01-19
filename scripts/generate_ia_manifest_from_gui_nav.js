#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("node:fs");
const path = require("node:path");

const REPO_ROOT = path.resolve(__dirname, "..");
const NAV_PATH = path.join(REPO_ROOT, "contracts", "gui", "gui_nav.latest.json");
const ROUTE_MAP_PATH = path.join(REPO_ROOT, "frontend", "src", "navigation", "routeComponentMap.ts");
const EXISTING_MANIFEST_PATH = path.join(
  REPO_ROOT,
  "frontend",
  "src",
  "data",
  "iaManifest.from_json.ts"
);

const TEMPLATE_FEATURE = "frontend/src/components/templates/FeaturePageTemplate.tsx";
const TEMPLATE_CATEGORY = "frontend/src/components/templates/CategoryHomeTemplate.tsx";

const PLATFORM_PATHS = {
  Core: "/dashboard",
  Common: "/mission",
  "Audit Official Records": "/governance",
  Automation: "/ai",
  Settings: "/settings",
  Admin: "/admin",
  Workstation: "/workspaces",
  Systems: "/drivers",
  Simulations: "/simulations",
  Research: "/roadmap",
  Encyclopedia: "/vision",
  Libraries: "/docs",
  Knowledge: "/data",
};

function stripTrailingCommas(text) {
  return text.replace(/,\s*([}\]])/g, "$1");
}

function extractJsonBlock(text, startToken) {
  const startIndex = text.indexOf(startToken);
  if (startIndex === -1) return null;
  const assignIndex = text.indexOf("=", startIndex);
  if (assignIndex === -1) return null;
  const firstBrace = text.indexOf("{", assignIndex);
  const firstBracket = text.indexOf("[", assignIndex);
  const openIndex =
    firstBrace === -1 ? firstBracket : firstBracket === -1 ? firstBrace : Math.min(firstBrace, firstBracket);
  const openChar = text[openIndex];
  const closeChar = openChar === "{" ? "}" : "]";
  let depth = 0;
  for (let i = openIndex; i < text.length; i += 1) {
    const ch = text[i];
    if (ch === openChar) depth += 1;
    if (ch === closeChar) depth -= 1;
    if (depth === 0) {
      return text.slice(openIndex, i + 1);
    }
  }
  return null;
}

function normalizePath(value) {
  if (!value) return "";
  let pathValue = value.startsWith("/") ? value : `/${value}`;
  pathValue = pathValue.replace(/\/+/g, "/");
  if (pathValue.length > 1 && pathValue.endsWith("/")) {
    pathValue = pathValue.slice(0, -1);
  }
  return pathValue;
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function deriveActorScope(edition) {
  if (edition.toLowerCase().includes("personal")) return "personal";
  if (edition.toLowerCase().includes("business") || edition.toLowerCase().includes("team")) {
    return "business";
  }
  if (edition.toLowerCase().includes("enterprise")) return "enterprise";
  return "both";
}

function mergeActorScope(current, next) {
  if (!current) return next;
  if (current === next) return current;
  return "both";
}

function loadExistingManifest() {
  const text = fs.readFileSync(EXISTING_MANIFEST_PATH, "utf8");
  const arrayText = extractJsonBlock(text, "export const iaManifest");
  const legacyText = extractJsonBlock(text, "export const legacyRedirects");
  const iaManifest = arrayText ? JSON.parse(stripTrailingCommas(arrayText)) : [];
  const legacyRedirects = legacyText ? JSON.parse(stripTrailingCommas(legacyText)) : {};

  const categories = [];
  const featureComponentByRoute = new Map();

  for (const platform of iaManifest) {
    for (const category of platform.categories) {
      categories.push({
        label: category.label,
        homeRoute: category.homeRoute,
        homeComponentPath: category.homeComponentPath,
        platformLabel: platform.label,
        featureRoutes: new Set(category.features.map((f) => f.route)),
      });
      for (const feature of category.features) {
        featureComponentByRoute.set(feature.route, feature.componentPath);
      }
    }
  }

  return { categories, featureComponentByRoute, legacyRedirects };
}

function loadRouteComponentMap() {
  const text = fs.readFileSync(ROUTE_MAP_PATH, "utf8");
  const block = extractJsonBlock(text, "export const routeComponentMap");
  return block ? JSON.parse(stripTrailingCommas(block)) : {};
}

function findBestCategoryMatch(existingCategories, label, featureRoutes) {
  let best = null;
  let bestScore = -1;
  for (const category of existingCategories) {
    let score = 0;
    if (category.label === label) score += 5;
    for (const route of featureRoutes) {
      if (category.featureRoutes.has(route)) score += 2;
    }
    if (score > bestScore) {
      best = category;
      bestScore = score;
    }
  }
  return bestScore > 0 ? best : null;
}

function ensureUniqueHomeRoute(candidate, usedHomeRoutes, featureRoutes) {
  let route = candidate;
  let suffix = 0;
  while (usedHomeRoutes.has(route) || featureRoutes.has(route)) {
    suffix += 1;
    route = `${candidate}-home-${suffix}`;
  }
  usedHomeRoutes.add(route);
  return route;
}

function generateManifest() {
  const guiNav = JSON.parse(fs.readFileSync(NAV_PATH, "utf8"));
  const { categories: existingCategories, featureComponentByRoute, legacyRedirects } =
    loadExistingManifest();
  const routeComponentMap = loadRouteComponentMap();

  const platforms = [];
  const platformIndex = new Map();
  const usedHomeRoutes = new Set();

  const editions = Array.isArray(guiNav.editions) ? guiNav.editions : [];
  let orderCounter = 1;

  for (const edition of editions) {
    const editionLabel = edition?.label;
    const actorScope = deriveActorScope(editionLabel || "");
    const editionPlatforms = Array.isArray(edition?.platforms) ? edition.platforms : [];
    if (!editionPlatforms.length) continue;

    for (const platformEntry of editionPlatforms) {
      const platformLabel = platformEntry?.label;
      const categories = platformEntry?.categories;
      if (!platformLabel || !categories) continue;
      const platformId = slugify(platformLabel);
      const platformPath = PLATFORM_PATHS[platformLabel] || `/${platformId}`;

      let platform = platformIndex.get(platformLabel);
      if (!platform) {
        platform = {
          id: platformId,
          label: platformLabel,
          path: platformPath,
          actorScope,
          order: orderCounter,
          categories: [],
        };
        platformIndex.set(platformLabel, platform);
        platforms.push(platform);
        orderCounter += 1;
      } else if (platform.actorScope !== actorScope) {
        platform.actorScope = "both";
      }

      if (!Array.isArray(categories)) continue;
      const categoryIndex = new Map(platform.categories.map((c) => [c.label, c]));

      for (const categoryEntry of categories) {
        const categoryLabel = categoryEntry?.label;
        const features = Array.isArray(categoryEntry?.features) ? categoryEntry.features : [];
        if (!categoryLabel) continue;
        const featureRoutes = new Set(
          features
            .filter((f) => f?.route)
            .map((f) => normalizePath(f.route))
        );
        const existingMatch = findBestCategoryMatch(existingCategories, categoryLabel, featureRoutes);

        let homeRoute = existingMatch?.homeRoute;
        if (!homeRoute) {
          const candidate = normalizePath(`${platformPath}/${slugify(categoryLabel)}`);
          homeRoute = ensureUniqueHomeRoute(candidate, usedHomeRoutes, featureRoutes);
        } else {
          usedHomeRoutes.add(homeRoute);
        }

        let category = categoryIndex.get(categoryLabel);
        if (!category) {
          category = {
            id: `${platformId}-${slugify(categoryLabel)}`,
            label: categoryLabel,
            homeRoute,
            homeComponentPath: existingMatch?.homeComponentPath || TEMPLATE_CATEGORY,
            homeBestCommit: "stable",
            actorScope,
            order: platform.categories.length + 1,
            features: [],
          };
          platform.categories.push(category);
          categoryIndex.set(categoryLabel, category);
        } else if (category.actorScope !== actorScope) {
          category.actorScope = "both";
        }

        const nextFeatures = features
          .filter((f) => f?.route)
          .map((feature, index) => {
            const route = normalizePath(feature.route);
            const componentPath =
              routeComponentMap[route] || featureComponentByRoute.get(route) || TEMPLATE_FEATURE;
            return {
              id: `${category.id}-${slugify(feature.label || "feature")}`,
              label: feature.label || "Untitled",
              route,
              componentPath,
              bestCommit: "stable",
              actorScope,
              order: index + 1,
              isNew: false,
            };
          });

        if (category.features.length === 0) {
          category.features = nextFeatures;
        } else {
          const featureIndex = new Map(category.features.map((feature) => [feature.route, feature]));
          for (const feature of nextFeatures) {
            const existing = featureIndex.get(feature.route);
            if (existing) {
              existing.actorScope = mergeActorScope(existing.actorScope, feature.actorScope);
              existing.order = Math.min(existing.order, feature.order);
              if (!existing.componentPath) {
                existing.componentPath = feature.componentPath;
              }
            } else {
              featureIndex.set(feature.route, feature);
            }
          }
          category.features = Array.from(featureIndex.values()).sort((a, b) => a.order - b.order);
        }
      }
    }
  }

  return { platforms, legacyRedirects };
}

function writeManifestFiles(manifest) {
  const jsonPath = path.join(REPO_ROOT, "frontend", "src", "data", "iaManifest.from_json.json");
  const tsPath = path.join(REPO_ROOT, "frontend", "src", "data", "iaManifest.from_json.ts");

  fs.writeFileSync(jsonPath, JSON.stringify(manifest, null, 2));

  const ts = `/**\n * Complete IA Manifest - Generated from gui_nav.latest.json\n * Single Source of Truth for UI navigation\n */\n\nexport type ActorScope = 'personal' | 'business' | 'enterprise' | 'both'\n\nexport interface IAFeature {\n  id: string\n  label: string\n  route: string\n  componentPath: string\n  bestCommit: 'stable' | 'increments' | 'backup'\n  actorScope: ActorScope\n  order: number\n  isNew?: boolean\n}\n\nexport interface IACategory {\n  id: string\n  label: string\n  homeRoute: string\n  homeComponentPath: string\n  homeBestCommit: 'stable' | 'increments' | 'backup'\n  features: IAFeature[]\n  actorScope: ActorScope\n  order: number\n}\n\nexport interface IAPlatform {\n  id: string\n  label: string\n  path: string\n  categories: IACategory[]\n  actorScope: ActorScope\n  order: number\n}\n\nexport const iaManifest: IAPlatform[] = ${JSON.stringify(
    manifest.platforms,
    null,
    2
  )}\n\nexport const legacyRedirects: Record<string, string> = ${JSON.stringify(
    manifest.legacyRedirects,
    null,
    2
  )}\n\nconst allowsActorScope = (itemScope: ActorScope | undefined, actorScope: ActorScope) => {\n  if (!itemScope) return true\n  if (itemScope === 'both' || itemScope === actorScope) return true\n  if (actorScope === 'enterprise' && (itemScope === 'personal' || itemScope === 'business')) return true\n  if (actorScope === 'business' && itemScope === 'personal') return true\n  return false\n}\n\nexport function getPlatforms(actorScope: ActorScope): IAPlatform[] {\n  return iaManifest.filter(p => allowsActorScope(p.actorScope, actorScope))\n}\n\nexport function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {\n  const platform = iaManifest.find(p => p.id === platformId)\n  if (!platform) return []\n  if (!allowsActorScope(platform.actorScope, actorScope)) return []\n  return platform.categories.filter(c => allowsActorScope(c.actorScope, actorScope))\n}\n\nexport function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {\n  const platform = iaManifest.find(p => p.id === platformId)\n  if (!platform) return []\n  const category = platform.categories.find(c => c.id === categoryId)\n  if (!category) return []\n  if (!allowsActorScope(category.actorScope, actorScope)) return []\n  return category.features.filter(f => allowsActorScope(f.actorScope, actorScope))\n}\n\nexport function findRouteContext(route: string): {\n  platform?: IAPlatform\n  category?: IACategory\n  feature?: IAFeature\n  isCategoryHome: boolean\n  isPlatformLanding: boolean\n} {\n  const normalized = route === '/' ? '/' : route.replace(/\\/+$/, '')\n  for (const platform of iaManifest) {\n    if (normalized === platform.path) {\n      return {\n        platform,\n        isCategoryHome: false,\n        isPlatformLanding: true,\n      }\n    }\n  }\n  for (const platform of iaManifest) {\n    for (const category of platform.categories) {\n      if (normalized === category.homeRoute) {\n        return {\n          platform,\n          category,\n          isCategoryHome: true,\n          isPlatformLanding: false,\n        }\n      }\n      for (const feature of category.features) {\n        if (normalized === feature.route) {\n          return {\n            platform,\n            category,\n            feature,\n            isCategoryHome: false,\n            isPlatformLanding: false,\n          }\n        }\n      }\n    }\n  }\n  return { isCategoryHome: false, isPlatformLanding: false }\n}\n`;

  fs.writeFileSync(tsPath, ts);
}

function main() {
  const manifest = generateManifest();
  writeManifestFiles(manifest);
  console.log("Generated IA manifest from gui_nav.latest.json.");
}

main();
