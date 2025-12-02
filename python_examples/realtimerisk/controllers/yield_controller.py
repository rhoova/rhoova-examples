"""Controller layer for yield data access."""
import streamlit as st

def get_latest_yield_data():
    return st.session_state.get("yield_data", {})
