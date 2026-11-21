---
name: backend-engineering
description: Use when designing, implementing, or reviewing backend APIs, services, data writes, or workers. Trace authorization, dependency lifetimes, persistence, transactions, concurrency, idempotency, retries, and failure handling.
---

# Backend Engineering

Describe the invariant and failure modes before changing a server-side operation. Put enforcement where every relevant caller and concurrent process must pass through it.

## Inputs

- The endpoint, service, worker, or failure under review, plus its existing API and data contracts.
- The auth model, storage and provider behavior, and an authorized test environment or fixtures.

## Workflow

1. Trace the operation from transport through authenticated identity, resource authorization, domain decision, persistence and side effects. Derive identity on the server and scope nested resources, downloads, and job results to the same policy. Validate untrusted input at the boundary, accept only writable fields, parameterize database values, and preserve safe, actionable error contracts.
2. Keep business rules in the existing domain or service boundary so transport and storage changes do not rewrite policy. Inject a narrow dependency when a caller genuinely needs to substitute an implementation. Check that substitutes honor the same result and failure contract. Match dependency lifetimes to the unit of work, especially in workers. Prefer a direct call when it already fits the architecture. Add a repository layer, queue, or interface only when it solves a current problem.
3. Identify the atomic database changes, constraint or lock that protects them, and response on conflict. Use constraints, conditional writes, or transaction isolation appropriate to the invariant. Keep remote calls out of long-held database transactions where possible. Check schema changes against the actual database engine for compatibility, locking, and rollout constraints. For reads, bound result size and inspect real query behavior before optimizing.
4. Treat replay as part of the contract. Scope idempotency keys to the caller and operation, match the semantic payload, and atomically claim work so concurrent duplicates cannot create another operation. Reuse the original outcome or return the documented pending or conflict state. A timeout can leave a remote effect unresolved. Reconcile it through the existing operation or provider identity before replaying. Retry eligible transient failures with bounded attempts and backoff. Distinguish request cancellation from cancellation of durable work.
5. Make failures diagnosable. Record correlation IDs, latency, safe status categories, and retry counts without exposing secrets or user payloads. For workers, verify claim recovery, duplicate delivery, shutdown, and terminal failures where applicable. Use the existing job or outbox mechanism when it is needed to keep committed data and promised effects consistent.
6. Verify the changed boundary with focused checks. Use unit tests for isolated policy and a disposable instance of the relevant database for transaction, constraint, or concurrency claims. Exercise the success path and applicable denied, stale, duplicate, and partially failed operations. Use test substitutes for costly or externally visible side effects.

## Output

Report the invariant, enforcement owner, API or schema impact, expected conflict and recovery behavior, and the checks actually run. Call out migration or rollout implications when they affect callers or stored data.

## Example

Fictional example: A client retries an export request after a timeout. Claim the request once per account and request key, verify that reuse matches the original payload, and return the original job identity for a valid replay. Check two simultaneous requests and a timeout after admission with a disposable database.

## Verification and limits

A successful mocked call does not establish isolation, locking, or crash recovery. Durable state and idempotency can prevent duplicate local effects, while remote execution guarantees depend on the provider and recovery contract.
