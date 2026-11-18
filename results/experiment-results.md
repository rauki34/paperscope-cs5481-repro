# PaperScope experiment results

18 November 2026 · 20 QASPER development papers · BGE-small-en-v1.5 · Qdrant · DeepSeek Flash · Top-5 · cross-encoder reranking · run `69d0a79c60f02ed7`

This revision reports the current code: stub chunks merged (ISS-001), numeric citation alignment (ISS-002) and cross-encoder reranking (ISS-003). Setup, cost and the reproduction log are in [REPRODUCTION.md](../REPRODUCTION.md); the issue history is in [ISSUES.md](../ISSUES.md). Four result sets are kept side by side.

| Directory | Code state |
| --- | --- |
| `results/` | current: stub fix + numeric citation rules + reranking |
| `results/rerun-pre-rerank/` | stub fix only |
| `results/rerun-pre-fix/` | as cloned |
| `results/published-run/` | original submission, untouched |

## Question answering and retrieval

Both chunkings use the same 20 answerable questions and 4 out-of-scope questions. Answerable questions come from QASPER and keep only human annotations that can be located in the body text. Fixed-size chunking uses 240 tokens with 32 tokens of overlap. Paragraph-aware chunking keeps whole paragraphs as far as the same token budget allows. Both restrict retrieval to the paper the user selected and rerank 20 vector candidates with a cross-encoder before keeping five.

| Chunking | Hit@5 | Recall@5 | Strict span match, 20 answerable | Overall strict score, 24 | Out-of-scope refusal |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed size | 17/20 (85%) | 82.5% | 9/20 (45%) | 13/24 (54.2%) | 4/4 |
| Paragraph aware | 18/20 (90%) | 82.5% | 9/20 (45%) | 13/24 (54.2%) | 4/4 |

Hit@5 counts a hit when the union of the top-5 chunks covers at least half of an annotated paragraph. Reranking moved fixed-size chunking from 14/20 to 17/20 and paragraph-aware chunking from 16/20 to 18/20, while Top-1 hits rose from 7/20 to 12/20 and 11/20. The out-of-scope questions differ obviously from the paper content, so 4/4 only shows that these samples can be refused.

Strict span matching requires the annotated answer span to appear verbatim in the generated answer, so it understates accuracy: `qa-01` answers "pivoting and pivot-synthetic" correctly and still scores zero. The per-question semantic review in the previous revision covered the pre-rerank run (15/20 and 17/20) and was not repeated here, because the retrieved passages changed. This revision therefore reports strict scores only; the review table remains in `published-run/experiment-results-zh.md` and in the previous commit.

## Claim verification

The 20 pairs give 40 statements: 20 supported, 12 contradicted and 8 with insufficient evidence. For each statement, Direct and Checked receive exactly the same top-5 passages under the same chunking. The Checked prompt asks for a condition-by-condition check of metric, value, dataset, population, comparison and scope.

| Chunking | Prompt | Correct | Supported preserved | Non-supported accepted | Median per case |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed size | Direct | 39/40 | 20/20 | 0/20 | 1.47 s |
| Fixed size | Checked | 40/40 | 20/20 | 0/20 | 1.53 s |
| Paragraph aware | Direct | 36/40 | 18/20 | 0/20 | 1.45 s |
| Paragraph aware | Checked | 39/40 | 19/20 | 0/20 | 1.43 s |

No configuration accepts a non-supported statement. Under fixed-size chunking the condition-by-condition prompt gains one case; under paragraph-aware chunking it gains three, which is the first run where the extra instruction clearly pays for its latency.

`claim-18-a` accounts for most of the paragraph-aware loss. The statement is labelled SUPPORTED from the abstract's unqualified wording, while the retrieved body separates variance after anisotropy correction from raw variance and the statement omits the correction. Under paragraph-aware chunking the two prompts cite a passage that does not carry the statement's value, the numeric rule withholds both responses, and the case is scored wrong. The remaining gap, a quote that carries the number but not the same quantity, is [ISS-014](../ISSUES.md).

Every configuration marks `claim-16-a` as insufficient. The frozen label follows the abstract's statement about SimpleQuestions and WebQSP, while retrieval favours experimental passages phrased as "better or comparable". The strength of the claim differs between abstract and results section and should be recorded as an evidence-coverage and scope issue.

## Verifiable files

- [Frozen case set with evidence coordinates](cases.json)
- [Per-case outcome of this run, 208 rows, with rerank scores](rerun-outcomes.json)
- [Per-case outcome before reranking](rerun-pre-rerank/rerun-outcomes.json)
- [Per-case outcome before the chunk fix](rerun-pre-fix/rerun-outcomes.json)
- [Archived submission results](published-run/)
- [Aggregate metrics, latency and token usage](metrics.json)

All 208 samples received an API response. Four responses were withheld: `qa-09` under both chunkings and `claim-18-a` under both paragraph-aware prompts. The run used 256,088 prompt and 22,463 completion tokens.
