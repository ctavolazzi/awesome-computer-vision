# Simple CV Demo MVP Outline

## Purpose and Target Audience
- **Who is this for?** Educators, workshop facilitators, and newcomers who want a self-contained demo that shows foundational computer-vision operations without external dependencies or complex setup.
- **Problem we solve:** Provide a reproducible sandbox for exploring classical CV concepts (grayscale conversion, blurring, gradients, corner detection) entirely within the standard library so it can run in restricted environments.

## MVP Goal
Deliver a one-click experience where a user can generate, inspect, and tweak a handful of classic image-processing stages through a browser-based interface backed by a deterministic Python pipeline.

## Core User Journey
1. Download or clone the repository.
2. Run a single command (e.g., `python server.py`) that both generates default outputs and starts the viewer.
3. Load the web UI to review the gallery, statistics, and download links.
4. Adjust allowed parameters (image size only in MVP) and regenerate to see how outputs change.
5. Leave with confidence that each stage behaved as described (through clear labeling and summary stats).

## Functional Requirements (MVP Scope)
- **Deterministic pipeline:** Pure Python implementation that renders the synthetic scene, grayscale, blur, Sobel, and Harris outputs identically across runs.
- **Artifact generation:** Save Netpbm (`.ppm`/`.pgm`) files and a JSON summary with per-image metadata (dimensions, min/max/mean intensity).
- **Static asset serving:** HTTP server must serve generated files, summary JSON, and the viewer assets without external frameworks.
- **Regeneration endpoint:** Accepts validated size parameter (128–512 px) to regenerate the pipeline synchronously, returning success/error JSON.
- **Browser viewer:** Responsive layout with
  - Gallery of images rendered to canvas.
  - Controls for regeneration (size selector + submit).
  - Display of summary statistics and download links.
  - Loading/progress indicators so users know when regeneration finishes.
- **Documentation:** Clear README guidance for running the script, understanding outputs, and troubleshooting common errors.

## Non-Functional Requirements
- **Zero external dependencies:** Works with stock Python 3.11 and a modern browser.
- **Run time:** Regeneration completes within ~3 seconds at 384×384 on typical laptops.
- **Accessibility:** Semantic markup and keyboard-accessible controls; adequate color contrast in light/dark modes.
- **Portability:** Works on macOS, Linux, and Windows without platform-specific tweaks.

## Deliberate Simplifications for MVP
- Limit adjustable parameters to image size; more advanced tuning (blur radius, thresholds) is deferred.
- Serve assets from the same process as the pipeline instead of modular microservices.
- Use Netpbm outputs and in-browser canvas conversion rather than bundling heavyweight image codecs.
- Regeneration requests are processed serially to avoid race conditions; full job queueing is out of scope.

## Avoiding Premature Optimization
- No caching layer or database; generated artifacts are small and regenerated on demand.
- Keep front-end JavaScript minimal (vanilla JS, no frameworks) to maintain clarity.
- Defer packaging to PyPI or Docker until the workflow stabilizes and real-world demand emerges.

## Implementation Checklist Toward MVP
1. ✅ Pure-Python pipeline with deterministic outputs and JSON metadata (already implemented in `main.py`).
2. ✅ Static server and viewer that display artifacts and allow size-controlled regeneration (`server.py`, `index.html`, `static/`).
3. ✅ Automated regression tests covering pipeline stages, JSON schema, and HTTP endpoints (`tests/test_simple_cv_project.py`).
4. ✅ Accessibility audit and adjustments (ARIA roles, focus outlines, contrast verification) applied to the viewer UI.
5. ✅ Performance profiling at upper-bound resolution to confirm latency target and document resource usage (see README runtime table).
6. ✅ Error-handling UX (inline feedback, retry guidance) for validation failures or server issues via live status messaging.
7. ✅ Packaging polish (entry-point script, optional `make` targets) for smoother onboarding (`python -m examples.simple_cv_project`, `Makefile`).

## Expert Recommendations: Next Steps to Reach MVP
1. **Wire the automated tests into CI.**
   - Add a GitHub Actions workflow (or similar) that runs `python -m unittest discover -s tests -t .` on pull requests.
   - Upload the generated summary JSON as an artifact when the suite fails to aid debugging.
2. **Plan post-MVP feature exploration.**
   - Collect feedback on which additional pipeline parameters or visualizations educators value most before expanding scope.
   - Prototype optional overlays (e.g., gradient directions) under a feature flag guarded by the existing test snapshots.
3. **Document classroom facilitation tips.**
   - Draft a short guide on lesson timing, suggested talking points per pipeline stage, and troubleshooting steps for students.
4. **Consider lightweight distribution.**
   - Evaluate packaging the project as a zip archive or PyPI module once the workflow stabilizes to simplify onboarding further.

By prioritizing testing, UX robustness, and documented performance, we can confidently ship the MVP while keeping the architecture lean and focused on the educational use case.
