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

            if "generated_sql" not in st.session_state:
                st.session_state.generated_sql = None

            with st.form("sql_form", clear_on_submit=False):
                user_query = st.text_input(
                    "What do you need?",
                    placeholder= "e.g., Show me the top 10 customers by revenue in 2025",
                    key= "query")

                submitted = st.form_submit_button("Generate SQL")

            if submitted and user_query:
                with st.spinner("Analyzing database db and generating query..."):
                    generated_sql = self.db_service.get_response(user_query)
                    st.session_state.generated_sql = generated_sql

            if st.session_state.generated_sql:
                st.subheader("Generated SQL Query")
                st.code(st.session_state.generated_sql, language="sql")

                # Optional: Display a data preview container below
                st.subheader("Query Results Preview")
                st.info("Click 'Execute' to run this query against the database.")

                if st.button("Execute Query"):
                    result = self.db_service.execute_query(st.session_state.generated_sql)
                    st.code(result, language="sql")
                    st.success("Query executed successfully")

        st.markdown("---")
        with st.expander("🛠️ Teach the AI (Add New Search Rules)"):
            st.write("If the AI failed to guess a specific word, teach it the correct mapping here.")

            new_phrase = st.text_input("When a user types this phrase:", placeholder="e.g., broken accounts")
            new_sql = st.text_area("It should generate this exact SQL query:",
                                   placeholder="SELECT * FROM customers WHERE status = 'Churned';")

            if st.button("Save Example"):
                if new_phrase and new_sql:
                    self.db_service.add_new_example(new_phrase, new_sql)
                    st.success("Example saved successfully! Try your query again above.")
                else:
                    st.warning("Please fill out both fields.")
