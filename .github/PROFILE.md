# Maintaining the House of the Hearth

The profile is `JosePerilla/JosePerilla`; `main` contains its source and the orphan `output` branch contains the three generated SVGs. The banner is stored locally under `.assets`.

## Daily refresh

`.github/workflows/snake.yml` runs at **00:00 America/Bogota**, expressed as `0 5 * * *` in GitHub's default UTC schedule. It also runs on relevant pushes to `main` and can be started manually from **Actions → House of the Hearth → Run workflow**. Scheduled runs can be delayed by GitHub; inactive public repositories may have their schedules disabled after 60 days.

The workflow uses the automatic `GITHUB_TOKEN` with `contents: write`; no personal access token is required. It generates the snake and both statistics cards, validates the SVGs, and publishes them together. A failed generation leaves the previous successful output in place. Only public repository statistics are requested; no additional access to private repositories is configured.

## Statistics availability

The public `github-readme-stats.vercel.app` endpoints returned HTTP 503 during setup. Each statistics `<picture>` therefore prefers the SVG generated daily by GitHub Readme Stats Action, while retaining the requested, color-configured API URL in its `<img>` fallback. Browser fallback is based on image format support, not network errors; if an output file is missing, check the workflow and regenerate it.

The Top Languages card reports languages detected in public repositories. If none are available yet, it will show an empty-data message; it does not invent a language breakdown from the declared tech stack.

## GitHub rendering

Images and generated cards use a permanent dark palette. GitHub controls the surrounding page theme and its table borders; README HTML cannot force the visitor's entire page into dark mode or override GitHub's CSS. `border="0"` expresses the layout intent, but GitHub may still draw table borders.

The snake uses a real `<img alt="Snake animation">` inside `<picture>`, the HTML equivalent of `![Snake animation](https://raw.githubusercontent.com/JosePerilla/JosePerilla/output/github-contribution-grid-snake-dark.svg)`. This keeps the README valid HTML and avoids displaying unparsed Markdown inside a raw HTML block.

To change the banner, replace `.assets/arlecchino-banner.gif` and update `.assets/SOURCES.md`. No placeholder or unresolved banner TODO remains.
