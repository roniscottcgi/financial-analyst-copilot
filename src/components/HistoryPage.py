import streamlit as st

class HistoryPage:
    def __init__(self, source_url: str):
        self.source_url = source_url

    def render(self):
        st.title("History Section")
        st.write("Here is the history of queries and there responses")
        st.write(f"Source URL: {self.source_url}")