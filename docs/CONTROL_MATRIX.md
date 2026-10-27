# Responsible AI Control Matrix

Synthetic controls; illustrative mappings, not regulatory requirements.

| Control | Owner role | Risk | Control statement | Status | Code reference | Evidence |
|---|---|---|---|---|---|---|
| RAI-01 | Synthetic Wording Product Lead (synthetic) | Hallucination: unsupported wording answer | Decline when no clause evidence is retrieved. | implemented | insure_ai.wording.ask | Outcome code INSUFFICIENT_EVIDENCE in QA evaluation. |
| RAI-02 | Synthetic Wording Quality Lead (synthetic) | Hallucination: fabricated or unsupported citations | Validate cited clause IDs against retrieved pack. | implemented | insure_ai.wording.validate_citations | Citation validity numerator and denominator in QA evaluation. |
| RAI-03 | Synthetic Underwriting AI Lead (synthetic) | Wrong contract used | Decline when requested contract is absent from the pack. | implemented | insure_ai.wording.ask | WRONG_CONTRACT expected-outcome cases. |
| RAI-04 | Synthetic Wording Product Lead (synthetic) | Version conflict hidden | Surface differing version clauses without choosing operative version. | implemented | insure_ai.wording.ask | CONFLICT answers cite clauses from each differing version. |
| RAI-05 | Synthetic Intake Operations Lead (synthetic) | Invalid intake proceeds | Route each validation failure to human review with reason codes. | implemented | insure_ai.intake.process_submissions | Reason codes and zero auto-accept count. |
| RAI-06 | Synthetic Privacy Lead (synthetic) | Privacy and PII exposure | Use synthetic data only; production minimization and PII controls remain to be designed. | described_only | described only | Synthetic-data notice and explicit scope boundary. |
| RAI-07 | Synthetic AI Platform Lead (synthetic) | Prompt injection | No model prompt exists in default mode; production prompt-injection controls remain a design item. | described_only | described only | Architecture marks model gateway as described only. |
| RAI-08 | Synthetic Responsible AI Lead (synthetic) | Triage bias | Assess class and source impacts before a production triage model; this prototype uses fixed rules. | described_only | described only | Standards identify bias review as a production requirement. |
| RAI-09 | Synthetic Underwriting Operations Lead (synthetic) | Human oversight missing | Keep explicit review outcomes for failed intake and wording conflicts. | implemented | insure_ai.intake.process_submissions | HUMAN_REVIEW_REQUIRED for every failed validation. |
| RAI-10 | Synthetic Model Governance Lead (synthetic) | Model change untracked | Version models/prompts and rerun evaluations before production changes. | described_only | described only | Model lifecycle requirements in standards and review criteria. |
| RAI-11 | Synthetic AI Governance Lead (synthetic) | Decisions not reconstructable | Maintain an append-only record of inputs, outcome, reason codes and citations per run. | described_only | described only | Control described in the matrix; application code does not write a per-run decision record. |
