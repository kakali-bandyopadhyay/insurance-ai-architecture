from __future__ import annotations

from .dataio import DATA, load_json
from .intake import intake_evaluation, process_submissions
from .wording import all_clauses, qa_evaluation


def _criterion_status(name: str, passed: bool, evidence: str) -> str:
    evidence_lower = evidence.lower()
    if any(marker in evidence_lower for marker in ("not implemented", "described only")):
        return "CONDITION"
    if name == "Data readiness" and not passed:
        return "CONDITION"
    if name == "Cost and TCO" and "not modelled" in evidence_lower:
        return "CONDITION"
    if passed:
        return "PASS"
    if name == "Evaluation evidence":
        return "CONDITION"
    return "RETURN"


def review_results():
    cfg = load_json(DATA / "design_authority" / "review_config.json")
    intake_metrics = intake_evaluation()
    wording_metrics = qa_evaluation()
    intake_rows = process_submissions()

    intake_minimum = cfg["submission_intake"]["minimum_labelled_examples"]
    wording_minimum = cfg["wording_qa"]["minimum_labelled_questions"]
    checksets = {
        "submission_intake": [
            ("Business value", True, "Supports underwriting intake extraction and human routing."),
            (
                "Data readiness",
                intake_metrics["labelled_submissions"] >= intake_minimum,
                f"Synthetic author-labelled set has {intake_metrics['labelled_submissions']} submissions; illustrative minimum is {intake_minimum}.",
            ),
            (
                "Architecture fit",
                True,
                "Deterministic parsing and validation are implemented; production integrations are described only.",
            ),
            (
                "Security and privacy",
                True,
                "Synthetic-only inputs; production PII controls are not implemented.",
            ),
            (
                "Responsible AI",
                all(row["status"] == "HUMAN_REVIEW_REQUIRED" for row in intake_rows if row["reason_codes"]),
                "Validation failures route to human review; no automatic acceptance path exists.",
            ),
            (
                "Evaluation evidence",
                intake_metrics["labelled_submissions"] >= intake_minimum
                and intake_metrics["field_level_accuracy"] >= cfg["submission_intake"]["minimum_field_accuracy"],
                f"Observed {intake_metrics['labelled_submissions']} labels and {intake_metrics['field_level_accuracy']:.0%} field accuracy; illustrative thresholds are {intake_minimum} labels and {cfg['submission_intake']['minimum_field_accuracy']:.0%} accuracy.",
            ),
            (
                "Operability",
                True,
                "CLI reason codes are available; production monitoring is described only.",
            ),
            (
                "Cost and TCO",
                True,
                "No model or external API call in default flow; full operating TCO is not modelled.",
            ),
        ],
        "wording_qa": [
            ("Business value", True, "Supports clause-grounded wording lookup with explicit declines."),
            (
                "Data readiness",
                wording_metrics["labelled_questions"] >= wording_minimum,
                f"Synthetic question set has {wording_metrics['labelled_questions']} labels; illustrative minimum is {wording_minimum}.",
            ),
            (
                "Architecture fit",
                True,
                "Keyword retrieval and citation checks are implemented; production model gateway is described only.",
            ),
            (
                "Security and privacy",
                True,
                "Synthetic-only pack; production access controls and PII handling are not implemented.",
            ),
            (
                "Responsible AI",
                wording_metrics["refusal_correctness"] >= cfg["wording_qa"]["minimum_refusal_correctness"],
                "Insufficient-evidence and wrong-contract cases are measured separately.",
            ),
            (
                "Evaluation evidence",
                wording_metrics["labelled_questions"] >= wording_minimum
                and wording_metrics["citation_validity"] >= cfg["wording_qa"]["minimum_citation_validity"]
                and wording_metrics["outcome_accuracy"] >= cfg["wording_qa"]["minimum_outcome_accuracy"],
                f"Observed {wording_metrics['labelled_questions']} questions; outcome accuracy {wording_metrics['outcome_accuracy']:.0%}; citation validity {wording_metrics['citation_validity']:.0%}.",
            ),
            (
                "Operability",
                True,
                "Reproducible local CLI; production telemetry and monitoring are described only.",
            ),
            (
                "Cost and TCO",
                True,
                "Default flow has zero external model calls; operating TCO is not modelled.",
            ),
        ],
    }

    results = []
    for use_case, checks in checksets.items():
        criteria = []
        conditions = []
        returns = []
        for name, passed, evidence in checks:
            status = _criterion_status(name, passed, evidence)
            criteria.append({"criterion": name, "status": status, "evidence": evidence})
            summary = f"{name}: {evidence}"
            if status == "CONDITION":
                conditions.append(summary)
            elif status == "RETURN":
                returns.append(summary)

        if returns:
            outcome = "RETURNED"
        elif conditions:
            outcome = "APPROVED WITH CONDITIONS"
        else:
            outcome = "APPROVED"
        results.append(
            {
                "use_case": use_case,
                "gate_stage": "pre-production readiness simulation",
                "outcome": outcome,
                "criteria": criteria,
                "conditions": conditions,
                "return_reasons": returns,
            }
        )
    return results
