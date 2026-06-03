# 06 Recommended Vector Loading Pattern for SQL Schema Metadata

## Purpose
This document describes the recommended way to load SQL schema metadata into a vector store for the  cohort capstones.

The goal is **not** to store raw DDL only.  
The goal is to store **schema meaning**, **join meaning**, and **business usage context** so the assistant can retrieve the right table, column, and join guidance before generating SQL or explaining results.

This guidance is intentionally high-level. It defines the **retrieval architecture expectation** without giving participants a full implementation.

---

## Objective
Use the metadata pack files:

- `01_table_definitions.md`
- `02_column_definitions.md`
- `03_join_rules.md`
- `04_example_business_questions.md`
- `05_quick_start_for_participants.md`

to create a **business-aware retrieval layer** for text-to-SQL, SQL explanation, and workflow-oriented copilot scenarios.

---

## What should be loaded

Load all 5 metadata files into the vector store, but treat them as **different object types**.

### 1. Table definition objects
Source:
- `01_table_definitions.md`

Each table should become one or more vector objects with:
- table name
- business purpose
- grain
- primary key
- foreign keys
- business use

**Recommended object type:** `table_definition`

---

### 2. Column definition objects
Source:
- `02_column_definitions.md`

Each column should become its own vector object, or a small grouped object, with:
- table name
- column name
- business label
- business definition
- data type
- allowed values
- metric usage
- sensitivity
- join usage

**Recommended object type:** `column_definition`

This is especially important for:
- ambiguous business terms
- metric fields
- filter fields
- coded status columns

---

### 3. Join rule objects
Source:
- `03_join_rules.md`

Each join rule should become a vector object with:
- left table
- right table
- join key
- join type or expected relationship
- business meaning of the join
- common usage pattern

**Recommended object type:** `join_rule`

This is critical because text-to-SQL systems often fail not on table selection, but on **wrong joins**.

---

### 4. Business question pattern objects
Source:
- `04_example_business_questions.md`

Each example question should become a retrieval object with:
- use case
- natural language question
- relevant tables
- likely joins
- expected measures
- expected filters
- optional SQL intent tag

**Recommended object type:** `business_question_pattern`

This gives the model semantic examples of how users ask questions.

---

### 5. Quick-start / workflow guidance objects
Source:
- `05_quick_start_for_participants.md`

These should not dominate retrieval, but they are useful for:
- query planning
- explaining how to approach schema exploration
- reinforcing workflow steps

**Recommended object type:** `usage_guidance`

---

## Recommended loading pattern

## Step 1: Parse the files into structured records
Do **not** embed the 5 markdown files as giant blobs.

Instead, parse them into smaller records.

Examples:
- one record per table
- one record per column
- one record per join
- one record per business question
- one record per guidance section

That gives much better retrieval quality than embedding entire pages.

---

## Step 2: Add metadata to every vector object
Every stored chunk/object should include metadata such as:

- `object_type`
  - `table_definition`
  - `column_definition`
  - `join_rule`
  - `business_question_pattern`
  - `usage_guidance`

- `use_case`
  - `financial_analyst`
  - `customer_support`
  - `internal_knowledge`
  - `it_service_desk`
  - `general`

- `table_name`
- `column_name` if applicable
- `source_file`
- `business_domain`
- `sensitivity_level`
- `join_group` if applicable

This metadata matters because later participants can filter retrieval by:
- object type
- use case
- table
- domain

That makes retrieval much stronger.

---

## Step 3: Build clean embedding text for each object
For each vector object, create a clean text payload that combines the most useful fields.

### Example: table object
```text
Object type: table_definition
Table: revenue_facts
Business purpose: Fact table for revenue and margin reporting.
Grain: One row per customer-product-period combination.
Primary key: revenue_id
Foreign keys: period_id -> finance_periods, customer_id -> customers, product_id -> products
Business use: Used for revenue, margin, and trend analysis.
Use case: financial_analyst
```

### Example: column object
```text
Object type: column_definition
Table: support_tickets
Column: priority
Business label: Ticket Priority
Definition: Business urgency classification for a support request.
Allowed values: P1, P2, P3, P4
Metric usage: backlog by priority, SLA analysis
Sensitivity: low
Use case: customer_support, it_service_desk
```

### Example: join object
```text
Object type: join_rule
Join: support_tickets.customer_id = customers.customer_id
Business meaning: connects operational support requests to customer master context
Common usage: support volume by customer segment and region
Use case: customer_support
```

This is better than embedding raw markdown only.

---

## Step 4: Chunk by object, not by page
Recommended chunking rule:

- **Tables:** one chunk per table
- **Columns:** one chunk per column, or one chunk per 3 to 5 related columns if fewer objects are preferred
- **Join rules:** one chunk per join
- **Business questions:** one chunk per question pattern
- **Guidance:** one chunk per guidance topic

Do not chunk by arbitrary token size first.  
Chunk by **semantic object boundary** first.

---

## Step 5: Load into vector store with stable IDs
Use stable IDs such as:

- `table::revenue_facts`
- `column::support_tickets::priority`
- `join::support_tickets::customers`
- `question::financial_analyst::margin_by_product_family`
- `guide::participant_quick_start::schema_exploration`

This helps with:
- debugging
- deduplication
- reloading
- metadata inspection

---

## Step 6: Retrieval strategy
When a participant asks a question, retrieval should not be one broad search only.

A better recommendation is:

### Retrieval order
1. retrieve relevant `business_question_pattern`
2. retrieve relevant `table_definition`
3. retrieve relevant `column_definition`
4. retrieve relevant `join_rule`
5. optionally retrieve `usage_guidance`

That gives the model both:
- business intent
- schema meaning
- join logic

---

## Step 7: Use metadata filtering
Recommend that participants filter by likely use case when possible.

Examples:
- finance question -> prefer `financial_analyst`
- service desk question -> prefer `it_service_desk`
- support response question -> prefer `customer_support`

Also allow a fallback with no filter if filtered retrieval returns weak results.

---

## Step 8: What not to do
Do **not** try to:
- embed the full SQL DDL only
- store giant markdown documents as one chunk each
- skip join rules
- skip column-level business meaning
- rely only on table names
- mix schema objects and user question history in the same collection without metadata separation

That usually causes weak retrieval.

---

## Minimum recommendation
Use this as your assignment requirement guide:

> Parse the 5 metadata markdown files into schema objects and load them into a vector store using object-based chunking. At minimum, store table definitions, key column definitions, join rules, and example business question patterns with metadata tags such as object type, use case, table name, and source file.

The above provides you enough guidance to help you with full implementation.

---

## Recommended collection design
Use a simple three-collection approach:

### Collection 1: `schema_metadata`
Store:
- table definitions
- column definitions
- join rules

### Collection 2: `business_question_patterns`
Store:
- example questions by use case

### Collection 3: `usage_guidance`
Store:
- quick-start and workflow guidance

This separation keeps retrieval cleaner and helps you participants learn the architecture properly.

---

## Final takeaway
The retrieval layer should help the assistant answer:
- what table to use
- what column to use
- how tables join
- what the business meaning is
- what kinds of questions belong to each use case

## Important 
If the schema metadata cannot support those tasks, then the vector store has not been loaded at the right level.
