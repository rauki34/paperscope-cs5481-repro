# Issue log

Living record of defects, evaluation weaknesses and engineering gaps. Status is updated after every change, and each fix gets an entry in the change log at the end.

Status values: `FIXED`, `OPEN`, `WONTFIX`.

Last updated: 18 November 2026.

| ID | Area | Issue | Evidence | Severity | Status |
| --- | --- | --- | --- | --- | --- |
| ISS-001 | Retrieval | Paragraph-aware chunking emits stub chunks that rank above real passages | `section-21-03` contained only `py.` (3 characters) and reached the top-5 in 3 of 208 cases with cosine 0.871 | high | FIXED 2026-11-18 |
| ISS-002 | Faithfulness | Citation validation checks substring presence, not whether the quote supports the claim | `claim-18-a` was once accepted with a quote about the first principal component for a claim about static embeddings | high | OPEN |
| ISS-003 | Retrieval | Top-1 retrieval is weak and nothing reranks the top-5 | Hit@1 is 7/20 (35%) for both chunkings; the report only shows Hit@5 | medium | OPEN |
| ISS-004 | Evaluation | Chunking comparison is underpowered and confounded | Both strategies cap at 240 tokens and split at section boundaries; n=20 with no confidence interval | medium | OPEN |
| ISS-005 | Evaluation | Refusal questions are out of domain | Liquid nitrogen boiling point, Neptune orbit, tungsten melting point, proton mass; 4/4 is trivially achieved | medium | OPEN |
| ISS-006 | Evaluation | Strict span matching penalises correct paraphrases | 30% and 45% strict versus 75% and 85% under semantic review | medium | OPEN |
| ISS-007 | Evaluation | Claim set is small, anchor-derived and no longer discriminates prompts | 40 statements from 6 papers, all built from exact source anchors; Checked shows no gain over Direct | medium | OPEN |
| ISS-008 | Retrieval scope | Search is restricted to the paper the user selects | "Cite the source document" is satisfied by construction, never tested | low | OPEN |
| ISS-009 | Storage | The vector store is in memory and rebuilt on every start | 63 s cold start; no persistent database file | low | OPEN |
| ISS-010 | Reliability | No retry or backoff, and failures are recorded as an exception type only | The first full run aborted at 72/208 on HTTP 402; the cause had to be reproduced by hand | medium | OPEN |
| ISS-011 | Portability | `reasoning_effort="none"` is undocumented and silently skipped for other endpoints | The parameter is sent only when the base URL equals `api.deepseek.com`; behind a proxy thinking mode stays on and `temperature=0` stops applying | low | OPEN |
| ISS-012 | Testing | No unit tests | `evaluate.py --prepare` is the only smoke test | low | OPEN |
| ISS-013 | Reproducibility | `deepseek-flash` is a rolling alias | Identical prompts reproduce today, but the target model changes without notice | low | WONTFIX |

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
| Strict span match, paragraph aware | 8/20 (40.0%) | 9/20 (45.0%) |
| Overall strict score, paragraph aware | 12/24 (50.0%) | 13/24 (54.2%) |
| Fixed-size chunking | unchanged | unchanged |

The fix also changes the retrieval comparison from a tie to a two-question lead for paragraph-aware chunking. Full evaluation was rerun after the change (`79cb7c3e96f215dd`, 208 requests, 0 errors, 253,552 prompt and 21,838 completion tokens); the pre-fix run is archived in `results/rerun-pre-fix/`.

## ISS-002: citation validation

`validate_api_answer` accepts a response when each quote appears verbatim in the cited passage. It never checks that the quote is about the same quantity, entity or condition as the claim, so a true sentence can support a false claim.

`claim-18-a` demonstrates how far this can drift. In the post-fix run the same statement produced four different outcomes:

| Configuration | Verdict | Citation check |
| --- | --- | --- |
| Fixed size, Checked | SUPPORTED | passed |
| Fixed size, Direct | INSUFFICIENT | failed, response withheld |
| Paragraph aware, Checked | CONTRADICTED | passed |
| Paragraph aware, Direct | INSUFFICIENT | failed, response withheld |

The paper does contain a qualified and an unqualified version of the 5% claim, and the statement omits the qualification, so every one of these answers has some textual basis. That is precisely why a substring check is not enough.

Proposed fix: require the quote to contain the numbers and the key nouns of the claim, then optionally score entailment with a small local NLI model. Both are offline and add no API cost.

## Change log

| Date | Change |
| --- | --- |
| 2026-11-18 | Initial log after the clean-machine reproduction |
| 2026-11-18 | ISS-001 fixed; index rebuilt; full 208-request evaluation rerun; results and documentation updated |
