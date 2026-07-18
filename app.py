"""
app.py
------
Streamlit front-end for the PCB AI Assistant.

Flow:
    1. User uploads a PCB image.
    2. Vision model inspects it.
    3. Detected defect is used to query the RAG knowledge base.
    4. Both results are merged into a downloadable inspection report.

Run:
    streamlit run app.py

Requirements:
    - Ollama running locally (`ollama serve`)
    - A vision model pulled (e.g. `ollama pull llava`)
    - A text model pulled (e.g. `ollama pull llama3`)
    - docs/*.txt populated with your PCB / soldering / IPC reference notes
"""

import time
from pathlib import Path

import streamlit as st

from vision_inspector import inspect_pcb_image, extract_defect_summary
from rag_engine import get_or_build_vectorstore, query_knowledge_base
from report_generator import generate_report

st.set_page_config(page_title="PCB AI Inspection Assistant", page_icon="🔧", layout="centered")

st.title("🔧 AI-Based PCB Visual Inspection Assistant")
st.caption("Vision AI + RAG + Automated Reporting — fully local via Ollama")


# ---- Build (and cache) the knowledge base once per session ----
@st.cache_resource
def load_knowledge_base():
    return get_or_build_vectorstore()


with st.spinner("Loading knowledge base (docs/*.txt) ..."):
    try:
        load_knowledge_base()
        st.success("Knowledge base ready.")
    except FileNotFoundError as e:
        st.warning(str(e))


uploaded_file = st.file_uploader("Upload a PCB image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the upload to disk so vision_inspector can read it by path
    temp_path = Path("images") / uploaded_file.name
    temp_path.parent.mkdir(exist_ok=True)
    temp_path.write_bytes(uploaded_file.getbuffer())

    st.image(str(temp_path), caption="Uploaded PCB", use_container_width=True)

    if st.button("Run Inspection"):
        start = time.time()

        with st.spinner("Running vision inspection..."):
            vision_result = inspect_pcb_image(str(temp_path))
        st.subheader("🔍 Vision Inspection Result")
        st.text(vision_result)

        defect_query = extract_defect_summary(vision_result)

        with st.spinner(f"Retrieving repair guidance for: {defect_query} ..."):
            rag_result = query_knowledge_base(defect_query)
        st.subheader("📚 Repair & Reference Guidance")
        st.text(rag_result)

        duration = time.time() - start
        report_text = generate_report(str(temp_path), vision_result, rag_result, duration)

        st.subheader("📄 Final Inspection Report")
        st.text(report_text)

        st.download_button(
            "Download Report",
            data=report_text,
            file_name=f"report_{temp_path.stem}.txt",
            mime="text/plain",
        )
else:
    st.info("Upload a PCB image to begin.")
