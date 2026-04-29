# -*- coding: utf-8 -*-
import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

V3_PROMPT = """You are a senior recruiter and resume coach with expertise in ATS systems and hiring.

STRICT RULES — follow without exception:
- Use ONLY information present in the JD and resume provided
- Do NOT invent skills, experience, or qualifications not mentioned
- Do NOT assume the candidate has skills because they worked in a related field
- If information is missing or ambiguous, flag it as "not verifiable"

JOB DESCRIPTION:
{jd_text}

CANDIDATE RESUME:
{resume_text}

Produce your analysis in EXACTLY this format:

## MATCH SCORE: [X]/100

### Score Breakdown
| Dimension | Score | Max | Reasoning |
|---|---|---|---|
| Skill Match | X | 35 | [specific reason] |
| Experience Relevance | X | 25 | [specific reason] |
| Keyword Alignment | X | 20 | [specific reason] |
| Role Specificity | X | 10 | [specific reason] |
| Presentation Quality | X | 10 | [specific reason] |

### Matched Skills
[Only skills explicitly present in BOTH the JD and the resume]

### Missing Skills — Critical (Dealbreakers)
[Required skills from JD not found in resume]

### Missing Skills — Preferred (Nice to Have)
[Preferred skills from JD not found in resume]

### Inline Gap Analysis
For each required skill and keyword in the JD produce one line:
[Skill] -> Found in [section] OR Missing — [where to add it and how]

### ATS Keyword Gap
[Exact keywords from JD that do not appear verbatim in resume]

### Top 5 Improvement Actions
[Number 1-5. Each must:
- Name the specific resume section to change
- Explain exactly what to add or rewrite
- Show BEFORE and AFTER example
Order by impact — most important first]

### Section Rewrite
ORIGINAL:
[paste the weakest section as-is]

REWRITTEN:
[improved version that better matches the JD]

### Honest Assessment
[2-3 sentences. Is this a realistic fit? What one change would most improve their chances? Be direct.]"""


def get_score_color(score):
    if score >= 75:
        return "green", "Strong Match"
    elif score >= 51:
        return "orange", "Partial Match"
    else:
        return "red", "Poor Match"


def extract_score(response_text):
    import re
    match = re.search(r"MATCH SCORE:\s*(\d+)/100", response_text)
    if match:
        return int(match.group(1))
    return 0


def show():
    st.title("Resume vs JD Analyzer")
    st.markdown("*Paste a job description and your resume to get a match score, gap analysis, and specific improvement actions.*")
    st.markdown("---")

    # ── EDGE CASE VALIDATION HELPERS ─────────────────────────────
    def validate_inputs(jd, resume):
        if not jd.strip():
            return False, "Please paste a job description before analyzing."
        if not resume.strip():
            return False, "Please paste your resume before analyzing."
        if len(resume.strip().split()) < 30:
            return False, "Your resume appears very short (under 50 words). Results may be limited."
        if len(resume.strip().split()) > 3000:
            st.warning("Long resume detected. Consider trimming to 2 pages for best ATS results.")
        if not any(c.isascii() for c in resume[:100]):
            st.info("Non-English content detected. Analysis may be less accurate.")
        if len(jd.strip().split()) < 30:
            st.info("JD has few specific requirements. Analysis will focus on experience alignment.")
        return True, ""

    # ── INPUT SECTION ─────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Job Description")

        # pre-fill from JD Generator if available
        jd_prefill = ""
        if "jd_from_generator" in st.session_state and st.session_state["jd_from_generator"]:
            jd_prefill = st.session_state["jd_from_generator"]
            st.info("JD pre-filled from JD Generator.")

        jd_text = st.text_area(
            label="jd_input",
            label_visibility="collapsed",
            placeholder="Paste the full job description here...",
            height=300,
            key="jd_input",
            value=jd_prefill
        )

    with col2:
        st.markdown("#### Your Resume")
        resume_text = st.text_area(
            label="resume_input",
            label_visibility="collapsed",
            placeholder="Paste your resume text here...",
            height=300,
            key="resume_input"
        )

    analyze_btn = st.button("Analyze Match", type="primary", use_container_width=True)

    if analyze_btn:
        valid, error_msg = validate_inputs(jd_text, resume_text)
        if not valid:
            st.error(error_msg)
            return

        with st.spinner("Analyzing your resume against the job description..."):
            try:
                prompt = V3_PROMPT.format(
                    jd_text=jd_text.strip(),
                    resume_text=resume_text.strip()
                )
                message = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text
                st.session_state["analysis_result"] = response
                st.session_state["jd_text"] = jd_text
                st.session_state["resume_text"] = resume_text

            except Exception as e:
                st.error(f"Analysis failed. Please try again. Error: {str(e)}")
                return

    # ── RESULTS SECTION ───────────────────────────────────────────
    if "analysis_result" in st.session_state:
        response = st.session_state["analysis_result"]
        score = extract_score(response)
        color, label = get_score_color(score)

        st.markdown("---")

        # Score card
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            if color == "green":
                st.success(f"### {score}/100 — {label}")
            elif color == "orange":
                st.warning(f"### {score}/100 — {label}")
            else:
                st.error(f"### {score}/100 — {label}")
            st.progress(score / 100)

        st.markdown("---")

        # Full analysis
        st.markdown(response)

        st.markdown("---")

        # Download buttons
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="Download as Markdown",
                data=response,
                file_name="resume_analysis.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_dl2:
            try:
                from utils.report_generator import generate_pdf_report
                pdf_bytes = generate_pdf_report(response, score, label)
                st.download_button(
                    label="Download as PDF",
                    data=pdf_bytes,
                    file_name="resume_analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception:
                st.info("PDF download available after report generator is set up.")