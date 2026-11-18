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

Strict span matching requires the annotated answer span to appear verbatim in the generated answer, so it understates accuracy: `qa-01` answers "pivoting and pivot-synthetic" correctly and still scores zero.

### Per-question semantic review

Every answer was re-read against its question, its reference span and the citation it produced. A paraphrase counts as correct when it covers the fact the question asks for and the citation supports it; a refusal on an answerable question, a missing half of a two-part question, or an answer about a different quantity counts as wrong. The review covers the answers of this run, so it replaces the table that shipped with the previous revision.

| Case | Fixed | Paragraph aware | Basis |
| --- | --- | --- | --- |
| qa-01 | correct | correct | Both list pivoting and pivot-synthetic with their definitions. |
| qa-02 | correct | correct | Both answer `ilur.am`. |
| qa-03 | correct | correct | Both give the four subreddits and the frontpage. |
| qa-04 | wrong | wrong | Neither names logistic regression; fixed mentions a linear regression on behavioural features, paragraph aware stays generic. |
| qa-05 | correct | correct | Both expand KBQA. |
| qa-06 | correct | correct | Both name relation detection. |
| qa-07 | correct | correct | Both name the first principal component at the given layer. |
| qa-08 | correct | correct | Both measure compactness by model size in megabytes; fixed adds 15.4 MB against 197.5 MB. |
| qa-09 | wrong | wrong | Both refuse, but the paper does report a baseline, so the refusal is unjustified. |
| qa-10 | correct | correct | Both identify the multilingual pronunciation corpus collected by deri2016grapheme. |
| qa-11 | correct | correct | Both give 20 reviewers recruited from the authors' institutions. |
| qa-12 | correct | correct | Both answer PG-net, pointer networks with a coverage mechanism. |
| qa-13 | correct | correct | Both give 30,000 images with five descriptions each. |
| qa-14 | correct | correct | Both name linguistic bias and unwarranted inferences and give examples. |
| qa-15 | wrong | correct | Fixed names only the relations it handles best; paragraph aware answers explicit best and implicit worst, which is what was asked. |
| qa-16 | correct | correct | Both give the 1 percent gain over the best previous system. |
| qa-17 | correct | correct | Both explain that the generator scores candidate answers by semantic relevance. |
| qa-18 | correct | correct | Both name QA PGNet and Multi-decoder QA PGNet. |
| qa-19 | correct | correct | Both answer that the transformer layer wins, with the CSAT caveat. |
| qa-20 | correct | correct | Both answer CrowdFlower with the chat-style collection. |
| Four out-of-scope questions | 4/4 | 4/4 | Both refuse when evidence is missing. |

On answerable questions the review gives fixed-size chunking **17/20 (85%)** and paragraph-aware chunking **18/20 (90%)**. Including the refusal questions the totals are **21/24 (87.5%)** and **22/24 (91.7%)**. Strict matching scores 9/20 for both, so the strict metric discards eight to nine answers that a reader would accept, almost all of them correct paraphrases.

## Claim verification

The 20 pairs give 40 statements: 20 supported, 12 contradicted and 8 with insufficient evidence. For each statement, Direct and Checked receive exactly the same top-5 passages under the same chunking. The Checked prompt asks for a condition-by-condition check of metric, value, dataset, population, comparison and scope.

| Chunking | Prompt | Correct | Supported preserved | Non-supported accepted | Median per case |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed size | Direct | 39/40 | 20/20 | 0/20 | 1.47 s |
| Fixed size | Checked | 40/40 | 20/20 | 0/20 | 1.53 s |
| Paragraph aware | Direct | 36/40 | 18/20 | 0/20 | 1.45 s |
| Paragraph aware | Checked | 39/40 | 19/20 | 0/20 | 1.43 s |

No configuration accepts a non-supported statement. Under fixed-size chunking the condition-by-condition prompt gains one case; under paragraph-aware chunking Checked leads Direct 39/40 to 36/40, its widest gap so far, but most of that gap comes from Direct over-committing rather than from Checked improving.

Under paragraph-aware chunking Direct loses `claim-16-b` and `claim-17-b`, both from `1704.06194`. Both statements are labelled INSUFFICIENT because they add a scope the paper never claims, and reranking changed the passages enough that the model moved both to CONTRADICTED. `claim-18-a` is a separate case: the statement is labelled SUPPORTED from the abstract's unqualified wording, while the retrieved body separates variance after anisotropy correction from raw variance, and the statement omits the correction. The numeric rule withholds both paragraph-aware responses, but the case was already wrong before reranking, so blocking it changes no score. The remaining gap, a quote that carries the number but not the same quantity, is [ISS-014](../ISSUES.md).

Every configuration marks `claim-16-a` as insufficient. The frozen label follows the abstract's statement about SimpleQuestions and WebQSP, while retrieval favours experimental passages phrased as "better or comparable". The strength of the claim differs between abstract and results section and should be recorded as an evidence-coverage and scope issue.

## Verifiable files

- [Frozen case set with evidence coordinates](cases.json)
- [Per-case outcome of this run, 208 rows, with rerank scores](rerun-outcomes.json)
- [Per-case outcome before reranking](rerun-pre-rerank/rerun-outcomes.json)
- [Per-case outcome before the chunk fix](rerun-pre-fix/rerun-outcomes.json)
- [Archived submission results](published-run/)
- [Aggregate metrics, latency and token usage](metrics.json)

All 208 samples received an API response. Four responses were withheld: `qa-09` under both chunkings and `claim-18-a` under both paragraph-aware prompts. The run used 256,088 prompt and 22,463 completion tokens.
