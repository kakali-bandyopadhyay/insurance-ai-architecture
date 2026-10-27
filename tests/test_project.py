from __future__ import annotations
import importlib, json, re, subprocess, sys
from pathlib import Path
import pytest
from insure_ai.dataio import ROOT, DATA, load_json
from insure_ai.intake import FIELDS, extract_fields, intake_evaluation, process_submissions
from insure_ai.wording import all_clauses, ask, qa_evaluation, validate_citations
from insure_ai.review import review_results
from insure_ai.inventory import inventory_records, portfolio_insight
from insure_ai.dashboard import render_dashboard, write_dashboard

SUBS=load_json(DATA/"submissions"/"submissions.json")["submissions"]
QUESTIONS=load_json(DATA/"wordings"/"evaluation_questions.json")["questions"]

def test_fixed_schema_has_expected_fields():
    assert len(FIELDS)==9 and set(FIELDS)==set(SUBS[0]["expected"])

@pytest.mark.parametrize("row",SUBS,ids=lambda r:r["submission_id"])
def test_extraction_matches_prelabelled_expected_fields(row):
    assert extract_fields(row)==row["expected"]

@pytest.mark.parametrize("result",process_submissions(),ids=lambda r:r["submission_id"])
def test_invalid_submission_never_auto_accepted(result):
    if result["reason_codes"]:
        assert result["status"]=="HUMAN_REVIEW_REQUIRED"
    else:
        assert result["status"]=="READY_FOR_UNDERWRITER_REVIEW"
    assert result["status"]!="ACCEPTED"

@pytest.mark.parametrize("sid,reason",[("SUB-006","LOSS_RUN_YEARS_INCOMPLETE"),("SUB-007","TIV_BELOW_LIMIT"),("SUB-008","INCEPTION_DATE_INVALID"),("SUB-008","REQUIRED_FIELD_MISSING:INSURED")])
def test_known_validation_reason_codes(sid,reason):
    row=next(r for r in process_submissions() if r["submission_id"]==sid)
    assert reason in row["reason_codes"]

def test_intake_evaluation_reports_field_denominator_and_human_queue():
    m=intake_evaluation()
    assert m["field_values_total"]==len(SUBS)*len(FIELDS)
    assert m["failed_items_routed_to_human_review"] and m["auto_accept_count"]==0

def test_valid_submission_is_only_ready_for_human_underwriter_review():
    assert all(r["status"]=="READY_FOR_UNDERWRITER_REVIEW" for r in process_submissions()[:5])

@pytest.mark.parametrize("item",QUESTIONS,ids=lambda q:q["question_id"])
def test_wording_evaluation_outcome_matches_author_label(item):
    got=ask(item["question"],item.get("contract_id"),item.get("version"))
    assert got["outcome"]==item["expected_outcome"]

@pytest.mark.parametrize("item",[q for q in QUESTIONS if q["expected_outcome"]=="ANSWERED"],ids=lambda q:q["question_id"])
def test_supported_answer_cites_valid_clause(item):
    got=ask(item["question"],item.get("contract_id"),item.get("version"))
    assert got["citations"] and got["citation_valid"]
    assert validate_citations(got["citations"],all_clauses())

def test_citation_validator_rejects_unknown_clause():
    assert not validate_citations(["FAKE-CLAUSE"],all_clauses())

def test_citation_validator_rejects_empty_citation_set():
    assert not validate_citations([],all_clauses())

def test_version_conflict_surfaces_both_versions():
    got=ask("Compare hours clauses across TREATY-ALPHA versions.","TREATY-ALPHA")
    assert got["outcome"]=="CONFLICT"
    assert set(got["citations"])=={"ALPHA-V1-HOURS-01","ALPHA-V2-HOURS-01"}

def test_wrong_contract_declines_without_citation():
    got=ask("What is covered?","TREATY-UNKNOWN")
    assert got["outcome"]=="WRONG_CONTRACT" and got["citations"]==[]

def test_missing_evidence_declines_without_citation():
    got=ask("What is the arbitration seat?","TREATY-DELTA","V1")
    assert got["outcome"]=="INSUFFICIENT_EVIDENCE" and not got["citations"]

def test_qa_metrics_keep_outcome_citation_and_refusal_denominators_separate():
    m=qa_evaluation()
    assert m["labelled_questions"]==20 and m["citation_ids_total"]>0
    assert m["refusal_total"]==7 and m["supported_answers_total"]==10
    assert m["citation_validity"]==1.0

def test_review_is_deterministic():
    assert review_results()==review_results()

def test_intake_review_has_condition_for_small_label_set():
    item=next(r for r in review_results() if r["use_case"]=="submission_intake")
    assert item["outcome"]=="APPROVED WITH CONDITIONS"
    assert any("Data readiness" in c and "8 submissions" in c and "minimum is 20" in c for c in item["conditions"])
    assert any("Evaluation evidence" in c and "8 labels" in c for c in item["conditions"])

def test_wording_review_conditions_unimplemented_production_controls():
    item=next(r for r in review_results() if r["use_case"]=="wording_qa")
    assert item["outcome"]=="APPROVED WITH CONDITIONS"
    by_name={criterion["criterion"]:criterion for criterion in item["criteria"]}
    assert by_name["Data readiness"]["status"]=="PASS"
    assert by_name["Evaluation evidence"]["status"]=="PASS"
    for name in ("Architecture fit","Security and privacy","Operability","Cost and TCO"):
        assert by_name[name]["status"]=="CONDITION"
    assert len(item["conditions"])==4

def test_review_never_passes_evidence_that_discloses_missing_production_control():
    for result in review_results():
        for criterion in result["criteria"]:
            evidence=criterion["evidence"].lower()
            if "not implemented" in evidence or "described only" in evidence:
                assert criterion["status"]=="CONDITION"

def test_review_covers_all_design_authority_criteria():
    expected={"Business value","Data readiness","Architecture fit","Security and privacy","Responsible AI","Evaluation evidence","Operability","Cost and TCO"}
    assert all({c["criterion"] for c in r["criteria"]}==expected for r in review_results())

@pytest.mark.parametrize("adr",["0001-model-selection.md","0002-document-extraction-build-buy.md","0003-rag-vs-fine-tuning.md"])
def test_adrs_exist_and_score_all_required_dimensions(adr):
    text=(ROOT/"docs"/"adr"/adr).read_text(encoding="utf-8-sig").lower()
    for term in ("value","risk","scalability","latency","resilience","reuse","tco"):
        assert term in text

def test_controls_marked_implemented_resolve_to_callable_functions():
    for control in load_json(DATA/"controls"/"rai_controls.json")["controls"]:
        if control["status"]=="implemented":
            module_name,function_name=control["implementation_reference"].rsplit(".",1)
            assert callable(getattr(importlib.import_module(module_name),function_name))

def test_every_control_has_a_synthetic_owner_role():
    controls=load_json(DATA/"controls"/"rai_controls.json")["controls"]
    assert all(control.get("owner_role","").strip().endswith("(synthetic)") for control in controls)

def test_auditability_control_is_described_only_without_a_per_run_writer():
    control=next(c for c in load_json(DATA/"controls"/"rai_controls.json")["controls"] if c["control_id"]=="RAI-11")
    assert control["status"]=="described_only"
    assert control["implementation_reference"]=="described only"
    assert all(term in control["control"].lower() for term in ("append-only","inputs","outcome","reason codes","citations","per run"))

def test_wording_risk_names_hallucination_explicitly():
    controls=load_json(DATA/"controls"/"rai_controls.json")["controls"]
    risks={c["control_id"]:c["risk"].lower() for c in controls}
    assert "hallucination" in risks["RAI-01"]
    assert "hallucination" in risks["RAI-02"]

def test_control_matrix_renders_every_control():
    text=(ROOT/"docs"/"CONTROL_MATRIX.md").read_text(encoding="utf-8-sig")
    assert all(c["control_id"] in text for c in load_json(DATA/"controls"/"rai_controls.json")["controls"])
    assert all(c["owner_role"] in text for c in load_json(DATA/"controls"/"rai_controls.json")["controls"])

def test_inventory_metrics_have_explicit_denominators():
    m=portfolio_insight()
    assert m["standards_adoption_denominator"]==m["use_case_count"]==10
    assert m["reuse_denominator"]==10
    assert m["missing_evaluation_count"]==3 and m["missing_owner_count"]==2

@pytest.mark.parametrize("row",inventory_records(),ids=lambda r:r["use_case_id"])
def test_inventory_rows_have_required_dimensions(row):
    assert all(k in row for k in ("domain","status","risk_tier","pattern","platform_services_reused","owner_role","evaluation_set"))
    assert "Synthetic" in row["data_notice"]

def test_portfolio_recommendations_are_deterministic_and_counted():
    a=portfolio_insight()
    assert a==portfolio_insight() and len(a["recommendations"])>=2
    assert all(str(n) in " ".join(a["recommendations"]) for n in (a["missing_evaluation_count"],a["missing_owner_count"]))

def test_dashboard_file_matches_fresh_render():
    expected=render_dashboard(); write_dashboard()
    assert (ROOT/"docs"/"index.html").read_text(encoding="utf-8")==expected

def test_dashboard_has_required_sections_and_synthetic_notice():
    html=render_dashboard()
    for phrase in ("Evaluation overview","Submission intake outcomes","Design-authority review","Responsible AI control matrix","Owner role","Portfolio insight","[SYNTHETIC]"):
        assert phrase in html
    assert all(c["owner_role"] in html for c in load_json(DATA/"controls"/"rai_controls.json")["controls"])

def _scan_paths():
    paths=[ROOT/"README.md",ROOT/"pyproject.toml",ROOT/"requirements-dev.txt",ROOT/".gitignore"]
    for folder in (ROOT/"insure_ai",ROOT/"tests",ROOT/"docs",ROOT/"data"):
        paths.extend(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in {".py",".md",".json",".html",".toml",".txt"})
    return paths

def _blocked_terms():
    return [
        "Swiss"+" Re","Munich"+" Re","Hannover"+" Re","S"+"COR","Llo"+"yd's",
        "A"+"XA","Alli"+"anz","A"+"on","Mar"+"sh","Will"+"is","Guy"+" Carpenter",
        "Delo"+"itte","P"+"wC","Black"+"Rock","JP"+"Morgan","Gold"+"man Sachs",
        "C"+"iti","H"+"SBC","Bar"+"clays","S"+"WIFT","S"+"WIFT gpi","S"+"WIFT Go",
        "S"+"WIFTNet","Alliance"+" Access","Alliance"+" Lite2","Alliance"+" Messaging Hub",
        "Alliance"+" Connect","Alliance"+" Gateway","Informa"+"tica","Colli"+"bra",
    ]

@pytest.mark.parametrize("term",_blocked_terms(),ids=lambda _:"blocked-term")
def test_blocklist_scanner_detects_each_firm_and_product_name(term):
    pattern=r"\b"+re.escape(term)+r"\b"
    assert re.search(pattern,"Synthetic text mentions "+term+" as an example.",re.I)
    assert not re.search(pattern,"x"+term+"y",re.I)

def test_repo_source_templates_docs_and_data_remain_firm_neutral():
    bad=[]
    for path in _scan_paths():
        text=path.read_text(encoding="utf-8-sig",errors="replace")
        for term in _blocked_terms():
            if re.search(r"\b"+re.escape(term)+r"\b",text,re.I): bad.append((str(path.relative_to(ROOT)),term))
    assert bad==[]

def test_restricted_career_word_is_absent_from_repo():
    restricted="inter"+"view"
    files=[p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and all(x not in p.parts for x in ("__pycache__",".pytest_cache",".venv","venv","site-packages","out"))]
    assert all(restricted not in p.read_text(encoding="utf-8-sig",errors="ignore").lower() for p in files)

def test_reference_architecture_marks_implementation_boundary_and_has_mermaid():
    text=(ROOT/"docs"/"REFERENCE_ARCHITECTURE.md").read_text(encoding="utf-8-sig")
    assert text.count("```mermaid")==3 and "described only" in text.lower() and "implemented" in text.lower()

@pytest.mark.parametrize("args",[["intake"],["intake-eval"],["ask","What is the hours clause for TREATY-ALPHA V1?"],["qa-eval"],["review"],["inventory"],["dashboard"]])
def test_cli_commands_run_and_label_output(args):
    result=subprocess.run([sys.executable,"-m","insure_ai",*args],cwd=ROOT,text=True,capture_output=True,check=True)
    assert "[SYNTHETIC]" in result.stdout
