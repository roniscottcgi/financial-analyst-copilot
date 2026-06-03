# Quick Start for Participants and Guide for projects in general


## How to use this metadata pack
1. Read the table definitions first to understand the business story.
2. Read the column definitions before writing SQL.
3. Use the join rules instead of guessing relationships.
4. Use the example business questions to test your SQL assistant or text-to-SQL flow.

## Recommended prompt pattern for SQL copilots
When generating SQL:
- identify the business question
- identify the likely fact table
- identify required dimensions and filters
- use the join rules from the metadata pack
- use KPI definitions when the question is about metric meaning
- explain assumptions if the business question is ambiguous

## Recommended workflow
- Start with metadata
- Then write SQL
- Then validate against expected business meaning
- Then summarize results with citations or references to definitions

## Important reminder
Do not treat this schema like raw tables only.
Treat it as a governed business model:
- `revenue_facts` = finance facts
- `support_tickets` = support operations facts
- `policy_articles` = structured article metadata
- `workflow_feedback` = adoption and trust signals
