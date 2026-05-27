import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from streamlit.elements.widgets.chat import ChatInputValue

class DBService:
    def __init__(self, client: SQLDatabase):
        self.client = client
        self.db_chain = None

    def create_db_chain(self, llm_client, db_client):
        try:
            self.db_chain = SQLDatabaseChain.from_llm(
                llm=llm_client,
                db=db_client,
                verbose=True)
        except Exception as e:
            error_msg = f"An error occurred while creating your database: {str(e)}"
            st.error(error_msg)

    @staticmethod
    def get_response(db_chain: SQLDatabaseChain, user_query: str | ChatInputValue | None):
        try:
            return db_chain.run(user_query)
        except Exception as e:
            error_msg = f"An error occurred while processing your query: {str(e)}"
            st.error(error_msg)