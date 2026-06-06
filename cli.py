"""Command-line interface for the Free ATS Resume Builder.

Examples
--------
    python cli.py my_resume.pdf
    python cli.py my_resume.docx -o ats_resume.docx
    python cli.py my_resume.pdf --enhance            # uses your own LLM API key
"""

import argparse
import sys
from pathlib import Path

from ats_resume import convert


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ats-resume",
        description="Convert any resume (PDF/DOCX/TXT) into a clean, 1-page, "
        "ATS-friendly DOCX.",
    )
    parser.add_argument("input", help="Path to the resume to convert (.pdf, .docx, .txt)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output .docx path (default: <input>_ATS.docx next to the input file)",
    )
    parser.add_argument(
        "--enhance",
        action="store_true",
        help="Use an LLM to restructure the content (requires your own API key "
        "via OPENAI_API_KEY or GEMINI_API_KEY).",
    )
    parser.add_argument("--model", help="LLM model name (optional)")
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini"],
        help="Force a specific LLM provider (optional)",
    )
    args = parser.parse_args(argv)

    in_path = Path(args.input)
    if not in_path.exists():
        parser.error(f"Input file not found: {in_path}")

    out_path = Path(args.output) if args.output else in_path.with_name(
        in_path.stem + "_ATS.docx"
    )

    try:
        convert(
            in_path,
            out_path,
            enhance=args.enhance,
            model=args.model,
            provider=args.provider,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Done -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
