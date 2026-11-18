# PaperScope

PaperScope is a CS5481 Data Engineering group project for **Topic 5: Knowledge Base Q&A with Verifiable Citations**. Select a research paper, ask an English question or check a statement, and inspect the exact evidence that led to the answer. The corpus uses 20 QASPER development papers.

This repository is a reproduction copy of the original submission. It records a clean-machine rerun, three fixes found during that rerun, and the benchmark after each change. See [Changes from the original submission](#changes-from-the-original-submission) and [ISSUES.md](ISSUES.md).

## Run on your computer

Use Python 3.12 and allow roughly 3.2 GB for a CPU environment, model files, and caches. Run the following in the cloned repository. The initial package and model downloads require internet access.

```sh
git clone https://github.com/rauki34/paperscope-cs5481-repro.git
cd paperscope-cs5481-repro
python -m venv .venv
```

Use `.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux in place of `python` below. On Windows or Linux, optionally install the CPU PyTorch wheel first using `python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`.

```sh
python -m pip install -r requirements.txt
python prepare_assets.py
python run_deepseek.py --serve --offline
```

Open [http://127.0.0.1:8517](http://127.0.0.1:8517). The offline mode uses MiniLM for extractive QA and can display existing evaluation results. For generated answers and statement checking, start `python run_deepseek.py --serve` and enter your own DeepSeek API key at the hidden terminal prompt. An existing `PAPERSCOPE_API_KEY` environment variable works for automated runs.

Select **pioNER: Datasets and Baselines for Armenian Named Entity Recognition** with **Paragraph aware** chunking. Ask “What is the source of the news sentences?” to see `ilur.am` with a citation. Ask about the boiling point of liquid nitrogen to test refusal. In statement checking, compare “The manually annotated test dataset contains 2,566 sentences” with the same statement changed to 5,266. The sidebar toggle switches reranking off, which is the only way to compare against plain vector search inside the app.

## Evaluation

Run `python run_deepseek.py --evaluate` with an API key to reproduce the benchmark. It makes 208 model requests on a fresh run and caches completed cases locally. The published results cover 20 answerable questions, four out-of-scope refusal questions, and 20 pairs of statements. [Metrics](results/metrics.json), [per-case outcomes](results/rerun-outcomes.json), and the [experiment discussion](results/experiment-results.md) report the current run. A local rerun writes the full retrieved passages to the ignored `results/runs.json` file.

| Measure | Fixed size | Paragraph aware |
| --- | ---: | ---: |
| Evidence Hit@5 on 20 answerable questions | 17/20 | 18/20 |
| Evidence Hit@1 on the same 20 questions | 12/20 | 11/20 |
| Strict answer-span match on 20 questions | 9/20 | 9/20 |
| Correct refusal on four out-of-scope questions | 4/4 | 4/4 |

The direct and condition-by-condition statement checks score 39/40 and 40/40 under fixed-size chunking, and 36/40 and 39/40 under paragraph-aware chunking. No configuration accepts a non-supported statement. Retrieval reranks 20 vector candidates with a cross-encoder before keeping five, which costs about 0.4 s per case. Strict span matching understates accuracy because it rejects correct paraphrases; see the report for examples and scoring limitations.

## Changes from the original submission

| ID | Change | Effect on the benchmark |
| --- | --- | --- |
| ISS-001 | Paragraph-aware chunking merged spans below 40 tokens, so stubs such as `py.` no longer enter the index | Chunks 636 → 618; Hit@5 14/20 → 16/20; Recall@5 65.0% → 72.5% |
| ISS-002 | Citation validation now requires an answer's numbers in its own quote, and a SUPPORTED verdict's numbers in the retained quotes | Four responses withheld in the rerun; no non-supported statement accepted |
| ISS-003 | Cross-encoder reranking of 20 vector candidates with `ms-marco-MiniLM-L6-v2` | Hit@1 7/20 → 12/20 (fixed) and 7/20 → 11/20 (paragraph); Hit@5 14/20 → 17/20 and 16/20 → 18/20; Recall@5 82.5% both |

Every item, including the open ones, is tracked with evidence and before/after numbers in [ISSUES.md](ISSUES.md). The open list covers evaluation weaknesses (sample size, out-of-domain refusals, strict scoring), the remaining entailment gap in citation checking, in-memory storage, missing retries and missing unit tests.

## Reproduction

A clean-machine reproduction on 18 November 2026 reproduced 207 of 208 per-case judgements of the submission and matched its token totals exactly, before any fix. Setup, timings, cost and the deviation analysis are in [REPRODUCTION.md](REPRODUCTION.md).

| Directory | Code state |
| --- | --- |
| `results/` | current: stub fix, numeric citation rules, reranking |
| `results/rerun-pre-rerank/` | stub fix only |
| `results/rerun-pre-fix/` | as cloned |
| `results/published-run/` | original submission, untouched |

## Collaboration

- `paperscope.py` owns document ingestion, chunking, embeddings, retrieval, reranking and citation validation.
- `app.py` contains the Streamlit workflows. `run_deepseek.py` starts the app or evaluation.
- `evaluate.py` defines benchmark execution and metrics. `claim_cases.py` records the statement pairs and source anchors.
- `submission/` contains the original report with appended slides, the editable PowerPoint and the submission checklist.

Anyone with the link can view, clone or fork this public repository. For changes, create a branch in a fork and open a pull request. Keep credentials, downloaded model weights and QASPER source files in the local ignored paths.

## Data and tools

QASPER by Dasigi et al. (2021) supplies the papers and QA annotations. The case set selects annotated spans and adds normalized offsets. The [QASPER dataset card](https://huggingface.co/datasets/allenai/qasper) lists CC BY 4.0 and links to the [original paper](https://aclanthology.org/2021.naacl-main.365/).

The setup script retrieves pinned [BGE-small](https://huggingface.co/BAAI/bge-small-en-v1.5), [MiniLM QA](https://huggingface.co/deepset/minilm-uncased-squad2) and [MiniLM cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) model revisions. [DeepSeek](https://api-docs.deepseek.com/) handles generation.
