# Reproduction report

Reproduction of PaperScope (CS5481 Topic 5, knowledge-base QA with verifiable citations) on a clean Windows machine, 18 November 2026.

This document records the state of the code as cloned, before any fix. The numbers below therefore describe the pre-fix chunking. The only code change since then is the stub-chunk fix tracked as ISS-001 in [ISSUES.md](ISSUES.md); the benchmark was rerun afterwards and the current numbers live in [results/experiment-results.md](results/experiment-results.md), with the pre-fix run archived in `results/rerun-pre-fix/`.

## Verdict

The published run reproduces. 208 of 208 benchmark requests returned, no API errors and no citation-validation failures, and 207 of 208 per-case judgements match the archived results byte for byte. One claim case flips because it sits on a genuine decision boundary in the source paper; see [The single deviation](#the-single-deviation).

| Check | Result |
| --- | --- |
| Environment build from `requirements.txt` | All pinned versions resolve and install |
| Dataset and model checksums | `prepare_assets.py --check` passes |
| Offline demo (local extractive QA) | Correct answer with citation, correct refusal |
| Full evaluation, 208 requests | 208/208, 0 API errors, 0 citation errors |
| Token usage | 252,092 prompt / 21,524 completion, identical to the published run |
| Per-case agreement | 207/208 |
| Wall clock, evaluation | 31.7 s for 136 fresh requests (5 workers) |

## Environment

| Item | Value |
| --- | --- |
| OS | Windows 11, Git Bash |
| Python | 3.13.14 (README asks for 3.12; 3.13 works) |
| Virtual environment | `.venv`, created with `python -m venv` |
| Dependency install | `pip install -r requirements.txt`, 4 min 34 s |
| PyTorch | 2.14.1 CPU wheel from PyPI |
| Vector store | Qdrant in-memory, two collections (`fixed`, `section`) |
| Generator | `deepseek-flash` (DeepSeek-V4.1-Flash), `temperature=0`, `reasoning_effort=none` |
| Embeddings | `BAAI/bge-small-en-v1.5` at `5c38ec7c` |
| Extractive QA | `deepset/minilm-uncased-squad2` at `934656cd` |

The working tree was cloned from `Kevin999-sudo/paperscope-cs5481` and used without modifying `paperscope.py`, `evaluate.py`, `claim_cases.py` or `app.py`, so the run fingerprint `abe7f554cce0628b` is unchanged.

## Assets

| Asset | Size | Check |
| --- | ---: | --- |
| `data/qasper-train-dev-v0.3.tgz` | 10,835,856 B | SHA256 `a28fdf96…bdb5a` matches the script constant |
| `data/bge-small-en-v1.5` | 129 MB | 10 files at revision `5c38ec7c` |
| `data/minilm-uncased-squad2` | 128 MB | 5 files at revision `934656cd` |

`prepare_assets.py --check` prints `Dataset checksum and model files verified.`

Corpus after filtering: 20 QASPER papers, 604 chunks with fixed-size chunking and 636 chunks with paragraph-aware chunking. First index build took 63.5 s including model loading; embeddings are cached in `.cache/*.npy` so later starts skip encoding.

## Timeline

| Time (GMT+8) | Step |
| --- | --- |
| 22:12 | Clone repository |
| 22:13 | Download QASPER archive, verify SHA256 |
| 22:14 | Download both model snapshots |
| 22:17 | Dependency install completes |
| 22:19 | `run_deepseek.py --serve --offline` serves on `127.0.0.1:8517` |
| 22:19 | Smoke tests: cited answer `ilur.am`, refusal on liquid-nitrogen question, evaluation tab renders |
| 23:11 | Evaluation attempt 1: 72/208 requests, then HTTP 402 `Insufficient Balance` |
| 23:15 | Evaluation attempt 2 after top-up: 136 remaining requests, 31.7 s, 208 rows saved |

Attempt 1 is not a code defect. The checkpoint at `.cache/runs-<fingerprint>.json` keeps every successful case, so the second attempt re-sent only the 136 missing requests and spent about USD 0.03.

## Results

`results/metrics.json` is the reproduction. The archived submission numbers are preserved unchanged in `results/published-run/`.

### Question answering

| Chunking | Cases | Hit@5 | Recall@5 | Strict span match (20 answerable) | Overall strict score (24) | Refusal (4) | Median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed size | 24 | 14/20 (70.0%) | 67.5% | 6/20 (30.0%) | 10/24 (41.7%) | 4/4 | 1.10 s |
| Paragraph aware | 24 | 14/20 (70.0%) | 65.0% | 8/20 (40.0%) | 12/24 (50.0%) | 4/4 | 1.09 s |

### Claim verification

| Chunking | Prompt | Correct | Supported preserved | Non-supported accepted | Median |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed size | Direct | 39/40 | 19/20 | 0/20 | 1.01 s |
| Fixed size | Checked | 39/40 | 19/20 | 0/20 | 1.05 s |
| Paragraph aware | Direct | 39/40 | 19/20 | 0/20 | 0.97 s |
| Paragraph aware | Checked | 38/40 | 18/20 | 0/20 | 1.01 s |

Token usage: 252,092 prompt and 21,524 completion tokens across all six groups. 316 claims were returned with a quote that passed exact-substring validation against the retrieved passage.

## The single deviation

`section / direct / claim-18-a`, paper `1909.00512`, statement:

> For ELMo, BERT and GPT-2, a static embedding explains less than 5% of contextualized variance on average across the examined layers.

| Run | Verdict | Judgement |
| --- | --- | --- |
| Archived | INSUFFICIENT | wrong against the frozen label |
| Reproduction | SUPPORTED | correct against the frozen label |

Retrieval is identical in both runs: same five chunks, same cosine similarities to four decimals (`0.8968`, `0.8766`, `0.8707`, `0.8702`, `0.8538`). The difference is purely in generation.

The case is borderline because the retrieved passage contains two sentences pulling in opposite directions. One supports the statement in its qualified form:

> In no layer of ELMo, BERT, or GPT-2 can more than 5% of the variance in a word's contextualized representations be explained by a static embedding, on average.

The next sentence limits that to the corrected measurement:

> Even the average raw MEV is below 5% for all layers of ELMo and BERT; only for GPT-2 is the raw MEV non-negligible, being around 30% on average for layers 2 to 11 due to extremely high anisotropy.

The statement omits the anisotropy correction, so INSUFFICIENT is defensible and SUPPORTED follows the abstract's unqualified wording, which is what the frozen label uses. Two independent signals confirm the case sits near a coin flip: within the same run the stricter `checked` prompt still answers INSUFFICIENT for identical evidence, and the archived run answered INSUFFICIENT for both prompts.

The reproduction's SUPPORTED answer also shows a citation weakness. Its first claim says "a static embedding", but the attached quote says "their first principal component". The quote is genuinely in the source, and `validate_api_answer` only checks that, not whether the quote entails the claim, so the response passes validation. This makes the flip a lenient pass rather than a better answer.

Impact is limited to one cell: paragraph-aware Direct moves from 38/40 to 39/40. Every other published number is unchanged, and the QA side, including the 48 human-reviewed judgements behind 15/20 and 16/20, is unaffected.

## Cost and time

| Item | Value |
| --- | --- |
| Total requests, full run | 208 |
| Requests billed in this reproduction | 72 (attempt 1) + 136 (attempt 2) |
| Tokens | 252,092 prompt / 21,524 completion |
| Estimated spend | USD 0.05 off-peak for the full run; about USD 0.03 billed here |
| Evaluation wall clock | 49 s total across both attempts |

## Reproduce from scratch

```sh
git clone <this repository>
cd paperscope-cs5481
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe prepare_assets.py
.venv/Scripts/python.exe prepare_assets.py --check
.venv/Scripts/python.exe run_deepseek.py --serve --offline
```

For generation, export the key rather than typing it at the prompt, because `run_deepseek.py` requires an interactive terminal otherwise:

```sh
export PAPERSCOPE_API_KEY=sk-...
.venv/Scripts/python.exe run_deepseek.py --evaluate
.venv/Scripts/python.exe run_deepseek.py --serve
```

The evaluation resumes from `.cache/runs-<fingerprint>.json`, so an interrupted run is not repeated.

## Artifacts

| Path | Content |
| --- | --- |
| `results/metrics.json` | Aggregate metrics from this reproduction |
| `results/rerun-outcomes.json` | Per-case outcome of all 208 requests, without passage text |
| `results/cases.json` | Frozen question and statement set with evidence coordinates |
| `results/published-run/` | Archived submission results, untouched |
| `results/experiment-results.md` | Experiment discussion, English |
| `results/runs.json` | Full retrieved passages and model output, local only, gitignored by design |

## Known limitations

- Twenty papers and twenty answerable questions give wide confidence intervals. The gap between the two chunking strategies is one rank position on one question.
- The four refusal questions are out of domain, so correct refusal is necessary but not strong evidence of grounding.
- `deepseek-flash` is a rolling alias that always points at the newest release, so exact reproduction is guaranteed only for the model version active on 18 November 2026.
- Retrieval is scoped to a single user-selected paper, which makes the "cite the document" requirement easy to satisfy.
