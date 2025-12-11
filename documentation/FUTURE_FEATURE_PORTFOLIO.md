# Future Feature Portfolio Scaffolding

This repository now ships with a canonical registry of forward-looking capabilities plus matching UI/UX scaffolding so each engine can be fleshed out without rewriting the GUI.

## Data layer (`assistant_hub_gui/assistant_hub/future_features.py`)
- `FutureFeature` records the 10.x capability metadata (code, tier, lifetime value, summary).
- `FUTURE_FEATURES` enumerates every entry from Master Stack (10.1) through the Meta Envelope (10.49).
- Helper functions (`get_features_by_tier`, `get_feature_lookup`, `tier_palette`) keep the UI data-driven.
- To add a new capability, drop another `FutureFeature` entry and it will automatically appear in the GUI, the tier filters, and the generated HTML roadmaps.

## Desktop GUI (`assistant_hub_gui/assistant_hub/gui.py`)
- A new **Future Features** workspace lives alongside the classic tabs (look for `_build_future_features_tab`).
- The top toolbar exposes reorganized "Suites" dropdowns plus the existing navigation control, so the interface reads like a collection of software stacks instead of a single monolith.
- The Future Features tab includes:
  - Tier filter + capability jump-to controls.
  - Tree navigation grouped by tier, driven entirely by the data module.
  - Blank implementation canvases using `ttkbootstrap`’s `ScrolledFrame` so future requirements can be sketched before any backend code exists.
  - Buttons for copying summaries and adding TODO boards to keep planning lightweight.
- `_build_future_feature_tier_doc_map` wires each tier to a static HTML canvas (see below) so product notes can live outside the Tk view if needed.

## Web placeholders (`docs/future_*.html`)
- Each tier now has a static HTML "blank page" generated from the data catalog (`future_core_os.html`, `future_advanced.html`, etc.).
- These pages show up inside the GUI’s "Web pages" dropdown and can also be opened directly via the "Open tier web page" button on the Future Features tab.
- The pages intentionally contain only structured placeholders: a feature backlog list, an empty implementation canvas, and a notes block.
- Update `assistant_hub_gui/assistant_hub/future_features.py` and re-run the generator snippet in `docs/` to refresh the content.

## Extending the scaffolding
1. Add/modify `FutureFeature` entries (and, if needed, extend `tier_palette`).
2. Re-run the short generator snippet (see commit history or copy it into a helper script) to rebuild the HTML placeholders inside `docs/` so the dropdown stays in sync.
3. Drop any concrete implementation widgets into `_build_future_features_tab`—every control is already wired to `self.future_feature_lookup` so you can fetch metadata in one line.
4. Reference the GUI tab from other modules through `_navigate_to_future_feature` to deep-link from analytics, AI Ops, etc.

This structure keeps today’s app lean while making it obvious where each future engine will live.
