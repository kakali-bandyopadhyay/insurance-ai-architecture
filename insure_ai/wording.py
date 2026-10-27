from __future__ import annotations
import re
from .dataio import load_json, DATA

STOP={"what","is","the","for","in","of","a","an","to","and","does","this","that","under","on","from","between","compare","tell","me","about","please","are","do","we","have","which","version","how","many","allow","apply","should","be","when","across","differs","match","same"}
TOKEN_RE=re.compile(r"[a-z0-9]+",re.I)
CONTRACT_RE=re.compile(r"\b(TREATY-[A-Z0-9-]+)\b",re.I)
VERSION_RE=re.compile(r"\bV(\d+)\b",re.I)

def _wordings():
    pack=[]
    for path in sorted((DATA/"wordings").glob("wording_*.json")): pack.extend(load_json(path)["documents"])
    return pack

def all_clauses(): return [{**c,"contract_id":d["contract_id"],"version":d["version"],"document_id":d["document_id"]} for d in _wordings() for c in d["clauses"]]

def _tokens(text):
    words={t.lower() for t in TOKEN_RE.findall(text) if t.lower() not in STOP}
    return words | {w[:-1] for w in words if len(w)>4 and w.endswith("s")}

def retrieve_clauses(question,contract_id=None,version=None,limit=6):
    clauses=all_clauses()
    if contract_id: clauses=[c for c in clauses if c["contract_id"].lower()==contract_id.lower()]
    if version:
        v=version.upper().removeprefix("V"); clauses=[c for c in clauses if c["version"].upper().removeprefix("V")==v]
    cleaned=CONTRACT_RE.sub(" ",question); cleaned=VERSION_RE.sub(" ",cleaned)
    query=_tokens(cleaned); scored=[]
    for c in clauses:
        body=_tokens(c["kind"].replace("_"," ")+" "+c["text"])
        score=len(query & body)
        if score: scored.append((score,c))
    if not scored: return []
    best=max(score for score,_ in scored)
    return sorted([c for score,c in scored if score==best],key=lambda c:(c["contract_id"],c["kind"],c["version"],c["clause_id"]))[:limit]

def validate_citations(citations,allowed_clauses=None):
    allowed={c["clause_id"] for c in (allowed_clauses if allowed_clauses is not None else all_clauses())}
    return bool(citations) and all(c in allowed for c in citations)

def ask(question,contract_id=None,version=None):
    explicit=CONTRACT_RE.search(question)
    if contract_id is None and explicit: contract_id=explicit.group(1).upper()
    known={c["contract_id"] for c in all_clauses()}
    if contract_id and contract_id not in known:
        return {"outcome":"WRONG_CONTRACT","answer":"Declined: requested contract is not in the synthetic wording pack.","citations":[],"citation_valid":True}
    if version is None:
        vm=VERSION_RE.search(question)
        if vm and "compare" not in _tokens(question): version="V"+vm.group(1)
    hits=retrieve_clauses(question,contract_id,version)
    if not hits: return {"outcome":"INSUFFICIENT_EVIDENCE","answer":"Declined: retrieved wording does not support an answer.","citations":[],"citation_valid":True}
    query_terms=_tokens(CONTRACT_RE.sub(" ",VERSION_RE.sub(" ",question)))
    best_score=max(len(query_terms & _tokens(c["kind"].replace("_"," ")+" "+c["text"])) for c in hits)
    if best_score < (2 if len(query_terms) >= 3 else 1): return {"outcome":"INSUFFICIENT_EVIDENCE","answer":"Declined: retrieved wording does not support an answer.","citations":[],"citation_valid":True}
    by_kind={}
    for c in hits: by_kind.setdefault((c["contract_id"],c["kind"]),[]).append(c)
    conflicts=[]
    for group in by_kind.values():
        if len({c["version"] for c in group})>1 and len({c["text"].strip().lower() for c in group})>1: conflicts.extend(group)
    if conflicts:
        cited=sorted({c["clause_id"] for c in conflicts})
        text=" ".join(c["clause_id"]+": "+c["text"] for c in sorted(conflicts,key=lambda x:x["version"]))
        return {"outcome":"CONFLICT","answer":"Conflict detected across wording versions; confirm the operative version with an accountable reviewer. "+text,"citations":cited,"citation_valid":validate_citations(cited,hits)}
    top=hits[0]; cited=[top["clause_id"]]
    return {"outcome":"ANSWERED","answer":top["text"],"citations":cited,"citation_valid":validate_citations(cited,hits)}

def qa_evaluation():
    items=load_json(DATA/"wordings"/"evaluation_questions.json")["questions"]
    correct=cit_n=cit_valid=ref_n=ref_correct=sup_n=sup_correct=0; results=[]; all_ids={c["clause_id"] for c in all_clauses()}
    for item in items:
        answer=ask(item["question"],item.get("contract_id"),item.get("version")); expected=item["expected_outcome"]; ok=answer["outcome"]==expected
        correct+=int(ok)
        if answer["outcome"] in ("ANSWERED","CONFLICT"):
            cit_n+=len(answer["citations"]); cit_valid+=sum(c in all_ids for c in answer["citations"])
        if expected in ("INSUFFICIENT_EVIDENCE","WRONG_CONTRACT"):
            ref_n+=1; ref_correct+=int(ok and not answer["citations"])
        if expected=="ANSWERED": sup_n+=1; sup_correct+=int(ok and bool(answer["citations"]))
        results.append({"question_id":item["question_id"],"expected_outcome":expected,"actual_outcome":answer["outcome"],"outcome_correct":ok,"citations":answer["citations"],"citation_valid":answer["citation_valid"]})
    n=len(items)
    return {"labelled_questions":n,"outcomes_correct":correct,"outcome_accuracy":round(correct/n,4) if n else 0.0,"citation_ids_valid":cit_valid,"citation_ids_total":cit_n,"citation_validity":round(cit_valid/cit_n,4) if cit_n else 1.0,"refusal_correct":ref_correct,"refusal_total":ref_n,"refusal_correctness":round(ref_correct/ref_n,4) if ref_n else 1.0,"supported_answers_correct":sup_correct,"supported_answers_total":sup_n,"results":results}
