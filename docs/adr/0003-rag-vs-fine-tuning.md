# ADR 0003 Retrieval Augmented Generation or Fine Tuning

Status: accepted for wording Q&A prototype direction. Retrieval is implemented; model generation and fine-tuning are not.

## Context

Wording answers need clause IDs and must surface differences between versions. The clause set changes over time, and answers need traceable evidence.

## Options and scores

Scores are illustrative, on a 1 (weak) to 5 (strong) scale; risk means manageability. Cost and latency assumptions are not benchmarks.

| Option | Value | Risk | Scalability | Latency | Resilience | Reuse | TCO |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keyword retrieval + deterministic answer | 4 | 5 | 3 | 5 | 4 | 4 | 5 |
| Retrieval + model phrasing | 5 | 3 | 4 | 3 | 3 | 4 | 3 |
| Fine-tune on wording text | 2 | 2 | 3 | 4 | 2 | 2 | 2 |

## Decision

Use retrieval over versioned clauses with deterministic phrasing and citation validation. If a model is added, use retrieved clauses as evidence, validate each cited ID against retrieved evidence, and decline on missing evidence or version conflicts. Do not fine-tune on changing contract wording for this task.

## Criterion scores (illustrative)

| Criterion | Deterministic retrieval | RAG phrasing | Fine-tuning |
|---|---:|---:|---:|
| Value | 4 | 5 | 2 |
| Risk manageability | 5 | 3 | 2 |
| Scalability | 3 | 4 | 3 |
| Latency | 5 | 3 | 4 |
| Resilience | 4 | 3 | 2 |
| Reuse | 4 | 4 | 2 |
| TCO | 5 | 3 | 2 |

## Consequences and review trigger

Versioned retrieval supports provenance but does not prove legal correctness or identify an operative version. Revisit if users require paraphrased answers or the approved model and evaluation context changes.
