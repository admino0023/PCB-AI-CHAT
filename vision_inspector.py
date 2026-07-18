"""
vision_inspector.py
--------------------
Vision layer of the PCB AI Assistant pipeline.

Responsibility:
    Send a PCB image to a locally running Ollama vision model
    (e.g. `gemma3` with vision support, or `llava`) and get back a
    structured defect assessment as text.

Why Ollama:
    Runs fully offline/local — no API key, no cloud cost, good fit
    for a classroom/workshop environment. Requires the Ollama app
    to be installed and running (`ollama serve`) with a vision-capable
    model pulled, e.g.:
        ollama pull llava
        ollama pull gemma3:4b   (gemma3 4b+ supports vision)

Usage:
    from vision_inspector import inspect_pcb_image

    result = inspect_pcb_image("images/pcb_missing_component.jpg")
    print(result)
"""

import base64
import json
import requests
from pathlib import Path

# ---- Config ----
OLLAMA_URL = "http://localhost:11434/api/generate"
VISION_MODEL = "llava"  # swap to "gemma3:4b" or another local vision model you've pulled

# The exact inspection prompt from the workshop spec.
# Keeping this centralized means grading/repair logic downstream
# can rely on a stable output shape.
INSPECTION_PROMPT = """You are an IPC Certified PCB Quality Inspector.

Analyze the uploaded PCB image.

Your task is to inspect the PCB for manufacturing defects.

Return the result in this format.

PCB Status:
PASS or FAIL

Detected Components:

Detected Defects:

Defect Location:

Possible Cause:

Severity:

Recommendation:

Confidence (Low/Medium/High):

Do not guess.
If uncertain, clearly mention that manual inspection is recommended.
"""


def _image_to_base64(image_path: str) -> str:
    """Read an image file from disk and return its base64-encoded string."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def inspect_pcb_image(image_path: str, model: str = VISION_MODEL, timeout: int = 120) -> str:
    """
    Send a PCB image to the local Ollama vision model and return its
    structured inspection text.

    Args:
        image_path: path to a .jpg/.png PCB image.
        model: Ollama vision model name (must already be pulled locally).
        timeout: request timeout in seconds (vision inference can be slow on CPU).

    Returns:
        Raw text response from the model, following INSPECTION_PROMPT's format.

    Raises:
        FileNotFoundError: if the image doesn't exist.
        requests.exceptions.RequestException: if Ollama isn't running / reachable.
    """
    image_b64 = _image_to_base64(image_path)

    payload = {
        "model": model,
        "prompt": INSPECTION_PROMPT,
        "images": [image_b64],
        "stream": False,
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def extract_defect_summary(inspection_text: str) -> str:
    """
    Pull just the 'Detected Defects' line out of the full inspection
    text, so it can be fed as a short query into the RAG engine.

    This is a simple line-based parser (not a strict JSON schema) because
    local vision models don't reliably emit clean JSON. Good enough for
    a workshop; swap for a JSON-mode / regex-validated parser in production.
    """
    for line in inspection_text.splitlines():
        if line.lower().startswith("detected defects"):
            # e.g. "Detected Defects: Missing Resistor" -> "Missing Resistor"
            return line.split(":", 1)[-1].strip() or "No defect text found"
    return "No defect line found — inspect manually."


if __name__ == "__main__":
    # Quick manual test:
    #   python vision_inspector.py images/sample_pcb.jpg
    import sys

    img = sys.argv[1] if len(sys.argv) > 1 else "images/sample_pcb.jpg"
    print(f"Inspecting: {img}\n")
    try:
        text = inspect_pcb_image(img)
        print(text)
        print("\n--- Extracted defect summary ---")
        print(extract_defect_summary(text))
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running (`ollama serve`) and the model is pulled.")
