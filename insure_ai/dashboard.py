from __future__ import annotations
import json
from html import escape
from .dataio import DATA, ROOT, load_json, synthetic_banner, write_text
from .intake import intake_evaluation, process_submissions
from .inventory import portfolio_insight
from .review import review_results
from .wording import qa_evaluation

OUTCOMES=(("ANSWERED","Supported","supported"),("INSUFFICIENT_EVIDENCE","Insufficient evidence","insufficient"),("WRONG_CONTRACT","Wrong contract","wrong-contract"),("CONFLICT","Conflict","conflict"))
COLORS={"supported":"#187b68","insufficient":"#c27a18","wrong-contract":"#bb4b58","conflict":"#5868b5"}

def dashboard_data():
    intake=intake_evaluation(); qa=qa_evaluation(); reviews=review_results(); insight=portfolio_insight()
    controls=load_json(DATA/"controls"/"rai_controls.json")["controls"]
    submissions=process_submissions()
    source_questions=load_json(DATA/"wordings"/"evaluation_questions.json")["questions"]
    results={row["question_id"]:row for row in qa["results"]}
    labels={outcome:(label,key) for outcome,label,key in OUTCOMES}
    types=[{"key":key,"label":label,"expected":sum(q["expected_outcome"]==outcome for q in source_questions),
            "actual":sum(results[q["question_id"]]["actual_outcome"]==outcome for q in source_questions)}
           for outcome,label,key in OUTCOMES]
    questions=[]
    for q in source_questions:
        result=results[q["question_id"]]; label,key=labels[q["expected_outcome"]]
        questions.append({"question_id":q["question_id"],"question":q["question"],"type":label,"filter":key,
                          "expected":q["expected_outcome"],"actual":result["actual_outcome"],"citations":result["citations"]})
    raw=[
      ("Intake field accuracy",intake["fields_correct"],intake["field_values_total"],"labelled field values matched"),
      ("Packs routed to review",intake["human_review_count"],intake["labelled_submissions"],"submission packs were routed to human review"),
      ("Auto-accepted",intake["auto_accept_count"],None,"submission packs were auto-accepted"),
      ("QA outcome accuracy",qa["outcomes_correct"],qa["labelled_questions"],"labelled questions were classified correctly"),
      ("Citation validity",qa["citation_ids_valid"],qa["citation_ids_total"],"cited clause IDs were valid"),
      ("Refusal correctness",qa["refusal_correct"],qa["refusal_total"],"refusal cases were correct"),
      ("Inventory size",insight["use_case_count"],insight["use_case_count"],"AI inventory use cases"),
      ("Standards adoption",insight["standards_adoption_numerator"],insight["standards_adoption_denominator"],"use cases met required inventory fields")]
    kpis=[{"label":n,"numerator":a,"denominator":b,"value":(f"{a} of {b}" if b is not None else str(a)),"scope":s} for n,a,b,s in raw]
    return {"kpis":kpis,
      "intake":{"fields":[{"field":n,**v} for n,v in intake["field_accuracy_by_field"].items()],
        "review_queue":[{"submission_id":r["submission_id"],"reason_codes":r["reason_codes"]} for r in submissions if r["status"]=="HUMAN_REVIEW_REQUIRED"]},
      "wording":{"total":qa["labelled_questions"],"types":types,"questions":questions},
      "reviews":reviews,"controls":controls,"portfolio":insight}

def _json(data):
    slash=chr(92)
    return json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("&",slash+"u0026").replace("<",slash+"u003c").replace(">",slash+"u003e")

def _kpis(items):
    out=[]
    for i,k in enumerate(items,1):
        count_text=f'{k["value"]} {k["scope"]}.'
        out.append(f'<article class="kpi"><strong>{escape(k["value"])}</strong>'
          f'<b>{escape(k["label"])}</b><small>{escape(count_text)}</small></article>')
    return "".join(out)

def _field_svg(fields):
    rows=[]; x=155; width=220; height=55+38*len(fields)
    for i,f in enumerate(fields):
        y=35+38*i; value=f'{f["correct"]}/{f["total"]}'; name=escape(f["field"].replace("_"," ").title())
        rows.append(f'<g><title>{escape(f["field"])}: {value}</title><text class="lbl" x="8" y="{y+5}">{name}</text>'
          f'<rect class="track" x="{x}" y="{y-13}" width="{width}" height="22" rx="5"/><rect x="{x}" y="{y-13}" width="{width*f["accuracy"]:.1f}" height="22" rx="5" fill="#187b68"/>'
          f'<text class="val" x="{x+width+10}" y="{y+5}">{value}</text></g>')
    return f'<svg class="chart" viewBox="0 0 540 {height}" role="img" aria-label="Field accuracy by field"><title>Field accuracy; bars show correct values over labelled values</title>{"".join(rows)}</svg>'

def _outcome_svg(wording):
    total=wording["total"]; left=135; unit=12.5; rows=[]
    for label,key,y in (("Expected","expected",48),("Actual","actual",105)):
        rows.append(f'<text class="lbl" x="8" y="{y+19}">{label}</text>'); x=left
        for item in wording["types"]:
            n=item[key]; w=n*unit; title=escape(f'{label} {item["label"]}: {n} of {total}')
            rows.append(f'<g><title>{title}</title><rect x="{x}" y="{y}" width="{w}" height="30" rx="3" fill="{COLORS[item["key"]]}"/>'
                        f'<text class="seg" x="{x+w/2}" y="{y+20}">{n}</text></g>'); x+=w
        rows.append(f'<text class="val" x="{left+total*unit+10}" y="{y+19}">{total}/{total}</text>')
    legend="".join(f'<li><i style="--swatch:{COLORS[t["key"]]}"></i>{escape(t["label"])}: expected {t["expected"]} of {total}, actual {t["actual"]} of {total}</li>' for t in wording["types"])
    return f'<svg class="chart outcome-chart" viewBox="0 0 {left+total*unit+75} 155" role="img" aria-label="Expected and actual outcome counts"><title>Stacked outcome counts; segment tooltips show each count and its total</title>{"".join(rows)}</svg><ul class="legend">{legend}</ul>'

def _heatmap(reviews):
    criteria=[c["criterion"] for c in reviews[0]["criteria"]]
    head="<thead><tr><th>Use case</th>"+"".join(f"<th>{escape(c)}</th>" for c in criteria)+"<th>Outcome</th></tr></thead>"
    rows=[]
    for r in reviews:
        cells=[]
        for c in r["criteria"]:
            cells.append(f'<td data-label="{escape(c["criterion"])}"><button type="button" class="heat status-{c["status"].lower()}" data-criterion="{escape(c["criterion"],quote=True)}" data-evidence="{escape(c["evidence"],quote=True)}">{escape(c["status"])}</button>'
              f'<span class="inline-evidence">Evidence: {escape(c["evidence"])}</span></td>')
        rows.append(f'<tr><th data-label="Use case">{escape(r["use_case"].replace("_"," ").title())}<small>{escape(r["outcome"])}</small></th>{"".join(cells)}<td data-label="Outcome"><b>{escape(r["outcome"])}</b></td></tr>')
    conditions="".join(f'<article class="condition"><h3>{escape(r["use_case"].replace("_"," ").title())}</h3><b>{escape(r["outcome"])}</b><ul>{"".join(f"<li>{escape(c)}</li>" for c in r["conditions"])}</ul></article>' for r in reviews)
    return '<table class="responsive heat"><caption>Criteria by use case; status is both textual and colored.</caption>'+head+"<tbody>"+"".join(rows)+"</tbody></table>"+'<div class="legend"><span class="pass">PASS</span><span class="condition-status">CONDITION</span><span class="return">RETURN</span></div><aside id="evidence"><b>Criterion evidence</b><p>Select a cell to view the review evidence.</p></aside><div class="twocol">'+conditions+"</div>"

def _control_rows(controls):
    rows=[]
    for c in controls:
        module=c["implementation_reference"].rsplit(".",1)[0].replace(".","/")+".py"
        link=f'<a href="../{escape(module,quote=True)}">View source</a>' if c["status"]=="implemented" else "Described only"
        rows.append(f'<tr data-status="{escape(c["status"])}"><td data-label="Control">{escape(c["control_id"])}</td><td data-label="Owner role">{escape(c["owner_role"])}</td>'
          f'<td data-label="Risk">{escape(c["risk"])}</td><td data-label="Control">{escape(c["control"])}</td>'
          f'<td data-label="Status"><span class="pill {c["status"].replace("_","-")}">{escape(c["status"].replace("_"," "))}</span></td>'
          f'<td data-label="Implementation">{link}</td><td data-label="Evidence">{escape(c["evidence_produced"])}</td></tr>')
    return "".join(rows)

def _bars(counts,denom,ident):
    rows=[]; left=180; width=250; maxval=max([v for v in counts.values()]+[1]); height=48+37*len(counts)
    for i,(name,n) in enumerate(counts.items()):
        y=30+37*i; title=escape(f"{name}: {n} of {denom} inventory use cases")
        rows.append(f'<g><title>{title}</title><text class="lbl" x="8" y="{y+5}">{escape(name.replace("_"," ").title())}</text>'
         f'<rect class="track" x="{left}" y="{y-13}" width="{width}" height="22" rx="5"/><rect x="{left}" y="{y-13}" width="{width*n/maxval:.1f}" height="22" rx="5" fill="#3c6c9f"/>'
         f'<text class="val" x="{left+width+10}" y="{y+5}">{n} of {denom}</text></g>')
    return f'<svg id="{ident}" class="chart" viewBox="0 0 550 {height}" role="img" aria-label="Inventory use-case counts"><title>Inventory use-case count out of {denom}</title>{"".join(rows)}</svg>'

def _layer():
    return """flowchart LR
  subgraph I[Implemented]
    IN[Intake and validation]
    HR[Human review queue]
    RET[Clause retrieval]
    GU[Citation and refusal checks]
    EV[Evaluation outputs]
    DA[Design-authority review]
    PI[Portfolio insight]
    DB[Dashboard]
  end
  subgraph D[Described only]
    OCR[OCR and classification]
    GW[Model gateway]
    PII[PII and injection controls]
    IAM[Production identity]
    OBS[Telemetry and monitoring]
    AUD[Append-only audit service]
  end
  IN --> HR
  RET --> GU --> EV
  IN --> EV --> DA --> PI --> DB
  OCR -. future .-> IN
  GW -. future .-> RET
  PII -. future .-> GU
  IAM -. future .-> HR
  OBS -. future .-> GW
  AUD -. future .-> DA
  classDef implemented fill:#dcefe8,stroke:#187b68,color:#133c35,stroke-width:2px
  classDef described fill:#fff0d6,stroke:#c27a18,color:#50320d,stroke-dasharray:5 4
  class IN,HR,RET,GU,EV,DA,PI,DB implemented
  class OCR,GW,PII,IAM,OBS,AUD described"""

def _gate():
    return """flowchart LR
  C[Concept] --> D[Design] --> P[Pre-production] --> L[Post-launch]
  classDef gate fill:#dcefe8,stroke:#187b68,color:#133c35,stroke-width:2px
  class C,D,P,L gate"""

def render_dashboard():
    data=dashboard_data(); insight=data["portfolio"]
    queue="".join(f'<article class="queue"><b>{escape(r["submission_id"])}</b><p>{escape(", ".join(r["reason_codes"]))}</p></article>' for r in data["intake"]["review_queue"])
    questions="".join(f'<tr data-type="{escape(q["filter"])}"><td data-label="ID">{escape(q["question_id"])}</td><td data-label="Question">{escape(q["question"])}</td><td data-label="Type">{escape(q["type"])}</td><td data-label="Expected">{escape(q["expected"])}</td><td data-label="Actual">{escape(q["actual"])}</td><td data-label="Citations">{escape(", ".join(q["citations"]) or "None")}</td></tr>' for q in data["wording"]["questions"])
    qbuttons=[]
    for key,label in (("all","All"),("supported","Supported"),("insufficient","Insufficient evidence"),("wrong-contract","Wrong contract"),("conflict","Conflict")):
        pressed="true" if key=="all" else "false"
        qbuttons.append(f'<button type="button" data-qfilter="{key}" aria-pressed="{pressed}">{label}</button>')
    qbuttons="".join(qbuttons)
    gaps='<div><h3>No evaluation set</h3><ul>'+"".join(f"<li>{escape(v)}</li>" for v in insight["missing_evaluation_ids"])+'</ul></div><div><h3>No owner role</h3><ul>'+"".join(f"<li>{escape(v)}</li>" for v in insight["missing_owner_ids"])+"</ul></div>"
    recs="".join(f"<li>{escape(v)}</li>" for v in insight["recommendations"])
    template=r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>Synthetic AI Architecture Dashboard</title><link rel="icon" href="/assets/favicon-32x32.png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><style>
:root{color-scheme:light;--bg:#f2f5f7;--card:#fff;--sub:#e9eff2;--ink:#172a36;--muted:#586b76;--line:#d5dfe3;--brand:#143b52;--accent:#08766e;--passbg:#dcefe8;--passink:#155c4b;--condbg:#fff0d6;--condink:#704500;--retbg:#f9dfe1;--retink:#862d36;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
@media(prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#10191e;--card:#17242b;--sub:#20323b;--ink:#e7eff2;--muted:#aec0c8;--line:#334852;--brand:#122d3d;--accent:#43c1ad;--passbg:#173d35;--passink:#8ad8bf;--condbg:#4a371c;--condink:#ffd282;--retbg:#4b252a;--retink:#ffacb3}}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:6rem;overflow-x:hidden;width:100%;max-width:100%}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;overflow-x:hidden;width:100%;max-width:100%}a{color:var(--accent)}button,input{font:inherit}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #2586b8;outline-offset:2px}
header{background:linear-gradient(115deg,#102f43,#17565c);color:#fff;padding:1.5rem max(1rem,calc((100vw - 1200px)/2))}.headrow{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between}.headrow>div{min-width:0;flex:1 1 30rem}h1{font-size:clamp(1.7rem,5vw,2.7rem);line-height:1.1;margin:.2rem 0}header p{color:#dbe9ec}.links{display:flex;gap:.4rem;flex-wrap:wrap;min-width:0;max-width:100%}.links a{color:white;text-decoration:none;border:1px solid #ffffff66;border-radius:999px;padding:.4rem .7rem;max-width:100%;white-space:normal;overflow-wrap:anywhere}
main{width:min(1200px,100%);margin:1rem auto 3rem;padding:0 .8rem}.banner{width:100%;max-width:100%;overflow-wrap:anywhere;background:var(--condbg);color:var(--condink);border:1px solid #b97817;border-left:6px solid #b97817;padding:.8rem 1rem;border-radius:11px;font-weight:700}
nav.sticky{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:.2rem;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.35rem;margin:.7rem 0}nav.sticky a{flex:1 1 auto;text-align:center;text-decoration:none;color:var(--ink);padding:.4rem;font-size:.82rem;font-weight:700}
section{background:var(--card);border:1px solid var(--line);border-radius:15px;padding:clamp(.8rem,2.4vw,1.3rem);margin:.8rem 0;scroll-margin-top:5rem;box-shadow:0 8px 24px #143b5210}.eyebrow,small,.scope{font-size:.75rem;color:var(--muted)}.eyebrow{color:var(--accent);text-transform:uppercase;font-weight:850;letter-spacing:.1em}h2{font-size:clamp(1.25rem,3vw,1.7rem);margin:.15rem 0}h3{font-size:1rem;margin:.2rem 0 .5rem}.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.6rem}.kpi{min-width:0;border:1px solid var(--line);border-radius:11px;padding:.7rem}.kpi strong{display:block;font-size:clamp(1.3rem,3vw,1.9rem);color:var(--accent);overflow-wrap:anywhere}.kpi b{display:block}.kpi small{display:block}.split,.twocol,.diagrams{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.7rem}.card{min-width:0;border:1px solid var(--line);border-radius:11px;padding:.7rem}.chart{display:block;width:100%;height:auto}.lbl{fill:var(--ink);font-size:15px;font-weight:650}.val{fill:var(--muted);font-size:13px;font-weight:700}.seg{fill:white;text-anchor:middle;font-size:14px;font-weight:850}.track{fill:var(--sub)}.legend{list-style:none;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.3rem}.legend li{font-size:.78rem;overflow-wrap:anywhere}.legend i{display:inline-block;width:.7rem;height:.7rem;background:var(--swatch);margin-right:.3rem}
.filters{display:flex;flex-wrap:wrap;gap:.3rem;margin:.6rem 0}.filters button,.control-filters button{border:1px solid var(--line);border-radius:999px;padding:.35rem .65rem;background:var(--card);color:var(--ink);cursor:pointer;font-size:.8rem}.filters button[aria-pressed=true],.control-filters button[aria-pressed=true]{background:var(--brand);color:white}.search{flex:1 1 170px;min-width:0;padding:.5rem;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink)}
table{width:100%;table-layout:fixed;border-collapse:collapse;font-size:.8rem}caption{text-align:left;color:var(--muted);padding:.4rem 0}th,td{text-align:left;vertical-align:top;padding:.52rem .4rem;border-bottom:1px solid var(--line);overflow-wrap:anywhere}thead th{background:var(--sub);font-size:.73rem}tbody tr:nth-child(even){background:color-mix(in srgb,var(--sub) 45%,var(--card))}.question th:nth-child(2){width:29%}.question th:nth-child(3){width:15%}.question th:nth-child(4),.question th:nth-child(5){width:14%}.control th:nth-child(2){width:14%}.control th:nth-child(3){width:14%}.control th:nth-child(4){width:20%}.control th:nth-child(6){width:10%}
.pass,.implemented{background:var(--passbg);color:var(--passink)}.condition-status,.described-only{background:var(--condbg);color:var(--condink)}.return{background:var(--retbg);color:var(--retink)}.heat{font-size:.7rem}.heat th:first-child{width:9rem}.heat th:last-child{width:11rem}.heat td{min-width:5rem}.heat button{padding:.25rem .4rem;border:1px solid currentColor;border-radius:7px;font-weight:800;cursor:pointer}.heat button.status-pass{background:var(--passbg);color:var(--passink)}.heat button.status-condition{background:var(--condbg);color:var(--condink)}.heat button.status-return{background:var(--retbg);color:var(--retink)}.inline-evidence{display:block;color:var(--muted);font-size:.7rem;margin-top:.3rem}.js-enabled .inline-evidence{display:none}.condition{border:1px solid var(--line);border-radius:10px;padding:.65rem;min-width:0}.condition li{margin:.25rem 0;overflow-wrap:anywhere}#evidence{background:var(--sub);border:1px solid var(--line);border-radius:9px;padding:.7rem;margin:.5rem 0}
.adoption{background:var(--brand);color:white;border-radius:12px;padding:.8rem;margin:.6rem 0}.adoption b{display:block;font-size:1.8rem}.gaps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.6rem;margin:.7rem 0}.gaps>div{border:1px solid var(--line);border-radius:10px;padding:.65rem}.diagram{border:1px solid var(--line);border-radius:10px;padding:.7rem;min-width:0;overflow:hidden}.diagram pre{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;background:var(--sub);padding:.6rem;border-radius:7px;font-size:.72rem;color:var(--ink)}.mermaid{max-width:100%;overflow:auto;text-align:center}.mermaid svg{max-width:100%;height:auto}.status-key{display:flex;flex-wrap:wrap;gap:.4rem}.status-key span,.pill{border-radius:7px;padding:.25rem .4rem;font-size:.72rem;font-weight:800}.noscript{border:1px dashed var(--line);padding:.6rem}footer{text-align:center;color:var(--muted);padding:1rem;font-size:.8rem}
@media(max-width:820px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.split{grid-template-columns:1fr}}
@media(max-width:560px){header{padding:1.1rem .8rem}main{padding:0 .5rem}.sticky a{flex:1 1 28%;font-size:.68rem;padding:.35rem .1rem}section{padding:.7rem;margin:.55rem 0;border-radius:11px}.kpis{gap:.35rem}.kpi{padding:.55rem}.kpi strong{font-size:1.2rem}.kpi small{font-size:.66rem}.twocol,.diagrams,.gaps,.legend{grid-template-columns:1fr}.card{padding:.45rem}.lbl{font-size:17px}.val{font-size:14px}table.responsive thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}table.responsive,table.responsive tbody,table.responsive tr,table.responsive td{display:block;width:100%}table.responsive tbody th{display:block;width:100%;text-align:left}table.responsive tbody th::before{content:attr(data-label);display:block;color:var(--muted);font-size:.72rem}table.responsive tr{border:1px solid var(--line);border-radius:9px;margin:.5rem 0;padding:.3rem .5rem;background:var(--card)}table.responsive td{display:grid;grid-template-columns:minmax(4.2rem,28%) minmax(0,1fr);gap:.4rem;padding:.4rem 0;border-bottom:1px dashed var(--line)}table.responsive td:last-child{border-bottom:0}.heat td{min-width:0}}
</style></head><body>
<header><div class="headrow"><div><span class="eyebrow" style="color:#9cddd0">Portfolio evidence • synthetic prototype</span><h1>Insurance AI architecture dashboard</h1><p>Deterministic evaluation, decision evidence, Responsible AI controls and synthetic inventory insight.</p></div><nav class="links" aria-label="Project links"><a href="../">Repository</a><a href="../README.md">README</a></nav></div></header><main>
<div class="banner">__BANNER__</div>
<nav class="sticky" aria-label="Dashboard sections"><a href="#problem">Problem</a><a href="#architecture">Architecture</a><a href="#authority">Design authority</a><a href="#controls">Controls</a><a href="#intake">Intake</a><a href="#wording">Wording QA</a><a href="#portfolio">Portfolio</a><a href="#evidence">Evidence</a></nav>
<section id="problem"><h2>Problem</h2><p>Before production, standards call for an accountable operating owner, human oversight, evaluation evidence, and lifecycle review. This prototype brings synthetic submission intake, wording review, model-risk controls, and accountability artefacts into one place. It demonstrates deterministic intake with reason codes and human-review routing, plus clause retrieval with citations and version-conflict detection. It is not a production underwriting or wording system and contains no real company data, production integrations, or regulatory guidance.</p></section>
<section id="architecture"><h2>Architecture</h2><p>Green nodes are implemented; amber dashed nodes are described only.</p><div class="status-key"><span class="pass">Implemented</span><span class="condition-status">Described only</span></div><div class="diagrams"><article class="diagram"><h3>Reference architecture layers</h3><pre class="mermaid-source" id="layer-source">__LAYER__</pre></article><article class="diagram"><h3>Design-authority gate flow</h3><pre class="mermaid-source" id="gate-source">__GATE__</pre></article></div></section>
<section id="authority"><h2>Design authority</h2><p>Pre-production status uses color and a text label. Click a cell for evidence.</p>__HEATMAP__</section>
<section id="controls"><h2>Controls</h2><p>Owner roles and status are illustrative; implemented rows link to source.</p><div class="control-filters filters"><button type="button" data-cfilter="all" aria-pressed="true">All</button><button type="button" data-cfilter="implemented" aria-pressed="false">Implemented</button><button type="button" data-cfilter="described_only" aria-pressed="false">Described only</button></div><table id="controls-table" class="responsive control"><caption>Controls, owners and evidence.</caption><thead><tr><th>Control</th><th>Owner role</th><th>Risk</th><th>Control statement</th><th>Status</th><th>Implementation</th><th>Evidence</th></tr></thead><tbody>__CONTROLS__</tbody></table></section>
<section id="intake"><h2>Intake</h2><p>Correct field values over labelled values; the review queue shows reason codes.</p><div class="split"><div class="card"><b>Field accuracy</b>__FIELDS__</div><div class="card"><b>Human review queue</b><div>__QUEUE__</div></div></div></section>
<section id="wording"><h2>Wording QA</h2><p>Expected and actual outcomes; table shows each synthetic question and citation.</p><div class="card"><b>Expected vs actual · stacked outcome counts</b>__OUTCOMES__</div><div class="filters" aria-label="Question filters">__QBUTTONS__<input id="search" class="search" type="search" placeholder="Search synthetic questions or citations" aria-label="Search questions and citations"></div><table id="questions" class="responsive question"><caption>Every row and citation is synthetic.</caption><thead><tr><th>ID</th><th>Question</th><th>Type</th><th>Expected</th><th>Actual</th><th>Citations</th></tr></thead><tbody>__QUESTIONS__</tbody></table></section>
<section id="portfolio"><h2>Portfolio</h2><p>Counts and recommendations derive from the synthetic inventory.</p><div class="adoption">Standards adoption<b>__ADOPTION__</b>__ADOPTED__ of __TOTAL__ use cases</div><div class="split"><div class="card"><b>Platform-service reuse</b>__SERVICES__</div><div class="card"><b>Architecture patterns</b>__PATTERNS__</div></div><div class="gaps">__GAPS__</div><div class="card"><h3>Deterministic recommendations</h3><ul>__RECS__</ul></div></section>
<section id="evidence"><h2>Evidence</h2><p>Author-labelled prototype evidence; each metric includes its count basis.</p><div class="kpis">__KPIS__</div></section>
<noscript><p class="noscript">JavaScript is off. Content, SVGs, tables, evidence and Mermaid source remain visible; filters and click-through are inactive.</p></noscript></main><footer>Personal prototype · no production use</footer>
<script id="dashboard-data" type="application/json">__DATA__</script><script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js" defer></script><script>
(function(){"use strict";document.body.classList.add("js-enabled");
const qrows=[...document.querySelectorAll("#questions tbody tr")],qbuttons=[...document.querySelectorAll("[data-qfilter]")],search=document.getElementById("search");let qtype="all";
function applyQuestionFilter(){const value=search.value.trim().toLowerCase();qrows.forEach(row=>row.hidden=!((qtype==="all"||row.dataset.type===qtype)&&(!value||row.textContent.toLowerCase().includes(value))));}
qbuttons.forEach(button=>button.addEventListener("click",()=>{qtype=button.dataset.qfilter;qbuttons.forEach(item=>item.setAttribute("aria-pressed",String(item===button)));applyQuestionFilter();}));search.addEventListener("input",applyQuestionFilter);
const cbuttons=[...document.querySelectorAll("[data-cfilter]")],crows=[...document.querySelectorAll("#controls-table tbody tr")];cbuttons.forEach(button=>button.addEventListener("click",()=>{const filter=button.dataset.cfilter;cbuttons.forEach(item=>item.setAttribute("aria-pressed",String(item===button)));crows.forEach(row=>row.hidden=filter!=="all"&&row.dataset.status!==filter);}));
const evidence=document.getElementById("evidence");document.querySelectorAll(".heat button").forEach(button=>button.addEventListener("click",()=>{evidence.replaceChildren();const title=document.createElement("b");title.textContent=button.dataset.criterion+" · "+button.textContent;const text=document.createElement("p");text.textContent=button.dataset.evidence;evidence.append(title,text);}));
function diagram(id){const pre=document.getElementById(id);if(!window.mermaid||!pre)return;const source=pre.textContent,el=document.createElement("div");el.className="mermaid";el.textContent=source;pre.replaceWith(el);window.mermaid.run({nodes:[el]}).catch(()=>{const fallback=document.createElement("pre");fallback.className="mermaid-source";fallback.textContent=source;el.replaceWith(fallback);});}
window.addEventListener("DOMContentLoaded",()=>{if(!window.mermaid)return;window.mermaid.initialize({startOnLoad:false,securityLevel:"strict",theme:"base"});diagram("layer-source");diagram("gate-source");});
})();
</script></body></html>"""
    replacements={"__BANNER__":escape(synthetic_banner()),"__KPIS__":_kpis(data["kpis"]),
      "__FIELDS__":_field_svg(data["intake"]["fields"]),"__QUEUE__":queue,"__OUTCOMES__":_outcome_svg(data["wording"]),
      "__QBUTTONS__":qbuttons,"__QUESTIONS__":questions,"__HEATMAP__":_heatmap(data["reviews"]),
      "__CONTROLS__":_control_rows(data["controls"]),
      "__ADOPTION__":f'{insight["standards_adoption_percent"]:.1f}%',
      "__ADOPTED__":str(insight["standards_adoption_numerator"]),"__TOTAL__":str(insight["standards_adoption_denominator"]),
      "__SERVICES__":_bars(insight["platform_service_counts"],insight["use_case_count"],"service-chart"),
      "__PATTERNS__":_bars(insight["pattern_counts"],insight["use_case_count"],"pattern-chart"),
      "__GAPS__":gaps,"__RECS__":recs,"__LAYER__":escape(_layer()),"__GATE__":escape(_gate()),"__DATA__":_json(data)}
    for marker,value in replacements.items(): template=template.replace(marker,value)
    return template

def write_dashboard():
    return str(write_text(ROOT/"docs"/"index.html",render_dashboard()))
