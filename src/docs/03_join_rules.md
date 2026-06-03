# Join Rules

## `Join Rules`
| Left Table | Right Table | Join Rule | Business Meaning |
|---|---|---|---|
| `support_tickets` | `customers` | `support_tickets.customer_id = customers.customer_id` | Join ticket context to customer attributes for support and segmentation. |
| `support_tickets` | `products` | `support_tickets.product_id = products.product_id` | Join ticket context to product family and support tier. |
| `support_tickets` | `agents` | `support_tickets.agent_id = agents.agent_id` | Join ticket ownership to team, location, and skill level. |
| `ticket_events` | `support_tickets` | `ticket_events.ticket_id = support_tickets.ticket_id` | Reconstruct ticket lifecycle and event history. |
| `revenue_facts` | `finance_periods` | `revenue_facts.period_id = finance_periods.period_id` | Join facts to fiscal period attributes. |
| `revenue_facts` | `customers` | `revenue_facts.customer_id = customers.customer_id` | Analyze finance metrics by customer and segment. |
| `revenue_facts` | `products` | `revenue_facts.product_id = products.product_id` | Analyze finance metrics by product and product family. |