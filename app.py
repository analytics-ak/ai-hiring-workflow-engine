# -*- coding: utf-8 -*-
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Hiring Workflow Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 AI Hiring Workflow Engine")
    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio(
        label="Select Page",
        options=["Resume Analyzer", "JD Generator"],
        index=0,
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Model:** claude-sonnet-4-5")
    st.markdown("**Prompt Version:** V3")
    st.markdown("---")
    st.markdown("*Built with structured prompt engineering*")

    # show indicator if JD was passed from generator
    if "jd_from_generator" in st.session_state and st.session_state["jd_from_generator"]:
        st.success("JD ready from Generator")

# ── PAGE ROUTING ──────────────────────────────────────────────────
if page == "Resume Analyzer":
    from modules.resume_analyzer import show
    show()
elif page == "JD Generator":
    from modules.jd_generator import show
    show()