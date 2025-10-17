"""Simple demo script to explore core computer-vision operations."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import cv2
import matplotlib.pyplot as plt
import numpy as np


def create_synthetic_scene(size: int = 512) -> np.ndarray:
    """Generate a colorful synthetic scene with geometric primitives."""
    x = np.linspace(0.0, 1.0, size)
    y = np.linspace(0.0, 1.0, size)
    xx, yy = np.meshgrid(x, y)

    # Create a smooth gradient background
    background = np.stack(
        [
            0.4 + 0.6 * xx,
            0.3 + 0.4 * (1 - yy),
            0.5 + 0.5 * (1 - xx * yy),
        ],
        axis=-1,
    )
    image = np.clip(background * 255, 0, 255).astype(np.uint8)

    # Draw rectangles
    for idx, color in enumerate([(220, 50, 20), (30, 180, 80), (30, 120, 220)]):
        offset = 70 + idx * 130
        cv2.rectangle(image, (offset, 60), (offset + 140, 200), color, thickness=4)
        cv2.circle(image, (offset + 70, 280), 60, color, thickness=4)

    # Draw polylines and text
    arrow = np.array([[60, 420], [200, 380], [340, 410], [460, 360]], dtype=np.int32)
    cv2.polylines(image, [arrow], False, (255, 160, 0), thickness=6)

    line_start = (120, 360)
    for idx in range(6):
        start = (line_start[0] + idx * 50, line_start[1] + (idx % 2) * 20)
        end = (start[0] + 30, start[1] + 80)
        cv2.line(image, start, end, (40, 40, 40), thickness=3)

    cv2.putText(
        image,
        "Awesome CV Demo",
        (90, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (20, 20, 20),
        thickness=2,
        lineType=cv2.LINE_AA,
    )
    return image


def run_pipeline(scene: np.ndarray) -> Dict[str, np.ndarray]:
    gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), sigmaX=1.2)
    edges = cv2.Canny(blurred, threshold1=80, threshold2=160)

    # Harris corner detection expects float32 grayscale
    corners = cv2.cornerHarris(np.float32(blurred) / 255.0, blockSize=3, ksize=3, k=0.05)
    corners = cv2.dilate(corners, None)
    corner_mask = corners > 0.02 * corners.max()
    corner_overlay = scene.copy()
    corner_overlay[corner_mask] = (255, 0, 0)

    return {
        "scene": scene,
        "grayscale": gray,
        "blurred": blurred,
        "edges": edges,
        "corners": corner_overlay,
    }


def save_outputs(outputs: Dict[str, np.ndarray], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_dir / "synthetic_scene.png"), outputs["scene"])
    cv2.imwrite(str(output_dir / "grayscale.png"), outputs["grayscale"])
    cv2.imwrite(str(output_dir / "blurred.png"), outputs["blurred"])
    cv2.imwrite(str(output_dir / "edges.png"), outputs["edges"])
    cv2.imwrite(str(output_dir / "corners.png"), outputs["corners"])


def show_visualization(outputs: Dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    fig.suptitle("Awesome Computer Vision Demo", fontsize=16)

    scenes_rgb = cv2.cvtColor(outputs["scene"], cv2.COLOR_BGR2RGB)
    corners_rgb = cv2.cvtColor(outputs["corners"], cv2.COLOR_BGR2RGB)

    axes[0, 0].imshow(scenes_rgb)
    axes[0, 0].set_title("Synthetic Scene")
    axes[0, 1].imshow(outputs["grayscale"], cmap="gray")
    axes[0, 1].set_title("Grayscale")
    axes[1, 0].imshow(outputs["edges"], cmap="gray")
    axes[1, 0].set_title("Canny Edges")
    axes[1, 1].imshow(corners_rgb)
    axes[1, 1].set_title("Harris Corners")

    for ax in axes.ravel():
        ax.axis("off")

    plt.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--size",
        type=int,
        default=512,
        help="Width/height of the generated square scene in pixels (default: 512)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory to store output images (default: ./output)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Skip the Matplotlib visualization window",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene = create_synthetic_scene(size=args.size)
    outputs = run_pipeline(scene)
    save_outputs(outputs, args.output)

    print(f"Saved results to {args.output.resolve()}")
    if args.no_show:
        return

    show_visualization(outputs)


if __name__ == "__main__":
    main()
