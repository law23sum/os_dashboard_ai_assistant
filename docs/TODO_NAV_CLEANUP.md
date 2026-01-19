# TODO: Navigation Cleanup Follow-Ups

1. Verify whether legacy `/mission-control/**` pages are still needed now that legacy redirects point to `/dashboard/**`.
   - Files: `frontend/src/pages/Missioncontrol/**`, `frontend/src/pages/__tests__/Missioncontrol/**`
2. Confirm that `/vision/**` capability routes render the intended content and decide if any `/future/**` routes should remain canonical or be treated as legacy-only.
3. Add an automated check to flag IA manifest routes missing `routeComponentMap` entries (if they should render custom pages).
4. Audit duplicate labels within Vision & Meta-Stack categories to ensure aliases are intentional and documented.
