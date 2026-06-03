import httpx
import streamlit as st

from pathlib import Path
from typing import Any
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from utils.factory import extract_schema_via_sqlite
from utils.parser import parse_table_definitions

def build_and_load_vector():
    with st.spinner("Initializing vector store..."):
        sqlite_schemas = extract_schema_via_sqlite("db/schema.sql")

        DOCS_PATH = Path("src/docs")
        all_table_definitions = {}
        for file in DOCS_PATH.glob("*.md"):
            print(f"Processing file: {file.name}")
            all_table_definitions[file.stem] = parse_table_definitions(md_file_path=file)

        documents = []
        stable_ids = []

        for table_name, table_body in sqlite_schemas.items():
            if table_name == 'prompt_examples':
                break

            table_definitions = all_table_definitions.get(
                "01_table_definitions",
                None)
            if table_definitions is not None:
                append_table_documents(documents, table_name, table_definitions, table_body, stable_ids)

            column_definitions = all_table_definitions.get(
                "02_column_definitions",
                None)
            if column_definitions is not None:
                append_column_documents(documents, table_name, column_definitions, stable_ids)

        join_rules_definitions = all_table_definitions.get(
            "03_join_rules",
            None)

        if join_rules_definitions is not None:
            append_join_rule_documents(documents, join_rules_definitions, stable_ids)

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=st.secrets["OPENAI_API_KEY"],
            http_client=httpx.Client(verify=False))

        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            ids=stable_ids)

        print(f"\nSuccessfully populated vector store with {len(documents)} enriched table schemas.")
        st.toast("Vector store initialized!")
    return vector_store


def append_join_rule_documents(documents: list[Any], join_rules_definitions: Any | None, stable_ids: list[Any]):
    join_rules = join_rules_definitions.get("Join Rules".lower(), [])
    for join_rule in join_rules:
        left_table = join_rule.get("Left Table")
        right_table = join_rule.get("Right Table")

        join_metadata, join_payload = get_join_rules_meta(join_rule, left_table, right_table)

        join_id = f"join::{left_table}::{right_table}"

        doc = Document(
            page_content=join_payload,
            metadata=join_metadata
        )
        documents.append(doc)
        stable_ids.append(join_id)


def append_column_documents(documents: list[Any], table_name, column_definitions: Any | None, stable_ids: list[Any]):
    columns_list = column_definitions.get(table_name, [])
    for col in columns_list:
        col_name = col.get('Column')

        column_metadata, column_payload = get_column_definitions_meta(
            col,
            col_name,
            column_definitions,
            table_name)

        column_id = f"column::{table_name}::{col_name}"

        column_doc = Document(
            page_content=column_payload,
            metadata=column_metadata
        )
        documents.append(column_doc)
        stable_ids.append(column_id)
    # print(f"Loaded and cross-referenced columns: {columns_list} for table: {table_name}")


def append_table_documents(documents: list[Any], table_name, table_definitions: Any | None, table_body,
                           stable_ids: list[Any]):
    table_metadata, table_payload = get_table_definition_meta(
        table_body,
        table_definitions,
        table_name)

    table_id = f"table::{table_name}"

    doc = Document(
        page_content=table_payload,
        metadata=table_metadata)

    documents.append(doc)
    stable_ids.append(table_id)
    print(f"Loaded and cross-referenced table: {table_name}")


def get_join_rules_meta(join_rule, left_table, right_table) -> tuple[dict[str, str | Any], str]:
    join_payload = f"""
                Object type: join_rule
                Left Table: {left_table}
                Right Table: {right_table}
                Join Key: {join_rule.get("join_key", "Join Key")}
                Join Type or Expected Relationship: {join_rule.get("Join Rule", "None.")}
                Business Meaning of Join: {join_rule.get("Business Meaning", "None.")}
                Common Usage Pattern: {join_rule.get("usage_pattern", "low")}
            """.strip()

    join_metadata = {
        "object_type": "join_rule",
        "left_table": left_table,
        "right_table": right_table,
        "join_key": join_rule.get("join_key", "Join Key"),
        "join_type_or_expected_relationship": join_rule.get("join_type", "schema_definitions.md"),
        "business_meaning_of_join": join_rule.get("business_meaning", "general"),
        "common_usage_pattern": join_rule.get("usage_pattern", "low")
    }
    return join_metadata, join_payload

def get_column_definitions_meta(col, col_name, column_definitions, table_name) -> tuple[dict[str, str | Any], str]:
    column_payload = f"""
                Object type: column_definition
                Table: {table_name}
                Column: {col_name}
                Business label: {col.get("Business label", col_name)}
                Business Definition: {col.get("Definition", "Column asset.")}
                Data Type: {col.get("Data Type", "Column asset.")}
                Allowed values: {col.get("Example / Allowed Values", "All values applicable.")}
                Metric usage: {col.get("metric_usage", "None.")}
                Sensitivity: {col.get("sensitivity", "low")}
                Join Usage: {col.get("Join / Metric Usage", "None.")}
                Use case: {column_definitions.get("use_case", "general")}
            """.strip()

    column_metadata = {
        "object_type": "column_definition",
        "use_case": column_definitions.get("use_case", "general"),
        "table_name": table_name,
        "column_name": col_name,
        "source_file": column_definitions.get("source_file", "schema_definitions.md"),
        "business_domain": column_definitions.get("business_domain", "general"),
        "sensitivity_level": col.get("sensitivity", "low")
    }
    return column_metadata, column_payload

def get_table_definition_meta(table_body, table_definitions, table_name) -> tuple[dict[str, str | Any], str]:
    table_definition = table_definitions.get(table_name, [])
    table_payload = f"""
            Object type: table_definition
            Table: {table_name}
            Business purpose: {table_definition.get("Business purpose", "Fact/Dimension table for system operations.")}
            Grain: {table_definition.get("Grain", "Not explicitly defined.")}
            Primary key: {table_definition.get("Primary key", "Managed by system.")}
            Foreign keys: {table_definition.get("Foreign keys", "None.")}
            Business use: {table_definition.get("Business use", "Used for data analysis and reporting.")}
            Use case: {table_definition.get("Use case", "general")}
        """.strip()

    # Step 2: Extract all mandatory metadata fields
    table_metadata = {
        "object_type": "table_definition",
        "use_case": table_definition.get("use_case", "general"),
        "table_name": table_name,
        "source_file": table_definition.get("source_file", "schema_definitions.md"),
        "business_domain": table_definition.get("business_domain", "general"),
        "sensitivity_level": table_definition.get("sensitivity_level", "low"),
        # Keep raw DDL inside metadata so the LLM can read it *after* retrieval
        "raw_ddl": table_body}
    return table_metadata, table_payload