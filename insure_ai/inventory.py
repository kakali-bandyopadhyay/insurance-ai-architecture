from __future__ import annotations
from collections import Counter
from .dataio import load_json, DATA

def inventory_records(): return load_json(DATA/"inventory"/"ai_inventory.json")["use_cases"]

def portfolio_insight():
    rows=inventory_records(); total=len(rows)
    no_eval=[r["use_case_id"] for r in rows if not r["evaluation_set"]]
    no_owner=[r["use_case_id"] for r in rows if not r["owner_role"]]
    complete=[r for r in rows if r["evaluation_set"] and r["owner_role"] and r["risk_tier"] and r["status"]]
    patterns=Counter(r["pattern"] for r in rows); services=Counter(s for r in rows for s in r["platform_services_reused"])
    reused=sum(bool(r["platform_services_reused"]) for r in rows); rec=[]
    if no_eval: rec.append(f"Create evaluation sets for {len(no_eval)} of {total} use cases missing them.")
    if no_owner: rec.append(f"Assign accountable owner roles to {len(no_owner)} of {total} use cases missing them.")
    if services: rec.append(f"Review the most reused service, {services.most_common(1)[0][0]}, in {services.most_common(1)[0][1]} of {total} synthetic use cases.")
    return {"use_case_count":total,"use_cases_with_evaluation":total-len(no_eval),"missing_evaluation_count":len(no_eval),"missing_evaluation_ids":no_eval,"use_cases_with_owner":total-len(no_owner),"missing_owner_count":len(no_owner),"missing_owner_ids":no_owner,"standards_adoption_numerator":len(complete),"standards_adoption_denominator":total,"standards_adoption_percent":round(100*len(complete)/total,1) if total else 0.0,"reuse_numerator":reused,"reuse_denominator":total,"pattern_counts":dict(sorted(patterns.items())),"platform_service_counts":dict(sorted(services.items())),"recommendations":rec}
