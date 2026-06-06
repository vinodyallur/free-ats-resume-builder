"""Heuristically parse raw resume text into a structured dictionary.

The structure produced here is consumed by ``ats_resume.build.build_docx``::

    {
        "name": "Jane Doe",
        "contact": {"email": ..., "phone": ..., "linkedin": ..., "github": ..., "website": ...},
        "sections": [
            {"heading": "Professional Summary",
             "entries": [{"title": "...", "date": "", "bullets": []}]},
            ...
        ],
    }
"""

import re

# Map the many header synonyms found in real resumes to a canonical heading.
SECTION_MAP = {
    "professional summary": "Professional Summary",
    "summary": "Professional Summary",
    "summary of qualifications": "Professional Summary",
    "objective": "Professional Summary",
    "career objective": "Professional Summary",
    "profile": "Professional Summary",
    "about": "Professional Summary",
    "about me": "Professional Summary",
    "experience": "Experience",
    "work experience": "Experience",
    "professional experience": "Experience",
    "employment": "Experience",
    "employment history": "Experience",
    "internship": "Experience",
    "internships": "Experience",
    "internship experience": "Experience",
    "education": "Education",
    "academics": "Education",
    "academic background": "Education",
    "academic qualifications": "Education",
    "technical skills": "Technical Skills",
    "skills": "Technical Skills",
    "key skills": "Technical Skills",
    "core competencies": "Technical Skills",
    "competencies": "Technical Skills",
    "projects": "Projects",
    "academic projects": "Projects",
    "personal projects": "Projects",
    "key projects": "Projects",
    "certifications": "Certifications",
    "certification": "Certifications",
    "certifications and achievements": "Certifications",
    "licenses and certifications": "Certifications",
    "courses": "Certifications",
    "coursework": "Certifications",
    "achievements": "Achievements",
    "awards": "Achievements",
    "awards and honors": "Achievements",
    "honors": "Achievements",
    "accomplishments": "Achievements",
    "languages": "Languages",
    "patents": "Patents",
    "patent": "Patents",
    "publications": "Publications",
    "interests": "Interests",
    "hobbies": "Interests",
    "volunteer": "Volunteer Experience",
    "volunteering": "Volunteer Experience",
    "volunteer experience": "Volunteer Experience",
    "references": "References",
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-%./]+", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-%./]+", re.I)
URL_RE = re.compile(r"(?:https?://)?(?:www\.)?[\w-]+\.[\w.-]+/[\w\-%./?=&]+", re.I)
PHONE_RE = re.compile(r"(\+?\d[\d\s().\-]{7,}\d)")
BULLET_RE = re.compile(r"^\s*(?:[•\-\*\u2022\u25aa\u25cf\u25e6\u00b7\u2023\u2043\u25cb\u2219o]|\d+[.)])\s+")

_MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?"
    r"|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
DATE_RE = re.compile(
    r"(" + _MONTH + r"\.?\s*\d{4}\s*[-\u2013\u2014]+\s*(?:Present|Current|" + _MONTH + r"\.?\s*\d{4})"
    r"|\d{4}\s*[-\u2013\u2014]\s*(?:Present|Current|\d{4})"
    r"|" + _MONTH + r"\.?\s*\d{4})",
    re.I,
)


def _canonical(line):
    key = re.sub(r"\s+", " ", line.strip().strip(":").lower())
    return SECTION_MAP.get(key)


def _is_header(line):
    if len(line.split()) > 6:
        return None
    return _canonical(line)


def _is_contact_line(line):
    low = line.lower()
    return bool(
        EMAIL_RE.search(line)
        or "linkedin.com" in low
        or "github.com" in low
        or "http" in low
        or sum(ch.isdigit() for ch in line) >= 7
    )


def _extract_contact(text):
    contact = {}
    m = EMAIL_RE.search(text)
    if m:
        contact["email"] = m.group(0)
    m = LINKEDIN_RE.search(text)
    if m:
        contact["linkedin"] = re.sub(r"^https?://", "", m.group(0))
    m = GITHUB_RE.search(text)
    if m:
        contact["github"] = re.sub(r"^https?://", "", m.group(0))
    head = text[:900]
    for m in PHONE_RE.finditer(head):
        digits = re.sub(r"\D", "", m.group(0))
        if 9 <= len(digits) <= 13:
            contact["phone"] = m.group(0).strip()
            break
    return contact


def _extract_name(lines):
    for ln in lines[:8]:
        s = ln.strip()
        if not s or _is_contact_line(s) or _canonical(s):
            continue
        words = s.split()
        if 1 <= len(words) <= 5 and re.match(r"^[A-Za-z][A-Za-z .,'\-]+$", s):
            return s
    return lines[0].strip() if lines else "Your Name"


def _split_date(line):
    best = None
    for m in DATE_RE.finditer(line):
        # Prefer a date sitting at (or very near) the end of the line.
        if len(line) - m.end() <= 4:
            best = m
    if best:
        date = best.group(0).strip()
        title = line[: best.start()].rstrip(" |-\u2013\u2014\t").strip()
        return (title or line), date
    return line, ""


def _merge_sections(sections):
    merged = []
    index = {}
    for sec in sections:
        if sec["heading"] in index:
            index[sec["heading"]]["entries"].extend(sec["entries"])
        else:
            index[sec["heading"]] = {"heading": sec["heading"], "entries": list(sec["entries"])}
            merged.append(index[sec["heading"]])
    return merged


def parse_resume(text):
    """Parse raw resume text into the structured dictionary used by the builder."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    nonempty = [ln for ln in lines if ln.strip()]

    contact = _extract_contact(text)
    name = _extract_name(nonempty)

    sections = []
    current = None
    current_entry = None
    started = False
    preamble = []

    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        head = _is_header(s)
        if head:
            current = {"heading": head, "entries": []}
            sections.append(current)
            current_entry = None
            started = True
            continue
        if not started:
            # Lines before the first recognised header: name + contact + maybe a summary.
            if s != name and not _is_contact_line(s):
                preamble.append(s)
            continue
        if BULLET_RE.match(ln):
            bullet = BULLET_RE.sub("", ln).strip()
            if not bullet:
                continue
            if current_entry is None:
                current_entry = {"title": "", "date": "", "bullets": []}
                current["entries"].append(current_entry)
            current_entry["bullets"].append(bullet)
        else:
            title, date = _split_date(s)
            current_entry = {"title": title, "date": date, "bullets": []}
            current["entries"].append(current_entry)

    sections = _merge_sections(sections)

    # If there was an un-headed summary paragraph at the top, surface it.
    preamble_text = " ".join(preamble).strip()
    if preamble_text and len(preamble_text) > 40:
        has_summary = any(s["heading"] == "Professional Summary" for s in sections)
        if not has_summary:
            sections.insert(
                0,
                {
                    "heading": "Professional Summary",
                    "entries": [{"title": preamble_text, "date": "", "bullets": []}],
                },
            )

    return {"name": name, "contact": contact, "sections": sections}
