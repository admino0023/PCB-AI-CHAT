# # 🤖 AI-Based PCB Visual Inspection Assistant

An AI-powered PCB inspection system that automates defect detection using Vision AI, retrieves repair guidance through Retrieval-Augmented Generation (RAG), and generates detailed inspection reports.

---

## 📌 Overview

Manual PCB inspection is time-consuming and prone to human error. This project provides an intelligent inspection assistant that:

- Detects PCB defects using a Vision Language Model
- Retrieves relevant repair information from a PCB knowledge base
- Generates a structured inspection report
- Provides a simple Streamlit web interface

The project runs completely offline using **Ollama**, making it suitable for laboratories, research, and industrial demonstrations.

---

## 🚀 Features

- 🔍 AI-based PCB defect detection
- 📚 RAG-powered repair recommendations
- 📄 Automatic inspection report generation
- 💻 Streamlit Web Application
- ⚡ Local execution using Ollama
- 🧠 FAISS vector database for fast document retrieval

---

## 🏗️ Project Architecture

```
PCB Image
     │
     ▼
Vision AI (Ollama)
     │
     ▼
Defect Detection
     │
     ▼
RAG Engine
(FAISS + LangChain + Ollama)
     │
     ▼
Repair Guidance
     │
     ▼
Inspection Report
```

---

## 📁 Project Structure

```
PCB_AI_Assistant/
│
├── app.py                     # Streamlit application
├── pipeline.py                # Complete inspection pipeline
├── vision_inspector.py        # Vision AI module
├── rag_engine.py              # RAG implementation
├── report_generator.py        # Report generation
├── docs/
│   └── pcb_inspection_manual.txt
├── images/
├── reports/
├── requirements.txt
└── README.md
```

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Ollama
- LangChain
- FAISS
- HuggingFace Embeddings
- LLaVA / Gemma Vision Model
- Llama 3

---

## 📋 Requirements

- Python 3.10+
- Ollama
- Streamlit
- LangChain
- FAISS
- HuggingFace Transformers

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

### 1. Install Ollama

Start Ollama server:

```bash
ollama serve
```

### 2. Download Models

```bash
ollama pull llava
ollama pull llama3
```

You can also use other vision models supported by Ollama.

---

## ▶️ Running the Project

### Command Line

```bash
python pipeline.py images/sample.jpg
```

### Streamlit UI

```bash
streamlit run app.py
```

Open the browser, upload a PCB image, and click **Run Inspection**.

---

## 🔄 Workflow

1. Upload PCB image
2. Vision AI identifies defects
3. Defect summary is sent to the RAG engine
4. Knowledge base retrieves repair information
5. Final inspection report is generated
6. Report can be downloaded

---

## 📄 Sample Report

```
PCB Status: FAIL

Detected Defects:
- Missing Resistor

Repair Guidance:
- Replace the missing resistor
- Verify solder joints
- Perform AOI inspection

Inspection Time:
2.4 seconds
```

---

## 📚 Knowledge Base

The RAG engine uses documents stored inside:

```
docs/
```

You can add:

- PCB inspection manuals
- IPC standards
- Datasheets
- Repair guides
- Manufacturing SOPs

---

## 🎯 Applications

- PCB Manufacturing
- Quality Control
- Electronics Production
- Educational Demonstrations
- AI Research
- Industrial Automation

---

## 🔮 Future Improvements

- YOLO-based defect localization
- Multi-defect detection
- PDF knowledge ingestion
- OCR for PCB labels
- Database integration
- Real-time camera support
- Dashboard analytics

---

## 👨‍💻 Author

**Aditya Jadhav**

Electronics Engineering Student

---

## 📜 License

This project is developed for educational and research purposes.