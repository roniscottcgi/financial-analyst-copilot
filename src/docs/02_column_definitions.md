# Column Definitions

## `customers`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `customer_id` | Customer ID | Unique identifier for a customer. | `INT` | example: 101 | Primary key; joins to support_tickets.customer_id and revenue_facts.customer_id |
| `customer_name` | Customer Name | Business-facing customer name. | `VARCHAR(120)` | example: Customer 12 | Display/reporting field |
| `segment` | Customer Segment | Commercial segment such as Enterprise, MidMarket, or Strategic. | `VARCHAR(40)` | Enterprise | MidMarket | Strategic | Filter and grouping field |
| `region` | Region | Geographic region used for reporting and support grouping. | `VARCHAR(40)` | NA | EMEA | APAC | Filter and grouping field |
| `status` | Customer Status | Lifecycle status such as Active or AtRisk. | `VARCHAR(20)` | Active | AtRisk | Useful for support and revenue risk analysis |
| `created_date` | Created Date | Date the customer record was created. | `DATE` | 2026-01-15 | Useful for cohort/trend analyses |

## `products`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `product_id` | Product ID | Unique product identifier. | `INT` | example: 3 | Primary key; joins to support_tickets.product_id and revenue_facts.product_id |
| `product_name` | Product Name | Business name of the product. | `VARCHAR(120)` | example: Product 3 | Display/reporting field |
| `product_family` | Product Family | Higher-level grouping such as Analytics, Platform, Security, or Support. | `VARCHAR(60)` | Analytics | Platform | Security | Support | Grouping field |
| `support_tier` | Support Tier | Service tier associated with the product. | `VARCHAR(30)` | Standard | Premium | Gold | Service analytics / prioritization |
| `active_flag` | Active Flag | Indicates whether the product is currently active. | `CHAR(1)` | Y | N | Filter field |

## `agents`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `agent_id` | Agent ID | Unique identifier for the agent. | `INT` | example: 17 | Primary key; joins to support_tickets.agent_id |
| `agent_name` | Agent Name | Business display name of the agent. | `VARCHAR(120)` | example: Agent 17 | Display field |
| `team_name` | Team Name | Functional team assignment. | `VARCHAR(60)` | L1 Support | L2 Support | Finance Ops | Knowledge Ops | Filter/grouping field |
| `location` | Location | Delivery location or geography. | `VARCHAR(40)` | US | Canada | India | UK | Filter/grouping field |
| `skill_level` | Skill Level | Experience tier such as Associate, Intermediate, or Senior. | `VARCHAR(20)` | Associate | Intermediate | Senior | Capacity/quality analysis |

## `support_tickets`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `ticket_id` | Ticket ID | Unique support ticket identifier. | `INT` | example: 1001 | Primary key |
| `customer_id` | Customer ID | Customer associated with the ticket. | `INT` | example: 12 | FK to customers |
| `product_id` | Product ID | Product related to the issue or request. | `INT` | example: 4 | FK to products |
| `agent_id` | Agent ID | Assigned or owning agent. | `INT` | example: 8 | FK to agents |
| `opened_date` | Opened Date | Date the ticket was opened. | `DATE` | 2026-04-11 | Time filter |
| `priority` | Priority | Business urgency classification. | `VARCHAR(20)` | P1 | P2 | P3 | P4 | SLA/queue analysis |
| `status` | Status | Ticket state such as Open, Pending, Resolved, or Closed. | `VARCHAR(20)` | Open | Pending | Resolved | Closed | Backlog/flow analysis |
| `issue_category` | Issue Category | Business issue type. | `VARCHAR(60)` | Password Reset | VPN Access | Billing Question | Refund Request | Data Access | Device Compliance | Routing/volume analysis |
| `resolution_code` | Resolution Code | Final or current handling outcome. | `VARCHAR(60)` | Resolved | Escalated | Awaiting User | Knowledge Article Used | Manual Review | Effectiveness/quality analysis |

## `ticket_events`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `event_id` | Event ID | Unique event identifier. | `INT` | example: 9001 | Primary key |
| `ticket_id` | Ticket ID | Parent ticket for the event. | `INT` | example: 1001 | FK to support_tickets |
| `event_ts` | Event Timestamp | Timestamp of the event. | `DATETIME` | 2026-04-11 09:00:00 | Sequence/timing analysis |
| `event_type` | Event Type | Type of event such as Created, Note, Assignment, Resolution, or User Reply. | `VARCHAR(40)` | Created | Note | Assignment | Resolution | User Reply | Process step analysis |
| `event_note` | Event Note | Narrative note describing the event. | `VARCHAR(255)` | example: Ticket 1001 event 2 for VPN Access | Audit/context |

## `kpi_definitions`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `kpi_id` | KPI ID | Unique KPI identifier. | `INT` | example: 1 | Primary key |
| `kpi_name` | KPI Name | Business name of the KPI. | `VARCHAR(120)` | First Response Time | Resolution Time | Gross Margin | Semantic label |
| `kpi_description` | KPI Description | Plain-language description of what the KPI measures. | `VARCHAR(255)` | example: Average minutes to first human response | Definition |
| `calculation_rule` | Calculation Rule | Business logic or formula used to derive the KPI. | `VARCHAR(255)` | example: sum(first_response_minutes)/count(ticket_id) | Metric logic |
| `owner_team` | Owner Team | Team responsible for the KPI definition. | `VARCHAR(60)` | Support Ops | Finance Ops | Knowledge Ops | Governance |

## `finance_periods`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `period_id` | Period ID | Unique fiscal period identifier. | `INT` | example: 4 | Primary key |
| `fiscal_year` | Fiscal Year | Fiscal year for the period. | `INT` | 2026 | Time hierarchy |
| `fiscal_month` | Fiscal Month | Fiscal month number. | `INT` | 4 | Time hierarchy |
| `period_start` | Period Start | Start date of the fiscal period. | `DATE` | 2026-04-01 | Time filter |
| `period_end` | Period End | End date of the fiscal period. | `DATE` | 2026-04-28 | Time filter |
| `close_status` | Close Status | Accounting close status such as Open or Closed. | `VARCHAR(20)` | Open | Closed | Finance process control |

## `revenue_facts`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `revenue_id` | Revenue ID | Unique fact row identifier. | `INT` | example: 250 | Primary key |
| `period_id` | Period ID | Fiscal period reference. | `INT` | example: 4 | FK to finance_periods |
| `customer_id` | Customer ID | Customer reference. | `INT` | example: 12 | FK to customers |
| `product_id` | Product ID | Product reference. | `INT` | example: 4 | FK to products |
| `recognized_revenue` | Recognized Revenue | Revenue recognized in the period. | `DECIMAL(14,2)` | example: 24000.50 | Primary measure |
| `cost_amount` | Cost Amount | Direct cost associated with that revenue. | `DECIMAL(14,2)` | example: 15200.10 | Primary measure |
| `margin_amount` | Margin Amount | Revenue minus direct cost. | `DECIMAL(14,2)` | example: 8800.40 | Primary measure |

## `policy_articles`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `article_id` | Article ID | Unique article identifier. | `INT` | example: 6 | Primary key |
| `article_title` | Article Title | Title of the article or policy entry. | `VARCHAR(160)` | example: Budget Variance Escalation | Display/title |
| `policy_domain` | Policy Domain | Business domain for the article. | `VARCHAR(60)` | Policy | Support | Project Delivery | Customer Support | Internal Knowledge | Filter/grouping field |
| `version_no` | Version Number | Version identifier of the policy/article. | `VARCHAR(20)` | v2.0 | Version control |
| `effective_date` | Effective Date | Date the article version became effective. | `DATE` | 2025-06-30 | Version/date filtering |
| `article_summary` | Article Summary | Short summary of article content. | `VARCHAR(255)` | example: Escalate when variance exceeds threshold. | Search/display aid |

## `workflow_feedback`
| Column | Business Label | Definition | Data Type | Example / Allowed Values | Join / Metric Usage |
|---|---|---|---|---|---|
| `feedback_id` | Feedback ID | Unique feedback event identifier. | `INT` | example: 77 | Primary key |
| `use_case_name` | Use Case Name | Name of the use case receiving feedback. | `VARCHAR(80)` | Financial Analyst Copilot | Customer Support Automation | Internal Knowledge Assistant | IT Service Desk Agentic Assist | Filter/grouping field |
| `actor_role` | Actor Role | Role of the person giving feedback. | `VARCHAR(60)` | Analyst | Support Agent | Architect | Delivery Lead | Filter/grouping field |
| `event_date` | Event Date | Date the feedback event was recorded. | `DATE` | 2026-05-17 | Trend analysis |
| `confidence_score` | Confidence Score | Numeric confidence rating for the AI-assisted result. | `DECIMAL(5,2)` | example: 4.35 | Adoption/trust metric |
| `adopted_flag` | Adopted Flag | Indicates whether the output was adopted in practice. | `CHAR(1)` | Y | N | Adoption metric |
| `feedback_note` | Feedback Note | Qualitative comment on usefulness, grounding, trust, or workflow fit. | `VARCHAR(255)` | example: Grounded answer was useful and cited correctly | Qualitative evidence |
