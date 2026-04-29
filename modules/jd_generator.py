# -*- coding: utf-8 -*-
import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

V3_PROMPT = """You are a senior talent acquisition specialist with 10 years of experience writing
high-converting, ATS-optimized job descriptions for {company_type} companies in the {industry} sector.

Write a job description using EXACTLY this structure:

## {job_title} | {employment_type} | {location}

### About the Role
[2-3 sentences. What this person will own. Why this role exists right now.
BANNED WORDS: rockstar, ninja, wizard, guru, passionate, dynamic, fast-paced, self-starter, thought leader, synergy]

### What You Will Do
[Exactly 6 bullet points. Start each with a strong action verb.
Name specific tools, processes, and stakeholders where relevant.]

### What You Bring
REQUIRED (maximum 6 — actual dealbreakers only):
PREFERRED (maximum 4 — genuine bonuses, not hidden requirements):

### What We Offer
[3-4 lines. Specific and honest. No vague statements.]

### How to Apply
[One clear sentence.]

Technical requirements to embed naturally: {skills}
Experience level: {experience_level}
Write at Grade 10 reading level — clear for any candidate.

After the JD, add:

## Quick Check
- Bias: any exclusionary phrases found (or "None detected")
- Keywords: top 5 ATS keywords embedded
- Missing: anything a candidate would need to know that is not included"""


def show():
    st.title("JD Generator")
    st.markdown("*Fill in the details below to generate a professional, ATS-optimized job description.*")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. Senior Data Analyst")
        skills = st.text_input("Required Skills", placeholder="e.g. Python, SQL, Power BI")
        location = st.text_input("Location", placeholder="e.g. Remote / Bangalore")
        industry = st.text_input("Industry", placeholder="e.g. Fintech / Healthcare")

    with col2:
        experience_level = st.selectbox("Experience Level", ["Junior", "Mid", "Senior"])
        employment_type = st.selectbox("Employment Type", ["Full-Time", "Part-Time", "Contract", "Freelance"])
        company_type = st.selectbox("Company Type", ["Startup", "Mid-size", "Enterprise"])

    generate_btn = st.button("Generate Job Description", type="primary", use_container_width=True)

    if generate_btn:
        if not job_title.strip():
            st.error("Please enter a job title.")
            return
        if not skills.strip():
            st.error("Please enter at least one required skill.")
            return

        with st.spinner("Generating job description..."):
            try:
                prompt = V3_PROMPT.format(
                    job_title=job_title.strip(),
                    skills=skills.strip(),
                    experience_level=experience_level,
                    employment_type=employment_type,
                    company_type=company_type,
                    location=location.strip() or "Remote",
                    industry=industry.strip() or "Technology"
                )
                message = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text
                st.session_state["generated_jd"] = response

            except Exception as e:
                st.error(f"Generation failed. Please try again. Error: {str(e)}")
                return

    if "generated_jd" in st.session_state:
        response = st.session_state["generated_jd"]

        st.markdown("---")
        st.markdown(response)
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download JD as Markdown",
                data=response,
                file_name="job_description.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col2:
           if st.button("Use this JD in Resume Analyzer →", use_container_width=True):
              st.session_state["jd_from_generator"] = response
              st.session_state["jd_input"] = response
              st.success("JD saved. Switch to Resume Analyzer — it will be pre-filled.")