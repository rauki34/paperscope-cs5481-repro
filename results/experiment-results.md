# PaperScope experiment results

18 November 2026 · 20 QASPER development papers · BGE-small-en-v1.5 · Qdrant · DeepSeek Flash · Top-5 · run `abe7f554cce0628b`

These numbers come from a full reproduction of the archived submission on a clean Windows machine. The archived run is preserved in `published-run/`; the two differ in one of 208 cases, described under [Claim verification](#claim-verification). Setup, cost and the reproduction log are in [REPRODUCTION.md](../REPRODUCTION.md).

## Question answering and retrieval

Both chunkings use the same 20 answerable questions and 4 out-of-scope questions. Answerable questions come from QASPER and keep only human annotations that can be located in the body text. Fixed-size chunking uses 240 tokens with 32 tokens of overlap. Paragraph-aware chunking keeps whole paragraphs as far as the same token budget allows. Both restrict retrieval to the paper the user selected.

| Chunking | Hit@5 | Recall@5 | Strict span match, 20 answerable | Overall strict score, 24 | Out-of-scope refusal |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed size | 14/20 (70%) | 67.5% | 6/20 (30%) | 10/24 (41.7%) | 4/4 |
| Paragraph aware | 14/20 (70%) | 65.0% | 8/20 (40%) | 12/24 (50.0%) | 4/4 |

Hit@5 counts a hit when the union of the top-5 chunks covers at least half of an annotated paragraph. Both chunkings hit the same number of questions and the same retrieval score within noise. The out-of-scope questions differ obviously from the paper content, so 4/4 only shows that these samples can be refused.

### Per-question semantic review

Beyond the strict score, each answer is checked against the question, the reference answer and the citation it actually produced. A correct paraphrase is accepted when it covers the required fact and the source supports it. A question missing a required comparison, an answer that does not address the question, or a citation blocked by validation is scored as wrong. This is a supplementary review of the current output; the script and the page keep the reproducible strict score.

| Case | Fixed | Paragraph aware | Basis |
| --- | --- | --- | --- |
| qa-01 | correct | correct | Both name and define the two methods as in the source. |
| qa-02 | wrong | correct | Fixed says only "news corpus"; paragraph aware answers `ilur.am` explicitly. |
| qa-03 | correct | correct | Both list target subreddits and the frontpage. The question asks for topic, not post counts. |
| qa-04 | correct | wrong | Fixed names logistic regression. Paragraph aware returns a generic "predicts dogmatism" answer that omits the model class. |
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

On answerable questions the review gives fixed-size chunking **15/20 (75%)** and paragraph-aware chunking **16/20 (80%)**. Including the refusal questions the totals are **19/24 (79.2%)** and **20/24 (83.3%)**. Both readings favour paragraph-aware chunking slightly in this question set. The gap is a single reviewed question and would need a larger test set and a second reviewer to be called stable.

## Claim verification

The 20 pairs give 40 statements: 20 supported, 12 contradicted and 8 with insufficient evidence. For each statement, Direct and Checked receive exactly the same top-5 passages under the same chunking. The Checked prompt asks for a condition-by-condition check of metric, value, dataset, population, comparison and scope.

| Chunking | Prompt | Correct | Supported preserved | Non-supported accepted | Median per case |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed size | Direct | 39/40 | 19/20 | 0/20 | 1.01 s |
| Fixed size | Checked | 39/40 | 19/20 | 0/20 | 1.05 s |
| Paragraph aware | Direct | 39/40 | 19/20 | 0/20 | 0.97 s |
| Paragraph aware | Checked | 38/40 | 18/20 | 0/20 | 1.01 s |

In the archived run both prompts tied under each chunking. In this reproduction they no longer tie under paragraph-aware chunking, because Direct accepts `claim-18-a` once and Checked still refuses it. The condition-by-condition prompt costs latency and shows no accuracy gain on this set.

Every configuration marks `claim-16-a` as insufficient. The frozen label follows the abstract's statement about SimpleQuestions and WebQSP, while retrieval favours experimental passages phrased as "better or comparable". The strength of the claim differs between abstract and results section and should be recorded as an evidence-coverage and scope issue.

`claim-18-a` is the case that moves between runs. The label is SUPPORTED, following the abstract's unqualified wording. The retrieved body separates variance after anisotropy correction from raw variance, and the statement omits the correction condition, so a refusal is well grounded; that is what the archived run and the Checked prompt do. When Direct accepts it, the attached quote is a sentence about the first principal component, not about a static embedding. The quote exists in the source, and validation only checks that, so the response passes. Treat the acceptance as a lenient pass, not an improvement. The main table keeps frozen labels so scoring is never adjusted after seeing output.

## Verifiable files

- [Frozen case set with evidence coordinates](cases.json)
- [Per-case outcome of this reproduction, 208 rows](rerun-outcomes.json)
- [Per-case outcome and citations of the archived run](outcomes.json)
- [Aggregate metrics, latency and token usage](metrics.json)
- [Archived submission results](published-run/)

All 208 samples received an API response. No response in this run was withheld for an unverifiable citation. The 316 retained quotes were checked against the top-5 passages of their own case. Exact-string matching and semantic review use separate criteria.
