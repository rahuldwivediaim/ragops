"""
Unit tests for TextChunker.
"""

from pathlib import Path

from backend.document_processing.chunker import TextChunker
from backend.document_processing.models import ParsedDocument
from backend.document_processing.models.parsed_page import ParsedPage


def test_chunk_document() -> None:
    """
    Verify that a document can be chunked.
    """

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists()

    text = sample_file.read_text(encoding="utf-8")

    document = ParsedDocument(
        filename=sample_file.name,
        document_type="TXT",
        page_count=0,
    )

    document.add_page(
        ParsedPage(
            page_number=1,
            text=text,
        )
    )

    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_document(document)

    print("\n" + "=" * 100)
    print(f"Generated {len(chunks)} chunks")
    print("=" * 100)

    for chunk in chunks:
        print(f"Chunk #{chunk.chunk_number}")
        print(f"Page      : {chunk.page_number}")
        print(f"Characters: {len(chunk.text)}")
        print(f"Start     : {chunk.character_start}")
        print(f"End       : {chunk.character_end}")
        print("-" * 100)
        print(chunk.text)
        print("=" * 100)

    assert len(chunks) > 0

    assert chunks[0].chunk_number == 1

    assert chunks[0].page_number == 1

    assert all(chunk.text.strip() for chunk in chunks)
