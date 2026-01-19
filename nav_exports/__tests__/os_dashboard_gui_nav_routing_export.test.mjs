// nav_exports/__tests__/os_dashboard_gui_nav_routing_export.test.mjs
// Node >= 18 recommended (uses node:test).
// Purpose: Validate OS_Dashboard_GUI_Nav_Routing_Export.json is structurally valid and self-consistent.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const DEFAULT_EXPORT_PATH = path.resolve(
  process.cwd(),
  "nav_exports/OS_Dashboard_GUI_Nav_Routing_Export.json"
);

const EXPORT_PATH = process.env.NAV_EXPORT_PATH
  ? path.resolve(process.env.NAV_EXPORT_PATH)
  : DEFAULT_EXPORT_PATH;

function loadExportJson() {
  assert.ok(
    fs.existsSync(EXPORT_PATH),
    `Missing export file.\nExpected at: ${EXPORT_PATH}\nTip: set NAV_EXPORT_PATH=/absolute/path/to/OS_Dashboard_GUI_Nav_Routing_Export.json`
  );

  const raw = fs.readFileSync(EXPORT_PATH, "utf8");
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    throw new Error(
      `Export is not valid JSON: ${EXPORT_PATH}\n` +
        `Parse error: ${String(e)}`
    );
  }
  return parsed;
}

function slugify(label) {
  return String(label)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function parseMarkdownRouteList(md) {
  const routes = new Set();
  const lines = String(md).split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/^\s*-\s*route:\s*(.+)\s*$/);
    if (m) routes.add(m[1]);
  }
  return routes;
}

function parseMarkdownSharedFeatureKeys(md) {
  const keys = new Set();
  const lines = String(md).split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/^\s*shared_feature_key:\s*(.+)\s*$/);
    if (m) keys.add(m[1]);
  }
  return keys;
}

function collectGuiNavRoutes(guiNav) {
  const platformPaths = [];
  const categoryHomeRoutes = [];
  const featureRoutes = [];

  for (const p of guiNav.platforms ?? []) {
    if (p?.path) platformPaths.push(p.path);

    for (const c of p.categories ?? []) {
      if (c?.homeRoute) categoryHomeRoutes.push(c.homeRoute);

      for (const f of c.features ?? []) {
        if (f?.route) featureRoutes.push(f.route);
      }
    }
  }

  return { platformPaths, categoryHomeRoutes, featureRoutes };
}

function collectFeatureLabels(guiNav) {
  const labels = [];
  for (const p of guiNav.platforms ?? []) {
    for (const c of p.categories ?? []) {
      for (const f of c.features ?? []) {
        labels.push(String(f.label ?? ""));
      }
    }
  }
  return labels;
}

test("export loads and has expected top-level keys", () => {
  const exp = loadExportJson();

  const expectedKeys = [
    "repo_metadata",
    "nav_sources",
    "ROUTE_MAP.json",
    "GUI_NAV.observed.json",
    "EMPTY_PAGES.md",
    "DUPLICATES.md",
    "PLATFORM_ORDER_RECONCILIATION.md",
  ];

  for (const k of expectedKeys) {
    assert.ok(k in exp, `Missing top-level key: ${k}`);
  }

  assert.equal(typeof exp.repo_metadata, "object");
  assert.ok(Array.isArray(exp.nav_sources), "nav_sources must be an array");
  assert.equal(typeof exp["ROUTE_MAP.json"], "object");
  assert.equal(typeof exp["GUI_NAV.observed.json"], "object");
  assert.equal(typeof exp["EMPTY_PAGES.md"], "string");
  assert.equal(typeof exp["DUPLICATES.md"], "string");
  assert.equal(typeof exp["PLATFORM_ORDER_RECONCILIATION.md"], "string");
});

test("repo_metadata looks sane (commit hash format)", () => {
  const exp = loadExportJson();
  const { branch, last_commit } = exp.repo_metadata ?? {};

  assert.equal(typeof branch, "string");
  assert.ok(branch.length > 0, "repo_metadata.branch must be non-empty");

  assert.equal(typeof last_commit, "string");
  assert.match(
    last_commit,
    /^[0-9a-f]{40}$/,
    "repo_metadata.last_commit must be a 40-char hex SHA"
  );
});

test("nav_sources includes critical nav/routing files", () => {
  const exp = loadExportJson();
  const paths = new Set(
    (exp.nav_sources ?? []).map((x) => x?.path).filter(Boolean)
  );

  const mustInclude = [
    "frontend/src/App.tsx",
    "frontend/src/data/gui_nav.latest.json",
    "frontend/src/data/iaManifest.from_json.ts",
    "frontend/src/navigation/iaGuardrails.ts",
    "frontend/src/components/Layout.tsx",
  ];

  for (const p of mustInclude) {
    assert.ok(paths.has(p), `nav_sources missing expected file: ${p}`);
  }
});

test("ROUTE_MAP routes are unique and structurally valid", () => {
  const exp = loadExportJson();
  const routeMap = exp["ROUTE_MAP.json"];
  assert.ok(
    Array.isArray(routeMap.routes),
    "ROUTE_MAP.json.routes must be an array"
  );

  const seen = new Set();
  for (const r of routeMap.routes) {
    assert.equal(typeof r.route, "string", "route must be string");
    assert.ok(r.route.length > 0, "route must be non-empty string");

    if (r.route !== "*") {
      assert.ok(
        r.route.startsWith("/"),
        `route must start with "/" (or be "*"): ${r.route}`
      );
    }

    assert.equal(typeof r.page_component_path, "string");
    assert.equal(typeof r.is_placeholder_page, "boolean");
    assert.equal(typeof r.has_parameters_execute_results_frame, "boolean");

    assert.ok(!seen.has(r.route), `Duplicate route found in ROUTE_MAP: ${r.route}`);
    seen.add(r.route);
  }
});

test("GUI_NAV routes all exist in ROUTE_MAP (no orphan nav items)", () => {
  const exp = loadExportJson();
  const guiNav = exp["GUI_NAV.observed.json"];
  const routeMap = exp["ROUTE_MAP.json"];

  assert.ok(Array.isArray(guiNav.editions), "GUI_NAV.editions must be array");
  assert.ok(Array.isArray(guiNav.platforms), "GUI_NAV.platforms must be array");

  const routeSet = new Set((routeMap.routes ?? []).map((r) => r.route));
  const { categoryHomeRoutes, featureRoutes } = collectGuiNavRoutes(guiNav);

  const missing = [];
  for (const rt of categoryHomeRoutes) {
    if (!routeSet.has(rt)) missing.push(`Missing category homeRoute in ROUTE_MAP: ${rt}`);
  }
  for (const rt of featureRoutes) {
    if (!routeSet.has(rt)) missing.push(`Missing feature route in ROUTE_MAP: ${rt}`);
  }

  assert.equal(
    missing.length,
    0,
    `GUI_NAV references routes not present in ROUTE_MAP:\n- ${missing.join("\n- ")}`
  );
});

test("EMPTY_PAGES.md exactly matches ROUTE_MAP placeholder flags", () => {
  const exp = loadExportJson();
  const mdRoutes = parseMarkdownRouteList(exp["EMPTY_PAGES.md"]);

  const routeMap = exp["ROUTE_MAP.json"];
  const placeholderRoutes = new Set(
    (routeMap.routes ?? [])
      .filter((r) => r.is_placeholder_page === true)
      .map((r) => r.route)
  );

  const missingInMd = [...placeholderRoutes].filter((r) => !mdRoutes.has(r));
  const extraInMd = [...mdRoutes].filter((r) => !placeholderRoutes.has(r));

  assert.equal(
    missingInMd.length,
    0,
    `Placeholder routes missing from EMPTY_PAGES.md:\n- ${missingInMd.join("\n- ")}`
  );
  assert.equal(
    extraInMd.length,
    0,
    `EMPTY_PAGES.md lists routes that are not placeholders:\n- ${extraInMd.join("\n- ")}`
  );
});

test("DUPLICATES.md covers all duplicate features (by shared_feature_key slug)", () => {
  const exp = loadExportJson();
  const guiNav = exp["GUI_NAV.observed.json"];

  const sharedKeysInMd = parseMarkdownSharedFeatureKeys(exp["DUPLICATES.md"]);
  assert.ok(sharedKeysInMd.size > 0, "DUPLICATES.md has zero shared_feature_key entries");

  const labels = collectFeatureLabels(guiNav);
  const slugCounts = new Map();
  for (const label of labels) {
    const s = slugify(label);
    if (!s) continue;
    slugCounts.set(s, (slugCounts.get(s) ?? 0) + 1);
  }

  const duplicateSlugs = new Set(
    [...slugCounts.entries()]
      .filter(([, count]) => count > 1)
      .map(([slug]) => slug)
  );

  const missingInMd = [...duplicateSlugs].filter((slug) => !sharedKeysInMd.has(slug));
  const extraInMd = [...sharedKeysInMd].filter((slug) => !duplicateSlugs.has(slug));

  assert.equal(
    missingInMd.length,
    0,
    `Duplicate features not documented in DUPLICATES.md:\n- ${missingInMd.join("\n- ")}`
  );
  assert.equal(
    extraInMd.length,
    0,
    `DUPLICATES.md contains keys that are not currently duplicates:\n- ${extraInMd.join("\n- ")}`
  );
});

test.skip("no identity redirects (redirect target equals route)", () => {
  const exp = loadExportJson();
  const routeMap = exp["ROUTE_MAP.json"];

  const identity = [];
  for (const r of routeMap.routes ?? []) {
    const p = r.page_component_path;
    if (typeof p === "string" && p.startsWith("redirect:")) {
      const target = p.slice("redirect:".length);
      if (target === r.route) identity.push(r.route);
    }
  }

  assert.equal(
    identity.length,
    0,
    `Found identity redirects:\n- ${identity.join("\n- ")}`
  );
});
