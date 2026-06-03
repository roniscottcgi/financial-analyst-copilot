# 07 Recommended Vector Loading Pattern for Sample Documents

## Purpose
This document describes the recommended way to load the sample document set into a vector store for the cohort capstones.

The goal is **not** to upload whole files as large opaque blobs.  
The goal is to create a retrieval layer that preserves:
- document meaning
- category meaning
- source traceability
- workflow relevance
- retrieval quality

This guidance is intentionally high-level. It defines the expected ingestion and retrieval pattern without giving participants a complete implementation.

---

## Scope
This guidance applies to the sample document packs created for the cohort, including mixed:
- `DOCX`
- `PDF`
- optionally `TXT`

and the five business-aligned categories:
- `finance_analyst`
- `customer_support`
- `internal_knowledge`
- `it_service_desk`
- `project_delivery`

---

## What should be loaded

Participants should load **document content plus business metadata**, not just raw extracted text.

For each document, the vector store should preserve:
- file name
- source type
- category
- section title if detected
- chunk id
- chunk text
- optional business tags
- optional use-case tags

---

## Recommended document object types

### 1. Document chunk objects
These are the main retrieval units.

Each chunk should contain:
- the actual extracted text
- the document source
- the category
- the section title or heading if available
- the chunk id

**Recommended object type:** `document_chunk`

This is the most important object type because it is what the assistant retrieves when answering grounded questions.

---

### 2. Document summary objects
Each document should also have one short summary object.

The summary should contain:
- document title
- category
- high-level purpose
- key topics covered
- typical question types it can answer

**Recommended object type:** `document_summary`

This helps retrieval when the user asks broad questions and the system first needs to identify the most relevant document.

---

### 3. Category definition objects
Each category should be represented in the vector store as its own metadata object.

Each category definition should explain:
- what kinds of documents belong there
- what kinds of user questions it supports
- what business workflow it relates to
- examples of relevant terms

**Recommended object type:** `category_definition`

This helps routing and category-aware retrieval.

---

### 4. Workflow question pattern objects
Each category should also have example question patterns.

For example:
- finance analyst questions
- support ticket questions
- internal policy questions
- service desk action questions
- project delivery governance questions

**Recommended object type:** `document_question_pattern`

This gives the retrieval layer semantic examples of how users phrase requests.

---

## Recommended category definitions

## `finance_analyst`
### Meaning
Documents related to financial reporting, KPI definitions, revenue, margin, expense rules, and performance analysis.

### Typical document types
- KPI definition packs
- financial variance analysis
- forecast memos
- expense policy interpretation
- close issue summaries

### Typical user questions
- What caused margin decline this month?
- What is the approved definition of gross margin?
- Which threshold triggers finance review?
- How should revenue variance be summarized?

### Workflow fit
Used in financial analysis, reporting assistance, metric interpretation, and narrative explanation.

---

## `customer_support`
### Meaning
Documents related to customer-facing service handling, escalation guidance, billing response, refund handling, and support response generation.

### Typical document types
- escalation procedures
- billing complaint guidance
- refund rules
- sentiment summaries
- response templates

### Typical user questions
- What is the next step for a billing complaint?
- When does a refund require approval?
- How should the agent respond to a delayed order case?
- What article supports the recommended response?

### Workflow fit
Used in support response drafting, case triage, and human-reviewed customer communication.

---

## `internal_knowledge`
### Meaning
Documents related to employee policies, internal SOPs, onboarding, travel rules, publishing standards, and enterprise knowledge content.

### Typical document types
- travel policy
- onboarding checklist
- access request SOP
- publishing standards
- awareness handbooks

### Typical user questions
- What approvals are needed for international travel?
- What is the access request procedure?
- What does the onboarding checklist include?
- Which document governs this internal process?

### Workflow fit
Used in employee self-service knowledge access and policy-grounded answering.

---

## `it_service_desk`
### Meaning
Documents related to support runbooks, incident procedures, password resets, VPN troubleshooting, priority assignment, and action-oriented service workflows.

### Typical document types
- password reset runbook
- lockout playbook
- VPN issue triage
- priority matrix
- compliance escalation guide

### Typical user questions
- What should I do first for a locked workstation?
- When should a VPN issue be escalated?
- What priority should this ticket be assigned?
- Can the assistant proceed after confirmation?

### Workflow fit
Used in service desk workflows that require grounded procedures, confirmation, and next-step execution.

---

## `project_delivery`
### Meaning
Documents related to delivery governance, dry run failure response, milestone replanning, budget escalation, cutover issues, and client status communication.

### Typical document types
- recovery plan template
- milestone replan checklist
- status update guidance
- budget escalation note
- issue log guidance

### Typical user questions
- What should a recovery plan include?
- When should a budget variance be escalated?
- What content belongs in a delivery status update?
- How should milestone slippage be handled?

### Workflow fit
Used in delivery management, escalation handling, recovery planning, and project governance.

---

## Recommended ingestion pattern

## Step 1: Extract text by file type
Participants should extract text using file-type-appropriate libraries.

### Recommended extraction rules
- `DOCX` -> preserve heading structure where possible
- `PDF` -> extract text page by page; if section structure is weak, use paragraph fallback
- `TXT` -> treat as already extracted text

The ingestion pipeline should not assume all formats behave the same.

---

## Step 2: Detect category before loading
Each file should be assigned a category before loading into the vector store.

### Recommended options
- folder-based category assignment
- filename/tag-based assignment
- rule-based keyword classification
- optional manual override

### Minimum requirement
Every file must be tagged with one category:
- `finance_analyst`
- `customer_support`
- `internal_knowledge`
- `it_service_desk`
- `project_delivery`
- or `uncategorized`

This category should be stored as metadata with every chunk.

---

## Step 3: Create one document summary object per file
Before chunking, create a short document-level summary object.

Example fields:
- `document_title`
- `source_file`
- `file_type`
- `category`
- `document_purpose`
- `key_topics`
- `typical_question_types`

This object helps retrieval when a broad user question first needs document-level matching.

---

## Step 4: Chunk by meaning first
Do **not** chunk only by size.

Recommended order:
1. split by heading or section if available
2. if a section is too large, split by paragraph
3. only then apply size-based fallback chunking if required

This preserves meaning and improves citation quality.

### Recommended chunking rule
- one chunk per section where possible
- one chunk per paragraph block when sectioning is unavailable
- add overlap only when needed for continuity

Do not start with arbitrary 500-token slices if semantic boundaries are available.

---

## Step 5: Build chunk metadata
Every chunk loaded into the vector store should include metadata such as:

- `object_type = document_chunk`
- `source_file`
- `file_type`
- `category`
- `section_title`
- `chunk_id`
- `document_title`
- `use_case`
- `source_pack`
- `page_number` if available
- `sensitivity_level` if relevant

This metadata matters because later participants can:
- filter by category
- filter by file type
- inspect source evidence
- debug retrieval quality

---

## Step 6: Build clean embedding text
The embedding payload should not be raw text only.

Recommended embedding text for each chunk:

```text
Object type: document_chunk
Category: project_delivery
Source file: dry_run_recovery_plan_template.docx
Section title: Escalation
Chunk ID: dry_run_recovery_plan_template_03_01
Document purpose: guidance for recovery planning after failed dry run
Content: A recovery plan after a failed dry run should include issue summary, systems impacted, root cause hypothesis, mitigation steps, owner, and deadline.
Use case: project_delivery
```

This is usually better than embedding the plain paragraph alone because it adds retrieval signals.

---

## Step 7: Use stable IDs
Use stable IDs such as:
- `doc::project_delivery::dry_run_recovery_plan_template::03_01`
- `summary::project_delivery::dry_run_recovery_plan_template`
- `category::project_delivery`
- `question::project_delivery::recovery_plan_required_content`

This helps with:
- deduplication
- reloads
- debugging
- auditability

---

## Step 8: Separate collections if useful
Recommended collection design:

### Collection 1: `document_chunks`
Store:
- document chunks
- document summaries

### Collection 2: `category_definitions`
Store:
- category definitions
- category guidance
- category question patterns

This separation can improve retrieval quality because category-routing information does not compete with raw document content.

If participants want a simpler design, they may use one collection with strong metadata tagging. That is acceptable if they can justify it.

---

## Recommended retrieval strategy

When a participant asks a question, retrieval should not be purely broad and blind.

### Recommended order
1. identify or infer likely category
2. retrieve relevant `document_summary` or `category_definition`
3. retrieve relevant `document_chunk`
4. answer only from retrieved evidence
5. cite the source file and chunk id

### Fallback behavior
If category-filtered retrieval returns weak or empty results:
- retry without category filter
- inspect whether category tagging was wrong
- log the mismatch for later correction

This is especially important for ambiguous questions.

---

## Example retrieval flow

### User question
“What approvals are needed for international travel?”

### Good retrieval pattern
1. infer likely category = `internal_knowledge`
2. retrieve category definition and travel policy document summary
3. retrieve top chunks from the travel policy document
4. answer with citations
5. if unsupported, say so clearly

This is better than retrieving across all documents without metadata filtering.

---

## What not to do
Participants should explicitly avoid:
- embedding whole PDFs or DOCX files as single chunks
- skipping category tagging
- skipping document summary objects
- relying only on file names
- mixing uploaded files and schema metadata in one undifferentiated collection
- hiding ingestion inside app startup with no visibility
- answering from the model without retrieved evidence

These patterns usually lead to poor retrieval and weak trust.

---

## Minimum recommendation for participants
Use this as the assignment requirement:

> Parse the sample documents into document chunks and document summaries, assign a category before loading, and store all objects in the vector store with metadata such as category, source file, chunk id, section title, and file type. At minimum, support category-aware retrieval and source-cited answering.

That is enough guidance without giving them the full implementation.

---

## Suggested assignment stretch goals
Participants can extend the design by adding:
- manual category override
- duplicate-file detection
- page number tracking for PDFs
- document-level confidence score
- reranking for retrieved chunks
- evaluation set by category
- hybrid retrieval using category definition + content chunk retrieval

---

## Why this is the right level of guidance
This is **not** spoon-feeding.

You are not giving them code.  
You are giving them:
- the ingestion pattern
- the category model
- the metadata structure
- the retrieval expectation

That is exactly what a strong capstone brief or SOW should do.

---

## Final takeaway
The vector store should help the assistant answer:
- which category the question belongs to
- which document is most relevant
- which chunk contains the evidence
- how to cite the source
- when to fall back because the answer is unsupported

If the ingestion design cannot support those tasks, then the document vector store has not been loaded at the right level.

---

## Do documents need a full definition pack like SQL metadata?

### Short answer
No. In most cases, documents do **not** need the same `01` to `05` style definition treatment as SQL schema metadata.

That level of metadata makes sense for SQL because:
- tables and columns are abstract
- business meaning is often not obvious
- joins are easy to get wrong
- text-to-SQL quality depends heavily on business metadata

Documents are different because the document content itself already carries much of the meaning.

---

## Recommended balance for document metadata

For document-based RAG, the right balance is:

### Required
- category definition at the **category** level
- document summary at the **document** level
- chunk metadata at the **chunk** level

### Optional
- a few question-pattern examples
- manual tagging for tricky documents
- quality labels such as `approved`, `draft`, or `reference`

This is enough to teach:
- ingestion
- chunking
- metadata
- retrieval
- grounded answering

without overengineering the solution.

---

## What is enough for documents

### Category level
Store:
- what the category means
- what kinds of questions the category should answer
- what workflow or use case the category supports

### Document level
Store:
- title
- short summary
- category
- file type
- source file
- optional status such as approved or reference

### Chunk level
Store:
- section title
- chunk id
- page number if available
- source file
- category

That is usually enough for a strong document retrieval design.

---

## What not to add unless justified
Participants should generally avoid creating:
- long semantic dictionaries for every document
- detailed business-definition packs that restate the document itself
- extra metadata files that repeat obvious content
- metadata layers that are more complex than the original document set

That usually turns into metadata about metadata and wastes project time.

---

## Rule of thumb for participants

**SQL metadata needs strong business definitions.**  
**Document metadata needs strong source traceability.**

That is the difference.

For SQL, the retrieval layer should help answer:
- what table to use
- what column to use
- how tables join
- what the business meaning is

For documents, the retrieval layer should help answer:
- which category the question belongs to
- which document is most relevant
- which chunk contains the evidence
- how to cite the source
- when to fall back because the answer is unsupported

---

## Recommended participant guidance
Use this as the design expectation:

> Do not over-model document metadata. Use category definitions, document summaries, and chunk-level source metadata as the baseline. Only add more metadata layers if they clearly improve retrieval quality, traceability, or workflow fit.

This keeps the solution practical and aligned to grounded answering.

