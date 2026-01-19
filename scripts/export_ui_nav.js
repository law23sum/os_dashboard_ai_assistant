#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("node:fs");
const path = require("node:path");

const REPO_ROOT = path.resolve(__dirname, "..");
const OUTPUT_DIR = path.join(REPO_ROOT, "agent_exports", "ui_nav");

const REQUIRED_PLATFORM_ORDER = [
  "Core",
  "Common",
  "Audit Official Records",
  "Automation",
  "Settings",
  "Admin",
  "Workstation",
  "Systems",
  "Simulations",
  "Research",
  "Encyclopedia",
  "Libraries",
  "Knowledge",
];

const TEMPLATE_FEATURE = "frontend/src/components/templates/FeaturePageTemplate.tsx";
const TEMPLATE_CATEGORY = "frontend/src/components/templates/CategoryHomeTemplate.tsx";
const TEMPLATE_PLATFORM = "frontend/src/components/templates/PlatformLandingTemplate.tsx";
const FEATURE_FRAME = "frontend/src/components/templates/FeaturePageFrame.tsx";

const NAV_SOURCE_FILES = [
  {
    path: "frontend/src/App.tsx",
    description: "Top-level routing (public/protected + dynamic routes).",
  },
  {
    path: "frontend/src/navigation/NavRouteRenderer.tsx",
    description: "IA route resolution + lazy loading + template fallbacks.",
  },
  {
    path: "frontend/src/navigation/routeComponentMap.ts",
    description: "Canonical route → component map for IA rendering.",
  },
  {
    path: "frontend/src/data/gui_nav.latest.json",
    description: "Edition-scoped nav source of truth.",
  },
  {
    path: "frontend/src/data/iaManifest.from_json.ts",
    description: "Generated IA manifest + legacyRedirects.",
  },
  {
    path: "frontend/src/data/iaManifest.from_json.json",
    description: "Manifest JSON snapshot.",
  },
  {
    path: "frontend/src/data/iaManifest.ts",
    description: "Canonical manifest re-export.",
  },
  {
    path: "frontend/src/navigation/iaContext.tsx",
    description: "Route → platform/category/feature context.",
  },
  {
    path: "frontend/src/navigation/iaGuardrails.ts",
    description: "IA route validation/duplicate checks.",
  },
  {
    path: "frontend/src/navigation/context.tsx",
    description: "Breadcrumb + active nav derivation.",
  },
  {
    path: "frontend/src/components/Layout.tsx",
    description: "Platform tabs, category dropdowns, feature sidebar, legacy redirects.",
  },
  {
    path: "frontend/src/components/NavigationTree.tsx",
    description: "Tree-network nav UI (uses navigationStructure).",
  },
  {
    path: "frontend/src/components/TreeNetworkNavigation.tsx",
    description: "Tree-network nav UI (uses navigationStructure).",
  },
  {
    path: "frontend/src/data/navigationStructure.ts",
    description: "Tree-network nav data.",
  },
  {
    path: "frontend/src/lib/navigationStructure.ts",
    description: "Helpers for navigationStructure.",
  },
  {
    path: "frontend/src/data/platformFeatures.ts",
    description: "Sidebar feature list by route prefix.",
  },
  {
    path: "frontend/src/components/PlatformFeatureSidebar.tsx",
    description: "Sidebar rendering from platformFeatures.",
  },
  {
    path: "frontend/src/components/templates/FeaturePageTemplate.tsx",
    description: "Feature page template fallback.",
  },
  {
    path: "frontend/src/components/templates/CategoryHomeTemplate.tsx",
    description: "Category home template fallback.",
  },
  {
    path: "frontend/src/components/templates/PlatformLandingTemplate.tsx",
    description: "Platform landing template fallback.",
  },
  {
    path: "frontend/src/pages/RouteScaffold.tsx",
    description: "Generic route scaffold.",
  },
  {
    path: "frontend/src/config/navigation.ts",
    description: "Legacy nav config (unused).",
  },
  {
    path: "frontend/src/data/navigationManifest.ts",
    description: "Spec-driven nav manifest (unused).",
  },
  {
    path: "frontend/src/data/iaCanonical.ts",
    description: "Legacy canonical routing helper (unused).",
  },
  {
    path: "frontend/src/components/LegacyRedirector.tsx",
    description: "Legacy redirect helper (unused).",
  },
];

const PLATFORM_MAPPING = [
  { current: "Mission Control", required: "Core" },
  { current: "Workspaces", required: "Workstation" },
  { current: "AI Fabric", required: "Automation" },
  { current: "Drivers & Integrations", required: "Systems" },
  { current: "Operations & Infrastructure", required: "Systems" },
  { current: "Mission & Architecture", required: "Common" },
  { current: "Observability & Evidence", required: "Common" },
  { current: "Governance & Security", required: "Audit Official Records" },
  { current: "Settings & Admin", required: "Settings/Admin split" },
  { current: "Settings & Admin (Enterprise Extensions)", required: "Settings/Admin split" },
  { current: "Docs & Spec", required: "Libraries" },
  { current: "Vision & Meta-Stack", required: "Encyclopedia" },
  { current: "Data & Knowledge", required: "Knowledge" },
  { current: "Roadmap & Risks", required: "Research" },
  { current: "Legacy Recovery", required: "Common (legacy routing bucket)" },
];

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

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

function resolveImportPath(relPath) {
  const base = relPath.startsWith("./")
    ? path.join(REPO_ROOT, "frontend", "src", relPath.slice(2))
    : path.join(REPO_ROOT, relPath);
  if (path.extname(base)) return path.relative(REPO_ROOT, base);
  const extensions = [".tsx", ".ts", ".jsx", ".js"];
  for (const ext of extensions) {
    const candidate = `${base}${ext}`;
    if (fs.existsSync(candidate)) {
      return path.relative(REPO_ROOT, candidate);
    }
  }
  return path.relative(REPO_ROOT, base);
}

function loadIaManifest() {
  const manifestPath = path.join(REPO_ROOT, "frontend", "src", "data", "iaManifest.from_json.ts");
  const text = fs.readFileSync(manifestPath, "utf8");
  const arrayText = extractJsonBlock(text, "export const iaManifest");
  const legacyText = extractJsonBlock(text, "export const legacyRedirects");
  const iaManifest = arrayText ? JSON.parse(stripTrailingCommas(arrayText)) : [];
  const legacyRedirects = legacyText ? JSON.parse(stripTrailingCommas(legacyText)) : {};
  return { iaManifest, legacyRedirects };
}

function loadRouteComponentMap() {
  const mapPath = path.join(REPO_ROOT, "frontend", "src", "navigation", "routeComponentMap.ts");
  const text = fs.readFileSync(mapPath, "utf8");
  const block = extractJsonBlock(text, "export const routeComponentMap");
  return block ? JSON.parse(stripTrailingCommas(block)) : {};
}

function loadAppRoutes() {
  const appPath = path.join(REPO_ROOT, "frontend", "src", "App.tsx");
  const text = fs.readFileSync(appPath, "utf8");
  const importMap = {};
  const importRegex = /import\s+(\w+)\s+from\s+['"](\.\/[^'"]+)['"]/g;
  let match = importRegex.exec(text);
  while (match) {
    importMap[match[1]] = match[2];
    match = importRegex.exec(text);
  }

  const routes = {};
  const routeRegex = /<Route\s+path="([^"]+)"\s+element=\{<([^\s>]+)/g;
  let routeMatch = routeRegex.exec(text);
  while (routeMatch) {
    const route = routeMatch[1];
    const component = routeMatch[2];
    if (importMap[component]) {
      routes[route] = resolveImportPath(importMap[component]);
    }
    routeMatch = routeRegex.exec(text);
  }

  if (!routes["/admin"] && importMap.Admin) {
    routes["/admin"] = resolveImportPath(importMap.Admin);
  }
  if (!routes["/docs/:page"] && importMap.Documentation) {
    routes["/docs/:page"] = resolveImportPath(importMap.Documentation);
  }
  if (!routes["/future/:slug"] && importMap.FutureDeck) {
    routes["/future/:slug"] = resolveImportPath(importMap.FutureDeck);
  }
  if (!routes["/pms/projects/:projectId"] && importMap.PmsProjectDetail) {
    routes["/pms/projects/:projectId"] = resolveImportPath(importMap.PmsProjectDetail);
  }

  return routes;
}

function buildRouteLabels(iaManifest) {
  const routeToLabels = {};
  const routeToComponent = {};

  for (const platform of iaManifest) {
    routeToLabels[platform.path] = {
      platform: platform.label,
      category: null,
      feature: null,
    };
    routeToComponent[platform.path] = TEMPLATE_PLATFORM;
    for (const category of platform.categories) {
      routeToLabels[category.homeRoute] = {
        platform: platform.label,
        category: category.label,
        feature: null,
      };
      routeToComponent[category.homeRoute] = category.homeComponentPath;
      for (const feature of category.features) {
        routeToLabels[feature.route] = {
          platform: platform.label,
          category: category.label,
          feature: feature.label,
        };
        routeToComponent[feature.route] = feature.componentPath;
      }
    }
  }

  return { routeToLabels, routeToComponent };
}

function isFeatureFrameImplemented(componentPath, content) {
  if (!componentPath) return false;
  if (componentPath === TEMPLATE_FEATURE) return true;
  if (componentPath === FEATURE_FRAME) return true;
  if (!content) return false;
  return (
    content.includes("FeaturePageFrame") ||
    content.includes("data-page-section=\"inputs\"") ||
    content.includes("data-page-section=\"execute\"") ||
    content.includes("data-page-section=\"results\"")
  );
}

function resolvePlaceholderStatus(componentPath, content) {
  if (!componentPath) return { isPlaceholder: true, reason: "Missing component path" };
  if (componentPath.startsWith("redirect:")) {
    return { isPlaceholder: false, reason: null };
  }
  if (componentPath === TEMPLATE_FEATURE) {
    return { isPlaceholder: false, reason: null };
  }
  if (componentPath === TEMPLATE_CATEGORY || componentPath === TEMPLATE_PLATFORM) {
    return { isPlaceholder: false, reason: null };
  }
  if (!content) {
    return { isPlaceholder: true, reason: "Missing file content" };
  }
  if (content.includes("TODO: Replace MVP scaffold")) {
    return { isPlaceholder: true, reason: "MVP scaffold TODO" };
  }
  if (content.match(/return\s+null\s*;/)) {
    return { isPlaceholder: true, reason: "Empty return" };
  }
  return { isPlaceholder: false, reason: null };
}

function loadGuiNav() {
  const navPath = path.join(REPO_ROOT, "frontend", "src", "data", "gui_nav.latest.json");
  return readJson(navPath);
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function ensureOutputDir() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function writeFile(relPath, content) {
  const filePath = path.join(OUTPUT_DIR, relPath);
  fs.writeFileSync(filePath, content);
  return filePath;
}

function main() {
  ensureOutputDir();

  const { iaManifest, legacyRedirects } = loadIaManifest();
  const routeComponentMap = loadRouteComponentMap();
  const appRoutes = loadAppRoutes();
  const guiNav = loadGuiNav();

  const { routeToLabels, routeToComponent } = buildRouteLabels(iaManifest);

  const allRoutes = new Set(Object.keys(routeToLabels));
  Object.keys(appRoutes).forEach((route) => allRoutes.add(route));
  Object.keys(legacyRedirects).forEach((route) => allRoutes.add(route));

  const fileCache = new Map();
  const readFile = (relPath) => {
    if (!relPath || relPath.startsWith("redirect:")) return null;
    if (fileCache.has(relPath)) return fileCache.get(relPath);
    const fullPath = path.join(REPO_ROOT, relPath);
    if (!fs.existsSync(fullPath)) return null;
    const data = fs.readFileSync(fullPath, "utf8");
    fileCache.set(relPath, data);
    return data;
  };

  const routeMap = [];
  const emptyPages = [];

  for (const route of Array.from(allRoutes).sort()) {
    let componentPath = null;
    if (legacyRedirects[route]) {
      componentPath = `redirect:${legacyRedirects[route]}`;
    } else if (appRoutes[route]) {
      componentPath = appRoutes[route];
    } else if (routeComponentMap[route]) {
      componentPath = routeComponentMap[route];
    } else if (routeToComponent[route]) {
      componentPath = routeToComponent[route];
    }

    const content = componentPath ? readFile(componentPath) : null;
    const { isPlaceholder, reason } = resolvePlaceholderStatus(componentPath, content);
    const hasFrame = isFeatureFrameImplemented(componentPath, content);

    const labels = routeToLabels[route] || {};

    routeMap.push({
      route,
      http_or_ui: "ui",
      page_component_path: componentPath ?? "",
      platform_guess: labels.platform ?? null,
      category_guess: labels.category ?? null,
      feature_guess: labels.feature ?? null,
      is_placeholder_page: Boolean(isPlaceholder),
      has_parameters_execute_results_frame: Boolean(hasFrame),
    });

    if (isPlaceholder) {
      emptyPages.push({
        route,
        component: componentPath,
        reason: reason || "Template/placeholder",
      });
    }
  }

  const editions = Object.keys(guiNav);
  const observedPlatforms = iaManifest.map((platform) => ({
    id: platform.id,
    label: platform.label,
    path: platform.path,
    order: platform.order,
    actorScope: platform.actorScope,
    categories: platform.categories.map((category) => ({
      id: category.id,
      label: category.label,
      homeRoute: category.homeRoute,
      homeComponentPath: routeComponentMap[category.homeRoute] || category.homeComponentPath,
      order: category.order,
      actorScope: category.actorScope,
      features: category.features.map((feature) => ({
        id: feature.id,
        label: feature.label,
        route: feature.route,
        componentPath: routeComponentMap[feature.route] || feature.componentPath,
        order: feature.order,
        actorScope: feature.actorScope,
        isNew: feature.isNew || false,
      })),
    })),
  }));

  const observedNav = {
    editions,
    platforms: observedPlatforms,
  };

  const labelMap = new Map();
  for (const platform of observedPlatforms) {
    for (const category of platform.categories) {
      for (const feature of category.features) {
        const key = slugify(feature.label);
        if (!labelMap.has(key)) labelMap.set(key, []);
        labelMap.get(key).push({
          label: feature.label,
          platform: platform.label,
          category: category.label,
          route: feature.route,
          componentPath: feature.componentPath,
        });
      }
    }
  }

  const duplicateGroups = [...labelMap.entries()].filter(([, items]) => items.length > 1);

  const duplicatesMd = [
    "# Duplicate Features",
    "",
    ...duplicateGroups.flatMap(([slug, items]) => {
      const label = items[0].label;
      const routes = new Set(items.map((item) => item.route));
      const components = new Set(items.map((item) => item.componentPath));
      return [
        `- feature_label: ${label}`,
        `  shared_feature_key: ${slug}`,
        ...items.map(
          (item) =>
            `  occurrence: ${item.platform} > ${item.category} | ${item.route} | ${item.componentPath}`
        ),
        `  same_route: ${routes.size === 1}`,
        `  same_component: ${components.size === 1}`,
      ];
    }),
  ].join("\n");

  const emptyPagesMd = [
    "# Empty/Placeholder Pages",
    "",
    ...emptyPages.map((item) => {
      const fix = item.reason?.includes("MVP scaffold")
        ? "Replace MVP scaffold with live data wiring and FeaturePageFrame."
        : "Replace placeholder content with real UI/data wiring.";
      return `- route: ${item.route}\n  component: ${item.component}\n  reason: ${item.reason}\n  quick_fix: ${fix}`;
    }),
  ].join("\n");

  const currentPlatformOrder = observedPlatforms.map((p) => p.label);
  const missing = REQUIRED_PLATFORM_ORDER.filter((p) => !currentPlatformOrder.includes(p));
  const extra = currentPlatformOrder.filter((p) => !REQUIRED_PLATFORM_ORDER.includes(p));

  const platformReconMd = [
    "# Platform Order Reconciliation",
    "",
    "## Current platform order (from iaManifest)",
    ...currentPlatformOrder.map((label) => `- ${label}`),
    "",
    "## Required platform order",
    ...REQUIRED_PLATFORM_ORDER.map((label) => `- ${label}`),
    "",
    "## Gaps",
    `- missing_required: ${missing.length ? missing.join(", ") : "none"}`,
    `- extra_current: ${extra.length ? extra.join(", ") : "none"}`,
  ].join("\n");

  const platformMappingMd = [
    "# Platform Mapping",
    "",
    "| current_platform | required_platform | notes |",
    "| --- | --- | --- |",
    ...PLATFORM_MAPPING.map(
      (row) => `| ${row.current} | ${row.required} | ${row.notes ?? ""} |`
    ),
    "",
    "Notes:",
    "- Re-bucketing preserves routes; only nav grouping changes.",
  ].join("\n");

  const resolvedByTemplate = routeMap.filter(
    (item) => item.page_component_path === TEMPLATE_FEATURE
  ).length;

  const emptyPagesResolutionMd = [
    "# Empty Pages Resolution Checklist",
    "",
    `- FeaturePageTemplate routes upgraded via FeaturePageFrame: ${resolvedByTemplate}`,
    `- Remaining placeholders: ${emptyPages.length}`,
    "",
    "Remaining placeholders (if any):",
    ...emptyPages.map((item) => `- ${item.route} (${item.reason})`),
  ].join("\n");

  const finalReportMd = [
    "# UI Nav Export Final Report",
    "",
    `- Total routes: ${routeMap.length}`,
    `- Placeholder routes: ${emptyPages.length}`,
    `- FeaturePageTemplate routes: ${resolvedByTemplate}`,
    `- Platforms (current): ${currentPlatformOrder.length}`,
    "",
    "Generated files:",
    "- ROUTE_MAP.json",
    "- GUI_NAV.observed.json",
    "- EMPTY_PAGES.md",
    "- DUPLICATES.md",
    "- PLATFORM_ORDER_RECONCILIATION.md",
    "- PLATFORM_MAPPING.md",
    "- EMPTY_PAGES_RESOLUTION.md",
  ].join("\n");

  let branch = process.env.GIT_BRANCH;
  let lastCommit = process.env.GIT_COMMIT;
  try {
    const { execSync } = require("node:child_process");
    if (!branch) {
      branch = execSync("git rev-parse --abbrev-ref HEAD", { cwd: REPO_ROOT, encoding: "utf8" }).trim();
    }
    if (!lastCommit) {
      lastCommit = execSync("git rev-parse HEAD", { cwd: REPO_ROOT, encoding: "utf8" }).trim();
    }
  } catch {
    // ignore git lookup failures
  }

  const repoMeta = {
    branch: branch || "unknown",
    last_commit: lastCommit || "unknown",
    package_managers_detected: [
      "npm (package.json, package-lock.json)",
      "pip (requirements.txt)",
      "pyproject.toml",
    ],
  };

  writeFile("ROUTE_MAP.json", JSON.stringify({ routes: routeMap }, null, 2));
  writeFile("GUI_NAV.observed.json", JSON.stringify(observedNav, null, 2));
  writeFile("EMPTY_PAGES.md", emptyPagesMd);
  writeFile("DUPLICATES.md", duplicatesMd);
  writeFile("PLATFORM_ORDER_RECONCILIATION.md", platformReconMd);
  writeFile("PLATFORM_MAPPING.md", platformMappingMd);
  writeFile("EMPTY_PAGES_RESOLUTION.md", emptyPagesResolutionMd);
  writeFile("FINAL_REPORT.md", finalReportMd);

  const consolidated = {
    repo_metadata: repoMeta,
    nav_sources: NAV_SOURCE_FILES,
    "ROUTE_MAP.json": { routes: routeMap },
    "GUI_NAV.observed.json": observedNav,
    "EMPTY_PAGES.md": emptyPagesMd,
    "DUPLICATES.md": duplicatesMd,
    "PLATFORM_ORDER_RECONCILIATION.md": platformReconMd,
  };
  writeFile("OS_Dashboard_GUI_Nav_Routing_Export.json", JSON.stringify(consolidated, null, 2));

  console.log(`Wrote exports to ${OUTPUT_DIR}`);
}

main();
