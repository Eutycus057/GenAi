import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="AI Teaching Assistant", layout="wide")

st.title("🎓 AI Teaching Assistant (Powered by Jac + byLLM)")

# Load API Key
JAC_API_KEY = os.getenv("JAC_API_KEY", "mysecretkey")
HEADERS = {"Authorization": f"Bearer {JAC_API_KEY}"}

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = "sess_" + st.session_state.get("run_id", "001")
if "slides" not in st.session_state:
    st.session_state.slides = []
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0
if "pptx_url" not in st.session_state:
    st.session_state.pptx_url = None
if "qa_log" not in st.session_state:
    st.session_state.qa_log = []

# Input: Lesson topic
topic = st.text_input("Enter a lesson topic", placeholder="e.g., Boolean Algebra")

if st.button("Start Lecture"):
    payload = {"topic": topic, "session_id": st.session_state.session_id}
    resp = requests.post(
        "http://localhost:8000/walker/start_lecture",
        json=payload,
        headers=HEADERS  # ✅ Added authentication
    )
    if resp.status_code == 200:
        data = resp.json()
        if "slides" in data:
            st.session_state.slides = data["slides"]
            st.session_state.pptx_url = data.get("pptx_url")
            st.session_state.current_slide = 0
    else:
        st.error(f"Server error {resp.status_code}: {resp.text}")

# Display slides
if st.session_state.slides:
    slide = st.session_state.slides[st.session_state.current_slide]
    st.subheader(slide["title"])
    for b in slide.get("bullets", []):
        st.write("•", b)
    if "image" in slide and slide["image"]:
        st.image(slide["image"])

    # Slide navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Previous") and st.session_state.current_slide > 0:
            st.session_state.current_slide -= 1
    with col2:
        if st.button("Next ➡") and st.session_state.current_slide < len(st.session_state.slides) - 1:
            st.session_state.current_slide += 1

# Question box
if st.session_state.slides:
    st.markdown("---")
    st.subheader("Ask the AI Assistant")
    question = st.text_input("Your question:")
    if st.button("Ask"):
        payload = {
            "session_id": st.session_state.session_id,
            "student_id": "student_001",
            "question_text": question,
        }
        resp = requests.post(
            "http://localhost:8000/walker/student_question",
            json=payload,
            headers=HEADERS  # ✅ Added authentication
        )
        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("answer", "No response")
            st.session_state.qa_log.append({"q": question, "a": answer})
        else:
            st.error(f"Server error {resp.status_code}: {resp.text}")

    # Show Q&A log
    for qa in st.session_state.qa_log:
        st.write(f"**Q:** {qa['q']}")
        st.write(f"**A:** {qa['a']}")

# Download PPTX
if st.session_state.pptx_url:
    st.markdown("---")
    try:
        file_data = requests.get(st.session_state.pptx_url, headers=HEADERS).content
        st.download_button(
            label="📥 Download Lecture PPTX",
            data=file_data,
            file_name="lecture_slides.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    except Exception as e:
        st.error(f"Could not download PPTX: {e}")
