"""
Pinecone index statistics test.

This is a read-only integration test.

It does not insert, query, or delete vectors.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pinecone import Pinecone


def test_pinecone_index_stats() -> None:
    """
    Verify that Pinecone index statistics can be retrieved
    and the clients can be closed cleanly.
    """

    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")

    index_name = os.getenv(
        "PINECONE_INDEX",
        "ragframeworkdev",
    )

    namespace = os.getenv(
        "PINECONE_NAMESPACE",
        "default",
    )

    assert api_key, (
        "PINECONE_API_KEY is not configured in .env."
    )

    client = Pinecone(
        api_key=api_key,
    )

    index = None

    try:
        index = client.Index(
            index_name,
        )

        statistics = index.describe_index_stats()

        print("\n" + "=" * 80)
        print("Pinecone Index Statistics Test")
        print("=" * 80)
        print(f"Index     : {index_name}")
        print(f"Namespace : {namespace}")

        namespace_statistics = statistics.namespaces.get(
            namespace,
        )

        if namespace_statistics is None:
            record_count = 0
        else:
            record_count = int(
                namespace_statistics.vector_count
            )

        print(f"Record Count: {record_count}")
        print("=" * 80)

        assert record_count >= 3

    finally:
        if index is not None:
            index.close()

        client.close()