# Evaluation findings

> **Synthetic prototype evidence.** Every record, question, label, metric, role, and result here is invented and illustrative. The samples are small and author-labelled; results must not be presented as production performance.

## Submission intake

- Scope: 8 synthetic submission packs, 9 extracted fields per pack, 72 expected field values.
- Exact field-value matches: 72/72 (100%) on this author-labelled sample.
- Validation routing: 3/8 packs were routed to human review for seeded issues; all failed items were routed; 0 packs were auto-accepted.
- Review examples: missing loss year, total insured value below limit, missing insured name and invalid inception date.
- Decision: **APPROVED WITH CONDITIONS** at the simulated pre-production gate. Conditions: 8 submissions are below the illustrative minimum of 20; production integrations and monitoring are described only; production PII controls are not implemented; and operating TCO is not modelled. The high sample accuracy does not override the label-count condition. This small set is a code-path demonstration, not evidence that extraction is production-ready.

## Wording Q&A

- Scope: 20 author-labelled questions over 16 clauses in synthetic, versioned wording documents.
- Composition: 10 supported questions, 4 insufficient-evidence questions, 3 wrong-contract questions, and 3 questions with conflicting version text.
- Outcomes: 20/20 correctly classified (100%); citation IDs valid in 16/16 cited answers (100%); refusal decisions correct in 7/7 refusal cases (100%); supported answers correct in 10/10 cases (100%).
- Decision: **APPROVED WITH CONDITIONS** at the simulated pre-production gate. Conditions: the production model gateway is described only; production access controls, PII handling, telemetry and monitoring are not implemented; and operating TCO is not modelled. The 20 labelled questions meet the illustrative data-readiness and evaluation thresholds. Keyword retrieval and deterministic conflict handling are implemented; a generative answer model is not. Citation-ID existence is not semantic entailment.

## Responsible AI control ownership and auditability

All 11 controls have synthetic owner roles, and RAI-01/RAI-02 explicitly identify hallucination risk. RAI-11 covers reconstructing decisions through an append-only per-run record of inputs, outcome, reason codes and citations. Its status is **described only**: the application does not currently write that record.

## Verification

- Pytest: **126 passed** after the control, review, dashboard and test changes.
- Review: intake and wording QA are both **APPROVED WITH CONDITIONS**; see the criterion-level conditions above and in `DESIGN_AUTHORITY.md`.
- Editable-install check: a fresh Python 3.14 virtual environment was created, but `pip install -e .` could not finish because this environment could not resolve `pypi.org` to fetch the required setuptools build backend. The packaging configuration explicitly includes only `insure_ai`, so `data/` is not declared as a package; a network-enabled install remains to be verified.

## Portfolio insight

The synthetic inventory contains 10 use cases across five domains. Evaluation sets exist for 7/10; owner roles are present for 8/10; 7/10 meet the prototype's required inventory fields (70% adoption); 9/10 list at least one reusable platform service. The deterministic recommendations identify missing evaluation coverage and owner roles and surface the most reused service. These are seeded portfolio facts, not observations about a real organisation.

## Known limitations and misses

- Labels and examples were authored for this prototype; there is no independent annotation or inter-rater analysis.
- The sets are too small and synthetic to support claims about production accuracy, performance by segment, or generalisation.
- No generative model is integrated, so hallucination, semantic citation support, model latency, prompt-injection resistance, and model cost are not measured.
- No real identity, document repository, access-control service, model gateway, telemetry platform, or operational support process is connected.
- Per-run decision inputs, outcomes, reason codes and citations are not persisted in an append-only audit record; RAI-11 remains described only.
- The evaluations do not establish regulatory compliance or production readiness.

The next evidence step is to expand and independently review representative test sets, then define production-specific security, privacy, operating, cost, and evaluation gates with accountable owners.
