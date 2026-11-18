# Issue log

Living record of defects, evaluation weaknesses and engineering gaps. Status is updated after every change, and each fix gets an entry in the change log at the end.

Status values: `FIXED`, `OPEN`, `WONTFIX`.

Last updated: 19 November 2026.

| ID | Area | Issue | Evidence | Severity | Status |
| --- | --- | --- | --- | --- | --- |
| ISS-001 | Retrieval | Paragraph-aware chunking emits stub chunks that rank above real passages | `section-21-03` contained only `py.` (3 characters) and reached the top-5 in 3 of 208 cases with cosine 0.871 | high | FIXED 2026-11-18 |
| ISS-002 | Faithfulness | Citation validation checked substring presence only, so a quote did not have to carry the values it justified | `claim-18-a` was accepted with a quote about the first principal component for a claim about static embeddings | high | FIXED 2026-11-18 |
| ISS-003 | Retrieval | Top-1 retrieval was weak and nothing reranked the top-5 | Hit@1 was 7/20 (35%) under both chunkings | high | FIXED 2026-11-18 |
| ISS-014 | Faithfulness | Numeric alignment does not test semantic entailment | A quote can carry the right number and still describe a different quantity; `claim-18-a` remains unsolved | medium | OPEN |
| ISS-004 | Evaluation | Chunking comparison is underpowered and confounded | Both strategies cap at 240 tokens and split at section boundaries; n=20 with no confidence interval | medium | OPEN |
| ISS-005 | Evaluation | Refusal questions are out of domain | Liquid nitrogen boiling point, Neptune orbit, tungsten melting point, proton mass; 4/4 is trivially achieved | medium | OPEN |
| ISS-006 | Evaluation | Strict span matching penalises correct paraphrases | 45% strict while inspection of the same answers finds far more correct; `qa-01` answers correctly and is scored wrong | medium | OPEN |
| ISS-007 | Evaluation | Claim set is small, anchor-derived and does not discriminate prompts | 40 statements from 6 papers, all built from exact source anchors; Checked shows no consistent gain | medium | OPEN |
| ISS-008 | Retrieval scope | Search is restricted to the paper the user selects | "Cite the source document" is satisfied by construction, never tested | low | OPEN |
| ISS-009 | Storage | The vector store is in memory and rebuilt on every start | 63 s cold start; no persistent database file | low | OPEN |
| ISS-010 | Reliability | No retry or backoff, and rejections are not logged with a reason | The first full run aborted at 72/208 on HTTP 402; withheld responses record only a boolean | medium | OPEN |
| ISS-011 | Portability | `reasoning_effort="none"` is undocumented and silently skipped for other endpoints | The parameter is sent only when the base URL equals `api.deepseek.com`; behind a proxy thinking mode stays on and `temperature=0` stops applying | low | OPEN |
| ISS-012 | Testing | No unit tests | `evaluate.py --prepare` is the only smoke test | low | OPEN |
| ISS-013 | Reproducibility | `deepseek-flash` is a rolling alias | Identical prompts reproduce on the same day, but the target model changes without notice | low | WONTFIX |

## ISS-001: stub chunks

A paragraph break landing one token after a chunk start produced a chunk holding a single word. Short chunks embed cleanly and score high on cosine similarity, so they displace real evidence.

Fix: `MIN_CHUNK_TOKENS = 40` in `paperscope.py`; the paragraph-aware pass now collects spans first and merges anything shorter into a neighbour.

| Measure | Before | After |
| --- | ---: | ---: |
| Paragraph-aware chunks | 636 | 618 |
| Shortest chunk | 3 characters | 56 characters (a formula) |
| Hit@5, paragraph aware | 14/20 | 16/20 |
| Recall@5, paragraph aware | 65.0% | 72.5% |
| MRR, paragraph aware | 0.488 | 0.510 |

## ISS-002: citation validation

`validate_api_answer` accepted a response whenever each quote appeared verbatim in the cited passage, so a true sentence could justify an unrelated claim.

Fix: two numeric rules, both offline and deterministic.

1. Every number in an answer sentence must appear in that sentence's own quote.
2. For a SUPPORTED verdict, every number in the input statement must appear somewhere in the retained quotes.

`CONTRADICTED` is exempt, because its quote carries the conflicting value rather than the claimed one. Numbers are matched with letter-boundary guards, so `Flickr30K` does not count as a `30`.

Replayed against the 311 accepted quote pairs of the previous run, both rules produced zero rejections, so they add no false positives on this data. In the rerun the validator withheld four responses: `qa-09` under both chunkings and `claim-18-a` under both paragraph-aware prompts. Rejection reasons are not stored per response yet, which is tracked under ISS-010.

Limitation: this checks that values travel with the citation, not that the quote covers the same quantity. That residual gap is ISS-014.

## ISS-003: reranking

Vector search returns 20 candidates and a cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2` at `233902d2`, 88 MB, CPU) rescores them before the top 5 are kept. Each pair is scored as `(question, section + chunk)`.

| Measure | Fixed before | Fixed after | Paragraph before | Paragraph after |
| --- | ---: | ---: | ---: | ---: |
| Hit@1 | 7/20 | 12/20 | 7/20 | 11/20 |
| Hit@5 | 14/20 | 17/20 | 16/20 | 18/20 |
| MRR | 0.471 | 0.702 | 0.510 | 0.676 |
| Recall@5 | 67.5% | 82.5% | 72.5% | 82.5% |
| Median end-to-end latency | 1.0 s | 1.47 s | 1.0 s | 1.47 s |

The reranker is exposed as a sidebar checkbox, is on by default, and its score is shown next to the cosine similarity in the passage list.

## Change log

| Date | Change |
| --- | --- |
| 2026-11-18 | Initial log after the clean-machine reproduction |
| 2026-11-18 | ISS-001 fixed; index rebuilt; full 208-request evaluation rerun |
| 2026-11-18 | ISS-002 fixed with numeric alignment; ISS-014 opened for entailment |
| 2026-11-18 | ISS-003 fixed with cross-encoder reranking; evaluation rerun `69d0a79c60f02ed7` |
| 2026-11-19 | Corrected the attribution of the paragraph-aware claim regression: `claim-16-b` and `claim-17-b` flip to CONTRADICTED, while the blocked `claim-18-a` was already wrong |
