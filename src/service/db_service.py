import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from streamlit.elements.widgets.chat import ChatInputValue

class DBService:
    def __init__(self, client: SQLDatabase):
        self.client = client
        self.db_chain = None

    def create_db_chain(self, llm_client, db_client):
        examples = [
            {
                "input": "List all tables in the database",
                "query": "SELECT name FROM sqlite_master WHERE type='table';"
            },
            {
                "input": "How many kpi definitions are there?",
                "query": "SELECT COUNT(*) FROM kpi_definitions;"
            }
        ]
        example_prompt = PromptTemplate(
            input_variables=["input", "query"],
            template="User Input: {input}\nSQL Query: {query}"
        )

        prefix = """You are an expert SQL assistant. 
        Convert the user query to SQL. 
        Given an input question, create a syntactically correct SQLite query to run. 
        You must return ONLY the executable SQL code and absolutely no other text.
        Ensure all datetime formats yield zero-padded hours (HH).
        
        Only use the following tables and schemas:
        {table_info}
        """

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix,
            suffix="User Input: {input}\nSQL Query:",
            input_variables=["input", "table_info"]
        )

        try:
            self.db_chain = SQLDatabaseChain.from_llm(
                llm=llm_client,
                db=db_client,
                prompt=few_shot_prompt,
                verbose=True)

        except Exception as e:
            error_msg = f"An error occurred while creating your database: {str(e)}"
            st.error(error_msg)

    def get_response(self, user_query: str | ChatInputValue | None):
        try:
            if not self.db_chain:
                raise ValueError("No database chain provided")
            return self.db_chain.invoke(user_query)
        except Exception as e:
            error_msg = f"An error occurred while processing your query: {str(e)}"
            st.error(error_msg)