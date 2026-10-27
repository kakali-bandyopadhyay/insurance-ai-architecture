# ADR 0002 Document Extraction Build or Buy

Status: accepted for prototype scope.

## Context

The intake demo uses fixed-layout synthetic text documents with explicit labels. Deterministic extraction keeps field-level results and validation routing inspectable.

## Options and scores

Scores are illustrative, on a 1 (weak) to 5 (strong) scale; risk score means manageability. Not vendor measurements.

| Option | Value | Risk | Scalability | Latency | Resilience | Reuse | TCO |
|---|---:|---:|---:|---:|---:|---:|---:|
| Deterministic parser for fixed synthetic schema | 4 | 5 | 2 | 5 | 4 | 3 | 5 |
| Managed document extraction | 3 | 3 | 5 | 3 | 4 | 4 | 2 |
| Custom OCR/classifier/extractor pipeline | 2 | 2 | 3 | 2 | 2 | 3 | 1 |

## Decision

Build the small deterministic parser for this prototype. Treat managed extraction as a production option to evaluate against document diversity, confidence calibration, data handling, integration, support and total cost. The local parser is not suitable for unstructured production submissions.

## Criterion scores (illustrative)

| Criterion | Deterministic build | Managed service | Custom ML build |
|---|---:|---:|---:|
| Value | 4 | 3 | 2 |
| Risk manageability | 5 | 3 | 2 |
| Scalability | 2 | 5 | 3 |
| Latency | 5 | 3 | 2 |
| Resilience | 4 | 4 | 2 |
| Reuse | 3 | 4 | 3 |
| TCO | 5 | 2 | 1 |

## Consequences and review trigger

The parser is explainable and dependency-free but supports only the synthetic labels and formats. Revisit for varied scans, handwriting, tables, languages or material volume growth.
