"""Run the pure-Python vision demo and serve a small UI to view the results."""
from __future__ import annotations

import argparse
import contextlib
import json
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator, Tuple
from urllib.parse import parse_qs, urlparse

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
DEFAULT_SIZE = 256
MIN_SIZE = 128
MAX_SIZE = 512
IO_LOCK = threading.Lock()
try:  # pragma: no cover - exercised via package imports
    from . import main as pipeline
except ImportError:  # pragma: no cover - fallback when executed as a script
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))
    import main as pipeline  # type: ignore[no-redef]


def ensure_outputs(output_dir: Path, size: int) -> dict:
    with IO_LOCK:
        scene = pipeline.create_synthetic_scene(size=size)
        outputs = pipeline.run_pipeline(scene)
        summary = pipeline.save_outputs(outputs, output_dir)
    return summary


class DemoRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, output_dir: Path, **kwargs):  # type: ignore[override]
        self.output_dir = output_dir
        super().__init__(*args, directory=directory, **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_POST(self) -> None:  # type: ignore[override]
        parsed = urlparse(self.path)
        if parsed.path != "/api/regenerate":
            self.send_error(404, "Unknown endpoint")
            return

        size = self._resolve_size(parsed)
        if size is None:
            return

        try:
            summary = ensure_outputs(self.output_dir, size=size)
        except Exception as exc:  # pragma: no cover - defensive logging
            self.send_error(500, f"Failed to regenerate outputs: {exc}")
            return

        print(f"[demo] Regenerated outputs at {size}px", flush=True)

        payload = json.dumps({"ok": True, "size": size, "summary": summary})
        data = payload.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _resolve_size(self, parsed) -> int | None:
        size_value = None
        query_args = parse_qs(parsed.query)
        if "size" in query_args:
            size_value = query_args["size"][0]

        content_length = int(self.headers.get("Content-Length", "0") or 0)
        if content_length:
            try:
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                size_value = payload.get("size", size_value)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON payload")
                return None

        if size_value is None:
            return DEFAULT_SIZE

        try:
            parsed_size = int(size_value)
        except (TypeError, ValueError):
            self.send_error(400, "size must be an integer")
            return None

        if not (MIN_SIZE <= parsed_size <= MAX_SIZE):
            self.send_error(
                400,
                f"size must be between {MIN_SIZE} and {MAX_SIZE} pixels",
            )
            return None

        return parsed_size


@contextlib.contextmanager
def serve(
    directory: Path, host: str, port: int, output_dir: Path = OUTPUT_DIR
) -> Iterator[ThreadingHTTPServer]:
    handler = partial(
        DemoRequestHandler,
        directory=str(directory),
        output_dir=output_dir,
    )
    server = ThreadingHTTPServer((host, port), handler)  # type: ignore[arg-type]
    try:
        yield server
    finally:
        server.server_close()


def pick_port(host: str, requested: int) -> Tuple[str, int]:
    if requested != 0:
        return host, requested
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()


def image_size(value: str) -> int:
    try:
        size = int(value)
    except ValueError as exc:  # pragma: no cover - argparse handles messaging
        raise argparse.ArgumentTypeError("size must be an integer") from exc

    if not (MIN_SIZE <= size <= MAX_SIZE):
        raise argparse.ArgumentTypeError(
            f"size must be between {MIN_SIZE} and {MAX_SIZE}"
        )
    return size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind the HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for the HTTP server (0 for random)")
    parser.add_argument(
        "--size",
        type=image_size,
        default=DEFAULT_SIZE,
        help=(
            f"Image size to generate before serving (between {MIN_SIZE} and {MAX_SIZE} pixels)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory where generated artifacts are stored",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Generate the outputs and exit without starting the server",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = PROJECT_DIR
    output_dir = args.output.resolve()
    summary = ensure_outputs(output_dir, size=args.size)

    if args.generate_only:
        reported_size = summary.get("meta", {}).get("size", args.size)
        print(
            f"Generated demo assets in {output_dir} at {reported_size}px; "
            "start the server without --generate-only to view them."
        )
        return

    host, port = pick_port(args.host, args.port)
    print(f"Serving demo UI from {project_root} at http://{host}:{port}")

    with serve(project_root, host, port, output_dir=output_dir) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server...")


if __name__ == "__main__":
    main()
