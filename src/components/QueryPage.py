import streamlit as st
import pandas as pd

from src.service.db_service import DBService
from src.service.llm_service import LLMService


class QueryPage:
    def __init__(self, llm_service: LLMService, db_service: DBService):
        self.llm_service = llm_service
        self.db_service = db_service

    def display_result(self, df: pd.DataFrame):
        """Dynamically analyzes data and renders the best matching chart."""
        if df.empty:
            st.warning("The dataset is empty.")
            return

        # 1. Create a safe local copy to modify
        df = df.copy()

        # 2. Match both legacy 'object' and modern native 'string' types
        for col in df.columns:
            if df[col].dtype in ['object', 'string'] or isinstance(df[col].dtype, pd.StringDtype):
                try:
                    # Parse dates safely while handling mixed database strings
                    converted = pd.to_datetime(df[col], format='mixed', errors='raise')

                    # Ignore columns that parse as pure numeric timestamps (like IDs)
                    if not pd.api.types.is_numeric_dtype(converted):
                        df[col] = converted
                except (ValueError, TypeError):
                    pass

        # 3. Extract fresh, explicit column metadata arrays
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

        # Debugging hook: Uncomment the line below to view type detection in your terminal
        # print(f"DEBUG -> Numbers: {num_cols} | Categories: {cat_cols} | Dates: {date_cols}")

        # Case 1: Time Series Data -> Line Chart
        if len(date_cols) > 0 and len(num_cols) > 0:
            st.subheader("Trends Over Time")
            # CRITICAL: Pass the primary string column name to set_index, not the whole list
            primary_date = date_cols[0]
            st.line_chart(df.set_index(primary_date)[num_cols])

        # Case 2: Single Categorical vs Single Numerical -> Bar or Pie Chart
        elif len(cat_cols) == 1 and len(num_cols) == 1:
            cat_col = cat_cols[0]
            num_col = num_cols[0]
            unique_count = df[cat_col].nunique()

            if 1 < unique_count <= 5:
                st.subheader(f"Composition by {cat_col}")
                import altair as alt
                chart = alt.Chart(df).mark_arc().encode(
                    color=alt.Color(cat_col, legend=alt.Legend(title=cat_col)),
                    theta=alt.Theta(num_col, type="quantitative")
                ).properties(width=400, height=400)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.subheader(f"{num_col} by {cat_col}")
                st.bar_chart(df.set_index(cat_col)[num_col])

        # Case 3: Multiple Numerical Columns -> Scatter Plot
        elif len(num_cols) >= 2:
            st.subheader(f"Correlation: {num_cols[0]} vs {num_cols[1]}")
            st.scatter_chart(df, x=num_cols[0], y=num_cols[1])

        # Case 4: Fallback -> Raw Interactive Data Table
        else:
            st.subheader("Data Overview")
            st.dataframe(df, use_container_width=True)

    def render(self):
        st.title("AI Database Assistant")
        st.write("This content is perfectly centered within the main area")

        if "generated_sql" not in st.session_state:
            st.session_state.generated_sql = None
        if "error_message" not in st.session_state:
            st.session_state.error_message = ""

        with st.form("sql_form", clear_on_submit=False):
            user_query = st.text_input(
                "What do you need?",
                placeholder= "e.g., Show me the top 10 customers by revenue in 2025",
                key= "query")

            submitted = st.form_submit_button("Generate SQL")

        if submitted and user_query:
            with st.spinner("Analyzing database db and generating query..."):
                if not contains_forbidden_words(user_query):
                    schema_context = self.db_service.get_grounding_context(user_query)
                    response = self.db_service.get_response(user_query, schema_context)
                    st.session_state.generated_sql = response
                else:
                    error_response = self.db_service.get_response(user_query, None)
                    st.session_state.error_message = error_response


        if st.session_state.generated_sql:
            st.subheader("Generated SQL Query")
            st.code(st.session_state.generated_sql, language="sql")

            st.subheader("Query Results Preview")
            st.info("Click 'Execute' to run this query against the database.")

            if st.button("Execute Query"):
                result = self.db_service.execute_query(st.session_state.generated_sql)

                self.display_result(result)
                st.success("Query executed successfully")
        elif st.session_state.error_message:
            st.subheader("Error Message")
            st.markdown(st.session_state.error_message, unsafe_allow_html=True)

def contains_forbidden_words(user_query: str | None):
    forbidden_words = ["drop", "delete", "insert", "update", "alter", "truncate", "grant"]

    # Simple lowercase check
    if any(word in user_query.lower() for word in forbidden_words):
        return True
    return False
