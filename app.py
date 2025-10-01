import streamlit as st
from jaclang_streamlit import run_streamlit

if __name__ == "__main__":
    st.set_page_config(page_title="MCP Chatbot", layout="wide")
    run_streamlit("client", ".")
