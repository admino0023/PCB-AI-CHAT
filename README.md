# 🤖 AI-Based PCB Visual Inspection Assistant

A local, offline capstone project that combines **Vision AI + RAG + Report Generation**
to simulate an industrial PCB quality-inspection assistant — built for a 2–3 hour workshop.

## The Problem
A PCB manufacturing company produces thousands of PCBs a day. Manual inspection is
slow, inconsistent, and expensive. This assistant automates the first pass:

1. Look at a PCB image and detect defects (Vision AI)
2. Explain the defect using real reference material (RAG)
3. Produce a structured, saveable inspection report

## Architecture

```
PCB Image
   │
   ▼
Ollama Vision Model (llava / gemma3)
   │
   ▼
Detect Defect ──► Detected Defects text
   │
   ▼
RAG Engine (FAISS + HuggingFace embeddings + Ollama LLM)
   │  queries docs/*.txt (inspection manuals, soldering guides, IPC notes)
   ▼
Repair / Cause / Precautions
   │
   ▼
Final Inspection Report (saved to reports/)
```

Only three AI concepts are used: **Vision, RAG, and Report Generation** — kept
intentionally minimal so the workshop focuses on the pipeline, not framework setup.

## Project Structure

```
PCB_AI_Assistant/
├── images/                     # PCB images to inspect (add your own .jpg/.png)
├── docs/
│   └── pcb_inspection_manual.txt   # sample knowledge base (defects, repair, IPC notes)
├── reports/                    # generated inspection reports land here
├── vision_inspector.py         # Vision layer — talks to Ollama vision model
├── rag_engine.py                # RAG layer — FAISS + HuggingFace + Ollama LLM
├── report_generator.py          # Merges vision + RAG output into a report
├── pipeline.py                  # CLI orchestrator: image in -> report out
├── app.py                       # Streamlit UI
├── requirements.txt
└── README.md
```

## Setup

1. **Install Ollama** (https://ollama.com) and start the server:
   ```bash
   ollama serve
   ```

2. **Pull the two local models you need:**
   ```bash
   ollama pull llava      # vision model — reads PCB images
   ollama pull llama3     # text model — powers the RAG explanations
   ```
   (Any Ollama vision-capable model works — e.g. `gemma3:4b` — just update
   `VISION_MODEL` in `vision_inspector.py` to match.)

3. **Create a virtual environment and install Python dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   ```

4. **Add your data:**
   - Drop PCB images (good and defective) into `images/`.
   - Add more `.txt` reference notes into `docs/` (a starter manual is
     already included). To use real PDFs (datasheets, IPC standards),
     swap the loader in `rag_engine.py` for a PDF loader — see the
     comment in `build_vectorstore()`.

## Usage

**Option A — Command line, one image at a time:**
```bash
python pipeline.py images/pcb_missing_component.jpg
```
This prints the vision result, the RAG repair guidance, and saves a full
report to `reports/`.

**Option B — Streamlit web app:**
```bash
streamlit run app.py
```
Upload a PCB image in the browser, click **Run Inspection**, and download
the generated report.

## Example Output

```
--------------------------------
PCB Inspection Report
--------------------------------
Image: pcb5.jpg
Timestamp: 2026-07-18 10:40:02

Inspection Result:
PCB Status: FAIL
Detected Components: Resistors, Capacitors, IC
Detected Defects: Missing Resistor
Defect Location: Bottom Right
Possible Cause: Component placement issue
Severity: High
Recommendation: Replace resistor
Confidence: Medium

--------------------------------
Repair & Reference Guidance (RAG)
--------------------------------
Cause: Missing component, typically due to a pick-and-place feeder
jam or programming error.
Repair Steps: Manually place and solder the correct resistor per
the BOM and schematic.
Inspection Method: Automated Optical Inspection (AOI) against the
golden board image, or manual visual check.
Precautions: Regularly calibrate feeders and verify the BOM before
production runs.

--------------------------------
Inspection Time: 2.31 seconds
--------------------------------
```

## Workshop Flow (2–3 hours)

| Part | Time | Topic |
|------|------|-------|
| 1 | 20 min | Traditional vs AI visual inspection |
| 2 | 30 min | Run the vision model on sample PCB images |
| 3 | 20 min | Structured defect classification prompt |
| 4 | 20 min | Build the RAG knowledge base from `docs/` |
| 5 | 20 min | Connect vision output → RAG query (one AI calls another) |
| 6 | 20 min | Generate and review the final report |

## Learning Outcomes
- Difference between traditional computer vision and vision-language models
- Running a local multimodal model with Ollama
- Building a simple RAG knowledge base for a domain (PCB repair)
- Chaining model outputs (vision → RAG) into one pipeline
- Producing a structured, presentation-ready inspection report

## Notes & Extensions
- The vector store is cached per process/session — rebuild it if you
  update `docs/`.
- `extract_defect_summary()` in `vision_inspector.py` does simple
  line parsing, not strict JSON — good enough for a workshop; for
  production, validate the model's output against a schema.
- To move this off local Ollama (e.g. for cloud deployment), swap
  `Ollama(...)` for a hosted LLM (Groq, HF Inference API) — vision-capable
  hosted APIs would replace `vision_inspector.py`'s Ollama call similarly.

## License
[Add your license here]
