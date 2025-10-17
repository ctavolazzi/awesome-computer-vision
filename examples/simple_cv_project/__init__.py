"""Pure Python computer-vision demo package."""

from .config import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SIZE,
    MAX_SIZE,
    MIN_SIZE,
    PROJECT_DIR,
    SIZE_STEP,
    parse_size_argument,
    validate_size,
)
from .main import (
    PipelineOutputs,
    collect_image_metadata,
    compute_image_statistics,
    create_synthetic_scene,
    run_pipeline,
    save_outputs,
)

__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SIZE",
    "MAX_SIZE",
    "MIN_SIZE",
    "PROJECT_DIR",
    "SIZE_STEP",
    "parse_size_argument",
    "validate_size",
    "PipelineOutputs",
    "collect_image_metadata",
    "compute_image_statistics",
    "create_synthetic_scene",
    "run_pipeline",
    "save_outputs",
]
