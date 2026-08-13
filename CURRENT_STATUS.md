# RAGFramework — Current Status & Project Memory

**Last Updated:** 2026-08-12  
**Document Purpose:** Running source of truth for implementation status, architecture decisions, pending decisions, known limitations, quality gates, and next steps.  
**Current Phase:** Authorization / RBAC  
**Current Milestone:** Document-level authorization + security metadata + retrieval-time authorization  
**Overall Status:** 🟡 IN PROGRESS — Authorization core complete; retrieval security next
**Status Legend:**  
- **DONE** — implemented and tested/verified.  
- **PENDING** — agreed work that is not yet implemented or not yet fully verified.  
- **PLANNED** — intentionally deferred/future capability.

### Latest Checkpoint — 2026-08-13

**Authorization Core:** DONE  
**Authorization Smoke Test:** DONE  
**Current Focus:** Document-level authorization, security metadata on every chunk, and pre-retrieval Pinecone authorization filtering.  
**Tenant Isolation:** PLANNED as a future framework capability; `tenant_id` will be designed into the metadata contract now.  
**Audit Logging:** PLANNED for the completed application flow; audit-event design can be introduced earlier if needed.  
**Prompt-Injection Protection:** PLANNED as the separate Guardrails plugin, independent of authorization.


---

## 1. How This Document Is Used

`CURRENT_STATUS.md` is the primary running project checkpoint for RAGFramework.

It should answer:

> Where exactly are we, what has been implemented, what has been decided, what remains undecided, what is pending, and what should we implement next?

Before taking a snapshot:

1. Share the previous `CURRENT_STATUS.md`.
2. Compare it with work completed since the previous checkpoint.
3. Remove completed items from Pending sections.
4. Move resolved architectural decisions into Architecture Decisions.
5. Add newly discovered pending decisions, limitations, and next steps.
6. Record the latest quality-gate results.
7. Save the updated `CURRENT_STATUS.md`.
8. Take the project snapshot.

Do not mark an item complete merely because it appears implied. It should remain pending until implemented/tested or explicitly decided.

---

## 2. Project Goal

RAGFramework is being developed as an extensible, enterprise-oriented RAG framework supporting:

- Configuration-driven architecture
- Pluggable domains
- Document parsing and chunking
- Embedding-provider abstraction
- Vector-store abstraction
- Pinecone and FAISS
- Retrieval
- Reranking
- AI-driven intent/domain routing
- Multiple knowledge bases
- Role-based authorization
- Metadata-based authorization
- Document classification
- Enterprise identity integration
- Extensible security and governance

A core design goal is that customers can add domains, roles, access policies, and knowledge bases primarily through configuration rather than modifying core application code.

---

## 3. Current High-Level Status

```text
Configuration Foundation             → COMPLETE
Document Processing                  → COMPLETE / EXTENSIBLE
Embeddings                           → COMPLETE
Vector Store Abstraction             → COMPLETE
Pinecone Integration                 → COMPLETE
Retrieval                            → COMPLETE
Reranking                            → COMPLETE
Configuration-driven Domain Registry → COMPLETE

Authorization Architecture           → DESIGNED
Authorization Implementation         → IN PROGRESS

AI Intent / Domain Router            → NOT STARTED
Authorized Retrieval Integration     → NOT STARTED
End-to-End Query/Answer Flow          → NOT STARTED
```

---

## 4. Completed Implementation

### 4.1 Configuration

- [DONE] Centralized application configuration
- [DONE] YAML/environment configuration architecture
- [DONE] Configuration loading and management
- [DONE] Provider configuration abstractions
- [DONE] Security configuration foundation
- [DONE] Configuration-driven domain definitions

### 4.2 Document Processing

- [DONE] Document ingestion service
- [DONE] Processing pipeline abstraction
- [DONE] Validation stage
- [DONE] Parsing stage
- [DONE] Chunking stage
- [DONE] Processing context/result abstractions
- [DONE] Parsing metadata persistence

Current ingestion orchestration:

```text
Upload
  ↓
DocumentIngestionService
  ↓
ProcessingContext
  ↓
ProcessingPipeline
  ↓
Validation
  ↓
Parsing
  ↓
Chunking
  ↓
Subsequent ingestion processing
```

### 4.3 Embeddings

- [DONE] Base embedding-provider abstraction
- [DONE] Embedding result abstraction
- [DONE] OpenAI embedding provider
- [DONE] Sentence Transformer provider
- [DONE] Batch embedding support

### 4.4 Vector Store

- [DONE] Base vector-store abstraction
- [DONE] Pinecone provider
- [DONE] FAISS provider
- [DONE] Upsert abstraction
- [DONE] Batch upsert support
- [DONE] Query abstraction
- [DONE] Delete abstraction
- [DONE] Metadata filtering interface
- [DONE] Pinecone namespace configuration

Current development/testing Pinecone namespace:

```text
batch-test
```

### 4.5 Retrieval

- [DONE] Retriever abstraction
- [DONE] Query validation
- [DONE] Query embedding
- [DONE] Vector-store search
- [DONE] `top_k` validation
- [DONE] Metadata-filter forwarding
- [DONE] Empty-result handling
- [DONE] Chunk-text validation
- [DONE] Reranker integration

### 4.6 Reranking

- [DONE] Reranking abstraction
- [DONE] Local CrossEncoder integration
- [DONE] Retriever + reranker integration
- [DONE] Comparison of Pinecone ranking and CrossEncoder ranking
- [DONE] Unit/integration validation

### 4.7 Domain Architecture

- [DONE] Domain model
- [DONE] Domain configuration model
- [DONE] Domain Registry
- [DONE] Configuration-driven Domain Registry
- [DONE] Enabled/disabled domain support
- [DONE] Domain unit tests

Current intended domain examples:

```text
Employee Policies
Customer Policies
Finance Policies
Technical Documentation
```

Domains are configuration-driven and should behave like framework plugins rather than hard-coded branches.

---

## 5. Known Quality-Gate Results

Quality gates used throughout the project:

```text
mypy
pytest
ruff check
ruff format --check
```

### Retrieval milestone

Known result:

```text
mypy backend/retrieval tests/backend/retrieval
→ PASS

pytest tests/backend/retrieval -v -s
→ 8 passed
```

The retrieval tests validated:

- Retrieval without reranker preserves vector-store order
- Reranking can reorder results
- Query and chunk text are passed correctly to reranker
- Empty vector-store results are handled
- Missing chunk text is rejected
- Empty query is rejected
- Invalid `top_k` is rejected
- Pinecone retrieval works end-to-end

### Domain/configuration milestone

Domain/configuration tests were brought to green after resolving:

- Missing test imports
- `DomainRegistry`/`Domain` test imports
- Unused `pydantic.Field` import

Final user-confirmed status:

```text
mypy  → GREEN
pytest → GREEN
ruff   → GREEN
format → GREEN
```

### Snapshot rule

Before the next snapshot, run the relevant quality gates again. This document records results supplied during development and does not independently claim that the entire repository is currently green unless a repository-wide check has been run.

---

## 6. Architecture Decisions — Confirmed

These decisions are considered agreed unless explicitly revisited.

### 6.1 Configuration-driven framework

- Domains should be configuration-driven.
- Adding a new domain should not require core authorization/retrieval code changes.
- Roles should be configuration-driven.
- Access policies should be configuration-driven.
- Customer-specific combinations should be represented as configuration/data rather than Python conditionals where practical.

### 6.2 Domain routing UX

- End users should not manually select domains through buttons/dropdowns.
- Domain selection should be abstracted from the end user.
- An AI Agent/intent router should determine relevant domain(s).
- One query may concern multiple domains.
- Low-confidence/ambiguous queries should use natural-language clarification.
- Example ambiguous query:
  - `What is the approval process for travel?`
  - This may concern both Employee/HR policy and Finance policy.
- Avoid searching all domains automatically when clarification can materially improve precision, latency, and cost.

### 6.3 Separation of routing and authorization

The AI Agent answers:

> What domain(s) are relevant to this query?

Authorization answers:

> What is this user allowed to access?

These responsibilities must remain independent.

The AI Agent must never grant, expand, or override user authorization.

### 6.4 Atomic roles

Roles are atomic responsibilities.

Examples:

```text
employee
finance_manager
hr_manager
admin
```

Avoid combination roles such as:

```text
employee_finance_manager
hr_finance_manager
```

A user can have multiple roles.

### 6.5 Multi-role union

Effective access is derived from the union of access granted by all assigned roles.

Example:

```text
User
├── employee
└── finance_manager
```

results in:

```text
Employee-policy access
+
Finance-policy access
```

Conceptually:

```text
Effective Permissions
    = UNION(all role permissions)

Effective Domain Scope
    = UNION(all role domain scopes)

Effective Knowledge Base Scope
    = UNION(all role KB scopes)
```

Resource-level security constraints may still restrict the resulting union.

### 6.6 Roles, permissions, and policies are separate concepts

Target relationship:

```text
User
 ↓
Role(s)
 ↓
Permission(s)
 +
Access Policy/Policies
 ↓
Effective Access Scope
```

Permissions represent actions such as:

```text
knowledge:read
knowledge:write
knowledge:admin
```

Access policies define where those permissions apply.

### 6.7 Central authorization configuration

There should be one centralized place to configure additional roles and the access scope associated with those roles.

Target conceptual structure:

```text
authorization
├── enabled
├── rbac
├── default_role
├── roles
├── permissions
├── access policies
├── classification access
└── development users
```

Adding a role or changing its access should not require authorization-engine code changes.

### 6.8 User identity vs authorization policy

User-to-role assignment and role-to-access configuration are separate concerns.

Development:

```text
Development user configuration
        ↓
Normalized User
        ↓
Authorization
```

Production target:

```text
Enterprise Identity Provider
        ↓
JWT/OIDC claims
        ↓
Identity Resolver
        ↓
Normalized User
        ↓
Authorization
```

The RAG framework should not become the production password/user credential store.

### 6.9 Development test users

Development/test users may be configured centrally.

Planned scenarios:

```text
employee_user
    roles = employee

finance_manager_user
    roles = finance_manager

employee_finance_user
    roles = employee + finance_manager

hr_manager_user
    roles = employee + hr_manager

admin_user
    roles = admin
```

The `employee_finance_user` test is required to prove multi-role union behavior.

### 6.10 Authorization before retrieval

Unauthorized vectors should not first be retrieved and then merely hidden from the user.

Target:

```text
User
 ↓
Roles
 ↓
Authorization
 ↓
Effective authorized scope
 ↓
Pinecone metadata filter
 ↓
Retrieval
```

Authorization therefore occurs before protected retrieval.

### 6.11 Pinecone is not the authorization authority

Pinecone metadata will enforce retrieval scope, but Pinecone itself is not the source of truth for authorization.

Target:

```text
Authorization configuration/policies
        ↓
Authorization Service
        ↓
Validated Effective Scope
        ↓
Pinecone Filter
```

### 6.12 Document security boundaries

Where practical, restricted content should be stored as separate documents rather than mixing general and restricted sections inside one document.

Preferred:

```text
Employee Leave Policy       → general access
Employee WFH Policy         → internal access
Employee Compensation       → restricted access
```

rather than:

```text
Single Employee Policy
├── general content
└── restricted section
```

Chunk-level security remains a fallback for source documents that inherently mix security levels.

### 6.13 Classification metadata

Document sensitivity should be represented as structured metadata.

Current proposed levels:

```text
PUBLIC
INTERNAL
CONFIDENTIAL
RESTRICTED
```

Classification describes sensitivity.

Classification alone does not automatically grant access. Authorization policy determines which users/roles can access resources at a given classification/scope.

### 6.14 Security metadata

Expected security/retrieval metadata includes concepts such as:

```text
tenant_id
domain_id
knowledge_base_id
classification
department
country
effective_date
expiry_date
```

The final schema is still pending.

### 6.15 ABAC readiness

Initial implementation will focus on RBAC.

However, models/interfaces should not prevent later attribute-based policies using values such as:

```text
department
country
clearance
tenant
```

### 6.16 Chunk storage — temporary decision

For now, use **Option A: keep required chunk content in Pinecone** rather than introducing the separate chunk-store path immediately.

Reason:

- Reliable response generation requires consistency/atomicity between vector data and chunk content.
- A separate chunk store introduces synchronization/atomicity concerns.
- Chunk-store architecture will be revisited later.

This is a deliberate temporary architecture decision, not a permanent rejection of a separate chunk store.

---

## 7. Planned Authorization Architecture

Target flow:

```text
Authenticated User
       │
       ▼
User + Multiple Role IDs
       │
       ▼
Role Registry
       │
       ├── Role A
       ├── Role B
       └── Role C
              │
              ▼
      Permissions + Policies
              │
              ▼
          UNION / MERGE
              │
              ▼
     Effective Access Scope
              │
       ┌──────┼─────────┐
       ▼      ▼         ▼
    Domains   KBs   Metadata Constraints
              │
              ▼
      Authorization Decision
              │
          ALLOW / DENY
```

Later integration:

```text
Authenticated User
        ↓
Authorization
        ↓
Effective Access Scope
        ↓
AI Intent / Domain Router
        ↓
Relevant ∩ Authorized Domains
        ↓
Authorized Knowledge Bases
        ↓
Pinecone Metadata Filter
        ↓
Retriever
        ↓
Reranker
        ↓
LLM
```

---

## 8. Planned Security Test Documents

Use separate controlled documents for realistic authorization testing.

### Employee Policies

```text
employee_leave_policy.txt
    classification = PUBLIC

employee_wfh_policy.txt
    classification = INTERNAL

employee_compensation_policy.txt
    classification = RESTRICTED
```

### Finance Policies

```text
finance_travel_policy.txt
    classification = INTERNAL

finance_expense_policy.txt
    classification = INTERNAL

finance_forecast.txt
    classification = RESTRICTED
```

These documents will be used to test:

- Domain routing
- Knowledge-base selection
- Single-role authorization
- Multi-role authorization
- Classification restrictions
- Unauthorized retrieval prevention
- Pinecone metadata filtering

---

## 9. Pending Implementation

### 9.1 Immediate — Authorization core

- [DONE] Implement centralized authorization configuration.
- [DONE] Define role configuration model.
- [DONE] Define permission configuration model/representation.
- [DONE] Define access-policy configuration model.
- [DONE] Define development-user configuration model.
- [DONE] Define classification configuration model if required.
- [DONE] Implement authorization models.
- [DONE] Implement Role Registry.
- [DONE] Implement Access Policy Registry.
- [DONE] Implement multi-role scope union.
- [DONE] Add unit tests for atomic roles.
- [DONE] Add unit tests for multi-role users.
- [DONE] Add test proving `employee + finance_manager` produces union access.
- [DONE] Run mypy.
- [DONE] Run pytest.
- [DONE] Run ruff check.
- [DONE] Run ruff format check.

### 9.2 Authorization service

- [DONE] Implement `AuthorizationService`.
- [DONE] Define authorization request/resource contract.
- [DONE] Define `AuthorizationDecision`.
- [DONE] Resolve role IDs to configured roles.
- [DONE] Resolve policies for all roles.
- [DONE] Calculate effective permissions.
- [DONE] Calculate effective domain scope.
- [DONE] Calculate effective knowledge-base scope.
- [DONE] Apply classification/resource constraints.
- [DONE] Return ALLOW/DENY plus effective scope/reason where appropriate.

### 9.3 Identity

- [DONE] Implement normalized identity/user context.
- [DONE] Implement development identity source/provider.
- [PLANNED] Define future JWT/OIDC identity-resolution interface.
- [PLANNED] Integrate enterprise IdP later.

### 9.4 Retrieval security

- [PENDING] Add required security metadata during ingestion.
- [PENDING] Persist domain ID in Pinecone metadata.
- [PENDING] Persist knowledge-base ID in Pinecone metadata.
- [PENDING] Persist classification in Pinecone metadata.
- [PENDING] Translate effective authorization scope into Pinecone filters.
- [PENDING] Apply filters before retrieval.
- [PENDING] Add defense-in-depth authorization validation after retrieval.
- [PENDING] Add security integration tests.

### 9.5 AI routing

- [PENDING] Implement AI Intent / Domain Router.
- [PENDING] Route against enabled Domain Registry entries.
- [PENDING] Support multi-domain intent.
- [PENDING] Implement confidence handling.
- [PENDING] Implement natural-language clarification for ambiguous queries.
- [PENDING] Intersect relevant domains with authorized domains.
- [PENDING] Prevent unauthorized domain retrieval even if router selects it.

### 9.6 End-to-end RAG

- [PENDING] Build query API/service orchestration.
- [PENDING] Resolve authenticated user.
- [PENDING] Resolve authorization.
- [PENDING] Route query.
- [PENDING] Retrieve authorized chunks.
- [PENDING] Rerank.
- [PENDING] Build LLM context.
- [PENDING] Generate answer.
- [PENDING] Add citations/source references.
- [PENDING] Add end-to-end tests.

---

## 10. Pending Architecture Decisions / Open Questions

These are intentionally unresolved and must not be silently treated as complete.

### 10.1 Authorization configuration schema

- [PENDING] Final YAML structure for roles.
- [PENDING] Final YAML structure for permissions.
- [PENDING] Final YAML structure for access policies.
- [PENDING] Decide whether permissions are declared centrally and referenced by ID, or represented directly as canonical strings such as `knowledge:read`.
- [PENDING] Final development-user configuration structure.

### 10.2 Access-policy model

- [PENDING] Decide exact relationship between role and policy.
- [PENDING] Decide whether a policy can grant multiple permissions or only scope existing role permissions.
- [PENDING] Decide exact representation of domain scope.
- [PENDING] Decide exact representation of knowledge-base scope.
- [PENDING] Decide how metadata constraints are represented.
- [PENDING] Decide how multiple policies are merged.
- [PENDING] Decide whether explicit `DENY` policies are required in the first version or whether the initial model is grant-only/default-deny.

### 10.3 Classification

- [PENDING] Confirm final classification values.
- [PENDING] Decide whether classification levels are fixed framework values or customer-configurable.
- [PENDING] Decide whether classification has an ordered hierarchy or is policy-mapped without assuming hierarchy.
- [PENDING] Decide how classification interacts with role policies.
- [PENDING] Decide whether classification access belongs inside each access policy or in a reusable classification policy.

### 10.4 Knowledge Base model

- [PENDING] Confirm exact Domain → Knowledge Base relationship in the runtime model.
- [PENDING] Decide whether Knowledge Bases need their own registry/configuration layer.
- [PENDING] Decide whether one Knowledge Base can belong to more than one domain.
- [PENDING] Decide how knowledge-base IDs are represented consistently across DB, configuration, ingestion, and Pinecone.

### 10.5 Metadata schema

- [PENDING] Finalize mandatory Pinecone metadata fields.
- [PENDING] Decide which security metadata belongs at document level.
- [PENDING] Decide which fields must also be copied to every chunk/vector.
- [PENDING] Decide how document-level and chunk-level classification overrides work.
- [PENDING] Decide how tenant ID will be represented.
- [PENDING] Decide how department/country attributes will be represented.
- [PENDING] Decide whether authorized-role IDs should ever be stored in Pinecone metadata or whether all filters should be derived from policy scopes.

### 10.6 Identity / authentication

- [PENDING] Final normalized `User` / `IdentityContext` contract.
- [PENDING] Final source of role claims in production.
- [PENDING] Decide expected JWT/OIDC claim mapping.
- [PENDING] Decide whether groups can map to roles.
- [PENDING] Decide tenant-resolution strategy.
- [PENDING] Decide behavior when an authenticated user has no recognized roles.
- [PENDING] Confirm use/meaning of `default_role`.

### 10.7 Multi-role policy semantics

- [DONE] Grant scopes from multiple roles are unioned.
- [PENDING] Define behavior if future policies include explicit deny rules.
- [PENDING] Define precedence if role/policy constraints conflict.
- [PENDING] Define behavior when one role grants a domain but another policy has a narrower resource constraint.

### 10.8 Authorization failure UX

- [PENDING] Decide user-facing behavior when the query targets a domain the user cannot access.
- [PENDING] Decide how much information can safely be revealed about inaccessible domains/documents.
- [PENDING] Decide whether mixed authorized/unauthorized multi-domain queries return partial answers, request clarification, or explicitly state that part of the request cannot be answered.

### 10.9 AI Intent Router

- [PENDING] Select router implementation/model/provider.
- [PENDING] Define router input/output contract.
- [PENDING] Define confidence representation.
- [PENDING] Define low-confidence threshold.
- [PENDING] Define multi-domain threshold.
- [PENDING] Define maximum number of domains queried per request.
- [PENDING] Decide whether clarification happens before or after authorization intersection.
- [PENDING] Define handling of follow-up conversation context.

### 10.10 Retrieval / reranking

- [PENDING] Decide whether retrieval `top_k` is global or configurable per domain/KB.
- [PENDING] Decide how results from multiple authorized domains are merged.
- [PENDING] Decide whether reranking is global across domains or performed per domain then merged.
- [PENDING] Decide final score/threshold strategy.
- [PENDING] Decide handling when no sufficiently relevant authorized chunks are found.

### 10.11 Chunk store

- [DONE] Temporary decision: keep chunk text/content in Pinecone for now.
- [PLANNED] Revisit separate chunk-store architecture.
- [PENDING] Define atomicity/consistency strategy if Pinecone + external chunk store are used.
- [PENDING] Define rollback/recovery behavior for partial ingestion failures.
- [PENDING] Decide authoritative source for chunk content in the future architecture.

### 10.12 Ingestion atomicity

- [PENDING] Define document ingestion transaction/compensation strategy across database + vector store.
- [PENDING] Define cleanup behavior if Pinecone upsert partially fails.
- [PENDING] Define version activation behavior if ingestion does not fully complete.
- [PENDING] Define idempotency/retry behavior.

### 10.13 Security defense in depth

- [PENDING] Decide exact location of post-retrieval authorization validation.
- [PENDING] Decide whether final LLM context builder performs another security assertion.
- [PENDING] Define audit events for denied access and filtered retrieval.
- [PENDING] Define safe logging rules so restricted content is not leaked through logs.

### 10.14 Tenant isolation

- [PENDING] Finalize tenant/workspace isolation model.
- [PENDING] Decide whether tenant isolation uses Pinecone namespaces, metadata filters, separate indexes, or a configurable strategy.
- [PENDING] Define interaction between tenant isolation and domains/knowledge bases.

### 10.15 Testing strategy

- [PENDING] Finalize permanent security fixture documents.
- [PENDING] Define authorization matrix for test users.
- [PENDING] Add negative security tests, not only positive-access tests.
- [PENDING] Add tests proving unauthorized chunks never reach reranker/LLM.
- [PENDING] Add multi-domain + multi-role integration tests.
- [PENDING] Add classification tests.
- [PENDING] Add tenant-isolation tests when tenant model is implemented.

---

## 11. Known Limitations / Technical Debt

- Authorization architecture is designed but not yet implemented end-to-end.
- Current retrieval does not yet enforce user authorization.
- AI Intent / Domain Router is not yet implemented.
- Production identity provider integration is not implemented.
- Security metadata schema is not finalized.
- Classification model is not finalized.
- Knowledge-base registry/model relationship needs further definition.
- Chunk content is currently intended to remain in Pinecone as a temporary simplification.
- Full ingestion atomicity across persistence systems remains to be designed.
- Repository-wide quality gates should be rerun before each formal snapshot.

---

## 12. Immediate Next Milestone

### Centralized Authorization Configuration + Models

Implement:

```text
ApplicationSettings
└── authorization
    ├── roles
    ├── permissions
    ├── policies
    ├── classification access
    └── development users
```

Then implement runtime models/registries sufficient to prove:

```text
employee_user
    ↓
employee
    ↓
Employee access
```

and:

```text
employee_finance_user
    ↓
employee + finance_manager
    ↓
Employee access ∪ Finance access
```

This milestone remains independent of Pinecone/retrieval integration.

### Required quality gate before milestone completion

```text
mypy  → PASS
pytest → PASS
ruff check → PASS
ruff format --check → PASS
```

---

## 13. Snapshot Procedure

Before creating a snapshot:

```text
1. Complete the intended milestone.
2. Run relevant mypy checks.
3. Run relevant pytest suites.
4. Run ruff check.
5. Run ruff format --check.
6. Share the previous CURRENT_STATUS.md.
7. Reconcile completed and pending items.
8. Generate/update CURRENT_STATUS.md.
9. Save it in the repository root.
10. Run snapshot.py.
```

A snapshot should represent:

```text
Source Code
+
Implementation State
+
Quality Status
+
Architecture Decisions
+
Pending Decisions
+
Known Limitations
+
Next Steps
```

---

# Current Checkpoint Summary

## 🟢 Completed

- Configuration foundation
- Document-processing pipeline foundation
- Parsing
- Chunking
- Embedding abstractions/providers
- Vector-store abstraction
- Pinecone integration
- FAISS integration
- Retrieval
- Reranking
- Retrieval tests
- Configuration-driven Domain Registry
- Domain architecture
- Authorization architecture/design decisions
- Atomic-role principle
- Multi-role union principle
- Centralized authorization configuration
- Authorization runtime models
- Role Registry
- Access Policy Registry
- AuthorizationService
- Development-user authorization scenarios
- Authorization unit tests
- Authorization smoke test
- Authorization quality gates
- Temporary Pinecone-only chunk-content decision

## 🟡 Pending — Current Focus

- Document-level authorization
- Final security metadata schema
- Metadata on every chunk/vector
- Authorization filter before Pinecone retrieval
- Real sample-policy ingestion into Pinecone
- End-to-end authorized retrieval
- Defense-in-depth post-retrieval validation
- Negative security tests proving unauthorized chunks never reach reranker/LLM
- Final Knowledge Base model/registry decisions
- Final classification policy semantics
- Final identity/OIDC contract

## 🔵 Planned

- Tenant isolation implementation
- Full audit logging/observability
- Enterprise IdP integration
- AI Intent / Domain Router
- Multi-domain routing
- Guardrails plugin for input/retrieval/output protection
- End-to-end RAG answer flow
- Separate chunk-store architecture revisit
- Full ingestion atomicity/compensation strategy

## Latest Authorization Gate Result

```text
mypy                     → PASS
pytest                   → PASS
ruff check               → PASS
ruff format --check      → PASS
python -m compileall     → PASS
authorization smoke test → PASS
```

These are the latest user-confirmed results for the authorization/configuration scope. A repository-wide formal gate should still be run before a repository-wide release claim.

## Next Implementation Milestone

```text
Document-level authorization
        ↓
Canonical security metadata
        ↓
Metadata copied to every chunk/vector
        ↓
AuthorizationService → Pinecone filter
        ↓
Pre-retrieval enforcement
        ↓
Real employee/finance policy ingestion
        ↓
End-to-end security tests
```
