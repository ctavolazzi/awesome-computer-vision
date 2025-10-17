"""Simple demo script to explore core computer-vision operations without external dependencies."""
from __future__ import annotations

import argparse
import math
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import List, Sequence, Tuple, Union

if __package__:
    from .config import (
        DEFAULT_OUTPUT_DIR,
        DEFAULT_SIZE,
        MAX_SIZE,
        MIN_SIZE,
        parse_size_argument,
    )
else:  # pragma: no cover - execution as a script
    from config import (
        DEFAULT_OUTPUT_DIR,
        DEFAULT_SIZE,
        MAX_SIZE,
        MIN_SIZE,
        parse_size_argument,
    )

ColorPixel = Tuple[int, int, int]
ColorImage = List[List[ColorPixel]]
GrayImage = List[List[int]]
ImageData = Union[ColorImage, GrayImage]


@dataclass
class PipelineOutputs:
    scene: ColorImage
    grayscale: GrayImage
    blurred: GrayImage
    edges: GrayImage
    corners: ColorImage


def clamp_color(value: float) -> int:
    return max(0, min(255, int(round(value))))


def blank_color_image(width: int, height: int, color: ColorPixel) -> ColorImage:
    return [[color for _ in range(width)] for _ in range(height)]


def create_synthetic_scene(size: int = 256) -> ColorImage:
    """Generate a colorful synthetic scene with geometric primitives."""
    image = blank_color_image(size, size, (0, 0, 0))

    for y in range(size):
        for x in range(size):
            rx = x / max(1, size - 1)
            ry = y / max(1, size - 1)
            r = 0.4 + 0.6 * rx
            g = 0.3 + 0.4 * (1 - ry)
            b = 0.5 + 0.5 * (1 - rx * ry)
            image[y][x] = (clamp_color(r * 255), clamp_color(g * 255), clamp_color(b * 255))

    rectangles = [
        ((int(size * 0.1), int(size * 0.12)), (int(size * 0.35), int(size * 0.36)), (220, 50, 20)),
        ((int(size * 0.4), int(size * 0.16)), (int(size * 0.65), int(size * 0.40)), (30, 180, 80)),
        ((int(size * 0.7), int(size * 0.20)), (int(size * 0.9), int(size * 0.44)), (30, 120, 220)),
    ]
    for (top_left, bottom_right, color) in rectangles:
        draw_rectangle(image, top_left, bottom_right, color, thickness=4)
        center = ((top_left[0] + bottom_right[0]) // 2, bottom_right[1] + int(size * 0.14))
        draw_circle(image, center, int(size * 0.1), color, thickness=4)

    arrow = [(int(size * x), int(size * y)) for (x, y) in [(0.12, 0.82), (0.39, 0.74), (0.66, 0.80), (0.9, 0.70)]]
    draw_polyline(image, arrow, (255, 160, 0), thickness=3)

    for idx in range(6):
        start_x = int(size * 0.18) + idx * int(size * 0.1)
        start_y = int(size * 0.70) + (idx % 2) * int(size * 0.05)
        end = (start_x + int(size * 0.06), start_y + int(size * 0.16))
        draw_line(image, (start_x, start_y), end, (40, 40, 40), thickness=2)

    return image


def draw_rectangle(image: ColorImage, top_left: Tuple[int, int], bottom_right: Tuple[int, int], color: ColorPixel, thickness: int = 1) -> None:
    width = len(image[0])
    height = len(image)
    for offset in range(thickness):
        y_top = min(height - 1, top_left[1] + offset)
        y_bottom = max(0, bottom_right[1] - offset)
        for x in range(max(0, top_left[0] + offset), min(width - 1, bottom_right[0] - offset) + 1):
            image[y_top][x] = color
            image[y_bottom][x] = color
    for offset in range(thickness):
        x_left = min(width - 1, top_left[0] + offset)
        x_right = max(0, bottom_right[0] - offset)
        for y in range(max(0, top_left[1] + offset), min(height - 1, bottom_right[1] - offset) + 1):
            image[y][x_left] = color
            image[y][x_right] = color


def draw_circle(image: ColorImage, center: Tuple[int, int], radius: int, color: ColorPixel, thickness: int = 1) -> None:
    cx, cy = center
    max_y = len(image)
    max_x = len(image[0])
    outer_sq = radius * radius
    inner_radius = max(0, radius - thickness)
    inner_sq = inner_radius * inner_radius

    for y in range(cy - radius, cy + radius + 1):
        if not (0 <= y < max_y):
            continue
        for x in range(cx - radius, cx + radius + 1):
            if not (0 <= x < max_x):
                continue
            dist_sq = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if inner_sq <= dist_sq <= outer_sq:
                image[y][x] = color


def draw_line(image: ColorImage, start: Tuple[int, int], end: Tuple[int, int], color: ColorPixel, thickness: int = 1) -> None:
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    radius = max(0, thickness - 1)
    while True:
        paint_circle(image, x0, y0, radius, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_polyline(image: ColorImage, points: Sequence[Tuple[int, int]], color: ColorPixel, thickness: int = 1) -> None:
    for start, end in zip(points[:-1], points[1:]):
        draw_line(image, start, end, color, thickness)


def paint_circle(image: ColorImage, cx: int, cy: int, radius: int, color: ColorPixel) -> None:
    if radius <= 0:
        if 0 <= cy < len(image) and 0 <= cx < len(image[0]):
            image[cy][cx] = color
        return
    radius_sq = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        if not (0 <= y < len(image)):
            continue
        for x in range(cx - radius, cx + radius + 1):
            if not (0 <= x < len(image[0])):
                continue
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius_sq:
                image[y][x] = color


def to_grayscale(image: ColorImage) -> GrayImage:
    return [
        [
            clamp_color(0.299 * r + 0.587 * g + 0.114 * b)
            for (r, g, b) in row
        ]
        for row in image
    ]


GAUSSIAN_KERNEL = (
    (1, 4, 7, 4, 1),
    (4, 16, 26, 16, 4),
    (7, 26, 41, 26, 7),
    (4, 16, 26, 16, 4),
    (1, 4, 7, 4, 1),
)
GAUSSIAN_DIVISOR = 273.0


def convolve_gray(image: GrayImage, kernel: Sequence[Sequence[float]], divisor: float = 1.0) -> GrayImage:
    size = len(kernel)
    radius = size // 2
    height = len(image)
    width = len(image[0])
    output: GrayImage = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            acc = 0.0
            for ky in range(size):
                for kx in range(size):
                    yy = min(max(y + ky - radius, 0), height - 1)
                    xx = min(max(x + kx - radius, 0), width - 1)
                    acc += image[yy][xx] * kernel[ky][kx]
            output[y][x] = clamp_color(acc / divisor)
    return output


SOBEL_X = ((-1, 0, 1), (-2, 0, 2), (-1, 0, 1))
SOBEL_Y = ((-1, -2, -1), (0, 0, 0), (1, 2, 1))


def sobel_gradients(image: GrayImage) -> Tuple[List[List[float]], List[List[float]]]:
    height = len(image)
    width = len(image[0])
    gx = [[0.0 for _ in range(width)] for _ in range(height)]
    gy = [[0.0 for _ in range(width)] for _ in range(height)]
    radius = 1

    for y in range(height):
        for x in range(width):
            acc_x = 0.0
            acc_y = 0.0
            for ky in range(3):
                for kx in range(3):
                    yy = min(max(y + ky - radius, 0), height - 1)
                    xx = min(max(x + kx - radius, 0), width - 1)
                    pixel = image[yy][xx]
                    acc_x += pixel * SOBEL_X[ky][kx]
                    acc_y += pixel * SOBEL_Y[ky][kx]
            gx[y][x] = acc_x
            gy[y][x] = acc_y
    return gx, gy


def gradient_magnitude(gx: List[List[float]], gy: List[List[float]]) -> GrayImage:
    height = len(gx)
    width = len(gx[0])
    output: List[List[float]] = [[0.0 for _ in range(width)] for _ in range(height)]
    max_mag = 1e-9

    for y in range(height):
        for x in range(width):
            magnitude = math.hypot(gx[y][x], gy[y][x])
            max_mag = max(max_mag, magnitude)
            output[y][x] = magnitude

    scale = 255.0 / max_mag
    return [[clamp_color(value * scale) for value in row] for row in output]


def harris_corners(gray: GrayImage, color_scene: ColorImage, k: float = 0.04, threshold_ratio: float = 0.2) -> ColorImage:
    gx, gy = sobel_gradients(gray)
    height = len(gray)
    width = len(gray[0])

    ixx = [[gx[y][x] * gx[y][x] for x in range(width)] for y in range(height)]
    iyy = [[gy[y][x] * gy[y][x] for x in range(width)] for y in range(height)]
    ixy = [[gx[y][x] * gy[y][x] for x in range(width)] for y in range(height)]

    smooth_ixx = convolve_float(ixx, GAUSSIAN_KERNEL, GAUSSIAN_DIVISOR)
    smooth_iyy = convolve_float(iyy, GAUSSIAN_KERNEL, GAUSSIAN_DIVISOR)
    smooth_ixy = convolve_float(ixy, GAUSSIAN_KERNEL, GAUSSIAN_DIVISOR)

    responses = [[0.0 for _ in range(width)] for _ in range(height)]
    max_response = 1e-9

    for y in range(height):
        for x in range(width):
            det = smooth_ixx[y][x] * smooth_iyy[y][x] - smooth_ixy[y][x] * smooth_ixy[y][x]
            trace = smooth_ixx[y][x] + smooth_iyy[y][x]
            response = det - k * (trace ** 2)
            responses[y][x] = response
            if response > max_response:
                max_response = response

    threshold = threshold_ratio * max_response
    overlay = [[pixel for pixel in row] for row in color_scene]
    for y in range(height):
        for x in range(width):
            if responses[y][x] >= threshold:
                overlay[y][x] = (255, 0, 0)
    return overlay


def convolve_float(image: List[List[float]], kernel: Sequence[Sequence[float]], divisor: float = 1.0) -> List[List[float]]:
    size = len(kernel)
    radius = size // 2
    height = len(image)
    width = len(image[0])
    output = [[0.0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            acc = 0.0
            for ky in range(size):
                for kx in range(size):
                    yy = min(max(y + ky - radius, 0), height - 1)
                    xx = min(max(x + kx - radius, 0), width - 1)
                    acc += image[yy][xx] * kernel[ky][kx]
            output[y][x] = acc / divisor
    return output


def run_pipeline(scene: ColorImage) -> PipelineOutputs:
    gray = to_grayscale(scene)
    blurred = convolve_gray(gray, GAUSSIAN_KERNEL, GAUSSIAN_DIVISOR)
    gx, gy = sobel_gradients(blurred)
    edges = gradient_magnitude(gx, gy)
    corners = harris_corners(blurred, scene)

    return PipelineOutputs(
        scene=scene,
        grayscale=gray,
        blurred=blurred,
        edges=edges,
        corners=corners,
    )


def write_ppm(path: Path, image: ColorImage) -> None:
    with path.open("w", encoding="ascii") as handle:
        handle.write("P3\n")
        handle.write(f"{len(image[0])} {len(image)}\n")
        handle.write("255\n")
        for row in image:
            handle.write(" ".join(f"{r} {g} {b}" for (r, g, b) in row) + "\n")


def write_pgm(path: Path, image: GrayImage) -> None:
    with path.open("w", encoding="ascii") as handle:
        handle.write("P2\n")
        handle.write(f"{len(image[0])} {len(image)}\n")
        handle.write("255\n")
        for row in image:
            handle.write(" ".join(str(value) for value in row) + "\n")


def save_outputs(outputs: PipelineOutputs, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_ppm(output_dir / "synthetic_scene.ppm", outputs.scene)
    write_pgm(output_dir / "grayscale.pgm", outputs.grayscale)
    write_pgm(output_dir / "blurred.pgm", outputs.blurred)
    write_pgm(output_dir / "edges.pgm", outputs.edges)
    write_ppm(output_dir / "corners.ppm", outputs.corners)
    stats = compute_image_statistics(outputs)
    metadata = collect_image_metadata(outputs)
    return write_summary(output_dir / "summary.json", stats, metadata)


def flatten_intensities(image: ImageData) -> List[int]:
    if not image or not image[0]:
        return [0]
    first_pixel = image[0][0]
    if isinstance(first_pixel, tuple):
        return [
            clamp_color(0.299 * r + 0.587 * g + 0.114 * b)
            for row in image
            for (r, g, b) in row
        ]
    return [value for row in image for value in row]


def compute_image_statistics(outputs: PipelineOutputs) -> dict:
    stats = {}
    for name in ("scene", "grayscale", "blurred", "edges", "corners"):
        data: ImageData = getattr(outputs, name)
        values = flatten_intensities(data)
        stats[name] = {
            "min": min(values),
            "max": max(values),
            "mean": round(mean(values), 2),
        }
    return stats


def collect_image_metadata(outputs: PipelineOutputs) -> dict:
    height = len(outputs.scene)
    width = len(outputs.scene[0]) if outputs.scene else 0
    metadata = {
        "width": width,
        "height": height,
    }
    if width == height:
        metadata["size"] = width
    return metadata


def summarize_images(outputs: PipelineOutputs) -> None:
    stats = compute_image_statistics(outputs)
    for name, info in stats.items():
        print(
            f"{name:10s} | min={info['min']:3d} max={info['max']:3d} mean={info['mean']:6.2f}"
        )


def write_summary(path: Path, stats: dict, metadata: dict) -> dict:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "images": stats,
        "meta": metadata,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--size",
        type=parse_size_argument,
        default=DEFAULT_SIZE,
        help=(
            f"Width/height of the generated square scene in pixels "
            f"(between {MIN_SIZE} and {MAX_SIZE}; default: {DEFAULT_SIZE})"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to store output images (default: ./output)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene = create_synthetic_scene(size=args.size)
    outputs = run_pipeline(scene)
    summary = save_outputs(outputs, args.output)
    stamp = summary.get("generated_at", "unknown time")
    print(
        f"Saved results to {args.output.resolve()} (generated at {stamp})",
        flush=True,
    )
    summarize_images(outputs)


if __name__ == "__main__":
    main()
