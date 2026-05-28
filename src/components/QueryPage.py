import streamlit as st

from src.service.db_service import DBService
from src.service.llm_service import LLMService


class QueryPage:
    def __init__(self, llm_service: LLMService, db_service: DBService):
        self.llm_service = llm_service
        self.db_service = db_service

    def render(self):
        empty_left, center_content, empty_right = st.columns([1, 2, 1])

        with center_content:
            # st.set_page_config(page_title="AI Database Assistant", page_icon="🤖")
            # st.title("🗄️ AI Database Assistant")
            st.title("AI Database Assistant")
            st.write("This content is perfectly centered within the main area")

            with st.form("sql_generator_form", clear_on_submit=False):
                user_query = st.text_input(
                    "What do you need?",
                    placeholder= "e.g., Show me the top 10 customers by revenue in 2025")

                submitted = st.form_submit_button("Generate SQL")

            if submitted and user_query:
                with st.spinner("Analyzing database schema and generating query..."):
                    # --- PLACEHOLDER FOR YOUR AI/LLM CALL ---
                    # generated_sql = call_your_llm_function(user_query)
                    generated_sql = self.db_service.get_response(user_query)
                    # generated_sql = f"SELECT * FROM customers WHERE year = 2025 ORDER BY revenue DESC LIMIT 10;"

                st.subheader("Generated SQL Query")
                st.code(generated_sql, language="sql")

                # Optional: Display a data preview container below
                st.subheader("Query Results Preview")
                st.info("Click 'Execute' to run this query against the database.")