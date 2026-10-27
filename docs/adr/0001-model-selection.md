# ADR 0001 Model Selection and Gateway Strategy

Status: accepted for prototype direction; model gateway is described only.

## Context

Default operation must not need an API key or network. Intake is deterministic. Wording Q&A retrieves clause text and validates clause IDs. No model call exists in this repository.

## Options

All cost, latency and quality figures are **illustrative assumptions**, not vendor quotes or benchmarks. Scores use 1 (weak) to 5 (strong); higher risk means easier to manage.

| Option | Assumed cost / 1,000 requests | Assumed median latency | Assumed task quality | Value | Risk | Scalability | Latency | Resilience | Reuse | TCO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Deterministic retrieval + templates | $0 model cost | 20 ms | 3/5 | 3 | 5 | 3 | 5 | 5 | 4 | 5 |
| Fast general model with retrieval | $4.00 | 900 ms | 4/5 | 4 | 3 | 4 | 3 | 3 | 4 | 3 |
| Frontier/reasoning model with retrieval | $30.00 | 3,000 ms | 4/5 | 4 | 2 | 4 | 2 | 3 | 3 | 2 |

## Decision

Keep deterministic retrieval and validation as the working default. If model phrasing is later introduced, use an abstraction with configurable cost caps, timeout, fallback, model/version logging and citation validation. Never allow a model to resolve a wording-version conflict.

## Criterion scores (illustrative)

| Criterion | Deterministic | Fast model | Frontier/reasoning |
|---|---:|---:|---:|
| Value | 3 | 4 | 4 |
| Risk manageability | 5 | 3 | 2 |
| Scalability | 3 | 4 | 4 |
| Latency | 5 | 3 | 2 |
| Resilience | 5 | 3 | 3 |
| Reuse | 4 | 4 | 3 |
| TCO | 5 | 3 | 2 |

## Consequences and review trigger

Default mode needs no provider SDK or model cost. The option estimates are not comparable to local synthetic evaluation metrics. Revisit if a use case needs language generation beyond deterministic phrasing or approved cost, latency or platform conditions change.
