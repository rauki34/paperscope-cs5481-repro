# PaperScope experiment results

18 November 2026 · 20 QASPER development papers · BGE-small-en-v1.5 · Qdrant · DeepSeek Flash · Top-5 · run `79cb7c3e96f215dd`

These numbers come from a clean-machine reproduction of the archived submission, after the chunk-boundary fix described in [ISSUES.md](../ISSUES.md) as ISS-001. Setup, cost and the reproduction log are in [REPRODUCTION.md](../REPRODUCTION.md). Three result sets are kept side by side:

| Directory | Code state | Purpose |
| --- | --- | --- |
| `results/` | current | Reported below |
| `results/rerun-pre-fix/` | before ISS-001 | Shows what the stub chunks cost |
| `results/published-run/` | original submission | Untouched reference |

## Question answering and retrieval

Both chunkings use the same 20 answerable questions and 4 out-of-scope questions. Answerable questions come from QASPER and keep only human annotations that can be located in the body text. Fixed-size chunking uses 240 tokens with 32 tokens of overlap. Paragraph-aware chunking keeps whole paragraphs as far as the same token budget allows. Both restrict retrieval to the paper the user selected.

| Chunking | Hit@5 | Recall@5 | Strict span match, 20 answerable | Overall strict score, 24 | Out-of-scope refusal |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed size | 14/20 (70%) | 67.5% | 6/20 (30%) | 10/24 (41.7%) | 4/4 |
| Paragraph aware | 16/20 (80%) | 72.5% | 9/20 (45%) | 13/24 (54.2%) | 4/4 |

Hit@5 counts a hit when the union of the top-5 chunks covers at least half of an annotated paragraph. Paragraph-aware chunking leads by two questions on Hit@5 and by 5.0 points on Recall@5, where before the chunk-boundary fix the two strategies tied at 14/20. The out-of-scope questions differ obviously from the paper content, so 4/4 only shows that these samples can be refused.

### Per-question semantic review

Beyond the strict score, each answer is checked against the question, the reference answer and the citation it actually produced. A correct paraphrase is accepted when it covers the required fact and the source supports it. A question missing a required comparison, an answer that does not address the question, or a citation blocked by validation is scored as wrong. This is a supplementary review of the current output; the script and the page keep the reproducible strict score.

| Case | Fixed | Paragraph aware | Basis |
| --- | --- | --- | --- |
| qa-01 | correct | correct | Both name and define the two methods as in the source. |
| qa-02 | wrong | correct | Fixed says only "news corpus"; paragraph aware answers `ilur.am` explicitly. |
| qa-03 | correct | correct | Both list target subreddits and the frontpage. The question asks for topic, not post counts. |
| qa-04 | correct | correct | Both name logistic regression as the classifier. |
| qa-05 | correct | correct | Both expand KBQA. |
| qa-06 | correct | correct | Both answer relation detection from the source. |
| qa-07 | correct | correct | Both answer the first principal component of the contextual representations at the given layer. |
| qa-08 | wrong | correct | Fixed refuses. Paragraph aware measures compactness by model size and gives 15.4 MB. |
| qa-09 | correct | correct | Both find the wFST baseline. |
| qa-10 | correct | correct | Both identify the multilingual pronunciation corpus extracted from Wiktionary. |
| qa-11 | correct | correct | Both state that 20 reviewers were recruited from the authors' institutions. |
| qa-12 | wrong | wrong | Neither identifies the pointer-generator with coverage. |
| qa-13 | correct | correct | Both give thirty thousand images with five captions each. |
| qa-14 | correct | correct | Both identify linguistic bias and unwarranted inferences, and the citations support both. |
| qa-15 | wrong | wrong | Neither says which of implicit and explicit relations performs better or worse. |
| qa-16 | wrong | wrong | The 3.02 and 0.96 figures are ensemble gains over a single model. The question asks for a comparison with the best published result. |
| qa-17 | correct | correct | Both state that the question generator is used to score candidate answers by semantic relevance. |
| qa-18 | correct | correct | Both identify QA PGNet and Multi-decoder QA PGNet. |
| qa-19 | correct | correct | Both answer that Transformer over BERT performs better and state the condition on the result. |
| qa-20 | correct | correct | Both answer CrowdFlower and the chat-style collection process. |
| Four out-of-scope questions | 4/4 | 4/4 | Both refuse when evidence is missing. |

On answerable questions the review gives fixed-size chunking **15/20 (75%)** and paragraph-aware chunking **17/20 (85%)**. Including the refusal questions the totals are **19/24 (79.2%)** and **21/24 (87.5%)**. The review and the strict score agree on the direction: paragraph-aware chunking is ahead once the stub chunks are gone.

## Claim verification

The 20 pairs give 40 statements: 20 supported, 12 contradicted and 8 with insufficient evidence. For each statement, Direct and Checked receive exactly the same top-5 passages under the same chunking. The Checked prompt asks for a condition-by-condition check of metric, value, dataset, population, comparison and scope.

| Chunking | Prompt | Correct | Supported preserved | Non-supported accepted | Median per case |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed size | Direct | 38/40 | 18/20 | 0/20 | 0.93 s |
| Fixed size | Checked | 39/40 | 19/20 | 0/20 | 1.11 s |
| Paragraph aware | Direct | 38/40 | 18/20 | 0/20 | 0.98 s |
| Paragraph aware | Checked | 38/40 | 18/20 | 0/20 | 1.00 s |

The condition-by-condition prompt costs latency and buys one case under fixed-size chunking and none under paragraph-aware chunking. No configuration accepts a non-supported statement.

Every configuration marks `claim-16-a` as insufficient. The frozen label follows the abstract's statement about SimpleQuestions and WebQSP, while retrieval favours experimental passages phrased as "better or comparable". The strength of the claim differs between abstract and results section and should be recorded as an evidence-coverage and scope issue.

`claim-18-a` is unstable rather than merely borderline. The label is SUPPORTED, following the abstract's unqualified wording, while the retrieved body separates variance after anisotropy correction from raw variance and the statement omits the correction. In this run the same statement produced four outcomes: SUPPORTED and CONTRADICTED where the citation passed, INSUFFICIENT twice where the citation check withheld the response. The case is recorded in [ISSUES.md](../ISSUES.md) as ISS-002, because a validator that only checks substring presence cannot separate these responses.

## Verifiable files

- [Frozen case set with evidence coordinates](cases.json)
- [Per-case outcome of this run, 208 rows](rerun-outcomes.json)
- [Per-case outcome before the chunk fix](rerun-pre-fix/rerun-outcomes.json)
- [Per-case outcome and citations of the archived run](outcomes.json)
- [Aggregate metrics, latency and token usage](metrics.json)
- [Archived submission results](published-run/)

All 208 samples received an API response. Two responses were withheld because a citation could not be verified, both on `claim-18-a`. The 311 retained quotes were checked against the top-5 passages of their own case. Exact-string matching and semantic review use separate criteria.
