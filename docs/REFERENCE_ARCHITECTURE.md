# Reference Architecture

Synthetic roles and data; illustrative. This document separates components implemented in the repository from production architecture described only. Any regulatory or Responsible-AI mapping is illustrative, not a statement of requirements.

## Enterprise AI layer view

```mermaid
flowchart TB
  subgraph Ingress[Source and document ingestion]
    S[Submission documents<br/>implemented local JSON] --> IN[Intake and staging<br/>implemented]
    W[Wording pack<br/>implemented local JSON] --> RET[Clause retrieval<br/>implemented keyword search]
  end
  IN --> EX[Extraction and validation<br/>implemented]
  EX --> HR[Human review queue<br/>implemented for failed records]
  RET --> GW[Model gateway: routing, cost caps, fallbacks<br/>described only]
  GW --> GU[Guardrails: input and output checks, PII handling, citation validation<br/>citation check implemented; others described only]
  GU --> RESP[Answer with clause IDs or decline<br/>implemented deterministically]
  EX --> EV[Evaluation harness<br/>implemented with author labels]
  RESP --> EV
  EV --> DA[Design-authority review<br/>implemented local evidence rules]
  DA --> INV[AI inventory and portfolio insight<br/>implemented]
  INV --> DASH[Static dashboard<br/>implemented]
  OBS[Observability and model monitoring<br/>described only] -.-> GW
  AUD[Central audit service and production identity<br/>described only] -.-> HR
  LEG[Legend: solid = implemented; dashed = described only. Human review is an accountable decision point.]
```

## Submission intake

```mermaid
flowchart LR
  DOC[Cover note, values summary, loss-run summary<br/>synthetic] --> PARSE[Deterministic field extraction<br/>implemented]
  PARSE --> VAL[Required, range, date, TIV/limit and year-completeness checks<br/>implemented]
  VAL -->|checks pass| UW[Ready for underwriter review<br/>not automatic acceptance]
  VAL -->|any check fails| QUEUE[Human-review queue with reason codes<br/>implemented]
  LABEL[Author-labelled expected fields] --> EVAL[Field-level evaluation<br/>implemented]
  PARSE --> EVAL
  LEG[Legend: solid = implemented. Human underwriting judgment remains outside the prototype.]
```

## Wording Q&A

```mermaid
flowchart LR
  Q[Question plus optional contract and version] --> RET[Keyword retrieval over clause pack<br/>implemented]
  RET --> EVID[Retrieved clauses and version comparison<br/>implemented]
  EVID --> DEC{Evidence sufficient and contract in pack?}
  DEC -->|yes, no conflict| ANS[Answer with validated clause IDs<br/>implemented]
  DEC -->|conflict| CON[Surface version conflict; ask reviewer to confirm operative text<br/>implemented]
  DEC -->|no or wrong contract| REF[Decline with reason<br/>implemented]
  GEN[Optional model phrasing from retrieved evidence<br/>described only; no provider integration] -.-> ANS
  ANS --> QA[Author-labelled outcome, citation and refusal evaluation<br/>implemented]
  CON --> QA
  REF --> QA
  LEG[Legend: solid = implemented; dashed = described only. Human contract interpretation remains outside the prototype.]
```

## Component inventory

| Layer | Implemented | Described only |
|---|---|---|
| Ingestion | Local synthetic JSON documents | Broker uploads, malware scanning, document storage |
| Extraction and validation | Deterministic parsing and business-rule checks | OCR, document classification, confidence model |
| Retrieval | Standard-library keyword retrieval | Managed vector store, embeddings and hybrid search |
| Model gateway | None | Model routing, rate/cost caps, fallback and provider abstraction |
| Guardrails | Citation-ID validation and wrong-contract / insufficient-evidence declines | PII detection, prompt-injection controls, managed policy enforcement |
| Evaluation | Labelled sample evaluation for fields, outcomes, citations and refusals | Continuous evaluation, drift, robustness and security suites |
| Human review | Failed intake queue output; wording conflict surfaced | Workflow platform, notifications, role entitlements and SLA operation |
| Observability | CLI evaluation reports | Traces, latency/cost telemetry, alerting and model monitoring |
| Audit | Evaluation and review outputs | Centralized immutable audit platform and retention controls |
| Portfolio | Synthetic inventory analytics and static dashboard | Enterprise repository integration and authoritative ownership |
