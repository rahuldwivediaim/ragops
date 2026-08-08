"""
Enterprise Document Processing Stages.

Each stage implements one well-defined responsibility within the
document processing pipeline.

Stages are intentionally independent and execute sequentially
through the ProcessingPipeline.

Current stages:

- ValidationStage
- ParsingStage
- ChunkingStage

Future stages:

- EmbeddingStage
- IndexingStage
- OCRStage
- ClassificationStage
- TranslationStage
"""

from .chunking_stage import ChunkingStage
from .parsing_stage import ParsingStage
from .validation_stage import ValidationStage

__all__ = [
    "ValidationStage",
    "ParsingStage",
    "ChunkingStage",
]
