from __future__ import annotations
import re
from datetime import date
from .dataio import load_json, DATA

FIELDS = ("insured", "line_of_business", "territory", "total_insured_value", "limit", "attachment", "deductible", "loss_runs", "inception_date")
ALIASES = {"insured":"insured", "line of business":"line_of_business", "line_of_business":"line_of_business", "territory":"territory", "total insured value":"total_insured_value", "total_insured_value":"total_insured_value", "limit":"limit", "attachment":"attachment", "deductible":"deductible", "inception date":"inception_date", "inception_date":"inception_date"}
LOSS_RE = re.compile(r"^\s*(20\d{2})\s*:\s*\$?([0-9,]+)\s*$", re.M)
LABEL_RE = re.compile(r"^\s*([^:]+):\s*(.*?)\s*$", re.M)
EXPECTED_LOSS_YEARS = list(range(2021, 2026))

def _amount(value: str):
    try: return int(value.replace(",", "").replace("$", "").strip())
    except (ValueError, AttributeError): return None

def extract_fields(submission: dict) -> dict:
    fields = {name: None for name in FIELDS}
    text = "\n".join(doc.get("text", "") for doc in submission.get("documents", []))
    for key, value in LABEL_RE.findall(text):
        canonical = ALIASES.get(key.strip().lower())
        if not canonical or not value.strip(): continue
        fields[canonical] = _amount(value) if canonical in ("total_insured_value", "limit", "attachment", "deductible") else value.strip()
    runs = [{"year":int(y), "amount":int(a.replace(",", ""))} for y,a in LOSS_RE.findall(text)]
    if runs: fields["loss_runs"] = sorted(runs, key=lambda row: row["year"])
    return fields

def validate_submission(fields: dict) -> list[str]:
    reasons=[]
    for name in FIELDS:
        value=fields.get(name)
        if value is None or value == "": reasons.append("REQUIRED_FIELD_MISSING:"+name.upper())
    for name in ("total_insured_value","limit","attachment","deductible"):
        value=fields.get(name)
        if value is not None and (not isinstance(value,int) or value < 0): reasons.append("NUMERIC_RANGE_INVALID:"+name.upper())
    tiv,limit=fields.get("total_insured_value"),fields.get("limit")
    if isinstance(tiv,int) and isinstance(limit,int) and tiv < limit: reasons.append("TIV_BELOW_LIMIT")
    inception=fields.get("inception_date")
    if inception:
        try: date.fromisoformat(inception)
        except (TypeError,ValueError): reasons.append("INCEPTION_DATE_INVALID")
    runs=fields.get("loss_runs") or []
    years=[row.get("year") for row in runs if isinstance(row,dict)]
    if years != EXPECTED_LOSS_YEARS: reasons.append("LOSS_RUN_YEARS_INCOMPLETE")
    if len(years) != len(set(years)): reasons.append("LOSS_RUN_YEAR_DUPLICATE")
    return sorted(set(reasons))

def process_submissions() -> list[dict]:
    rows=load_json(DATA/"submissions"/"submissions.json")["submissions"]; out=[]
    for row in rows:
        fields=extract_fields(row); reasons=validate_submission(fields)
        out.append({"submission_id":row["submission_id"],"status":"HUMAN_REVIEW_REQUIRED" if reasons else "READY_FOR_UNDERWRITER_REVIEW","fields":fields,"reason_codes":reasons})
    return out

def intake_evaluation() -> dict:
    rows=load_json(DATA/"submissions"/"submissions.json")["submissions"]; matched=total=0
    field_correct={field:0 for field in FIELDS}
    for row in rows:
        actual=extract_fields(row); expected=row["expected"]
        for field in FIELDS:
            correct=int(actual.get(field)==expected.get(field))
            total+=1; matched+=correct; field_correct[field]+=correct
    processed=process_submissions(); review=sum(r["status"]=="HUMAN_REVIEW_REQUIRED" for r in processed)
    return {"labelled_submissions":len(rows),"fields_correct":matched,"field_values_total":total,"field_level_accuracy":round(matched/total,4) if total else 0.0,"field_accuracy_by_field":{field:{"correct":field_correct[field],"total":len(rows),"accuracy":round(field_correct[field]/len(rows),4) if rows else 0.0} for field in FIELDS},"human_review_count":review,"failed_validation_count":review,"failed_items_routed_to_human_review":all(r["status"]=="HUMAN_REVIEW_REQUIRED" for r in processed if r["reason_codes"]),"auto_accept_count":0}

