# Maintaining Manuel Perilla's profile

The profile is `ManuelPerilla/ManuelPerilla`; `main` contains its source and the orphan `output` branch contains four generated SVGs. The 2172 × 724 PNG banner, technology icons and small vector animations are stored under `.assets`.

## Daily refresh

`.github/workflows/snake.yml` runs at **00:00 America/Bogota**, expressed as `0 5 * * *` in GitHub's default UTC schedule. It also runs on relevant pushes to `main` and can be started manually from **Actions → Profile | Manuel Perilla → Run workflow**. Scheduled runs can be delayed by GitHub; inactive public repositories may have their schedules disabled after 60 days.

The workflow uses the automatic `GITHUB_TOKEN` with `contents: write`; no personal access token is required. It generates the snake, both statistics cards and the activity dashboard, validates the SVGs, and publishes them together. A failed generation leaves the previous successful output in place. Only activity visible to this workflow is requested; no additional access to private repositories is configured. No repository is made public by this workflow.

## Activity calculations

`activity.svg` uses the contribution dates and counts returned by GitHub's GraphQL contribution calendar. It does not estimate activity from the listed tech stack or use simulated data.

- Contributions and active days cover the last 365 calendar dates, ending today in UTC.
- The current streak counts consecutive dates with contributions. If today has no contributions yet, counting starts yesterday; a quiet yesterday breaks the streak.
- The longest streak is limited to that same 365-day window, not the account's entire lifetime.
- The chart groups the last 84 dates into twelve consecutive seven-day buckets. Its final bucket includes the current partial day; these are not necessarily Monday-to-Sunday weeks.
- Counts follow GitHub's contribution attribution rules and may not match every commit ever pushed.
- Unit tests cover quiet days, gaps, window boundaries, leap days, empty data and invalid data.

The subtle pulse animations have reduced-motion alternatives. The banner is a sharp static PNG; typing and the contribution snake provide larger movement without an autoplaying low-resolution video.

## Statistics availability

The public `github-readme-stats.vercel.app` endpoints returned HTTP 503 during setup. Each statistics `<picture>` therefore prefers the SVG generated daily by GitHub Readme Stats Action, while retaining the requested, color-configured API URL in its `<img>` fallback. Browser fallback is based on image format support, not network errors; if an output file is missing, check the workflow and regenerate it.

The Top Languages card reports languages detected in public repositories. If none are available yet, it will show an empty-data message; it does not invent a language breakdown from the declared tech stack.

## GitHub rendering

Images and generated cards use a permanent dark palette. GitHub controls the surrounding page theme and its table borders; README HTML cannot force the visitor's entire page into dark mode or override GitHub's CSS. `border="0"` expresses the layout intent, but GitHub may still draw table borders.

The snake uses a real `<img alt="Snake animation">` inside `<picture>`, the HTML equivalent of `![Snake animation](https://raw.githubusercontent.com/ManuelPerilla/ManuelPerilla/output/github-contribution-grid-snake-dark.svg)`. This keeps the README valid HTML and avoids displaying unparsed Markdown inside a raw HTML block.

To change the banner, replace `.assets/manuel-perilla-banner.png` and update `.assets/SOURCES.md`. No placeholder or unresolved banner TODO remains. Technology icons are stored locally, with their license, so their rendering does not depend on an icon API.

For the separate GitHub profile settings, see [PROFILE-SETTINGS.md](PROFILE-SETTINGS.md).
