# Simple Computer Vision Demo Project

This example project accompanies the **Awesome Computer Vision** list and lets you quickly try a few classic image-processing operations locally.  It generates a synthetic test scene, applies multiple processing steps with OpenCV, and saves side-by-side visualizations so you can inspect the results without hunting down external datasets.

## Prerequisites

* Python 3.8+
* A virtual environment is recommended

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the demo script from this directory:

```bash
python main.py
```

The script will:

1. Generate a synthetic scene with geometric shapes and a gradient background
2. Apply grayscale conversion, Gaussian blurring, Canny edge detection, and Harris corner detection
3. Save the intermediate outputs to `output/` and pop up a Matplotlib window with a 2×2 comparison grid

Example output files:

```
output/
├── synthetic_scene.png
├── grayscale.png
├── blurred.png
├── edges.png
└── corners.png
```

To skip the interactive Matplotlib window (useful on headless servers), pass the `--no-show` flag:

```bash
python main.py --no-show
```

## Next steps

You can modify `main.py` to experiment with other algorithms listed in the Awesome Computer Vision repository—simply import the relevant libraries, plug in additional processing steps, and extend the visualization grid.
