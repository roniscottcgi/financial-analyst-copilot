# Table Definitions

## `customers`
**Business purpose**  
Master list of customers used across support, revenue, and workflow analysis.

**Grain**  
One row per customer.

**Primary key**  
`customer_id`

**Business use**  
- Join customer context into tickets, revenue, and support analysis.
- Segment KPI analysis by region, status, and customer type.

## `products`
**Business purpose**  
Reference table for products or service offerings tied to revenue and support cases.

**Grain**  
One row per product.

**Primary key**  
`product_id`

**Business use**  
- Product-level support and revenue analysis.
- Product family rollups for KPI and case trend reporting.

## `agents`
**Business purpose**  
Reference table for internal personnel handling support, finance operations, or knowledge operations.

**Grain**  
One row per agent/user.

**Primary key**  
`agent_id`

**Business use**  
- Measure workload and performance by team or skill level.
- Link ticket ownership to operational teams.

## `support_tickets`
**Business purpose**  
Core operational fact table for customer and employee support requests.

**Grain**  
One row per support ticket.

**Primary key**  
`ticket_id`

**Foreign keys**  
- `customer_id -> customers.customer_id`
- `product_id -> products.product_id`
- `agent_id -> agents.agent_id`

**Business use**  
- Core table for support operations dashboards.
- Used for counts, backlog, category trends, and queue analysis.

## `ticket_events`
**Business purpose**  
Event history for each support ticket.

**Grain**  
One row per event on a ticket.

**Primary key**  
`event_id`

**Foreign keys**  
- `ticket_id -> support_tickets.ticket_id`

**Business use**  
- Reconstruct ticket lifecycle.
- Calculate process timings and event-driven workflow metrics.
- Useful for audit trails.

## `kpi_definitions`
**Business purpose**  
Business glossary for KPIs used by copilots and dashboards.

**Grain**  
One row per KPI definition.

**Primary key**  
`kpi_id`

**Business use**  
- Ground Financial Analyst Copilot answers in approved definitions.
- Provide semantic context before SQL summarization.

## `finance_periods`
**Business purpose**  
Reference table for fiscal reporting periods.

**Grain**  
One row per fiscal period.

**Primary key**  
`period_id`

**Business use**  
- Time dimension for financial reporting.
- Needed for monthly trend, period comparison, and close-status logic.

## `revenue_facts`
**Business purpose**  
Fact table for revenue and margin reporting.

**Grain**  
One row per customer-product-period combination in the sample dataset.

**Primary key**  
`revenue_id`

**Foreign keys**  
- `period_id -> finance_periods.period_id`
- `customer_id -> customers.customer_id`
- `product_id -> products.product_id`

**Business use**  
- Core finance fact table for KPI questions.
- Used for revenue, margin, and trend analysis.

## `policy_articles`
**Business purpose**  
Structured catalog of policy and knowledge article records.

**Grain**  
One row per policy article.

**Primary key**  
`article_id`

**Business use**  
- Lightweight structured metadata for RAG and policy lookup.
- Useful for filtering article types before document retrieval.

## `workflow_feedback`
**Business purpose**  
Tracks user feedback and adoption signals for workflow-oriented AI use cases.

**Grain**  
One row per feedback event.

**Primary key**  
`feedback_id`

**Business use**  
- Tracks adoption and trust, which is important for A3F-style measurement.
- Useful for feedback loops and solution refinement.
