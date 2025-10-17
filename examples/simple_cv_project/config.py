"""Shared configuration constants for the simple CV demo."""
from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "output"
DEFAULT_SIZE = 256
MIN_SIZE = 128
MAX_SIZE = 512
SIZE_STEP = 32


def validate_size(size: int) -> int:
    """Ensure ``size`` falls within the supported bounds.

    Raises ``ValueError`` with a human-readable message when ``size`` is outside
    the accepted range so callers can surface the failure directly to users.
    """

    if not (MIN_SIZE <= size <= MAX_SIZE):
        raise ValueError(f"size must be between {MIN_SIZE} and {MAX_SIZE} pixels")
    return size


def parse_size_argument(value: str) -> int:
    """``argparse`` helper that parses and validates an image size."""

    try:
        size = int(value)
    except ValueError as exc:  # pragma: no cover - argparse handles messaging
        raise argparse.ArgumentTypeError("size must be an integer") from exc

    try:
        return validate_size(size)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SIZE",
    "MAX_SIZE",
    "MIN_SIZE",
    "PROJECT_DIR",
    "SIZE_STEP",
    "parse_size_argument",
    "validate_size",
]
