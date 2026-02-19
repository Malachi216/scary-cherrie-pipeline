import os
from docx import Document
from .utils import RUNS_DIR

def export_script_docx(run_id: str, script_text: str) -> str:
    doc = Document()
    for line in script_text.split("\n"):
        doc.add_paragraph(line)
    outpath = os.path.join(RUNS_DIR, run_id, "final_script.docx")
    doc.save(outpath)
    return outpath
