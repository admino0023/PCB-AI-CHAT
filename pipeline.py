"""
pipeline.py
-----------
Orchestrates the full PCB AI Assistant flow:

    PCB Image -> Vision AI -> Defect -> RAG -> Repair Guide -> Final Report

This is the "one AI calls another AI" step from the workshop —
the vision model's defect line becomes the RAG engine's query,
and both outputs get merged into a single report.

Usage (CLI):
    python pipeline.py images/pcb_missing_component.jpg

Usage (import):
    from pipeline import run_pipeline
    report_text = run_pipeline("images/pcb_missing_component.jpg")
"""

import time
import sys

from vision_inspector import inspect_pcb_image, extract_defect_summary
from rag_engine import query_knowledge_base
from report_generator import generate_report


def run_pipeline(image_path: str) -> str:
    """
    Run the full inspection pipeline for a single PCB image and
    return the final report text.
    """
    start = time.time()

    # 1. Vision: inspect the image
    print(f"[1/3] Running vision inspection on {image_path} ...")
    vision_result = inspect_pcb_image(image_path)

    # 2. RAG: look up repair guidance for whatever defect was found
    defect_query = extract_defect_summary(vision_result)
    print(f"[2/3] Querying knowledge base for: '{defect_query}' ...")
    rag_result = query_knowledge_base(defect_query)

    # 3. Report: merge both into the final structured report
    print("[3/3] Generating report ...")
    duration = time.time() - start
    report_text = generate_report(image_path, vision_result, rag_result, duration)

    return report_text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <path-to-pcb-image>")
        sys.exit(1)

    image_path = sys.argv[1]
    report = run_pipeline(image_path)
    print("\n" + report)
