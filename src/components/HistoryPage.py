from typing import Any

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
            return

        print(f"Query history: {query_history}")

        history = []
        for index, interaction in enumerate(st.session_state.query_history):
            db_schema_references = interaction.get('db_schema_results', [])
            query_reference = interaction.get('query_to_run', [])
            document_references = interaction.get('user_docs_results', [])

            table_data = []
            table_scores = []
            document_data = []
            document_scores = []

            if db_schema_references:
                self.append_db_data(db_schema_references, table_data, table_scores)

            if document_references:
                self.append_doc_data(document_data, document_references, document_scores)

            current_table_data = {
                "Table": table_data,
                "Score": table_scores,
            }

            current_doc_data = {
                "Document": document_data,
                "Score": document_scores,
            }

            history.append({
                "user_query": interaction.get("user_query", "something went wrong!"),
                "assistant_response": interaction.get("assistant_response", "N/A"),
                "table_history": current_table_data,
                "doc_history": current_doc_data,
                "sql_query": query_reference
            })

        for index, data in enumerate(history):
            query = data.get("user_query", "something went wrong!")
            response = data.get("assistant_response", "something went wrong!")

            table_data = data.get("table_history", {})
            doc_data = data.get("doc_history", {})

            sql_query = data.get("sql_query", "")

            table_df = pd.DataFrame(table_data)
            doc_df = pd.DataFrame(doc_data)

            min_table_score = table_df["Score"].min() if not table_df.empty else 0.0
            min_docs_score = doc_df["Score"].min() if not doc_df.empty else 0.0

            header_text = (
                f":blue[:material/push_pin:] Run {index + 1} | "
                f"Min Score: :green[:material/table_chart:] {min_table_score:.2f} | "
                f":orange[:material/description:] {min_docs_score:.2f}"
            )
            with st.expander(header_text, expanded=(index == (len(history) - 1))):
                st.caption(f"**Query:** {query}")

                tab1, tab2, tab3, tab4 = st.tabs([
                    ":green[:material/table_chart:] Tables",
                    ":orange[:material/description:] Docs",
                    ":violet[:material/database:] SQL Query",
                    ":red[:material/forum:] Response"
                ])

                with tab1:
                    if not table_df.empty:
                        st.dataframe(
                            data=table_df[["Table", "Score"]],
                            column_config={
                                "Table": st.column_config.TextColumn("Table", width="medium"),
                                "Score": st.column_config.ProgressColumn("Score",
                                                                         format="%.2f",
                                                                         min_value=0.0,
                                                                         max_value=1.0,
                                                                         width="small",
                                                                         color="auto-inverse"),
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.caption("No tables used in this run.")
                with tab2:
                    if not doc_df.empty:
                        st.dataframe(
                            doc_df[["Document", "Score"]],
                            column_config={
                                "Document": st.column_config.TextColumn("Doc Source", width="medium"),
                                "Score": st.column_config.ProgressColumn("Score",
                                                                         format="%.2f",
                                                                         min_value=0.0,
                                                                         max_value=1.0,
                                                                         width="small",
                                                                         color="auto-inverse"),
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.caption("No documents used in this run.")
                with tab3:
                    if sql_query:
                        st.code(sql_query, language="sql")
                    else:
                        st.caption("No sql query used in this run.")
                with tab4:
                    st.markdown(response)
    @staticmethod
    def append_doc_data(document_data: list[Any], document_references, document_scores: list[Any]):
        for doc_reference in document_references:
            document = doc_reference[0]
            score = doc_reference[1]
            document_data.append(document.metadata.get("source", "N/A"))
            document_scores.append(score)

    @staticmethod
    def append_db_data(db_schema_references, table_data: list[Any], table_scores: list[Any]):
        for db_schema_reference in db_schema_references:
            document = db_schema_reference[0]
            score = db_schema_reference[1]

            if document.id == "global_relationship_matrix":
                continue
            table_data.append(document.metadata.get("table_name", "N/A"))
            table_scores.append(score)






