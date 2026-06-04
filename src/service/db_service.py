import re

import streamlit as st
import pandas as pd

from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from sqlalchemy import text
from streamlit.elements.widgets.chat import ChatInputValue

from src.utils.factory import get_engine, get_vector_store


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

    @staticmethod
    def get_live_examples():
        db_engine = get_engine()
        with db_engine.connect() as conn:
            rows = conn.execute(text("SELECT user_input, sql_query FROM prompt_examples;"))
            # rows = conn.fetchall()
            return [{"input": row[0], "query": row[1]} for row in rows]

    @staticmethod
    def add_new_example(user_input: str, sql_query: str):
        try:
            engine = get_engine()
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO prompt_examples (user_input, sql_query) VALUES (:user_input, :sql_query);"),
                    {"user_input":user_input, "sql_query": sql_query})
        except Exception as e:
            error_msg = f"An error occurred while creating your database: {str(e)}"
            st.error(error_msg)

    def create_db_chain(self, llm_client, db_client):
        example_prompt = PromptTemplate(
            template="User Input: {input}\nSQL Query: {query}",
            input_variables=["input", "table_info"]
        )

        prefix = """You are an expert SQL assistant. 
        Convert the user query to SQL. 
        Given an input question, create a syntactically correct SQLite query to run. 
        
        CRITICAL: 
        1. You are a read-only assistant. You only have access to SELECT data. 
        Never attempt to write INSERT, UPDATE, DELETE, or DROP queries. 
        If a user asks you to change, delete, or add data, politely inform them that you only have read-only access.
        2. You must return ONLY the executable SQL code and absolutely no other text, 
        including markdown formatting.
        3. Ensure all datetime formats yield zero-padded hours (HH).
        4. Limit your results to {top_k} rows unless the user asks for more.

        Only use the following tables and schemas:
        {table_info}
        
        Question:
        {input}
        """

        live_examples = self.get_live_examples()

        few_shot_prompt = FewShotPromptTemplate(
            # example_selector=example_selector,
            examples=live_examples,
            # examples=examples,
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

    def get_response(self, user_query: str | ChatInputValue | None, schema_context: str | None = None):
        try:
            if not self.sql_generation_chain:
                raise ValueError("No database chain provided")
            return self.sql_generation_chain.invoke({
            "schema_context": schema_context,
            "question": user_query})
        except Exception as e:
            error_msg = f"An error occurred while processing your query: {str(e)}"
            st.error(error_msg)

    def execute_query(self, sql: str) -> pd.DataFrame:
        try:
            if not self.db_client:
                raise ValueError("No database client provided")

            df = pd.read_sql(sql, con=self.db_client._engine)
            return df

        except Exception as e:
            error_msg = f"An error occurred while executing your query: {str(e)}"
            st.error(error_msg)
            return pd.DataFrame()  # Return empty df on failure so UI doesn't crash


    def get_grounding_rules(self, user_query: str | ChatInputValue | None):
        if "vector_store" not in st.session_state:
            st.error("No vector store provided")
        vector_store = get_vector_store("db_schema")
        relevant_docs = vector_store.similarity_search(user_query, k=3)
        schema_context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        return schema_context


     # if "llm_client" not in st.session_state:
     #        ValueError("missing llm client in session")
     #
     #    llm = st.session_state.llm_client
     #
     #    chain = prompt_template | llm
     #
     #    response = chain.invoke({
     #        "schema_context": schema_context,
     #        "question": user_query})
     #
     #    return response.content, relevant_docs

