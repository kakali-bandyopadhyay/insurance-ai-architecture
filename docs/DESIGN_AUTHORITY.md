# Design Authority Pack

Synthetic roles and data; illustrative. The local `review` command simulates a pre-production readiness review using evidence generated in this repository. Its output is not an enterprise approval. Regulatory or Responsible-AI mappings are illustrative, not statements of requirements.

## Review criteria

| Criterion | Evidence considered |
|---|---|
| Business value | Defined workflow and decision supported; no measured benefit claim without synthetic computation. |
| Data readiness | Documented synthetic sources, schema, labels, completeness and limitations. |
| Architecture fit | Implemented flow and explicit boundary between delivered code and described services. |
| Security and privacy | Data classification, minimization, access design, PII approach and security tests; synthetic-only scope is not production assurance. |
| Responsible AI | Human decision points, refusal behavior, conflict handling, transparency and control ownership. |
| Evaluation evidence | Frozen author-labelled sets, adequate sample size for the gate, task-specific outcomes and thresholds. |
| Operability | Run instructions, failure handling, observability, ownership and support model. |
| Cost and TCO | Cost per request, scale assumptions, cost limits, resilience and total operating cost. |

## Gate stages

| Stage | Required decision evidence |
|---|---|
| Concept | Problem, owner, users, outcomes, data plausibility and alternatives. |
| Design | Target flow, data, model/retrieval, security, privacy, controls and integration decisions. |
| Pre-production | Evaluation thresholds, readiness, access, resilience, runbook, cost, rollback and owner sign-off. |
| Post-launch | Adoption, quality, drift, incidents, cost, control effectiveness and continue/change/retire decision. |

Run `python -m insure_ai review`. A criterion is **CONDITION** whenever its evidence says a production control is "not implemented" or "described only". Data readiness also follows the use case's minimum labelled-set threshold: a set below that threshold is a condition even when observed accuracy is high. Cost and TCO is a condition while operating TCO is not modelled.

## Latest simulated pre-production review

| Use case | Outcome | Conditions |
|---|---|---|
| Submission intake | **APPROVED WITH CONDITIONS** | Data readiness (8 submissions vs. 20 minimum); architecture fit (production integrations described only); security and privacy (production PII controls not implemented); evaluation evidence (8 labels vs. 20 minimum); operability (production monitoring described only); cost and TCO (operating TCO not modelled). |
| Wording QA | **APPROVED WITH CONDITIONS** | Architecture fit (production model gateway described only); security and privacy (production access controls and PII handling not implemented); operability (production telemetry and monitoring described only); cost and TCO (operating TCO not modelled). |

No criterion is returned in this simulation. These outcomes are prototype review evidence, not production approval. Auditability for reconstructing each run is described only because the application does not persist an append-only record of inputs, outcome, reason codes and citations.
