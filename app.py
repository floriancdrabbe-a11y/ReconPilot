import json
import tempfile
from pathlib import Path

import streamlit as st

from reconpilot_team_baseline import (
    DEFAULT_OLLAMA_URL,
    analyse_finding,
    build_guided_result,
    get_open_ports,
    parse_nmap_xml,
)

st.set_page_config(
    page_title="ReconPilot",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 15% 0%,
                rgba(0, 122, 255, 0.12),
                transparent 28%
            ),
            #07111f;
    }

    [data-testid="stSidebar"] {
        background: #0a1626;
        border-right: 1px solid #1d3652;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1500px;
    }

    .rp-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
        color: #f4f8ff;
    }

    .rp-title span {
        color: #3ba7ff;
    }

    .rp-subtitle {
        font-size: 1.05rem;
        color: #9ab0c9;
        margin-top: 0.2rem;
        margin-bottom: 1.8rem;
    }

    .rp-tag {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        margin-right: 0.35rem;
        border-radius: 999px;
        border: 1px solid #26537d;
        background: #10263d;
        color: #9fd2ff;
        font-size: 0.78rem;
    }

    .rp-warning {
        border: 1px solid #c84b55;
        background: rgba(126, 28, 36, 0.20);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-top: 0.8rem;
        margin-bottom: 1rem;
        color: #ffb2b8;
        font-weight: 600;
    }

    .rp-section {
        font-size: 1.35rem;
        font-weight: 700;
        color: #edf6ff;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
    }

    div[data-testid="stMetric"] {
        background: #0d1c2e;
        border: 1px solid #1d3652;
        border-radius: 12px;
        padding: 0.8rem 1rem;
    }

    div[data-testid="stExpander"] {
        background: #0c1929;
        border: 1px solid #1b3551;
        border-radius: 10px;
    }

    div[data-testid="stFileUploader"] {
        background: #0c1929;
        border-radius: 10px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        min-height: 2.8rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "reconpilot_results" not in st.session_state:
    st.session_state.reconpilot_results = None
if "reconpilot_failures" not in st.session_state:
    st.session_state.reconpilot_failures = []
if "scan_name" not in st.session_state:
    st.session_state.scan_name = None
if "selected_model_used" not in st.session_state:
    st.session_state.selected_model_used = None

st.markdown(
    """
    <div class="rp-title">Recon<span>Pilot</span></div>
    <div class="rp-subtitle">AI-Assisted Reconnaissance Guidance</div>
    <span class="rp-tag">Local AI</span>
    <span class="rp-tag">Evidence First</span>
    <span class="rp-tag">Human Controlled</span>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ReconPilot")
    st.caption(
        "Turn authorised Nmap evidence into structured, guided next steps."
    )
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Nmap XML",
        type=["xml"],
        help="Upload an XML file produced by Nmap using -oX.",
    )

    selected_model = st.selectbox(
        "AI model",
        ["qwen2.5:3b", "llama3.2:3b"],
        index=0,
    )

    st.caption(
        "Qwen2.5 3B is currently the preferred model based on the team benchmark."
    )

    st.divider()

    analyse_button = st.button(
        "Analyse Scan",
        type="primary",
        disabled=uploaded_file is None,
    )

    st.divider()
    st.markdown("### Safety boundary")
    st.caption(
        "ReconPilot recommends and explains. It does not automatically authenticate, exploit or modify a target."
    )
    st.caption(
        "Human approval is required before active testing."
    )

if analyse_button:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".xml",
            delete=False,
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        scan_data = parse_nmap_xml(temp_path)
        open_ports = get_open_ports(scan_data)

        if not open_ports:
            st.error("No open ports were found in this scan.")
            st.stop()

        results = []
        failures = []

        progress = st.progress(0, text="Preparing analysis...")
        status_box = st.empty()
        total = len(open_ports)

        for index, evidence in enumerate(open_ports, start=1):
            status_box.info(
                f"Analysing {index}/{total}: "
                f"{evidence['service']} on port {evidence['port']}"
            )

            llm_result = analyse_finding(
                evidence,
                selected_model,
                DEFAULT_OLLAMA_URL,
            )

            if llm_result.get("status") == "pass":
                guided_result = build_guided_result(
                    evidence,
                    llm_result,
                )
                results.append(guided_result)
            else:
                failures.append(
                    {
                        "evidence": evidence,
                        "result": llm_result,
                    }
                )

            progress.progress(
                index / total,
                text=f"Processed {index}/{total} services",
            )

        results.sort(
            key=lambda item: item["priority_score"],
            reverse=True,
        )

        st.session_state.reconpilot_results = results
        st.session_state.reconpilot_failures = failures
        st.session_state.scan_name = uploaded_file.name
        st.session_state.selected_model_used = selected_model

        status_box.success("ReconPilot analysis complete.")
        progress.empty()

    except Exception as error:
        st.error(f"Analysis failed: {error}")

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass

if st.session_state.reconpilot_results is None:
    st.markdown(
        '<div class="rp-section">Reconnaissance workflow</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown("### 1. Upload")
            st.write("Provide Nmap XML evidence from an authorised scan.")

    with col2:
        with st.container(border=True):
            st.markdown("### 2. Structure")
            st.write(
                "Python extracts ports, services, products and versions."
            )

    with col3:
        with st.container(border=True):
            st.markdown("### 3. Analyse")
            st.write(
                "The local LLM chooses only from context-approved actions."
            )

    with col4:
        with st.container(border=True):
            st.markdown("### 4. Review")
            st.write(
                "ReconPilot explains the next step while keeping a human in control."
            )

    st.info(
        "Upload an authorised Nmap XML file from the sidebar to begin."
    )
    st.stop()

results = st.session_state.reconpilot_results
failures = st.session_state.reconpilot_failures

st.markdown(
    '<div class="rp-section">Scan overview</div>',
    unsafe_allow_html=True,
)

targets = sorted({item["target"] for item in results})

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric(
        "Target",
        targets[0] if len(targets) == 1 else f"{len(targets)} targets",
    )

with metric2:
    st.metric("Services analysed", len(results))

with metric3:
    st.metric("Validated", len(results))

with metric4:
    st.metric("Rejected / failed", len(failures))

st.caption(
    f"Source: {st.session_state.scan_name} "
    f"• Model: {st.session_state.selected_model_used}"
)

st.markdown(
    """
    <div class="rp-warning">
        ⚠ Human review required before any active
        vulnerability validation, authentication attempt
        or exploitation step.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="rp-section">Suggested investigation order</div>',
    unsafe_allow_html=True,
)

for index, item in enumerate(results, start=1):
    col_a, col_b, col_c, col_d = st.columns([0.6, 1.2, 2.2, 6])

    with col_a:
        st.markdown(f"**{index}**")

    with col_b:
        st.markdown(f"**{item['port']}**")

    with col_c:
        st.write(item["service"].upper())

    with col_d:
        st.write(
            f"{item['workflow_priority']} — "
            f"{item['recommended_next_step']}"
        )

st.caption(
    "This ordering is workflow guidance only. It is not a vulnerability severity rating."
)

st.markdown(
    '<div class="rp-section">Recommendation details</div>',
    unsafe_allow_html=True,
)

for index, item in enumerate(results, start=1):
    title = (
        f"{index}. {item['service'].upper()} "
        f"• Port {item['port']} "
        f"• {item['workflow_priority']}"
    )

    with st.expander(title, expanded=(index == 1)):
        top1, top2, top3 = st.columns(3)

        with top1:
            st.metric("Service", item["service"])

        with top2:
            st.metric("Product", item["product"])

        with top3:
            st.metric(
                "Confidence",
                item["confidence"].capitalize(),
            )

        tab1, tab2, tab3 = st.tabs(
            ["Guidance", "Evidence", "Safety"]
        )

        with tab1:
            st.markdown("#### Finding")
            st.write(item["finding"])

            st.markdown("#### What this means")
            st.write(item["what_this_means"])

            st.markdown("#### Why it matters")
            st.write(item["why_it_matters"])

            st.markdown("#### Recommended next step")
            st.info(item["recommended_next_step"])

            st.markdown("#### Why this step")
            st.write(item["why_this_step"])

            st.markdown("#### What to do next")
            st.write(item["what_to_do_next"])

            st.markdown("#### What to look for")
            st.write(item["what_to_look_for"])

            st.markdown("#### Why this helps")
            st.write(item["why_this_helps"])

            st.markdown("#### What to record")
            st.write(item["what_to_record"])

        with tab2:
            evidence = {
                "target": item["target"],
                "port": item["port"],
                "protocol": item["protocol"],
                "service": item["service"],
                "product": item["product"],
                "version": item["version"],
                "banner": item["banner"],
            }

            st.json(evidence)

            st.markdown("#### Approved action set")
            st.code(
                "\n".join(item["allowed_actions"]),
                language="text",
            )

        with tab3:
            st.warning(item["stop_condition"])
            st.write(
                "**Validation:** "
                f"{item['validation']}"
            )
            st.write(
                "**Risk assessment:** "
                f"{item['risk']}"
            )
            st.caption(
                "Target-controlled scan data is treated as "
                "untrusted evidence. The model cannot select "
                "actions outside the Python-controlled allow-list."
            )

st.markdown(
    '<div class="rp-section">Export results</div>',
    unsafe_allow_html=True,
)

report_data = {
    "project": "ReconPilot",
    "baseline": "team-integrated",
    "model": st.session_state.selected_model_used,
    "source": st.session_state.scan_name,
    "validated_results": len(results),
    "failed_or_rejected": len(failures),
    "results": results,
    "failures": failures,
}

json_report = json.dumps(report_data, indent=2)

text_lines = [
    "RECONPILOT GUIDED RECONNAISSANCE REPORT",
    "=" * 60,
    "",
    f"Source: {st.session_state.scan_name}",
    f"Model: {st.session_state.selected_model_used}",
    f"Services analysed: {len(results)}",
    "",
]

for index, item in enumerate(results, start=1):
    text_lines.extend(
        [
            "-" * 60,
            f"{index}. {item['service'].upper()} - Port {item['port']}",
            "-" * 60,
            "",
            f"Finding: {item['finding']}",
            "",
            (
                "Recommended next step: "
                f"{item['recommended_next_step']}"
            ),
            "",
            (
                "What to do next: "
                f"{item['what_to_do_next']}"
            ),
            "",
            (
                "What to look for: "
                f"{item['what_to_look_for']}"
            ),
            "",
            (
                "What to record: "
                f"{item['what_to_record']}"
            ),
            "",
            (
                "Stop / approval condition: "
                f"{item['stop_condition']}"
            ),
            "",
        ]
    )

text_report = "\n".join(text_lines)

download1, download2 = st.columns(2)

with download1:
    st.download_button(
        "Download JSON report",
        data=json_report,
        file_name="reconpilot_report.json",
        mime="application/json",
        use_container_width=True,
    )

with download2:
    st.download_button(
        "Download text report",
        data=text_report,
        file_name="reconpilot_report.txt",
        mime="text/plain",
        use_container_width=True,
    )