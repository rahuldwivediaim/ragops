"""
Pinecone Index client lifecycle test.

This test creates and closes a Pinecone Index client.
It does not insert, query, or delete vectors.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pinecone import Pinecone


def test_pinecone_index_lifecycle() -> None:
    """
    Verify that the Pinecone Index client can be created
    and closed without leaving network resources behind.
    """

    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv(
        "PINECONE_INDEX",
        "ragframeworkdev",
    )

    assert api_key, "PINECONE_API_KEY is not configured in .env."

    client = Pinecone(
        api_key=api_key,
    )

    index = None

    try:
        index = client.Index(index_name)

        print("\n" + "=" * 80)
        print("Pinecone Index Lifecycle Test")
        print("=" * 80)
        print(f"Index: {index_name}")
        print("Index client created successfully.")
        print("=" * 80)

    finally:
        if index is not None:
            index.close()

        client.close()
