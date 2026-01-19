#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("node:fs");
const path = require("node:path");

const REPO_ROOT = path.resolve(__dirname, "..");
const GUI_NAV_PATH = path.join(REPO_ROOT, "contracts", "gui", "gui_nav.latest.json");
const ROUTE_MAP_PATH = path.join(REPO_ROOT, "frontend", "src", "navigation", "routeComponentMap.ts");
const APP_PATH = path.join(REPO_ROOT, "frontend", "src", "App.tsx");
const IA_MANIFEST_PATH = path.join(
  REPO_ROOT,
  "frontend",
  "src",
  "data",
  "iaManifest.from_json.ts"
);

const TEMPLATE_FEATURE = "frontend/src/components/templates/FeaturePageTemplate.tsx";
const TEMPLATE_CATEGORY = "frontend/src/components/templates/CategoryHomeTemplate.tsx";
const TEMPLATE_PLATFORM = "frontend/src/components/templates/PlatformLandingTemplate.tsx";

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

const NON_NAV_ROUTES = new Set(['/work']);

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

function loadRouteComponentMap() {
  const text = fs.readFileSync(ROUTE_MAP_PATH, "utf8");
  const block = extractJsonBlock(text, "export const routeComponentMap");
  return block ? JSON.parse(stripTrailingCommas(block)) : {};
}

function loadAppRoutes() {
  const text = fs.readFileSync(APP_PATH, "utf8");
  const importMap = {};
  const importRegex = /import\s+(\w+)\s+from\s+['"](\.\/[^'"]+)['"]/g;
  let match = importRegex.exec(text);
  while (match) {
    importMap[match[1]] = match[2];
    match = importRegex.exec(text);
  }
  const routes = new Set();
  const routeRegex = /<Route\s+path="([^"]+)"\s+element=\{<([^\s>]+)/g;
  let routeMatch = routeRegex.exec(text);
  while (routeMatch) {
    routes.add(routeMatch[1]);
    routeMatch = routeRegex.exec(text);
  }
  return routes;
}

function resolvePlaceholderStatus(componentPath, content) {
  if (!componentPath) return { isPlaceholder: true, reason: "Missing component path" };
  if (componentPath.startsWith("redirect:")) return { isPlaceholder: true, reason: "Redirect placeholder" };
  if (componentPath === TEMPLATE_FEATURE) return { isPlaceholder: false, reason: null };
  if (componentPath === TEMPLATE_CATEGORY || componentPath === TEMPLATE_PLATFORM) {
    return { isPlaceholder: false, reason: null };
  }
  if (!content) return { isPlaceholder: true, reason: "Missing file content" };
  if (content.includes("TODO: Replace MVP scaffold")) {
    return { isPlaceholder: true, reason: "MVP scaffold TODO" };
  }
  if (content.match(/return\s+null\s*;/)) {
    return { isPlaceholder: true, reason: "Empty return" };
  }
  return { isPlaceholder: false, reason: null };
}

function loadLegacyRedirects() {
  const text = fs.readFileSync(IA_MANIFEST_PATH, "utf8");
  const block = extractJsonBlock(text, "export const legacyRedirects");
  return block ? JSON.parse(stripTrailingCommas(block)) : {};
}

function main() {
  const guiNav = JSON.parse(fs.readFileSync(GUI_NAV_PATH, "utf8"));
  const routeComponentMap = loadRouteComponentMap();
  const appRoutes = loadAppRoutes();
  const legacyRedirects = loadLegacyRedirects();

  const failures = [];

  const editions = Array.isArray(guiNav.editions) ? guiNav.editions : [];
  const navRoutes = new Set();
  const routeContracts = new Map();

  for (const edition of editions) {
    const editionLabel = edition?.label || "Unknown";
    const platforms = Array.isArray(edition?.platforms) ? edition.platforms : [];
    const platformLabels = platforms.map((platform) => platform.label);
    const requiredMatch =
      platformLabels.length === REQUIRED_PLATFORM_ORDER.length &&
      platformLabels.every((label, idx) => label === REQUIRED_PLATFORM_ORDER[idx]);
    if (!requiredMatch) {
      failures.push(
        `Edition "${editionLabel}" platform order mismatch. Expected: ${REQUIRED_PLATFORM_ORDER.join(
          " → "
        )}. Found: ${platformLabels.join(" → ")}`
      );
    }

    for (const platform of platforms) {
      const platformLabel = platform?.label || "Unknown";
      const categories = Array.isArray(platform?.categories) ? platform.categories : [];
      if (categories.length < 2) {
        failures.push(`Platform "${platformLabel}" has fewer than 2 categories.`);
      }
      for (const category of categories) {
        const categoryLabel = category?.label || "Unknown";
        const features = Array.isArray(category?.features) ? category.features : [];
        if (features.length < 3) {
          failures.push(
            `Category "${categoryLabel}" under "${platformLabel}" has fewer than 3 features.`
          );
        }
        for (const feature of features) {
          if (!feature || typeof feature !== "object") {
            failures.push(
              `Feature entry in "${platformLabel}" → "${categoryLabel}" is not an object.`
            );
            continue;
          }
          if (!feature.route || typeof feature.route !== "string") {
            failures.push(
              `Feature missing route in "${platformLabel}" → "${categoryLabel}" (${feature.label || "Untitled"})`
            );
            continue;
          }
          if (!Array.isArray(feature.widgets) || feature.widgets.length === 0) {
            failures.push(`Feature "${feature.label || "Untitled"}" missing widgets: ${feature.route}`);
          }
          if (!Array.isArray(feature.displays) || feature.displays.length === 0) {
            failures.push(`Feature "${feature.label || "Untitled"}" missing displays: ${feature.route}`);
          }
          const route = feature.route;
          navRoutes.add(route);
          const contractRef = feature.contracts?.page_contract_ref || "";
          if (!routeContracts.has(route)) {
            routeContracts.set(route, []);
          }
          routeContracts.get(route).push({
            sharedFeatureKey: feature.shared_feature_key,
            contractRef,
          });

          if (!route.startsWith("/")) {
            failures.push(`Feature route must start with "/": ${route}`);
          }
          const componentPath = routeComponentMap[route] || TEMPLATE_FEATURE;
          const fullPath = componentPath.startsWith("frontend/")
            ? path.join(REPO_ROOT, componentPath)
            : path.join(REPO_ROOT, componentPath);
          const content = fs.existsSync(fullPath) ? fs.readFileSync(fullPath, "utf8") : null;

          if (componentPath === TEMPLATE_CATEGORY || componentPath === TEMPLATE_PLATFORM) {
            failures.push(`Feature route uses category/platform template: ${route} → ${componentPath}`);
          }

          const { isPlaceholder, reason } = resolvePlaceholderStatus(componentPath, content);
          if (isPlaceholder) {
            failures.push(`Feature route resolves to placeholder (${reason}): ${route}`);
          }
        }
      }
    }
  }

  for (const route of Object.keys(routeComponentMap)) {
    if (NON_NAV_ROUTES.has(route)) {
      continue;
    }
    const componentPath = routeComponentMap[route];
    if (componentPath === TEMPLATE_CATEGORY || componentPath === TEMPLATE_PLATFORM) {
      continue;
    }
    if (navRoutes.has(route) || appRoutes.has(route) || legacyRedirects[route]) {
      continue;
    }
    failures.push(`Route exists without gui_nav entry: ${route}`);
  }

  for (const [route, entries] of routeContracts.entries()) {
    if (entries.length <= 1) continue;
    const sharedKeys = new Set(entries.map((entry) => entry.sharedFeatureKey));
    const contractRefs = new Set(entries.map((entry) => entry.contractRef));
    if (sharedKeys.has(undefined) || sharedKeys.size > 1) {
      failures.push(`Shared feature key mismatch for route: ${route}`);
    }
    if (contractRefs.size > 1) {
      failures.push(`page_contract_ref mismatch for shared route: ${route}`);
    }
  }

  if (failures.length) {
    console.error("GUI nav validation failed:");
    for (const failure of failures) {
      console.error(`- ${failure}`);
    }
    process.exit(1);
  }

  console.log("GUI nav validation passed.");
}

main();
