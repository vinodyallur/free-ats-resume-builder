"""Free ATS Resume Builder — convert any resume into a clean, 1-page, ATS-friendly DOCX."""

from .build import build_docx
from .extract import extract_text
from .parse import parse_resume
from .pipeline import convert

__version__ = "1.0.0"
__all__ = ["extract_text", "parse_resume", "build_docx", "convert"]
