# Simple CV Demo MVP Report

## Executive Summary
The simple computer-vision demo delivers a zero-dependency, reproducible pipeline that showcases foundational image-processing techniques. Educators and learners can generate deterministic Netpbm artifacts, inspect numeric statistics, and trigger regeneration through an accessibility-minded web UI—all guarded by regression tests and shared validation helpers so behaviour stays stable across iterations.

## Audience, Goals, and Outcomes
### Who is this for?
- Instructors, workshop facilitators, and students who need a portable sandbox for classical computer-vision concepts without third-party installs.
- Contributors to the Awesome Computer Vision list who want a hands-on example that mirrors the curated resources.

### Problems the MVP solves
- Demonstrates grayscale conversion, Gaussian blurring, Sobel edge detection, and Harris corner detection entirely within the Python standard library.
- Provides deterministic outputs and JSON summaries so classroom walkthroughs and automated tests can compare runs confidently.
- Packages the experience behind simple commands (`python -m examples.simple_cv_project.server`, `make demo`) that work on macOS, Linux, and Windows.

### Core objectives
1. Ship a one-command workflow that renders a synthetic scene, generates intermediate images, and serves a browser viewer.
2. Surface per-stage statistics and last-run metadata so users know exactly which dataset they are exploring.
3. Enforce validated resolution bounds (128–512 px) across CLI, server, and UI to keep workloads predictable.
4. Document the entire journey—setup, usage, tests, and roadmap—in a single reference for educators and contributors.

## User Journey
1. **Clone the repository** – No external dependencies are required beyond Python 3.11.
2. **Generate outputs or start the viewer** – Run `python examples/simple_cv_project/main.py` for artifacts or `python examples/simple_cv_project/server.py` to launch the UI (Makefile shortcuts mirror both paths).
3. **Explore the UI** – Review the gallery, statistics panel, regeneration controls, and download links rendered directly in the browser.
4. **Regenerate safely** – Submit the “Regenerate outputs” form to request new sizes between 128 and 512 px; the server validates input and serializes requests to avoid race conditions.
5. **Validate behaviour** – Execute `python -m unittest discover -s tests -t .` (or `make test`) to confirm the JSON summaries and HTTP responses stay deterministic.
6. **Reset the workspace** – `make clean` removes generated Netpbm files so working trees remain pristine.

## Functional Requirements (Delivered)
- Pure-Python pipeline that draws a synthetic scene, then emits grayscale, blurred, Sobel edge, and Harris-corner stages with identical results across runs.
- Netpbm (`.ppm`/`.pgm`) artifacts and a `summary.json` file containing dimensions, intensity stats, and timestamps for each stage.
- Standard-library HTTP server that serves static assets, generated files, and a `/api/regenerate` endpoint guarded by strict validation and a threading lock.
- Browser viewer with:
  - Regeneration form backed by the API.
  - Live status messaging and last-run metadata.
  - Canvas-based rendering of Netpbm images and download links for every artifact.
  - Statistics panel synchronized with `summary.json`.
- Documentation and automation (README guides, Makefile targets, package entry points) that keep onboarding to a single command.

## Non-Functional Requirements
- **Zero external dependencies:** Runs with stock Python 3.11 and any modern browser.
- **Performance:** Regeneration completes within ~30 seconds at 384×384 and under a minute at 512×512, with lower sizes remaining near-instant in teaching scenarios.
- **Accessibility:** Skip-navigation link, ARIA landmarks, live regions, and focus outlines ensure keyboard and assistive-technology support.
- **Portability:** Works identically on macOS, Linux, and Windows; all file paths and commands rely on cross-platform standard-library modules.

## Deliberate Simplifications
- Adjustable parameter surface is limited to image size; advanced tuning (kernel radii, thresholds) is deferred until user feedback demonstrates demand.
- Assets are served from the same Python process as the pipeline to avoid premature multi-service complexity.
- Netpbm output is used instead of bundling heavier codecs so files remain transparent and easy to inspect or convert.
- Regeneration requests are processed serially; job queues and asynchronous workers are intentionally out of scope for the MVP.

## Architecture Overview
### Pipeline (`examples/simple_cv_project/main.py`)
- Generates the base scene (gradient background, geometric primitives, anchor markers).
- Implements grayscale conversion, Gaussian blur (separable convolution), Sobel gradient magnitude, and Harris corner scoring/overlay entirely in pure Python.
- Writes ASCII Netpbm files and produces a JSON summary with metrics (min, max, mean intensity) and timestamps for every stage.
- Exposes CLI arguments for output directory and resolution while reusing shared validation helpers to enforce guardrails.

### Shared Configuration (`config.py`)
- Defines default output locations and supported size bounds (128–512 px in 32 px increments).
- Provides validation utilities consumed by both the CLI and server.
- Offers convenience helpers for resolving paths relative to the package for consistent artifact placement.

### HTTP Server (`server.py`)
- Wraps the pipeline execution behind a threading lock to keep concurrent regeneration requests deterministic.
- Serves `index.html`, JavaScript, CSS, JSON summaries, and generated images without third-party frameworks.
- Implements `/api/regenerate` to validate payloads, rerun the pipeline, and return updated summaries or informative error messages.
- Supports `--generate-only`, `--size`, `--host`, and `--port` flags for flexible local workflows.

### Web Assets (`index.html`, `static/styles.css`, `static/app.js`)
- Compose a two-column layout with a masthead overview, regeneration controls, and statistics sidebar alongside the gallery.
- Use design tokens, responsive breakpoints, and dark/light-friendly colours for consistent presentation.
- Render Netpbm files directly to `<canvas>` elements in vanilla JavaScript while keeping download links in sync.
- Toggle `aria-busy` states, disable controls during regeneration, and broadcast live status messages for accessible feedback.

### Tooling and Automation
- Package entry points (`examples/simple_cv_project/__init__.py`, `__main__.py`) align module execution with direct script usage.
- `Makefile` targets (`make demo`, `make generate`, `make test`, `make clean`) wrap the common workflows and expose `SIZE`/`OUTPUT` overrides.
- `.gitignore` excludes generated Netpbm artifacts to keep repositories clean during local runs.

## Key Workflows and Commands
| Goal | Command | Notes |
| --- | --- | --- |
| Generate artifacts only | `python examples/simple_cv_project/main.py --size 256` | Produces Netpbm images and `summary.json` under `output/` (override with `--output`). |
| Launch the viewer | `python examples/simple_cv_project/server.py --size 256` | Regenerates assets, serves the UI, and prints the access URL. |
| Regenerate via Makefile | `make generate SIZE=256` | Uses the same validation helpers, accepts optional `OUTPUT` path. |
| Serve via Makefile | `make demo SIZE=256` | Regenerates assets and starts the server in one command. |
| Run regression tests | `python -m unittest discover -s tests -t .` | Mirrors `make test`; confirms summaries and API behaviour. |
| Reset the workspace | `make clean` | Deletes files under `examples/simple_cv_project/output/`. |

## Accessibility and UX Highlights
- Skip link jumps directly to the regeneration form for keyboard users.
- ARIA landmarks and descriptive headings clarify structure for screen readers.
- Live region broadcasts regeneration progress (“Starting run…”, “Generation complete”) without requiring manual refreshes.
- Last-run timestamp and size persist beside the controls, helping instructors keep class sessions synchronized.
- Responsive card layout preserves readability from narrow mobile widths through widescreen monitors.

## Determinism and Testing
- `tests/test_simple_cv_project.py` executes the pipeline twice, asserting identical JSON summaries to guarantee deterministic numeric outputs.
- The same suite spins up the HTTP server in-process, hits `/api/regenerate`, and validates both the HTTP response schema and the updated summary contents.
- Timestamps are normalized when comparing summaries so tests remain stable while still reporting recency in the UI.

## Operational Guardrails
- Supported resolutions are restricted to {128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, 480, 512}; validation rejects out-of-range or non-multiple-of-32 values with informative errors.
- Generated artifacts default to `examples/simple_cv_project/output/`, keeping all outputs localized for easy cleanup or sharing.
- The server serializes regeneration requests to prevent overlapping writes and ensures error responses leave existing artifacts intact.
- `.gitignore` prevents accidental commits of generated Netpbm data, while `make clean` and the CLI `--output` flag help developers maintain separate workspaces.

## Documentation and Support Materials
- **Root README:** Highlights the demo, local testing checklist, and automation commands for quick discovery.
- **Example README:** Serves as the operator manual with CLI walkthroughs, UI guidance, regression instructions, and performance expectations.
- **This dossier:** Combines architectural details, requirements, workflows, testing strategy, and roadmap guidance into a single reference that can be shared with educators or stakeholders.

## Roadmap and Expert Recommendations
1. **Integrate Continuous Integration:** Run the regression suite (`python -m unittest discover -s tests -t .`) on every pull request and publish failing summaries as artifacts for debugging.
2. **Gather classroom feedback:** Observe which parameters or visualizations instructors request most often before expanding the UI beyond size selection.
3. **Author facilitation tips:** Document lesson pacing, talking points per pipeline stage, and troubleshooting advice for live sessions.
4. **Evaluate lightweight distribution:** Explore zip bundles or PyPI packaging once workflows stabilize to streamline onboarding for non-developers.
5. **Monitor performance envelopes:** Continue profiling at the upper resolution bound when introducing new stages to keep run times predictable.

## Appendix A: Performance Benchmarks
Generation time scales roughly quadratically with the requested size. Typical wall-clock times observed in the development environment:

| Size (px) | Runtime (s) |
| --- | --- |
| 128 | ~3.9 |
| 256 | ~13.3 |
| 384 | ~28.9 |
| 512 | ~52.2 |

## Appendix B: File Inventory
- `examples/simple_cv_project/main.py` – Pipeline implementation and CLI entry point.
- `examples/simple_cv_project/server.py` – HTTP server and regeneration API.
- `examples/simple_cv_project/config.py` – Shared configuration and validation helpers.
- `examples/simple_cv_project/index.html` – Viewer markup with skip links and layout scaffolding.
- `examples/simple_cv_project/static/app.js` – Vanilla JS renderer for Netpbm files and regeneration logic.
- `examples/simple_cv_project/static/styles.css` – Design tokens, responsive layout, and dark/light theme support.
- `examples/simple_cv_project/README.md` – Operator guide for the demo.
- `tests/test_simple_cv_project.py` – Regression coverage for the pipeline and server.
- `Makefile` – Automation shortcuts for generate/serve/test/clean.
- `.gitignore` – Ignores generated Netpbm outputs.
