#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("node:fs");
const path = require("node:path");

const REPO_ROOT = path.resolve(__dirname, "..");
const NAV_PATHS = [
  path.join(REPO_ROOT, "frontend", "src", "data", "gui_nav.latest.json"),
  path.join(REPO_ROOT, "frontend", "public", "gui_nav.latest.json"),
  path.join(REPO_ROOT, "documentation", "gui_nav_structure", "gui_nav.latest.json"),
];

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

const adminKeywords = [
  "admin",
  "tenant",
  "billing",
  "audit",
  "compliance",
  "security",
  "identity",
  "regulator",
  "policy",
  "governance",
  "rbac",
  "scim",
  "sso",
  "roles",
];

const settingsKeywords = [
  "preferences",
  "notification",
  "profile",
  "credential",
  "team",
  "user",
];

const slugIncludes = (value, keywords) => {
  const lowered = value.toLowerCase();
  return keywords.some((keyword) => lowered.includes(keyword));
};

const normalizeEditionName = (edition) => {
  if (edition.toLowerCase().includes("personal")) return "Personal";
  if (edition.toLowerCase().includes("enterprise")) return "Enterprise";
  return edition;
};

const ensurePlatformBuckets = () => {
  const buckets = {};
  for (const label of REQUIRED_PLATFORM_ORDER) {
    buckets[label] = {};
  }
  return buckets;
};

const mergeFeatures = (existing = [], incoming = []) => {
  const byPath = new Map();
  for (const feature of existing) {
    if (feature?.path) byPath.set(feature.path, feature);
  }
  for (const feature of incoming) {
    if (feature?.path && !byPath.has(feature.path)) {
      byPath.set(feature.path, feature);
    }
  }
  return Array.from(byPath.values());
};

const mapPlatform = (platformLabel, categoryLabel) => {
  if (platformLabel === "Mission Control") return "Core";
  if (platformLabel === "AI Fabric") return "Automation";
  if (platformLabel === "Drivers & Integrations") return "Systems";
  if (platformLabel === "Operations & Infrastructure") return "Systems";
  if (platformLabel === "Docs & Spec") return "Libraries";
  if (platformLabel === "Data & Knowledge") return "Knowledge";
  if (platformLabel === "Vision & Meta-Stack") return "Encyclopedia";
  if (platformLabel === "Roadmap & Risks") return "Research";
  if (platformLabel === "Governance & Security") return "Audit Official Records";
  if (platformLabel === "Mission & Architecture") return "Common";
  if (platformLabel === "Observability & Evidence") return "Common";
  if (platformLabel === "Legacy Recovery") return "Common";
  if (platformLabel.startsWith("Settings & Admin")) {
    const lower = categoryLabel.toLowerCase();
    if (slugIncludes(lower, adminKeywords) && !slugIncludes(lower, settingsKeywords)) {
      return "Admin";
    }
    if (slugIncludes(lower, settingsKeywords)) {
      return "Settings";
    }
    return "Settings";
  }
  if (platformLabel === "Workspaces") {
    const lower = categoryLabel.toLowerCase();
    if (lower.includes("research")) return "Research";
    if (lower.includes("simulation") || lower.includes("twin")) return "Simulations";
    return "Workstation";
  }
  return "Common";
};

const ensureKnowledgeAndEncyclopedia = (platforms) => {
  if (!platforms["Encyclopedia"]) platforms["Encyclopedia"] = {};
  if (!platforms["Knowledge"]) platforms["Knowledge"] = {};

  const encyclopediaCategories = {
    Topics: [
      { title: "Topics", path: "/encyclopedia/topics", new: true },
    ],
    Explanations: [
      { title: "Explanations", path: "/encyclopedia/explanations", new: true },
    ],
    History: [
      { title: "History", path: "/encyclopedia/history", new: true },
    ],
    Glossary: [
      { title: "Glossary", path: "/encyclopedia/glossary", new: true },
    ],
  };

  const knowledgeCategories = {
    Perspective: [
      { title: "Perspective", path: "/knowledge/perspective", new: true },
    ],
    Insight: [
      { title: "Insight", path: "/knowledge/insight", new: true },
    ],
    Wisdom: [
      { title: "Wisdom", path: "/knowledge/wisdom", new: true },
    ],
    Experience: [
      { title: "Experience", path: "/knowledge/experience", new: true },
    ],
  };

  for (const [category, features] of Object.entries(encyclopediaCategories)) {
    platforms["Encyclopedia"][category] = mergeFeatures(
      platforms["Encyclopedia"][category],
      features
    );
  }

  for (const [category, features] of Object.entries(knowledgeCategories)) {
    platforms["Knowledge"][category] = mergeFeatures(
      platforms["Knowledge"][category],
      features
    );
  }
};

function migrate() {
  const rawNav = JSON.parse(fs.readFileSync(NAV_PATHS[0], "utf8"));
  const migrated = {};

  for (const [editionLabel, platforms] of Object.entries(rawNav)) {
    const edition = normalizeEditionName(editionLabel);
    if (!migrated[edition]) migrated[edition] = ensurePlatformBuckets();
    if (!platforms || typeof platforms !== "object") continue;

    for (const [platformLabel, categories] of Object.entries(platforms)) {
      if (!categories || typeof categories !== "object") continue;
      for (const [categoryLabel, features] of Object.entries(categories)) {
        const targetPlatform = mapPlatform(platformLabel, categoryLabel);
        if (!migrated[edition][targetPlatform]) {
          migrated[edition][targetPlatform] = {};
        }
        const existing = migrated[edition][targetPlatform][categoryLabel];
        migrated[edition][targetPlatform][categoryLabel] = mergeFeatures(existing, features);
      }
    }

    ensureKnowledgeAndEncyclopedia(migrated[edition]);
  }

  for (const edition of Object.keys(migrated)) {
    const ordered = {};
    for (const label of REQUIRED_PLATFORM_ORDER) {
      ordered[label] = migrated[edition][label] ?? {};
    }
    migrated[edition] = ordered;
  }

  for (const navPath of NAV_PATHS) {
    if (!fs.existsSync(path.dirname(navPath))) continue;
    fs.writeFileSync(navPath, JSON.stringify(migrated, null, 2));
  }

  console.log("Updated gui_nav.latest.json in:", NAV_PATHS.join(", "));
}

migrate();
