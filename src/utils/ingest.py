import streamlit as st
import inspect
from pathlib import Path
from typing import Any
from langchain_core.documents import Document
from utils.factory import extract_schema_via_sqlite, append_to_vector_store
from utils.parser import parse_table_definitions
from langchain_core.documents import Document as LCDocument

def build_and_load_vector():
    sqlite_schemas = extract_schema_via_sqlite("db/schema.sql")

    DOCS_PATH = Path("src/docs")
    all_table_definitions = {}
    for file in DOCS_PATH.glob("*.md"):
        print(f"Processing file: {file.name}")
        all_table_definitions[file.stem] = parse_table_definitions(md_file_path=file)

    chunks = []
    stable_ids = []

    table_definitions = all_table_definitions.get("01_table_definitions", {})
    column_definitions = all_table_definitions.get("02_column_definitions", {})
    join_rules_definitions = all_table_definitions.get("03_join_rules", {})

    # =========================================================================
    # STEP 1: Build Enriched "Mega Chunks" per Table (Unifies Table + Columns + DDL)
    # =========================================================================
    for table_name, raw_ddl in sqlite_schemas.items():
        if table_name == 'prompt_examples':
            continue

        # Pull the descriptive dictionary items matching this table name
        t_meta = table_definitions.get(table_name, {})
        c_list = column_definitions.get(table_name, [])

        # Format EVERY column for this table into a single clear block of text
        columns_block = ""
        for col in c_list:
            columns_block += (
                f"  - Column: {col.get('Column')}\n"
                f"    Type: {col.get('Data Type', 'UNKNOWN')}\n"
                f"    Label: {col.get('Business label', 'N/A')}\n"
                f"    Definition: {col.get('Definition', 'N/A')}\n"
                f"    Allowed Values: {col.get('Example / Allowed Values', 'N/A')}\n\n"
            )

        # Assemble the comprehensive table context
        enriched_table_payload = inspect.cleandoc(f"""
            === DATABASE TABLE BLUEPRINT ===
            Table Name: {table_name}
            Business Purpose: {t_meta.get("Business purpose", "Fact/Dimension table.")}
            Grain: {t_meta.get("Grain", "Not defined.")}
            Primary Key: {t_meta.get("Primary key", "Managed by system.")}
            Foreign Keys: {t_meta.get("Foreign keys", "None.")}
            Business Use Case: {t_meta.get("Business use", "Analysis and reporting.")}

            --- EXPLICIT COLUMN DEFINITIONS ---
            {columns_block if columns_block else "No explicit column definition metadata available."}

            --- RAW SQL TABLE DDL STRUCTURE ---
            {raw_ddl}
        """)

        table_metadata = {
            "object_type": "enriched_table_schema",
            "table_name": table_name,
            "business_domain": t_meta.get("business_domain", "general"),
            "use_case": t_meta.get("Use case", "general")
        }

        chunks.append(LCDocument(page_content=enriched_table_payload, metadata=table_metadata))
        stable_ids.append(f"table_blueprint::{table_name}")
        print(f"Aggregated fully unified schema context for table: {table_name}")

    # =========================================================================
    # STEP 2: Build a Singular Cohesive Join Matrix (Prevents Drop-outs)
    # =========================================================================
    if join_rules_definitions:
        # Match whatever case your parser generates
        join_rules = join_rules_definitions.get("Join Rules".lower(), [])

        matrix_block = ""
        for rule in join_rules:
            matrix_block += (
                f"- Connection: {rule.get('Left Table')} <-> {rule.get('Right Table')}\n"
                f"  Join Key Connection Column: {rule.get('join_key')}\n"
                f"  Relational Rules: {rule.get('Join Rule')}\n"
                f"  Business Context: {rule.get('Business Meaning')}\n\n"
            )

        enriched_join_payload = inspect.cleandoc(f"""
            === GLOBAL DATABASE RELATIONSHIP & JOIN MATRIX ===
            Use the following exact mappings when connecting tables inside a SQL JOIN block. Never guess columns.

            {matrix_block}
        """)

        join_metadata = {"object_type": "global_join_rules"}

        chunks.append(LCDocument(page_content=enriched_join_payload, metadata=join_metadata))
        stable_ids.append("global_relationship_matrix")
        print("Generated unified global relationship and join matrix.")

    # =========================================================================
    # STEP 3: Push Aggregated Manifest to Vector Store
    # =========================================================================
    vector_store = append_to_vector_store(
        chunks=chunks,
        ids=stable_ids,
        collection_name="db_schema"
    )

    print(f"\nSuccessfully populated vector store with {len(chunks)} cohesive schema blocks.")
    return vector_store