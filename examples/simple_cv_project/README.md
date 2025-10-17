# Simple Computer Vision Demo Project

This example project accompanies the **Awesome Computer Vision** list and lets you try a few classic image-processing operations locally. It generates a synthetic test scene, applies multiple processing steps, and saves side-by-side visualizations so you can inspect the results without hunting down external datasets or third-party packages.

## Prerequisites

This demo relies only on the Python standard library (tested with Python 3.11). No additional packages or internet access are required.

## Usage

Run the demo script from this directory:

```bash
python main.py
```

The script will:

1. Generate a synthetic scene with geometric shapes and gradient backgrounds
2. Apply grayscale conversion, Gaussian blurring, Sobel edge magnitude, and Harris corner detection
3. Save the intermediate outputs to `output/`
4. Print quick statistics (min / max / mean intensity) for each stage to the terminal

Example output files:

```
output/
├── synthetic_scene.ppm
├── grayscale.pgm
├── blurred.pgm
├── edges.pgm
└── corners.ppm
```

The images are written in the portable PPM/PGM text formats, which most image viewers can open directly. On macOS or Linux you can convert them to PNGs with ImageMagick (`magick input.ppm output.png`) or inspect them with any tool that understands Netpbm files.

### Customization

Use `--size` to change the rendered resolution (higher values provide more detail at the cost of runtime) and `--output` to override the destination directory. The CLI now enforces the supported range between **128** and **512** pixels, matching the browser viewer:

```bash
python main.py --size 384 --output ./my_outputs
```

Feel free to extend `main.py` with additional processing blocks inspired by algorithms listed in the main awesome repository.

### Automated regression tests

The MVP ships with standard-library regression tests that verify the numerical summary of each pipeline stage and exercise the HTTP regeneration endpoint. Run them from the repository root:

```bash
python -m unittest discover -s tests -t .
```

If you prefer `make`, the shortcut below executes the same suite:

```bash
make test
```

### MVP roadmap

Curious about where the project is headed? The [MVP outline](MVP_PLAN.md) captures the intended target audience, success criteria, technical requirements, and prioritized next steps for bringing this demo to a polished, classroom-ready state.

### Interactive viewer

Prefer to explore the results visually? Launch the built-in UI, which uses only the Python standard library plus a small amount of browser-side JavaScript to render the Netpbm files onto an HTML canvas and trigger regeneration without leaving the page:

```bash
python server.py
```

This will regenerate the demo outputs (respecting `--size` if provided) and start a local web server. Visit the printed URL to see the pipeline stages, download the raw files, review their summary statistics, and queue additional runs via the **Regenerate outputs** form. The form lets you request new resolutions between 128 and 512 pixels and updates the gallery once the server finishes processing. Use `python server.py --generate-only` when you just want to refresh the assets without keeping the server running.

Additional conveniences:

- `python -m examples.simple_cv_project.server` runs the same server entry-point via the package name.
- `python -m examples.simple_cv_project` is equivalent to the command above for fast demos.
- `make demo SIZE=256` launches the UI and regenerates assets into `examples/simple_cv_project/output/` by default.
- `make generate SIZE=256 OUTPUT=/tmp/demo_output` refreshes the artifacts without serving.

While the regeneration job runs, the UI disables the submit button, sets ARIA `aria-busy` flags for assistive technologies, and streams progress to the live status line. Once a run finishes the viewer records the timestamp and size of the last generation next to the controls so you always know which dataset you are looking at. Validation errors and server issues surface inline to keep the workflow self-contained.

### Performance expectations

Generation time scales roughly quadratically with the selected size. The table below captures typical wall-clock times observed on the execution environment used for development:

| Size (px) | Runtime (s) |
|-----------|-------------|
| 128       | ~3.9        |
| 256       | ~13.3       |
| 384       | ~28.9       |
| 512       | ~52.2       |

At 512 px the full pipeline still completes in under a minute, but expect proportionally faster results at smaller sizes when presenting live.
