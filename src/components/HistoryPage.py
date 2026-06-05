import streamlit as st
import pandas as pd

class HistoryPage:
    def __init__(self, source_url: str):
        self.source_url = source_url

    def render(self):
        st.title("History Section")
        st.subheader("Recent Queries")

        if "query_history" not in st.session_state:
            st.session_state.query_history = []

        query_history = st.session_state.query_history

        if not query_history:
            st.info("No queries submitted yet. Use the chat to start.")

        print(f"Query history: {query_history}")

        table_data = []
        table_scores = []
        document_data = []
        document_scores = []
        current_history = {}
        history = []
        for index, interaction in enumerate(st.session_state.query_history):
            db_schema_references = interaction.get('db_schema_results')
            query_reference = interaction.get('query_to_run')
            document_references = interaction.get('user_docs_results')
            for index, db_schema_reference in enumerate(db_schema_references):
                document = db_schema_reference[0]
                score = db_schema_reference[1]
                #
                # if document.metadata.id == 'global_relationship_matrix':
                #     table_data.append(document.page_content)
                table_data.append(document.metadata.get("table_name", "N/A"))
                table_scores.append(score)

            for index, db_schema_reference in enumerate(document_references):
                document = db_schema_reference[0]
                score = db_schema_reference[1]

                document_data.append(document.metadata.get("source", "N/A"))
                document_scores.append(score)

            print(table_data)
            print(table_scores)
            print(document_data)
            print(document_scores)

            current_history = {
                "Table": table_data,
                "Query": query_reference,
                "Score": table_scores,
            }

            history.append({
                "user_query": interaction.get("user_query", "something went wrong!"),
                "history": current_history,
            })

            user_query = interaction.get("user_query", "something went wrong!")
        for index, data in enumerate(history):
            query = data.get("user_query", "something went wrong!")
            table_data = data.get("history", "something went wrong!")
            with st.expander(f"{query}", expanded=(index==(len(history)-1))):
                # Display the actual answer generated
                st.markdown(f"**Answer:** {query}")
                st.divider()
                df = pd.DataFrame(table_data)

                # Title or header
                st.caption("🔍 Matched Tables & Scores")

                # High-density, compact display configuration
                st.dataframe(
                    df,
                    column_config={
                        "Table": st.column_config.TextColumn("Table", width="small"),
                        "Query": st.column_config.TextColumn("SQL Snippet", width="medium"),
                        "Score": st.column_config.ProgressColumn(
                            "Score",
                            format="%.2f",
                            min_value=0.0,
                            max_value=1.0,
                            width="small"
                        ),
                    },
                    hide_index=True,
                    use_container_width=True  # Forces table to fit tight sidebars or columns perfectly
                )





