from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".pdf"}


def extract_text(path):
    """Read the text content of a .txt or .pdf file."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    raise ValueError(f"Unsupported file type: {suffix}")