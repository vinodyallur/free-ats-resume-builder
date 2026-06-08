# 📄 Free ATS Resume Builder

Turn **any** resume (PDF, DOCX, or TXT) into a clean, single‑column, **ATS‑friendly**
one‑page resume in seconds — **free and open source**.

Applicant Tracking Systems (ATS) reject or mangle resumes that use tables, columns,
text boxes, images, and fancy fonts. This tool re‑flows your existing content into a
simple, standardized layout that parses perfectly — boosting your ATS score without
you having to reformat anything by hand.

- ✅ **Free & offline** — no account, no API key, nothing uploaded anywhere
- ✅ Reads **PDF / DOCX / TXT**
- ✅ Outputs a tidy **one‑page `.docx`** with standard headings and real bullet lists
- ✅ Optional **AI enhancement** (bring your own OpenAI/Gemini key) for nicer wording
- ✅ Use it as a **command‑line tool**, a **Python library**, or a **web app**

---

## Why it's ATS‑friendly

The generated DOCX deliberately uses only things ATS parsers handle well:

| Good (what we output)            | Avoided (what breaks ATS)        |
| -------------------------------- | -------------------------------- |
| Single column, plain text        | Multi‑column layouts, text boxes |
| Standard headings (Experience…)  | Creative/renamed section titles  |
| Real bullet lists                | Tables for layout                |
| Common font (Calibri), 0.5" margins | Images, icons, logos          |
| Selectable, machine‑readable text | Text baked into graphics        |

---

## Quick start

```bash
# 1) Get the code
git clone https://github.com/vinodyallur/free-ats-resume-builder.git
cd free-ats-resume-builder

# 2) Install dependencies
pip install -r requirements.txt

# 3) Convert a resume
python cli.py path/to/your_resume.pdf
#   -> writes your_resume_ATS.docx next to the input
```

Try it on the bundled sample:

```bash
python cli.py examples/sample_resume.txt -o examples/sample_ATS.docx
```

### CLI options

```text
python cli.py INPUT [-o OUTPUT] [--enhance] [--provider openai|gemini] [--model NAME]

INPUT         resume to convert (.pdf, .docx, .txt)
-o, --output  output .docx path (default: <input>_ATS.docx)
--enhance     use an LLM to rewrite/restructure (needs your own API key)
--provider    force a provider (optional)
--model       LLM model name (optional)
```

---

## Web app (anyone can use it in a browser)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL it prints. To let **anyone** use it for free, push this repo to
GitHub and deploy it on [Streamlit Community Cloud](https://streamlit.io/cloud) — it's
free hosting for public apps.

---

## Optional: AI enhancement (bring your own key)

The offline formatter already produces a clean ATS resume. If you want an LLM to also
rewrite bullets and tighten the structure, supply **your own** API key — it's used only
for that request and never stored:

```bash
# OpenAI (or any OpenAI-compatible endpoint)
pip install openai
setx OPENAI_API_KEY "sk-..."        # Windows (new terminal after)
python cli.py resume.pdf --enhance

# Google Gemini
pip install google-generativeai
setx GEMINI_API_KEY "..."
python cli.py resume.pdf --enhance --provider gemini
```

If no key is found, the tool automatically falls back to the offline formatter.

---

## Use as a Python library

```python
from ats_resume import convert

convert("resume.pdf", "resume_ATS.docx")            # offline
convert("resume.pdf", "resume_ATS.docx", enhance=True)  # with your LLM key
```

---

## Project structure

```text
free-ats-resume-builder/
├── ats_resume/
│   ├── extract.py     # text extraction (PDF / DOCX / TXT)
│   ├── parse.py       # heuristic section parser
│   ├── build.py       # the ATS-friendly DOCX style engine
│   ├── llm.py         # optional AI enhancement (bring your own key)
│   └── pipeline.py    # convert(): file in -> DOCX out
├── cli.py             # command-line interface
├── app.py             # Streamlit web app
├── examples/          # sample resume
├── requirements.txt
├── LICENSE            # MIT
└── README.md
```

---

## Tips for the best result

- After downloading, open in Word and quickly proofread, then **export to PDF** for applications.
- Keep it to one page; trim the oldest/least‑relevant bullets if it spills over.
- Mirror keywords from the job description in your Skills and Experience sections.

## Contributing

Issues and pull requests are welcome. Ideas: smarter section detection, more output
templates, language localisation.

## License

[MIT](LICENSE) — free to use, modify, and share.

> Disclaimer: This tool reformats your existing content. Always review the output for
> accuracy before submitting. No ATS score is guaranteed; results vary by system.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=vinodyallur/free-ats-resume-builder&type=Date)](https://star-history.com/#vinodyallur/free-ats-resume-builder&Date)
