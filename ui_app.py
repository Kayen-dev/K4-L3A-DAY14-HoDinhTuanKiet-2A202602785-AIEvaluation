"""Streamlit dashboard for the OrbitTech AI Evaluation lab."""

from __future__ import annotations

import html
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent
DATASET_PATH = ROOT / "golden_dataset.json"
ACTUAL_PATH = ROOT / "artifacts" / "actual_answers.json"
BENCHMARK_PATH = ROOT / "artifacts" / "benchmark_results.json"
DIFFICULTIES = ("easy", "medium", "hard", "adversarial")
METRICS = {
    "avg_context_recall": "Context recall",
    "avg_context_precision": "Context precision",
    "avg_faithfulness": "Faithfulness",
    "avg_relevance": "Relevance",
    "avg_completeness": "Completeness",
}

st.set_page_config(page_title="OrbitEval Lab", layout="wide")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def score(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return max(0.0, min(1.0, float(value)))


def tone(value: float) -> str:
    return "good" if value >= 0.8 else "warn" if value >= 0.6 else "bad"


def metric(label: str, value: Any) -> None:
    normalized = score(value)
    if normalized is None:
        st.markdown(
            f'<div class="metric"><div><b>{esc(label)}</b><small>Waiting for benchmark</small></div><strong>—</strong></div>',
            unsafe_allow_html=True,
        )
        return
    state = (
        "Good"
        if normalized >= 0.8
        else "Needs work"
        if normalized >= 0.6
        else "Significant issue"
    )
    st.markdown(
        f"""
        <div class="metric" aria-label="{esc(label)} {normalized:.3f}">
          <div><b>{esc(label)}</b><small>{state}</small></div>
          <div class="track" aria-hidden="true"><i class="{tone(normalized)}" style="width:{normalized * 100:.1f}%"></i></div>
          <strong>{normalized:.3f}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str, detail: str, state: str = "") -> None:
    st.markdown(
        f'<div class="kpi {state}"><span>{esc(label)}</span><strong>{esc(value)}</strong><small>{esc(detail)}</small></div>',
        unsafe_allow_html=True,
    )


def run_python(arguments: list[str], timeout: int = 900) -> tuple[int, str]:
    try:
        process = subprocess.run(
            [sys.executable, *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 124, f"Command timed out after {timeout} seconds."
    output = "\n".join(
        part.strip() for part in (process.stdout, process.stderr) if part.strip()
    )
    return process.returncode, output or "Command completed without output."


def command_result(name: str, result: tuple[int, str]) -> None:
    code, output = result
    if code == 0:
        st.success(f"{name} completed.")
    else:
        st.error(f"{name} failed with exit code {code}.")
    st.code(output, language="text")


def by_id(
    artifact: dict[str, Any] | None, key: str
) -> dict[str, dict[str, Any]]:
    rows = artifact.get(key, []) if artifact else []
    return {
        str(row.get("id")): row
        for row in rows
        if isinstance(row, dict) and row.get("id")
    }


def styles() -> None:
    st.markdown(
        """
        <style>
        :root{--ink:#172033;--muted:#5f6b7d;--line:#d9e0ea;--surface:#fff;--canvas:#f3f6fa;--blue:#2357d9;--red:#b4233a;--green:#18794e;--amber:#b56800;--mono:"Cascadia Code",Consolas,monospace;--sans:"Aptos","Segoe UI",Arial,sans-serif}
        html,body,[class*="css"]{font-family:var(--sans);color:var(--ink)}.stApp{background:var(--canvas)}.block-container{max-width:1440px;padding-top:2rem;padding-bottom:4rem}
        [data-testid="stSidebar"]{background:#101829;border-right:1px solid #26324a}[data-testid="stSidebar"] *{color:#e8eefb}[data-testid="stSidebar"] .stRadio label{min-height:44px;padding:8px 10px;border-radius:8px}[data-testid="stSidebar"] .stRadio label:hover{background:#1b2740}
        h1,h2,h3{letter-spacing:-.03em;color:var(--ink)}h1{font-size:clamp(2.2rem,5vw,4.6rem)!important;line-height:.96!important}code,pre{font-family:var(--mono)}
        .eyebrow,.section-rule{font:700 .74rem var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--blue)}
        .hero{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(280px,.6fr);gap:32px;align-items:end;padding:30px 0 34px;border-bottom:1px solid var(--line);margin-bottom:26px}.hero h1{margin:0}.hero h1 em{color:var(--blue);font-style:normal}.hero p{color:var(--muted);font-size:1.05rem;line-height:1.65;margin:0;border-left:3px solid var(--blue);padding-left:18px}
        .pipeline{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);background:var(--surface);margin:8px 0 26px}.step{min-height:104px;padding:18px 20px;position:relative;border-right:1px solid var(--line)}.step:last-child{border:0}.step:before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:var(--amber)}.step.ready:before{background:var(--green)}.step b{display:block;font:700 .72rem var(--mono);color:var(--muted)}.step strong{display:block;margin:8px 0 4px}.step span{color:var(--muted);font-size:.82rem}
        .kpi{background:var(--surface);border:1px solid var(--line);border-top:3px solid #778398;padding:18px 20px;min-height:138px}.kpi.good{border-top-color:var(--green)}.kpi.warn{border-top-color:var(--amber)}.kpi.bad{border-top-color:var(--red)}.kpi span,.kpi small{display:block;color:var(--muted)}.kpi span{font:700 .7rem var(--mono);letter-spacing:.06em;text-transform:uppercase}.kpi strong{display:block;font-size:2rem;line-height:1;margin:14px 0 10px}
        .section-rule{display:flex;align-items:center;gap:14px;color:var(--muted);margin:28px 0 14px}.section-rule:after{content:"";height:1px;background:var(--line);flex:1}
        .metric{display:grid;grid-template-columns:minmax(150px,1fr) minmax(120px,2fr) 58px;align-items:center;gap:16px;background:var(--surface);border-bottom:1px solid var(--line);padding:15px 4px}.metric b,.metric small{display:block}.metric small{color:var(--muted);font-size:.74rem;margin-top:2px}.metric strong{font-family:var(--mono);text-align:right}.track{height:8px;background:#e7ebf1;border-radius:99px;overflow:hidden}.track i{display:block;height:100%;border-radius:inherit}.track .good{background:var(--green)}.track .warn{background:var(--amber)}.track .bad{background:var(--red)}
        .note{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--blue);padding:22px 24px;margin:12px 0 22px}.note strong{display:block;margin-bottom:6px}.note p{color:var(--muted);margin:0;line-height:1.55}
        .tags{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 18px}.tag{display:inline-flex;align-items:center;min-height:28px;padding:4px 9px;border:1px solid var(--line);background:#f8fafc;color:#3d4a60;font:700 .7rem var(--mono);text-transform:uppercase}.tag.pass{color:var(--green);border-color:#9ac9b3;background:#effaf4}.tag.fail{color:var(--red);border-color:#e4aab5;background:#fff2f4}
        .trace{border-left:2px solid #9db2e9;padding:2px 0 2px 16px;margin:12px 0}.trace b{color:var(--blue);font:700 .72rem var(--mono)}.trace p{color:#354157;line-height:1.6;margin:5px 0 0}
        .stButton>button,.stDownloadButton>button{min-height:44px;border-radius:6px;border:1px solid #9eabba;font-weight:650}.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--blue);color:var(--blue)}.stButton>button:focus-visible,.stDownloadButton>button:focus-visible{outline:3px solid #8fb0ff;outline-offset:2px}
        @media(max-width:760px){.block-container{padding-top:1rem}.hero{grid-template-columns:1fr;gap:18px}.pipeline{grid-template-columns:1fr 1fr}.step:nth-child(2){border-right:0}.metric{grid-template-columns:1fr 58px}.track{grid-column:1/-1;grid-row:2}}
        @media(prefers-reduced-motion:reduce){*,*:before,*:after{transition:none!important;scroll-behavior:auto!important}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar(
    dataset: dict[str, Any] | None, benchmark: dict[str, Any] | None
) -> str:
    with st.sidebar:
        st.markdown(
            '<div style="padding:12px 2px 18px"><div style="font:700 .7rem var(--mono);letter-spacing:.12em;color:#8da8e8">ORBITTECH / LAB 14</div><div style="font-size:1.45rem;font-weight:760;margin-top:6px">OrbitEval</div></div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Workspace",
            ("Overview", "Golden dataset", "Benchmark", "Failures", "Run lab"),
            label_visibility="collapsed",
        )
        st.divider()
        st.caption(
            f"Dataset · {len(dataset.get('qa_pairs', [])) if dataset else 0}/20 records"
        )
        st.caption(
            f"Benchmark · {len(benchmark.get('results', [])) if benchmark else 0}/20 results"
        )
        st.caption("Core tests · 42 expected")
        st.divider()
        st.caption("Local-first UI. Credentials stay in the ignored .env file.")
    return page


def pipeline(
    dataset: dict[str, Any] | None,
    actual: dict[str, Any] | None,
    benchmark: dict[str, Any] | None,
) -> None:
    dataset_ok = bool(dataset and len(dataset.get("qa_pairs", [])) == 20)
    actual_count = len(actual.get("answers", [])) if actual else 0
    result_count = len(benchmark.get("results", [])) if benchmark else 0
    items = (
        ("01", "Golden dataset", "20 QA ready" if dataset_ok else "Needs attention", dataset_ok),
        ("02", "Retrieval trace", f"{actual_count}/20 answers", actual_count == 20),
        ("03", "Evaluation", f"{result_count}/20 scored", result_count == 20),
        ("04", "Failure analysis", "Ready" if benchmark else "Waiting", bool(benchmark)),
    )
    content = "".join(
        f'<div class="step {"ready" if ready else ""}"><b>{number}</b><strong>{esc(title)}</strong><span>{esc(detail)}</span></div>'
        for number, title, detail, ready in items
    )
    st.markdown(f'<div class="pipeline">{content}</div>', unsafe_allow_html=True)


def overview(
    dataset: dict[str, Any] | None,
    actual: dict[str, Any] | None,
    benchmark: dict[str, Any] | None,
) -> None:
    st.markdown(
        '<div class="hero"><div><div class="eyebrow">AI evaluation workbench</div><h1>Measure the answer.<br><em>Inspect the evidence.</em></h1></div><p>A local control room for the OrbitTech RAG benchmark—from curated questions to deployment gates.</p></div>',
        unsafe_allow_html=True,
    )
    pipeline(dataset, actual, benchmark)
    pairs = dataset.get("qa_pairs", []) if dataset else []
    summary = benchmark.get("summary", {}) if benchmark else {}
    coverage = {
        context.get("source_doc")
        for pair in pairs
        if isinstance(pair, dict)
        for context in pair.get("contexts", [])
        if isinstance(context, dict)
    }
    columns = st.columns(4)
    with columns[0]:
        kpi("Golden records", str(len(pairs)), "Target: 20", "good" if len(pairs) == 20 else "warn")
    with columns[1]:
        kpi("Document coverage", f"{len(coverage)}/10", "Source provenance", "good" if len(coverage) == 10 else "warn")
    with columns[2]:
        if summary:
            value = float(summary.get("pass_rate", 0.0))
            kpi("Pass rate", f"{value:.0%}", f"{summary.get('passed', 0)}/{summary.get('total', 0)} cases", tone(value))
        else:
            kpi("Pass rate", "Pending", "Run the benchmark", "warn")
    with columns[3]:
        failures = sum(summary.get("failure_types", {}).values()) if summary else 0
        kpi("Failures", str(failures) if summary else "Pending", "Cases below threshold", "bad" if failures else "")
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown('<div class="section-rule">Metric health</div>', unsafe_allow_html=True)
        for key, label in METRICS.items():
            metric(label, summary.get(key) if summary else None)
    with right:
        st.markdown('<div class="section-rule">Dataset composition</div>', unsafe_allow_html=True)
        counts = Counter(
            str(pair.get("difficulty", "unknown"))
            for pair in pairs
            if isinstance(pair, dict)
        )
        st.bar_chart(
            {level.title(): counts.get(level, 0) for level in DIFFICULTIES},
            horizontal=True,
            color="#2357d9",
        )
        st.caption("Target: 5 Easy · 7 Medium · 5 Hard · 3 Adversarial")


def dataset_page(
    dataset: dict[str, Any] | None, benchmark: dict[str, Any] | None
) -> None:
    st.title("Golden dataset")
    st.caption("Questions, expected answers, evidence provenance and outcomes.")
    if not dataset:
        st.error("golden_dataset.json could not be loaded.")
        return
    pairs = [pair for pair in dataset.get("qa_pairs", []) if isinstance(pair, dict)]
    results = by_id(benchmark, "results")
    first, second = st.columns([1, 2])
    with first:
        level = st.selectbox(
            "Difficulty",
            ("all", *DIFFICULTIES),
            format_func=lambda value: value.title(),
        )
    filtered = [
        pair
        for pair in pairs
        if level == "all" or pair.get("difficulty") == level
    ]
    with second:
        selected_id = st.selectbox(
            "QA record",
            [str(pair.get("id")) for pair in filtered],
            format_func=lambda item: next(
                f"{item} · {pair.get('question', '')}"
                for pair in filtered
                if str(pair.get("id")) == item
            ),
        )
    pair = next(pair for pair in filtered if str(pair.get("id")) == selected_id)
    result = results.get(selected_id)
    tags = [
        f'<span class="tag">{esc(selected_id)}</span>',
        f'<span class="tag">{esc(pair.get("difficulty", ""))}</span>',
    ]
    if pair.get("attack_type"):
        tags.append(f'<span class="tag">{esc(pair["attack_type"])}</span>')
    if result:
        passed = bool(result.get("passed"))
        tags.append(
            f'<span class="tag {"pass" if passed else "fail"}">'
            f'{"passed" if passed else esc(result.get("failure_type") or "failed")}</span>'
        )
    st.markdown(f'<div class="tags">{"".join(tags)}</div>', unsafe_allow_html=True)
    st.subheader(str(pair.get("question", "")))
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### Expected answer")
        st.write(pair.get("expected_answer", ""))
    with right:
        st.markdown("#### Actual answer")
        if result:
            st.write(result.get("actual_answer", ""))
        else:
            st.info("Available after answer generation and evaluation.")
    st.markdown('<div class="section-rule">Gold evidence</div>', unsafe_allow_html=True)
    for index, context in enumerate(pair.get("contexts", []), start=1):
        if isinstance(context, dict):
            st.markdown(
                f'<div class="trace"><b>CONTEXT {index} · {esc(context.get("source_doc", ""))}</b><p>{esc(context.get("text", ""))}</p></div>',
                unsafe_allow_html=True,
            )
    if result:
        st.markdown('<div class="section-rule">Scores</div>', unsafe_allow_html=True)
        for key, label in (
            ("context_recall", "Context recall"),
            ("context_precision", "Context precision"),
            ("faithfulness", "Faithfulness"),
            ("relevance", "Relevance"),
            ("completeness", "Completeness"),
            ("overall", "Overall"),
        ):
            metric(label, result.get(key))


def benchmark_page(benchmark: dict[str, Any] | None) -> None:
    st.title("Benchmark")
    st.caption("Answer-side and retrieval-side metrics for the saved run.")
    if not benchmark:
        st.markdown(
            '<div class="note"><strong>No benchmark artifact yet</strong><p>Use Run lab to generate answers and evaluate them. This view updates from artifacts/benchmark_results.json.</p></div>',
            unsafe_allow_html=True,
        )
        return
    summary = benchmark.get("summary", {})
    columns = st.columns(3)
    value = float(summary.get("pass_rate", 0.0))
    with columns[0]:
        kpi("Pass rate", f"{value:.1%}", f"{summary.get('passed', 0)} passed", tone(value))
    with columns[1]:
        kpi("Evaluated", str(summary.get("total", 0)), "Saved answer traces")
    with columns[2]:
        failures = int(summary.get("total", 0)) - int(summary.get("passed", 0))
        kpi("Failed", str(failures), "Inspect before deploy", "bad" if failures else "good")
    st.markdown('<div class="section-rule">Aggregate metrics</div>', unsafe_allow_html=True)
    for key, label in METRICS.items():
        metric(label, summary.get(key))
    table = []
    for row in benchmark.get("results", []):
        if isinstance(row, dict):
            table.append(
                {
                    "ID": row.get("id"),
                    "Difficulty": row.get("difficulty"),
                    "Overall": round(float(row.get("overall", 0)), 3),
                    "Faithfulness": round(float(row.get("faithfulness", 0)), 3),
                    "Relevance": round(float(row.get("relevance", 0)), 3),
                    "Completeness": round(float(row.get("completeness", 0)), 3),
                    "Passed": bool(row.get("passed")),
                    "Failure": row.get("failure_type") or "—",
                }
            )
    st.markdown('<div class="section-rule">Case results</div>', unsafe_allow_html=True)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "Download benchmark JSON",
        json.dumps(benchmark, ensure_ascii=False, indent=2),
        "benchmark_results.json",
        "application/json",
    )


def failures_page(
    benchmark: dict[str, Any] | None, actual: dict[str, Any] | None
) -> None:
    st.title("Failure analysis")
    st.caption("Prioritize low-scoring cases and inspect their retrieval trace.")
    if not benchmark:
        st.info("Failure analysis becomes available after a benchmark run.")
        return
    rows = [
        row
        for row in benchmark.get("results", [])
        if isinstance(row, dict) and not row.get("passed")
    ]
    if not rows:
        st.success("No failing cases in the current benchmark.")
        return
    rows.sort(key=lambda row: float(row.get("overall", 0)))
    st.bar_chart(
        dict(Counter(str(row.get("failure_type") or "unknown") for row in rows)),
        horizontal=True,
        color="#b4233a",
    )
    selected_id = st.selectbox(
        "Failure case",
        [str(row.get("id")) for row in rows],
        format_func=lambda item: next(
            f"{item} · {row.get('failure_type') or 'unknown'} · {float(row.get('overall', 0)):.3f}"
            for row in rows
            if str(row.get("id")) == item
        ),
    )
    row = next(row for row in rows if str(row.get("id")) == selected_id)
    trace = by_id(actual, "answers").get(selected_id, {})
    st.subheader(str(row.get("question", "")))
    st.markdown(
        f'<div class="tags"><span class="tag fail">{esc(row.get("failure_type") or "failed")}</span><span class="tag">overall {float(row.get("overall", 0)):.3f}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("#### Actual answer")
    st.write(row.get("actual_answer", ""))
    st.markdown('<div class="section-rule">Retrieved chunks</div>', unsafe_allow_html=True)
    chunks = trace.get("retrieved_contexts", []) if isinstance(trace, dict) else []
    if not chunks:
        st.warning("No retrieval trace is available for this case.")
    for index, chunk in enumerate(chunks, start=1):
        if isinstance(chunk, dict):
            st.markdown(
                f'<div class="trace"><b>RANK {index} · {esc(chunk.get("source_doc", ""))} · SCORE {esc(chunk.get("score", "n/a"))}</b><p>{esc(chunk.get("text", ""))}</p></div>',
                unsafe_allow_html=True,
            )
    st.markdown('<div class="section-rule">Suggested actions</div>', unsafe_allow_html=True)
    analysis = benchmark.get("failure_analysis", {})
    suggestions = analysis.get("suggestions", []) if isinstance(analysis, dict) else []
    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")


def run_page() -> None:
    st.title("Run lab")
    st.caption("Execute fixed project commands and inspect their output.")
    st.markdown(
        '<div class="note"><strong>Execution order</strong><p>Validate dataset and tests first. Generation reads credentials from the ignored .env file; credential values are never displayed.</p></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown("### Local checks")
        if st.button("Validate golden dataset", use_container_width=True):
            with st.spinner("Validating schema and provenance…"):
                command_result(
                    "Dataset validation",
                    run_python(["validate_golden_dataset.py"], 60),
                )
        if st.button("Run 42 tests", use_container_width=True):
            with st.spinner("Running evaluation-core tests…"):
                command_result(
                    "Test suite",
                    run_python(["-m", "pytest", "tests/", "-q"], 120),
                )
    with right:
        st.markdown("### RAG benchmark")
        if st.button(
            "Generate 20 actual answers",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("Calling the configured gateway for 20 questions…"):
                command_result(
                    "Answer generation",
                    run_python(["domain_assistant.py"], 1200),
                )
        if st.button("Evaluate saved answers", use_container_width=True):
            with st.spinner("Calculating answer and retrieval metrics…"):
                command_result(
                    "Benchmark evaluation",
                    run_python(["evaluate_answers.py"], 120),
                )
    st.markdown('<div class="section-rule">Artifact status</div>', unsafe_allow_html=True)
    columns = st.columns(2)
    for column, path, detail in (
        (columns[0], ACTUAL_PATH, "Answers and retrieved chunks"),
        (columns[1], BENCHMARK_PATH, "Metrics and failure analysis"),
    ):
        with column:
            kpi(
                path.name,
                "Ready" if path.is_file() else "Missing",
                detail,
                "good" if path.is_file() else "warn",
            )
    if st.button("Refresh dashboard data", use_container_width=True):
        st.rerun()


def main() -> None:
    styles()
    dataset = read_json(DATASET_PATH)
    actual = read_json(ACTUAL_PATH)
    benchmark = read_json(BENCHMARK_PATH)
    page = sidebar(dataset, benchmark)
    if page == "Overview":
        overview(dataset, actual, benchmark)
    elif page == "Golden dataset":
        dataset_page(dataset, benchmark)
    elif page == "Benchmark":
        benchmark_page(benchmark)
    elif page == "Failures":
        failures_page(benchmark, actual)
    else:
        run_page()


if __name__ == "__main__":
    main()
