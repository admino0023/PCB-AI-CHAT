"""
report_generator.py
--------------------
Final stage of the PCB AI Assistant pipeline.

Responsibility:
    Combine the Vision inspection result + the RAG repair explanation
    into one structured, saveable inspection report — matching the
    format used on a real QC floor.
"""

import time
from pathlib import Path
from datetime import datetime

REPORT_TEMPLATE = """\
--------------------------------
PCB Inspection Report
--------------------------------
Image: {image_name}
Timestamp: {timestamp}

Inspection Result:
{vision_result}

--------------------------------
Repair & Reference Guidance (RAG)
--------------------------------
{rag_result}

--------------------------------
Inspection Time: {duration:.2f} seconds
--------------------------------
"""


def generate_report(image_path: str, vision_result: str, rag_result: str,
                     duration: float, output_dir: str = "reports") -> str:
    """
    Assemble the final report text, save it to `reports/`, and return
    the report text (so it can also be shown directly in a UI).

    Args:
        image_path: path to the inspected PCB image (used for the filename/label).
        vision_result: raw text from vision_inspector.inspect_pcb_image().
        rag_result: raw text from rag_engine.query_knowledge_base().
        duration: seconds the full pipeline took (for the report footer).
        output_dir: folder to save the .txt report into.

    Returns:
        The full report as a string.
    """
    image_name = Path(image_path).name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_text = REPORT_TEMPLATE.format(
        image_name=image_name,
        timestamp=timestamp,
        vision_result=vision_result.strip(),
        rag_result=rag_result.strip(),
        duration=duration,
    )

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = Path(image_name).stem
    out_path = out_dir / f"report_{safe_stem}_{int(time.time())}.txt"
    out_path.write_text(report_text, encoding="utf-8")

    return report_text


if __name__ == "__main__":
    # Quick manual test with dummy data
    sample = generate_report(
        image_path="images/pcb5.jpg",
        vision_result="PCB Status: FAIL\nDetected Defects: Missing Resistor\nDefect Location: Bottom Right",
        rag_result="Cause: Component placement error.\nRepair: Solder in replacement resistor.",
        duration=2.3,
    )
    print(sample)
