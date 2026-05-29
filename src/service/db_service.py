import re

import streamlit as st
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import OpenAIEmbeddings
from streamlit.elements.widgets.chat import ChatInputValue

class DBService:
    def __init__(self, db_client: SQLDatabase):
        self.db_client = db_client
        self.sql_generation_chain = None

    @staticmethod
    def clean_sql(sql_query: str):
        cleaned = sql_query.strip()
        # Remove ```sql ... ``` or ``` ... ``` wrappers
        cleaned = re.sub(r"^```(?:sql)?\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        return cleaned.strip()

    def create_db_chain(self, llm_client, db_client):
        examples = [
            {
                "input": "List all tables in the database",
                "query": "SELECT name FROM sqlite_master WHERE type='table';"
            },
            {
                "input": "How many kpi definitions are there?",
                "query": "SELECT COUNT(*) FROM kpi_definitions;"
            },
            {
                "input": "Find the highest KPI value achieved last month",
                "query": "SELECT MAX(kpi_value) FROM kpi_logs WHERE log_date >= date('now', '-1 month');"
            }
        ]
        example_prompt = PromptTemplate(
            template="User Input: {input}\nSQL Query: {query}",
            input_variables=["input", "table_info"]
        )

        # example_selector = SemanticSimilarityExampleSelector.from_examples(
        #     examples,
        #     OpenAIEmbeddings(),  # Vectorizes the inputs to check relevance
        #     FAISS,  # In-memory vector store
        #     k=1  # Number of examples to dynamically inject
        # )

        prefix = """You are an expert SQL assistant. 
        Convert the user query to SQL. 
        Given an input question, create a syntactically correct SQLite query to run. 
        CRITICAL: You must return ONLY the executable SQL code and absolutely no other text, 
        including markdown formatting.
        Ensure all datetime formats yield zero-padded hours (HH).
        
        Limit your results to {top_k} rows unless the user asks for more.

        Only use the following tables and schemas:
        {table_info}
        
        Question:
        {input}
        """

        few_shot_prompt = FewShotPromptTemplate(
            # example_selector=example_selector,
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix,
            suffix="User Input: {input}\nSQL Query: ",
            input_variables=["input", "top_k", "table_info"]
        )

        try:
            top_k = 10

            base_generation_chain = create_sql_query_chain(
                llm=llm_client,
                db=db_client,
                prompt=few_shot_prompt,
                k=top_k)

            self.sql_generation_chain = base_generation_chain | RunnableLambda(self.clean_sql)

        except Exception as e:
            error_msg = f"An error occurred while creating your database: {str(e)}"
            st.error(error_msg)

    def get_response(self, user_query: str | ChatInputValue | None):
        try:
            if not self.sql_generation_chain:
                raise ValueError("No database chain provided")
            return self.sql_generation_chain.invoke({"question": user_query})
        except Exception as e:
            error_msg = f"An error occurred while processing your query: {str(e)}"
            st.error(error_msg)

    def execute_query(self, sql: str):
        try:
            if not self.db_client:
                raise ValueError("No database client provided")
            return self.db_client.run(sql)
        except Exception as e:
            error_msg = f"An error occurred while executing your query: {str(e)}"