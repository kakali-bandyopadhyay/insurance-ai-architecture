# Architecture Principles and Minimum Standards

Synthetic roles and data; illustrative. This prototype checklist is not production approval or regulatory guidance. Any regulatory or Responsible-AI mapping is illustrative, not a statement of requirements.

## Principles

1. **Evidence before fluency.** Answers expose the clause IDs and versions that support them.
2. **Humans own material outcomes.** No submission is accepted and no contract interpretation is finalized by this prototype.
3. **Decline cleanly.** Missing evidence, an out-of-pack contract, or conflicting versions produces an explicit decline or escalation.
4. **Validate at boundaries.** Required fields, ranges, dates and completeness are checked before downstream use.
5. **Evaluate the intended task.** Keep labels fixed before a run; report denominators and separate answer quality, citation validity and refusal correctness.
6. **Prefer reusable services.** Share evaluation, inventory and control patterns where they are genuinely common; avoid unnecessary platform dependencies.
7. **Make limitations visible.** Mark synthetic content, assumptions, unimplemented components and measured versus assumed values.
8. **Design for operation.** Define ownership, error paths, monitoring, cost controls and handover before production.
9. **Protect data by design.** Minimize data, enforce access, define retention and test privacy/security controls before handling real records.
10. **Review lifecycle changes.** Re-evaluate when data, model, prompts, retrieval, policies or downstream actions change.

## Minimum standards before production

| Area | Minimum evidence expected |
|---|---|
| Value and ownership | Named business owner, intended workflow, accountable operating owner and measurable success criteria. |
| Data readiness | Documented sources, rights, quality, classification, retention, lineage and access boundaries. |
| Architecture | Approved design, dependencies, integrations, failure modes, capacity, resilience and lifecycle plan. |
| Model and retrieval | Model/provider decision, prompt/context controls, versioning, fallback, retrieval and output validation where applicable. |
| Evaluation | Frozen representative test set, task-specific metrics, thresholds, negative cases, robustness checks and approval evidence. |
| Security and privacy | Threat model, identity, data minimization, PII handling, secrets, logging and security-test evidence. |
| Responsible AI | Human oversight, escalation, refusal behavior, risk assessment, transparency and accountable review. |
| Operability | Service measures, alerting, traceability, incident/runbook, support ownership, rollback and change controls. |
| Economics | Cost per request, volume assumptions, latency budget, infrastructure/TCO, routing and budget controls. |
| Governance | Architecture review outcome, inventory record, control evidence, decision log and post-launch review plan. |

A prototype passing local tests is not evidence that production controls are satisfied.
