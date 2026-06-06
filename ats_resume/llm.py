"""Optional AI enhancement: use an LLM to restructure messy resumes more cleanly.

This is entirely optional. The tool works fully offline without it. When enabled,
the user supplies *their own* API key (nothing is hard-coded or sent anywhere
except the provider the user chooses), so the project stays free to host and run.

Supported providers (auto-detected from the key / env vars):
  * OpenAI-compatible  -> OPENAI_API_KEY        (also works with OPENAI_BASE_URL)
  * Google Gemini      -> GEMINI_API_KEY / GOOGLE_API_KEY
"""

import json
import os
import re

from .parse import parse_resume

SCHEMA_HINT = {
    "name": "Full Name",
    "contact": {
        "location": "City, Country",
        "phone": "+00 0000000000",
        "email": "name@example.com",
        "linkedin": "linkedin.com/in/...",
        "github": "github.com/...",
        "website": "",
    },
    "sections": [
        {
            "heading": "Professional Summary",
            "entries": [{"title": "2-3 line summary text", "date": "", "bullets": []}],
        },
        {
            "heading": "Technical Skills",
            "entries": [{"title": "", "date": "", "bullets": ["Category: a, b, c"]}],
        },
        {
            "heading": "Experience",
            "entries": [
                {"title": "Role — Company", "date": "Mon YYYY – Mon YYYY", "bullets": ["..."]}
            ],
        },
    ],
}

PROMPT = """You are an expert resume writer specialising in ATS (Applicant Tracking System) optimisation.

Rewrite the resume text below into clean, structured JSON. Rules:
- Keep ALL real facts; never invent employers, dates, or degrees.
- Use standard, recognisable section headings (Professional Summary, Technical Skills,
  Experience, Projects, Education, Certifications, Achievements, Languages, etc.).
- Group skills under short labelled categories like "Programming: C, C++, Python".
- Make bullets concise, achievement-oriented, and keyword-rich for the candidate's field.
- Write a 2-3 line Professional Summary if one is missing.
- Output ONLY valid JSON matching this exact shape (no markdown, no commentary):

{schema}

Resume text:
\"\"\"
{resume}
\"\"\"
"""


def _extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def _call_openai(prompt, api_key, model, base_url):
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url or None)
    resp = client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def _call_gemini(prompt, api_key, model):
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    gm = genai.GenerativeModel(model or "gemini-1.5-flash")
    return gm.generate_content(prompt).text


def structure_with_llm(raw_text, api_key=None, model=None, provider=None, base_url=None):
    """Return a structured resume dict produced by an LLM, falling back to the
    offline parser if no key/provider is available or the call fails."""
    prompt = PROMPT.format(schema=json.dumps(SCHEMA_HINT, indent=2), resume=raw_text)

    openai_key = api_key if (provider in (None, "openai")) else None
    openai_key = openai_key or os.getenv("OPENAI_API_KEY")
    gemini_key = api_key if provider == "gemini" else None
    gemini_key = gemini_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")

    try:
        if provider == "gemini" or (provider is None and gemini_key and not openai_key):
            content = _call_gemini(prompt, gemini_key, model)
        elif openai_key:
            content = _call_openai(prompt, openai_key, model, base_url)
        else:
            raise RuntimeError("No API key found for AI enhancement.")
        data = _extract_json(content)
        if isinstance(data, dict) and data.get("sections"):
            data.setdefault("contact", {})
            return data
    except Exception as exc:  # noqa: BLE001 - graceful fallback is intentional
        print(f"[ai] enhancement unavailable ({exc}); using offline parser instead.")
    return parse_resume(raw_text)
