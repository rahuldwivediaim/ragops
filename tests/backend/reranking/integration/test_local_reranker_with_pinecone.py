"""
Local reranker + Pinecone integration test.

Uses the current RAGOps configuration and the real Edmira employee
policy fixture. The test creates an isolated temporary Pinecone
namespace, embeds and upserts the document chunks, retrieves them,
and then reranks the retrieved candidates using the local
Sentence Transformers CrossEncoder.

Flow:

    employee_policies.txt
        ↓
    TextChunker
        ↓
    OpenAI embeddings
        ↓
    Pinecone temporary namespace
        ↓
    Retriever
        ↓
    Candidate chunks
        ↓
    Sentence Transformers CrossEncoder
        ↓
    Reranked results
        ↓
    Cleanup
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from backend.common.config.loader import load_settings
from backend.document_processing.chunker import TextChunker
from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from backend.reranking.reranker_factory import RerankerFactory
from backend.retrieval.retriever import Retriever
from backend.vector_store.providers.pinecone_provider import (
    PineconeProvider,
)


QUERIES = [
    "How many annual leave days can employees take?",
    "What is the policy for working from home?",
    "Who can access confidential employee information?",
    "What should an employee do when reporting an incident?",
]


def _shorten_text(
    text: str,
    max_length: int = 140,
) -> str:
    """Return a compact single-line preview of document text."""

    text = " ".join(text.split())

    if len(text) <= max_length:
        return text

    return f"{text[:max_length]}..."


def test_local_reranker_with_pinecone() -> None:
    """
    Retrieve and rerank real Edmira employee-policy chunks.

    The test uses a unique Pinecone namespace so that previous test
    executions cannot contaminate the current run.
    """

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    load_dotenv()

    settings = load_settings()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    assert openai_api_key, (
        "OPENAI_API_KEY is not configured in .env."
    )

    assert pinecone_api_key, (
        "PINECONE_API_KEY is not configured in .env."
    )

    pinecone_index_name = settings.vector_store.index_name

    assert pinecone_index_name, (
        "Pinecone index name is not configured."
    )

    # Never use the permanent production/application namespace
    # for this integration test.
    pinecone_namespace = (
        f"test-reranker-{uuid.uuid4().hex[:12]}"
    )

    reranker_model = os.getenv(
        "RERANKER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L6-v2",
    )

    reranker_device = os.getenv("RERANKER_DEVICE")

    # ------------------------------------------------------------------
    # Sample document
    # ------------------------------------------------------------------

    sample_file = Path(
        "samples/employee_policies.txt"
    )

    assert sample_file.exists(), (
        f"Sample file not found: {sample_file}"
    )

    document_text = sample_file.read_text(
        encoding="utf-8",
    )

    assert document_text.strip(), (
        f"Sample file is empty: {sample_file}"
    )

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name=settings.embeddings.model,
        dimensions=settings.embeddings.dimensions or 1536,
    )

    vector_store = PineconeProvider(
        api_key=pinecone_api_key,
        index_name=pinecone_index_name,
        namespace=pinecone_namespace,
    )

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    reranker = RerankerFactory.create(
        provider="sentence_transformers",
        model_name=reranker_model,
        device=reranker_device,
    )

    vectors: list[dict] = []

    try:
        # ==============================================================
        # Step 1 — Chunk document
        # ==============================================================

        chunker = TextChunker()

        chunks = chunker.chunk(
            document_text,
        )

        assert chunks, (
            "No chunks were generated from employee_policies.txt."
        )

        # ==============================================================
        # Step 2 — Generate embeddings
        # ==============================================================

        embeddings = embedding_provider.embed_batch(
            chunks,
        )

        assert len(embeddings) == len(chunks), (
            "Number of embeddings does not match "
            "number of chunks."
        )

        # ==============================================================
        # Step 3 — Build Pinecone vectors
        # ==============================================================

        for index, embedding in enumerate(embeddings):
            chunk_number = index + 1

            vector_id = (
                "ragops-edmira-reranker-"
                f"hr-employee-v1-{chunk_number:04d}"
            )

            metadata = {
                "tenant_code": "edmira",
                "top_level_domain": "hr",
                "sub_domain_code": "employee_policies",
                "knowledge_base": "HR Employee Policies",
                "classification": "INTERNAL",
                "document_id": "HR-EMP-POL-001",
                "document_version_id": "1",
                "chunk_id": (
                    f"hr-employee-chunk-{chunk_number:04d}"
                ),
                "chunk_number": chunk_number,
                "filename": sample_file.name,
                "provider": embedding.provider,
                "model_name": embedding.model_name,
                "embedding_version": "1",
                "text": chunks[index],
            }

            vectors.append(
                {
                    "id": vector_id,
                    "values": embedding.vector,
                    "metadata": metadata,
                }
            )

        assert len(vectors) == len(chunks)

        # ==============================================================
        # Step 4 — Upsert controlled test data
        # ==============================================================

        vector_store.upsert_batch(
            vectors,
        )

        stored_count = vector_store.count()

        assert stored_count == len(vectors), (
            f"Expected {len(vectors)} vectors but found "
            f"{stored_count} in namespace "
            f"'{pinecone_namespace}'."
        )

        # ==============================================================
        # Step 5 — Retrieval + reranking
        # ==============================================================

        print("\n" + "=" * 100)
        print("EDMIRA LOCAL RERANKER + PINECONE INTEGRATION TEST")
        print("=" * 100)

        print(
            f"Index       : {pinecone_index_name}"
        )

        print(
            f"Namespace   : {pinecone_namespace}"
        )

        print(
            f"Document    : {sample_file.name}"
        )

        print(
            f"Chunks      : {len(chunks)}"
        )

        print(
            f"Reranker    : {reranker.provider_name}"
        )

        print(
            f"Model       : {reranker.model_name}"
        )

        print(
            f"Queries     : {len(QUERIES)}"
        )

        summary: list[dict[str, object]] = []

        for query_number, query in enumerate(
            QUERIES,
            start=1,
        ):
            print("\n")
            print("=" * 100)
            print(
                f"QUERY {query_number} OF {len(QUERIES)}"
            )
            print("=" * 100)
            print(
                f"Query: {query}"
            )

            # ----------------------------------------------------------
            # Retrieve candidates
            # ----------------------------------------------------------

            retrieved_results = retriever.retrieve(
                query=query,
                top_k=5,
            )

            assert retrieved_results, (
                f"No Pinecone results returned for query: {query}"
            )

            documents: list[str] = []

            for result in retrieved_results:
                metadata = result["metadata"]

                text = metadata.get("text")

                assert text, (
                    "Retrieved result does not contain chunk text "
                    f"for query: {query}"
                )

                # Verify our important metadata survived the vector
                # round trip.
                assert metadata.get(
                    "tenant_code"
                ) == "edmira"

                assert metadata.get(
                    "top_level_domain"
                ) == "hr"

                assert metadata.get(
                    "sub_domain_code"
                ) == "employee_policies"

                documents.append(
                    str(text)
                )

            # ----------------------------------------------------------
            # Before reranking
            # ----------------------------------------------------------

            print("\n" + "-" * 100)
            print("BEFORE RERANKING - Pinecone")
            print("-" * 100)

            for rank, result in enumerate(
                retrieved_results,
                start=1,
            ):
                metadata = result["metadata"]

                print(f"\n#{rank}")
                print(
                    "  Pinecone Score : "
                    f"{float(result['score']):.6f}"
                )

                print(
                    "  Vector ID      : "
                    f"{result['vector_id']}"
                )

                print(
                    "  Chunk ID       : "
                    f"{metadata.get('chunk_id')}"
                )

                print(
                    "  Chunk Number   : "
                    f"{metadata.get('chunk_number')}"
                )

                print(
                    "  Domain         : "
                    f"{metadata.get('top_level_domain')}"
                )

                print(
                    "  Sub-domain     : "
                    f"{metadata.get('sub_domain_code')}"
                )

                print(
                    "  Text           : "
                    f"{_shorten_text(str(metadata['text']))}"
                )

            # ----------------------------------------------------------
            # Rerank
            # ----------------------------------------------------------

            reranked_results = reranker.rerank(
                query=query,
                documents=documents,
                top_k=5,
            )

            assert reranked_results, (
                f"Reranker returned no results for query: {query}"
            )

            assert len(reranked_results) <= 5

            # ----------------------------------------------------------
            # Validate reranked indexes
            # ----------------------------------------------------------

            for rerank_result in reranked_results:
                assert (
                    0
                    <= rerank_result.index
                    < len(retrieved_results)
                )

            # ----------------------------------------------------------
            # After reranking
            # ----------------------------------------------------------

            print("\n" + "-" * 100)
            print("AFTER RERANKING - CrossEncoder")
            print("-" * 100)

            for rank, rerank_result in enumerate(
                reranked_results,
                start=1,
            ):
                original_result = retrieved_results[
                    rerank_result.index
                ]

                metadata = original_result["metadata"]

                print(f"\n#{rank}")

                print(
                    "  Reranker Score : "
                    f"{rerank_result.score:.6f}"
                )

                print(
                    "  Original Index : "
                    f"{rerank_result.index + 1}"
                )

                print(
                    "  Pinecone Score : "
                    f"{float(original_result['score']):.6f}"
                )

                print(
                    "  Vector ID      : "
                    f"{original_result['vector_id']}"
                )

                print(
                    "  Chunk ID       : "
                    f"{metadata.get('chunk_id')}"
                )

                print(
                    "  Text           : "
                    f"{_shorten_text(str(metadata['text']))}"
                )

            # ----------------------------------------------------------
            # Compare ranking
            # ----------------------------------------------------------

            pinecone_order = [
                result["vector_id"]
                for result in retrieved_results
            ]

            reranked_order = [
                retrieved_results[
                    result.index
                ]["vector_id"]
                for result in reranked_results
            ]

            ranking_changed = (
                pinecone_order != reranked_order
            )

            summary.append(
                {
                    "query": query,
                    "ranking_changed": ranking_changed,
                    "pinecone_order": pinecone_order,
                    "reranked_order": reranked_order,
                }
            )

        # ==============================================================
        # Final summary
        # ==============================================================

        changed_count = sum(
            1
            for result in summary
            if result["ranking_changed"]
        )

        unchanged_count = (
            len(summary) - changed_count
        )

        print("\n\n")
        print("=" * 100)
        print("OVERALL RERANKING SUMMARY")
        print("=" * 100)

        for index, result in enumerate(
            summary,
            start=1,
        ):
            print(f"\nQuery {index}:")
            print(
                f"  {result['query']}"
            )

            print(
                "  Ranking changed : "
                f"{result['ranking_changed']}"
            )

        print("\n" + "-" * 100)
        print(
            f"Queries tested       : {len(summary)}"
        )

        print(
            f"Ranking changed      : {changed_count}"
        )

        print(
            f"Ranking unchanged    : {unchanged_count}"
        )

        print("-" * 100)

        print(
            "\nStatus      : PASSED"
        )

        print("=" * 100)

    finally:
        # ==============================================================
        # Cleanup
        # ==============================================================
        #
        # Delete ONLY vectors created by this test.
        # Do not delete the Pinecone index or application namespace.
        #

        try:
            vector_ids = [
                vector["id"]
                for vector in vectors
            ]

            if vector_ids:
                vector_store.delete(
                    vector_ids,
                )

        finally:
            reranker.close()
            vector_store.close()
            embedding_provider.close()