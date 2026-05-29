import re

import streamlit as st
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnableLambda
from sqlalchemy.engine import row
from streamlit.elements.widgets.chat import ChatInputValue

from src.utils.factory import get_database_client


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
        if "db_connection" not in st.session_state:
            ValueError("No database connection provided")
        db_client, db_connection = get_database_client()
        cursor = db_connection.cursor()
        cursor.execute("SELECT user_input, sql_query FROM prompt_examples;")
        rows = cursor.fetchall()
        return [{"input": row[0], "query": row[1]} for row in rows]

    def create_db_chain(self, llm_client, db_client):
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

    def add_new_example(self, user_input: str, sql_query: str):
        if "db_connection" not in st.session_state:
            ValueError("No database connection provided")
        db_client, db_connection = get_database_client()
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO prompt_examples (user_input, sql_query) VALUES (?, ?);", (user_input, sql_query))
        db_connection.commit()