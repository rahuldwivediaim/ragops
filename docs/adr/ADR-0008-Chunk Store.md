# ADR-0008: Chunk Store as Source of Truth with Transactional Vector Synchronization

**Status:** Accepted  
**Date:** 2026-08-10

---

## Context

RAGFramework uses a vector database such as **Pinecone** or **FAISS** for semantic retrieval.

A vector record represents a document chunk through:

- Vector ID
- Embedding
- `document_id`
- `document_version_id`
- `chunk_id`
- `chunk_number`
- Embedding provider/model information
- Other retrieval metadata

The framework also needs to retain the **actual chunk text** and support lifecycle operations such as:

- Create
- Update
- Delete
- Re-index
- Document/version changes

Using the vector database as the only source of chunk data creates coupling between document management and vector search.

A separate **Chunk Store** provides a system of record for chunk content and lifecycle state, while Pinecone/FAISS acts as a derived search index.

However, this introduces a consistency problem.

For example:

```text
Chunk Store
    chunk-001 → deleted

Pinecone
    chunk-001 → still exists

    A subsequent vector search could return chunk-001, even though its authoritative chunk no longer exists.

Similarly, an update could succeed in the Chunk Store but fail while updating the vector database.

Therefore, the framework requires a mechanism for:

Coordinating chunk lifecycle operations
Recovering from partial failures
Retrying failed vector-store operations
Preventing orphan vectors
Maintaining consistency between the Chunk Store and vector indexes
Supporting rollback/recovery
Decision

RAGFramework will introduce a persistent Chunk Store as the source of truth for chunk content and lifecycle state.

Pinecone and FAISS will be treated as derived vector search indexes.

The architecture will use a transactional chunk-operation table to record changes that affect both the Chunk Store and vector stores.

The operation record will preserve the information necessary to complete, retry, or recover an operation.

High-Level Architecture
                         RAGFramework
                              │
                ┌─────────────┴─────────────┐
                │                           │
          Chunk Store                 Vector Store
          PostgreSQL                Pinecone / FAISS
        Source of Truth              Derived Index
                │                           │
                │                           │
                └───────┬───────────────────┘
                        │
                Chunk Operation
                / Recovery Layer
Chunk Store

The Chunk Store will contain the authoritative chunk information.

Conceptually:

chunks
────────────────────────────────────
chunk_id
document_id
document_version_id
chunk_number
chunk_text
status
created_at
updated_at

The chunk status will support lifecycle states such as:

ACTIVE
PENDING_UPDATE
PENDING_DELETE
INDEXED
FAILED
DELETED

The exact state machine will be finalized during implementation.

Transactional Operation Table

A dedicated table will track operations that must be synchronized with the vector store.

Conceptually:

chunk_operations
────────────────────────────────────────────
operation_id
operation_type
chunk_id
document_id
document_version_id
vector_id
status
original_chunk_data
new_chunk_data
retry_count
error_message
created_at
updated_at

Possible operation types:

CREATE
UPDATE
DELETE
REINDEX

The table will act as both:

Operation tracking
Recovery/rollback information
Delete Strategy

A chunk will not be immediately physically deleted from the Chunk Store.

Instead:

ACTIVE
  ↓
PENDING_DELETE
  ↓
Create operation record
  ↓
Delete vector from Pinecone/FAISS
  ↓
SUCCESS
  ↓
Physically delete chunk
  ↓
Remove completed operation record

If the vector-store operation fails:

PENDING_DELETE
       ↓
FAILED
       ↓
Retry

The original chunk data retained by the operation record can be used for recovery if required.

Update Strategy

Updates will similarly be coordinated.

Example:

Old chunk:
"Employees receive 20 days of leave."

New chunk:
"Employees receive 25 days of leave."

The operation records both states:

original_chunk_data
        +
new_chunk_data

The system then:

PENDING_UPDATE
      ↓
Update Chunk Store
      ↓
Generate new embedding
      ↓
Update/upsert vector
      ↓
SUCCESS
      ↓
INDEXED

If the vector operation fails, the system can retry or restore the previous state.

Retrieval Consistency

The Chunk Store is authoritative.

Therefore, a vector returned by Pinecone/FAISS must not automatically be considered valid context.

Retrieval will follow:

User Query
    ↓
Query Embedding
    ↓
Vector Search
    ↓
Top-N Vector IDs
    ↓
Chunk Store Lookup
    ↓
Validate chunk status/version
    ↓
Retrieve chunk text
    ↓
Reranking
    ↓
Context Construction
    ↓
LLM

If a vector exists in Pinecone but its chunk_id does not exist or is not active in the Chunk Store:

Vector
  ↓
Chunk lookup
  ↓
NOT FOUND / INVALID
  ↓
Discard result
  ↓
Log consistency issue

This protects the LLM from using stale or orphaned content.

Reconciliation

The framework will eventually provide a reconciliation capability to detect inconsistencies between the Chunk Store and vector stores.

Examples:

Chunk Store:
10,000 chunks

Pinecone:
9,998 vectors

Potential results:

Missing vector:
chunk-00451

Orphan vector:
chunk-00892

The reconciliation process can initiate corrective operations.

Versioning

Document and chunk versions will be supported.

Example:

Document: RAG-EMP-001

Version 1
 ├── chunk-001
 ├── chunk-002
 └── chunk-003

Version 2
 ├── chunk-001
 ├── chunk-002
 ├── chunk-003
 └── chunk-004

Vector metadata will contain:

document_id
document_version_id
chunk_id

This allows retrieval and vector lifecycle operations to be associated with the correct document version.

Embedding metadata will also retain:

provider
model_name
embedding_version

to support future re-embedding and model migration.

Consequences
Positive
1. Clear source of truth

The Chunk Store becomes authoritative for:

Chunk text
Chunk lifecycle
Document/version relationships
Chunk status
2. Vector database becomes replaceable

The same Chunk Store can support:

Pinecone
FAISS
Other vector databases

without making the vector database the master data store.

3. Safer updates and deletes

Partial failures can be recovered using the transactional operation record.

4. Retry capability

Failed Pinecone/FAISS operations can be retried without losing the original operation context.

5. Better auditability

We can determine:

Who/what changed the chunk?
What changed?
When?
Was the vector index updated?
Did the operation fail?
Was it retried?
6. Re-indexing becomes easier

The Chunk Store remains intact while vectors can be regenerated using a different embedding model.

For example:

Chunk Store
     ↓
New embedding model
     ↓
New vector index
7. Better RAG quality and safety

Retrieval can validate that returned vector IDs correspond to valid, active chunks before sending context to the LLM.

Negative / Trade-offs
1. Additional infrastructure

We introduce a relational database such as PostgreSQL.

2. Eventual consistency

Chunk Store and vector indexes are separate systems and cannot normally be updated atomically as one database transaction.

3. More implementation complexity

We need:

Operation tracking
Retry handling
Recovery
Reconciliation
Status management
4. Additional database lookup during retrieval

The retrieval path may become:

Pinecone
   ↓
Chunk IDs
   ↓
PostgreSQL
   ↓
Chunk text

This adds some latency, but batch retrieval will be used rather than one database call per chunk.

Alternatives Considered
Alternative 1 — Store everything in Pinecone
Pinecone
 ├── vector
 └── chunk text + metadata

Rejected as the long-term architecture.

It is simple and will remain supported for the initial implementation, but it couples document storage with vector search.

Alternative 2 — Store chunks only as files
Document
   ↓
Chunk files
   ↓
Vector database

Rejected as the primary Chunk Store.

Files are useful for raw documents and snapshots but provide weaker transactional lifecycle management, querying, concurrency, version management, and operational auditing than a relational database.

Alternative 3 — Directly modify both systems
Application
   ├── update PostgreSQL
   └── update Pinecone

Rejected.

A failure between the two operations can leave inconsistent state without a durable recovery mechanism.

Future Enhancements

The transactional operation table can evolve into an Outbox / indexing operation mechanism.

Potential future architecture:

PostgreSQL
│
├── documents
├── document_versions
├── chunks
├── chunk_operations
└── outbox_events
          │
          ▼
    Indexing Worker
          │
          ├── Pinecone
          └── FAISS

This would allow:

Asynchronous processing
Retries
Monitoring
Reconciliation
Better scalability
Better failure recovery
Decision Summary

RAGFramework will use a persistent Chunk Store as the authoritative source of chunk content and lifecycle state. Pinecone and FAISS will be treated as derived vector indexes. Chunk modifications will be coordinated through a durable transactional operation mechanism that supports retry, recovery, and reconciliation.

The key principle is:

             SOURCE OF TRUTH
                   │
                   ▼
              Chunk Store
                   │
                   │ derives
                   ▼
             Vector Index
          ┌────────┴────────┐
          ▼                 ▼
       Pinecone            FAISS

This ADR provides the foundation for:

PostgreSQL Chunk Store
Chunk lifecycle management
Transactional operations
Pinecone synchronization
Persistent FAISS
Retrieval
Hybrid retrieval
Reranking
RAG answer generation
RAG evaluation with Ragas
Reconciliation
Audit and operational logging