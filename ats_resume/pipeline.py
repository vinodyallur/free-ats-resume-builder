"""High-level conversion pipeline: file in -> ATS-friendly DOCX out."""

from .build import build_docx
from .extract import extract_text
from .parse import parse_resume


def convert(input_path, output_path, enhance=False, api_key=None, model=None,
            provider=None, base_url=None):
    """Convert a resume file into an ATS-friendly DOCX.

    Parameters
    ----------
    input_path : path to a .pdf / .docx / .txt resume
    output_path : where to write the generated .docx
    enhance : when True, use an LLM (bring-your-own key) for nicer restructuring
    api_key, model, provider, base_url : optional LLM settings
    """
    raw = extract_text(input_path)
    if enhance:
        from .llm import structure_with_llm

        structured = structure_with_llm(
            raw, api_key=api_key, model=model, provider=provider, base_url=base_url
        )
    else:
        structured = parse_resume(raw)
    build_docx(structured, output_path)
    return output_path
