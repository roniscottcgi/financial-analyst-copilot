import streamlit as st

class QueryPage:
    def __init__(self, source_url: str):
        self.source_url = source_url

    def render(self):
        empty_left, center_content, empty_right = st.columns([1, 2, 1])

        with center_content:
            st.header("Main Centered Section")
            st.write("This content is perfectly centered within the main area")
            st.write(f"Source URL: {self.source_url}")