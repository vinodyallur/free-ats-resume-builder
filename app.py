"""Streamlit web app for the Free ATS Resume Builder.

Run locally:
    streamlit run app.py

Deploy free for anyone to use:
    Push this repo to GitHub, then deploy on https://streamlit.io/cloud
"""

import tempfile
from pathlib import Path

import streamlit as st

from ats_resume import convert

st.set_page_config(page_title="Free ATS Resume Builder", page_icon="📄", layout="centered")

st.title("📄 Free ATS Resume Builder")
st.write(
    "Upload your resume and download a clean, single-column, **ATS-friendly** "
    "version in seconds. Works fully offline and free — no sign-up required."
)

uploaded = st.file_uploader(
    "Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt", "md"]
)

with st.expander("Optional: AI enhancement (bring your own API key)"):
    st.caption(
        "Leave blank to use the fast, free offline formatter. Provide a key to let "
        "an LLM rewrite bullets and structure for an even cleaner result. Your key "
        "is used only for this request and is never stored."
    )
    provider = st.selectbox("Provider", ["(offline / none)", "openai", "gemini"])
    api_key = st.text_input("API key", type="password")
    model = st.text_input("Model (optional)")

if uploaded is not None:
    if st.button("Generate ATS resume", type="primary"):
        with st.spinner("Building your ATS-friendly resume..."):
            suffix = Path(uploaded.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                tmp_in.write(uploaded.getbuffer())
                in_path = tmp_in.name
            out_path = str(Path(tempfile.gettempdir()) / "resume_ATS.docx")

            enhance = provider in ("openai", "gemini") and bool(api_key)
            try:
                convert(
                    in_path,
                    out_path,
                    enhance=enhance,
                    api_key=api_key or None,
                    model=model or None,
                    provider=provider if enhance else None,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Something went wrong: {exc}")
            else:
                st.success("Your ATS-friendly resume is ready!")
                with open(out_path, "rb") as fh:
                    st.download_button(
                        "⬇️ Download DOCX",
                        data=fh.read(),
                        file_name="resume_ATS.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

st.markdown("---")
st.caption(
    "Tip: After downloading, open in Word and export to PDF for submitting. "
    "Keep the file format simple — no tables, columns, or images — for best ATS results."
)
