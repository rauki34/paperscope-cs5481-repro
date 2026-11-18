# PaperScope

PaperScope is a CS5481 Data Engineering group project for **Topic 5: Knowledge Base Q&A with Verifiable Citations**. Select a research paper, ask an English question or check a statement, and inspect the exact evidence that led to the answer. The corpus uses 20 QASPER development papers.

## Run on your computer

Use Python 3.12 and allow roughly 3 GB for a CPU environment, model files, and caches. Run the following in the cloned repository. The initial package and model downloads require internet access.

```sh
git clone https://github.com/Kevin999-sudo/paperscope-cs5481.git
cd paperscope-cs5481
python -m venv .venv
```

Use `.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux in place of `python` below. On Windows or Linux, optionally install the CPU PyTorch wheel first using `python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`.

```sh
python -m pip install -r requirements.txt
python prepare_assets.py
python run_deepseek.py --serve --offline
```

Open [http://127.0.0.1:8517](http://127.0.0.1:8517). The offline mode uses MiniLM for extractive QA and can display existing evaluation results. For generated answers and statement checking, start `python run_deepseek.py --serve` and enter your own DeepSeek API key at the hidden terminal prompt. An existing `PAPERSCOPE_API_KEY` environment variable works for automated runs.

Select **pioNER: Datasets and Baselines for Armenian Named Entity Recognition** with **Paragraph aware** chunking. Ask “What is the source of the news sentences?” to see `ilur.am` with a citation. Ask about the boiling point of liquid nitrogen to test refusal. In statement checking, compare “The manually annotated test dataset contains 2,566 sentences” with the same statement changed to 5,266.

## Evaluation

Run `python run_deepseek.py --evaluate` with an API key to reproduce the benchmark. It makes 208 model requests on a fresh run and caches completed cases locally. Published results cover 20 answerable questions, four out-of-scope refusal questions, and 20 pairs of statements. [Metrics](results/metrics.json), [per-case outcomes](results/outcomes.json), and the [experiment discussion](results/experiment-results.md) report the observed run. A local rerun writes the full retrieved passages to the ignored `results/runs.json` file.

| Measure | Fixed size | Paragraph aware |
| --- | ---: | ---: |
| Evidence Hit@5 on 20 answerable questions | 17/20 | 18/20 |
| Strict answer-span match on 20 questions | 9/20 | 9/20 |
| Correct refusal on four out-of-scope questions | 4/4 | 4/4 |

The direct and condition-by-condition statement checks score 39/40 and 40/40 under fixed-size chunking, and 36/40 and 39/40 under paragraph-aware chunking. Retrieval reranks 20 vector candidates with a cross-encoder before keeping five; the sidebar toggle compares against plain vector search, and the benchmark runs with reranking on. See the report for examples and scoring limitations.

A clean-machine reproduction on 18 November 2026 matched 207 of 208 per-case judgements and reproduced the published token totals exactly; one borderline claim case flips. Setup, timings, cost and the deviation analysis are in [REPRODUCTION.md](REPRODUCTION.md). The archived submission results are kept unchanged in `results/published-run/`, and `results/rerun-outcomes.json` records the current run case by case. Known defects and evaluation gaps are tracked in [ISSUES.md](ISSUES.md); ISS-001 (stub chunks in paragraph-aware chunking) is fixed and the benchmark was rerun after the change.

## Collaboration

- `paperscope.py` owns document ingestion, chunking, embeddings, retrieval and citation validation.
- `app.py` contains the Streamlit workflows. `run_deepseek.py` starts the app or evaluation.
- `evaluate.py` defines benchmark execution and metrics. `claim_cases.py` records the statement pairs and source anchors.
- `submission/` contains the report with appended slides, the editable PowerPoint and the submission checklist.

Anyone with the link can view, clone or fork this public repository. For changes, create a branch in a fork and open a pull request. Keep credentials, downloaded model weights and QASPER source files in the local ignored paths.

## Data and tools

QASPER by Dasigi et al. (2021) supplies the papers and QA annotations. The case set selects annotated spans and adds normalized offsets. The [QASPER dataset card](https://huggingface.co/datasets/allenai/qasper) lists CC BY 4.0 and links to the [original paper](https://aclanthology.org/2021.naacl-main.365/).

The setup script retrieves pinned [BGE-small](https://huggingface.co/BAAI/bge-small-en-v1.5), [MiniLM QA](https://huggingface.co/deepset/minilm-uncased-squad2) and [MiniLM cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) model revisions. [DeepSeek](https://api-docs.deepseek.com/) handles generation.
