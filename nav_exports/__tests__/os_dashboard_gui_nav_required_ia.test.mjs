// nav_exports/__tests__/os_dashboard_gui_nav_required_ia.test.mjs
// Node >= 18 recommended (uses node:test).
// Purpose: Enforce required IA (editions + platform order) for OS Dashboard nav exports.

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

const REQUIRED_EDITIONS = ["Personal", "Enterprise"];

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

function normalizeEditionLabel(edition) {
  if (typeof edition === "string") return edition;
  if (edition && typeof edition === "object") {
    if (typeof edition.label === "string") return edition.label;
    if (typeof edition.name === "string") return edition.name;
    if (typeof edition.id === "string") return edition.id;
  }
  return null;
}

test("GUI_NAV editions match required Personal + Enterprise 🔒", () => {
  const exp = loadExportJson();
  const guiNav = exp["GUI_NAV.observed.json"] ?? {};
  const editions = Array.isArray(guiNav.editions) ? guiNav.editions : [];

  const editionLabels = editions
    .map(normalizeEditionLabel)
    .filter((label) => typeof label === "string" && label.length > 0);

  assert.deepEqual(
    editionLabels,
    REQUIRED_EDITIONS,
    `Expected editions in order: ${REQUIRED_EDITIONS.join(", ")}`
  );
});

test("GUI_NAV platforms are required order and set 🧭", () => {
  const exp = loadExportJson();
  const guiNav = exp["GUI_NAV.observed.json"] ?? {};
  const platforms = Array.isArray(guiNav.platforms) ? guiNav.platforms : [];

  const platformLabels = platforms
    .map((platform) => platform?.label)
    .filter((label) => typeof label === "string" && label.length > 0);

  assert.deepEqual(
    platformLabels,
    REQUIRED_PLATFORM_ORDER,
    "Platform order must match required IA order exactly."
  );
});
