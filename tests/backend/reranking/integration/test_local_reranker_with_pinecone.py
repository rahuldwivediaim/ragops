"""
Local reranker + Pinecone integration test.

Runs multiple real-world queries through the production retrieval flow
and compares Pinecone's vector ranking against the local
Sentence Transformers CrossEncoder ranking.

Flow:

    Query
        ↓
    OpenAI embedding
        ↓
    Pinecone similarity search
        ↓
    Retrieved chunk text
        ↓
    Local CrossEncoder
        ↓
    Reranked results
        ↓
    Ranking comparison

No mock retrieval or mock reranking is used.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

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
    "How many unused leave days can be carried forward?",
    "What is the policy for working from home?",
    "Who can access confidential employee information?",
    "What should an employee do when reporting an incident?",
]


def _shorten_text(text: str, max_length: int = 140) -> str:
    """Return a compact single-line preview of document text."""

    text = " ".join(text.split())

    if len(text) <= max_length:
        return text

    return f"{text[:max_length]}..."


def test_local_reranker_with_pinecone() -> None:
    """
    Retrieve and rerank multiple real queries using Pinecone
    and the local Sentence Transformers CrossEncoder.
    """

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    pinecone_index_name = os.getenv(
        "PINECONE_INDEX_NAME",
        "ragframeworkdev",
    )

    pinecone_namespace = os.getenv(
        "PINECONE_NAMESPACE",
        "default",
    )

    reranker_model = os.getenv(
        "RERANKER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L6-v2",
    )

    reranker_device = os.getenv("RERANKER_DEVICE")

    assert openai_api_key, "OPENAI_API_KEY is not configured in .env."

    assert pinecone_api_key, "PINECONE_API_KEY is not configured in .env."

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name="text-embedding-3-small",
        dimensions=1536,
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

    try:
        print("\n" + "=" * 100)
        print("MULTI-QUERY RERANKING INTEGRATION TEST")
        print("=" * 100)
        print(f"Index       : {pinecone_index_name}")
        print(f"Namespace   : {pinecone_namespace}")
        print(f"Reranker    : {reranker.provider_name}")
        print(f"Model       : {reranker.model_name}")
        print(f"Queries     : {len(QUERIES)}")

        summary: list[dict[str, object]] = []

        # ==============================================================
        # Execute all queries
        # ==============================================================

        for query_number, query in enumerate(
            QUERIES,
            start=1,
        ):
            print("\n")
            print("=" * 100)
            print(f"QUERY {query_number} OF {len(QUERIES)}")
            print("=" * 100)
            print(f"Query: {query}")

            # ----------------------------------------------------------
            # Retrieve candidates from Pinecone
            # ----------------------------------------------------------

            retrieved_results = retriever.retrieve(
                query=query,
                top_k=5,
            )

            assert retrieved_results, f"No Pinecone results returned for query: {query}"

            documents: list[str] = []

            for result in retrieved_results:
                metadata = result["metadata"]

                text = metadata.get("text")

                assert text, (
                    f"Retrieved result does not contain chunk text for query: {query}"
                )

                documents.append(str(text))

            # ----------------------------------------------------------
            # BEFORE RERANKING
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
                print(f"  Pinecone Score : {float(result['score']):.6f}")
                print(f"  Vector ID      : {result['vector_id']}")
                print(f"  Chunk ID       : {metadata.get('chunk_id')}")
                print(f"  Chunk Number   : {metadata.get('chunk_number')}")
                print(f"  Text           : {_shorten_text(str(metadata['text']))}")

            # ----------------------------------------------------------
            # Rerank
            # ----------------------------------------------------------

            reranked_results = reranker.rerank(
                query=query,
                documents=documents,
                top_k=5,
            )

            assert reranked_results, f"Reranker returned no results for query: {query}"

            assert len(reranked_results) <= 5

            # ----------------------------------------------------------
            # AFTER RERANKING
            # ----------------------------------------------------------

            print("\n" + "-" * 100)
            print("AFTER RERANKING - CrossEncoder")
            print("-" * 100)

            for rank, rerank_result in enumerate(
                reranked_results,
                start=1,
            ):
                original_result = retrieved_results[rerank_result.index]

                metadata = original_result["metadata"]

                print(f"\n#{rank}")
                print(f"  Reranker Score : {rerank_result.score:.6f}")
                print(f"  Original Index : {rerank_result.index + 1}")
                print(f"  Pinecone Score : {float(original_result['score']):.6f}")
                print(f"  Vector ID      : {original_result['vector_id']}")
                print(f"  Chunk ID       : {metadata.get('chunk_id')}")
                print(f"  Chunk Number   : {metadata.get('chunk_number')}")
                print(f"  Text           : {_shorten_text(str(metadata['text']))}")

            # ----------------------------------------------------------
            # Compare ranking
            # ----------------------------------------------------------

            pinecone_order = [result["vector_id"] for result in retrieved_results]

            reranked_order = [
                retrieved_results[result.index]["vector_id"]
                for result in reranked_results
            ]

            ranking_changed = pinecone_order != reranked_order

            # ----------------------------------------------------------
            # Identify moved chunks
            # ----------------------------------------------------------

            moved_chunks: list[str] = []

            for original_position, vector_id in enumerate(
                pinecone_order,
                start=1,
            ):
                if vector_id not in reranked_order:
                    continue

                new_position = reranked_order.index(vector_id) + 1

                if original_position != new_position:
                    moved_chunks.append(
                        f"{vector_id}: {original_position} -> {new_position}"
                    )

            print("\n" + "-" * 100)
            print("RANKING COMPARISON")
            print("-" * 100)

            print("\nPinecone order:")

            for position, vector_id in enumerate(
                pinecone_order,
                start=1,
            ):
                print(f"  {position}. {vector_id}")

            print("\nCrossEncoder order:")

            for position, vector_id in enumerate(
                reranked_order,
                start=1,
            ):
                print(f"  {position}. {vector_id}")

            print(f"\nRanking changed : {ranking_changed}")

            if moved_chunks:
                print("\nMoved chunks:")

                for moved_chunk in moved_chunks:
                    print(f"  - {moved_chunk}")

            else:
                print("\nMoved chunks: None")

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

        changed_count = sum(1 for result in summary if result["ranking_changed"])

        unchanged_count = len(summary) - changed_count

        print("\n\n")
        print("=" * 100)
        print("OVERALL RERANKING SUMMARY")
        print("=" * 100)

        for index, result in enumerate(
            summary,
            start=1,
        ):
            print(f"\nQuery {index}:")
            print(f"  {result['query']}")

            print(f"  Ranking changed : {result['ranking_changed']}")

        print("\n" + "-" * 100)
        print(f"Queries tested       : {len(summary)}")
        print(f"Ranking changed      : {changed_count}")
        print(f"Ranking unchanged    : {unchanged_count}")
        print("-" * 100)

        print("\nStatus      : PASSED")
        print("=" * 100)

    finally:
        reranker.close()
        vector_store.close()
        embedding_provider.close()
