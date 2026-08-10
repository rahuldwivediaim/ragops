"""
Pinecone connection lifecycle test.

This test only creates and closes the Pinecone client.
It does not create, query, or delete any vectors.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pinecone import Pinecone


def test_pinecone_connection_lifecycle() -> None:
    """
    Verify that the Pinecone client can be created and closed
    without leaving network resources behind.
    """

    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")

    assert api_key, (
        "PINECONE_API_KEY is not configured in .env."
    )

    client = Pinecone(
        api_key=api_key,
    )

    try:
        indexes = client.list_indexes()

        print("\n" + "=" * 80)
        print("Pinecone Connection Test")
        print("=" * 80)
        print(f"Indexes available: {len(indexes)}")
        print("=" * 80)

    finally:
        client.close()