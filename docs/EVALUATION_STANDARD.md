# Evaluation standard

> **Synthetic prototype evidence.** All data, labels, thresholds, owners, and measurements in this document are invented or illustrative. These results are not production evidence or regulatory guidance.

## Evaluation design

The prototype uses deterministic extraction and keyword retrieval. It makes no model/API calls and sends no data over a network. Expected values and question outcomes are author-labelled before evaluation. The small sets are useful for exercising controls and reporting, not for estimating generalisable real-world performance.

| Use case | Set and denominator | Metrics reported | Current result |
|---|---:|---|---|
| Submission intake | 8 synthetic labelled submissions; 9 fields each (72 field values) | Exact field-value accuracy; validation routing; auto-accept count | 72/72 = 100%; 3/8 submissions require human review; 0 auto-accepted |
| Wording Q&A | 20 author-labelled questions | Outcome accuracy; citation-ID validity; refusal correctness; supported-answer accuracy | 20/20 outcomes; 16/16 cited IDs valid; 7/7 refusal cases correct; 10/10 supported answers correct |

A citation-ID validity score only confirms that cited IDs exist in the synthetic clause set. It does not prove that a passage semantically supports an answer. This prototype has no generative model, so generative hallucination rate is **not measured**.

## Illustrative gate thresholds

These are prototype demonstration thresholds, not external standards or compliance requirements. The review command reads these values from `data/design_authority/review_config.json`.

| Gate signal | Illustrative threshold | Intake observed | Wording observed |
|---|---:|---:|---:|
| Minimum labelled sample | 20 records/questions | 8 — condition | 20 — pass |
| Field or answer outcome accuracy | ≥95% | 100% — condition remains because sample is below minimum | 100% |
| Citation-ID validity | ≥95% | Not applicable | 100% |
| Refusal correctness | ≥90% | Not applicable | 100% |

The intake use case is **APPROVED WITH CONDITIONS** because its eight labelled examples do not meet the illustrative minimum sample size, despite the observed 72/72 field matches. The wording use case is **APPROVED** for this simulated prototype gate only. Neither result authorises production deployment.

## Latency and cost

A local micro-measurement ran each evaluation function 50 times on the same development machine. Observed median / p95 execution time was 0.946 / 2.618 ms for intake evaluation and 42.703 / 85.508 ms for wording evaluation. These figures include local file loading and evaluation work, exclude user/network/model latency, and are not service-level objectives. They are machine-specific measurements from one small synthetic workload.

External model/API cost per request is **$0.00 by design** in the implemented default path: no model call is made. Human review, hosting, storage, support, and broader operating TCO are not costed. Any future model option would require an explicit token/volume/currency assumption and measured provider pricing before comparison.

## Production evaluation plan (described only)

Before any real deployment, establish representative and independently reviewed datasets, segment-level metrics, versioned baselines, and a documented approval owner. Add tests for semantic grounding, unsupported-claim rate, citation entailment, wrong-contract isolation, prompt injection, sensitive-data leakage, robustness, fairness where relevant, and operational failure modes. Define latency and cost budgets using an agreed workload, then monitor them in production.

Re-evaluate when source wording, extraction logic, retrieval configuration, model/prompt, or user population changes. Illustrative triggers include a material decline against an agreed metric, a newly observed unsupported answer, a citation failure, a cross-contract retrieval, an incident, or a material input-distribution shift. Thresholds and escalation owners must be set with accountable business, risk, security, privacy, and operations roles; they are not implemented here.

