"""Pure Python computer-vision demo package."""

from .main import (
    PipelineOutputs,
    collect_image_metadata,
    compute_image_statistics,
    create_synthetic_scene,
    run_pipeline,
    save_outputs,
)

__all__ = [
    "PipelineOutputs",
    "collect_image_metadata",
    "compute_image_statistics",
    "create_synthetic_scene",
    "run_pipeline",
    "save_outputs",
]
