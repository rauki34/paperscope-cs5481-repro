import json
import os

import streamlit as st

from paperscope import (
    DEEPSEEK_MODEL, RERANK_ON, ROOT, PaperScope, STRATEGIES, answer_with_api,
)


st.set_page_config(page_title="PaperScope", layout="wide")
st.html("<style>[data-testid='stText'] {white-space: pre-wrap; overflow-wrap: anywhere;}</style>")


@st.cache_resource(show_spinner="Loading papers and building the vector index…")
def open_paperscope():
    return PaperScope()


st.title("PaperScope")
st.markdown("Ask about a research paper or check a statement against its source passages.")

page = st.radio("Workspace", ["Ask a question", "Check a statement", "Evaluation"],
                horizontal=True, label_visibility="collapsed")
if page == "Evaluation":
    st.header("Evaluation results")
    report_path = ROOT / "results" / "metrics.json"
    if not report_path.exists():
        st.info("Evaluation results will appear here after the benchmark completes.")
        st.stop()
    summary = json.loads(report_path.read_text(encoding="utf-8"))
    st.caption(f"{summary['model']} · top {summary['top_k']} passages · run {summary['fingerprint']}")
    st.subheader("Question answering")
    qa_rows, claim_rows = [], []
    for key, metrics in summary["metrics"].items():
        strategy, task = key.split("/")
        record = {
            "Chunking": STRATEGIES[strategy],
            "Cases": metrics["cases"],
            "Accuracy": f"{metrics['accuracy']:.1%}",
            "Median time": f"{metrics['median_seconds']:.2f} s",
        }
        if task == "qa":
            record.update({
                "Hit@5": f"{metrics['hit_at_5']:.1%}",
                "Recall@5": f"{metrics['recall_at_5']:.1%}",
                "Answerable span match": f"{metrics['answerable_span_accuracy']:.1%}",
                "Correct refusal": f"{metrics['correct_refusal_rate']:.1%}",
            })
            qa_rows.append(record)
        else:
            record.update({
                "Method": task.title(),
                "Supported preserved": f"{metrics['preservation_rate']:.1%}",
                "False acceptance": f"{metrics['false_acceptance_rate']:.1%}",
            })
            claim_rows.append(record)
    st.dataframe(qa_rows, hide_index=True, width="stretch")
    st.caption("QA accuracy uses a normalized reference-span match. Refusal is measured on four unrelated questions.")
    st.subheader("Statement checking")
    st.dataframe(claim_rows, hide_index=True, width="stretch")
    st.caption("Both checking methods receive the same retrieved passages for each chunking strategy.")
    st.download_button("Download metrics", data=report_path.read_bytes(),
                       file_name="paperscope-metrics.json", mime="application/json")
    st.stop()

try:
    scope = open_paperscope()
except Exception as error:
    st.error(f"Could not load the local corpus or models ({type(error).__name__}).")
    st.info("Check that the dataset archive and model folders are present under data/.")
    st.stop()

st.sidebar.header("Search settings")
strategy = st.sidebar.radio("Chunking", list(STRATEGIES), index=1, format_func=STRATEGIES.get)
rerank = st.sidebar.checkbox(
    "Rerank top 20 candidates", value=RERANK_ON,
    help="Reorder vector hits with a local cross-encoder before showing five passages.",
)
api_enabled = bool(os.getenv("PAPERSCOPE_API_KEY"))
checking = page == "Check a statement"
modes = ["DeepSeek API", "Local extractive QA"] if api_enabled else ["Local extractive QA"]
if checking and not api_enabled:
    st.info("Start PaperScope in DeepSeek mode to check statements.")
    st.stop()
mode = "DeepSeek API" if checking else st.sidebar.radio("Answer mode", modes)
if mode == "Local extractive QA":
    st.sidebar.caption("Answers are short excerpts selected by a local model.")
else:
    st.sidebar.caption(f"{os.getenv('PAPERSCOPE_MODEL', DEEPSEEK_MODEL)} receives the input and retrieved excerpts.")
st.sidebar.caption(f"Corpus: {len(scope.papers)} QASPER papers")

paper_id = st.selectbox(
    "Research paper", list(scope.papers),
    format_func=lambda key: scope.papers[key]["title"],
)
with st.form("statement_form" if checking else "question_form"):
    if checking:
        question = st.text_area(
            "Statement", max_chars=400, placeholder="Paste a claim about the selected paper…"
        )
    else:
        question = st.text_input("Question", max_chars=400, placeholder="Ask in English…")
    submitted = st.form_submit_button(
        "Check evidence" if checking else "Find an answer", type="primary"
    )

settings = (paper_id, strategy, rerank, mode, page)
if submitted:
    st.session_state.pop("result", None)
    if not question.strip():
        st.warning("Enter a statement to check." if checking else "Enter a question to search this paper.")
    else:
        with st.spinner("Searching the paper…"):
            try:
                evidence = scope.retrieve(
                    paper_id, question.strip(), strategy, rerank=rerank
                )
                if mode == "DeepSeek API":
                    answer = answer_with_api(
                        question.strip(), evidence, "checked" if checking else "qa"
                    )
                else:
                    answer = scope.answer_locally(question.strip(), evidence)
                st.session_state.result = (settings, question.strip(), answer, evidence)
            except Exception as error:
                st.error(f"The answer could not be generated ({type(error).__name__}).")

result = st.session_state.get("result")
if result and result[0] == settings:
    _, submitted_question, answer, evidence = result
    st.divider()
    left, right = st.columns([1, 1.3], gap="large")
    left.subheader("Verdict" if checking else "Answer")
    left.text(submitted_question)
    cited = {source_id for _, source_id in answer.lines}
    if checking:
        label = answer.verdict.title()
        if answer.verdict == "SUPPORTED":
            left.success(label)
        elif answer.verdict == "CONTRADICTED":
            left.error(label)
        else:
            left.warning("Insufficient evidence")
    if answer.citation_error:
        left.warning("The response was withheld because a citation could not be verified.")
    if cited:
        for index, (claim, source_id) in enumerate(answer.lines):
            left.text(claim)
            source = next(item for item in evidence if item["id"] == source_id)
            left.text(f"{source['section']} · {source_id}")
            if answer.citations:
                left.caption(f"“{answer.citations[index]}”")
    elif not checking and not answer.citation_error:
        left.warning("I couldn't find enough evidence in this paper to answer.")
    left.caption(mode)

    right.subheader("Source passages")
    if not cited:
        right.caption("Retrieved for inspection. The passages did not produce a supported answer.")
    for item in sorted(evidence, key=lambda hit: hit["id"] not in cited):
        used = item["id"] in cited
        label = f"{item['section']} · {item['id']}"
        if used:
            label += " · Cited"
        with right.expander(label, expanded=used):
            scores = f"Cosine similarity {item['similarity']:.3f}"
            if "rerank_score" in item:
                scores += f" · rerank {item['rerank_score']:.3f}"
            st.caption(f"{paper_id} · {scores}")
            st.text(item["text"])
