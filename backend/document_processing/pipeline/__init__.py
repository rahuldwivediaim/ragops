"""
Enterprise Document Processing Pipeline.

The pipeline orchestrates the execution of document processing stages.

A stage performs one well-defined responsibility such as:

- Validation
- Parsing
- Chunking
- Embedding
- Indexing

The pipeline itself contains no business logic. It simply executes
registered stages in order while passing a shared ProcessingContext.
"""

from .context import ProcessingContext
from .exceptions import (
    PipelineError,
    StageExecutionError,
)
from .pipeline import ProcessingPipeline
from .result import ProcessingResult
from .stage import ProcessingStage
from .observer import ProcessingStageObserver

__all__ = [
    "ProcessingContext",
    "ProcessingPipeline",
    "ProcessingResult",
    "ProcessingStage",
    "PipelineError",
    "StageExecutionError",
    "ProcessingStageObserver",
]
