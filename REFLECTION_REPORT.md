# Beaver's Choice Paper Company – Multi-Agent System: Reflection Report

## 1. Explanation of the Multi-Agent System

### 1.1 Architecture and Workflow

The system uses **four agents** (within the maximum of five):

1. **Orchestrator Agent** – Receives every customer request and decides which specialist to call. It can also request a financial summary. It returns a single, customer-facing response that summarizes outcomes and explains decisions (e.g. quote rationale, why an order could not be fulfilled).

2. **Inventory Agent** – Handles stock questions and reordering:
   - Uses **get_all_inventory** and **get_stock_level** to answer “what do we have?”
   - Uses **create_transaction** with `transaction_type='stock_orders'` to place reorders when stock is low.

3. **Quoting Agent** – Handles quote requests:
   - Uses **search_quote_history** for similar past quotes and pricing guidance.
   - Uses **get_stock_level** and **generate_financial_report** (inventory summary with unit prices) to build quotes.
   - Uses **get_supplier_delivery_date** for delivery estimates and **get_cash_balance** when relevant.

4. **Sales Agent** – Handles order fulfillment:
   - Uses **get_stock_level** before fulfilling.
   - Uses **create_transaction** with `transaction_type='sales'` to record sales.
   - Uses **get_supplier_delivery_date** and **get_cash_balance** for delivery and context.

All agents receive a **RequestContext** containing `request_date` so every DB and delivery query uses the same “as of” date (e.g. the sample request date).

### 1.2 Decision-Making and Design Choices

- **Single entry point**: One orchestrator keeps the flow clear and makes it easy to add rationale and avoid leaking internal details in the final reply.
- **Delegation via tools**: The orchestrator has three tools (`delegate_to_inventory`, `delegate_to_quoting`, `delegate_to_sales`) that call the corresponding agent with the same context. This matches the rubric’s requirement for an orchestrator that “manages task delegation to other agents.”
- **Starter helpers in tools**: Every required helper is used in at least one tool:
  - **create_transaction** – Inventory (reorders), Sales (sales).
  - **get_all_inventory** – Inventory.
  - **get_stock_level** – Inventory, Quoting, Sales.
  - **get_supplier_delivery_date** – Quoting, Sales.
  - **get_cash_balance** – Quoting, Sales.
  - **generate_financial_report** – Orchestrator (`get_financial_summary`), Quoting (`get_financial_report_for_quote`).
  - **search_quote_history** – Quoting.
- **Framework**: **pydantic-ai** is used for agents, tools, and dependency injection (`RequestContext`), with the Vocareum OpenAI-compatible endpoint configured via `OpenAIProvider(base_url=..., api_key=...)`.

The workflow diagram (see `workflow_diagram.md` or `workflow_diagram.png`) shows these four agents, their tools, and which starter functions each tool uses.

---

## 2. Evaluation Results (test_results.csv)

The system was evaluated by running `python project_starter.py`, which loads the full **quote_requests_sample.csv** (20 requests), processes each row in date order via `process_customer_request`, and writes **test_results.csv** with columns: `request_id`, `request_date`, `cash_balance`, `inventory_value`, `response`. The submitted **test_results.csv** is included with this report.

### 2.1 Rubric conditions demonstrated in test_results.csv

**At least three requests result in a change to cash balance.**  
In **test_results.csv**, the `cash_balance` column shows multiple step changes. For example: after request 1 it is $50,118.50; after request 4 it is $50,294.00; after request 5 it is $50,516.80; after request 6 it is $50,702.30; and it continues to increase after requests 9, 10, 12, 13, 16, and 18. Thus requests 1, 4, 5, 6, 9, 10, 12, 13, 16, and 18 each result in a change to cash balance (fulfilled sales), satisfying the requirement of at least three.

**At least three quote requests successfully fulfilled.**  
The `response` column shows multiple orders and quotes fulfilled. For example: Request 1 — “We have fulfilled your request… Total: $118.50”; Request 4 — “Quote accepted and order fulfilled… Total $175.50”; Request 5 — “Order fulfilled… Total $222.80”; Request 6 — “Your order has been fulfilled… Total $185.50”; Request 9 — “Order fulfilled… Total $112.90”; Request 10 — “Order fulfilled… Total $183.30”; Request 12 — “Order fulfilled… Total $187.30”; Request 13 — “Order fulfilled… Total $183.00”; Request 16 — “Order fulfilled… Total $183.50”; Request 18 — “Order fulfilled… Total $183.50”. Request 19 provides a quote (“We have provided a quote… Total quote: $710.00”) without a sale in that row. Thus at least three (and in fact many more) quote/order requests are successfully fulfilled.

**Not all requests fulfilled, with reasons provided.**  
Several rows show the system declining to fulfill and explain why. Examples from the `response` column: Request 2 — “We are unable to fulfill this order in full. We do not carry balloons.”; Request 3 — “We cannot fulfill this order as requested. We do not stock A3 paper or reams of printer paper in the quantities specified.”; Request 7 — “We cannot fulfill the full order. We do not stock A3 paper or 24x36 poster boards…”; Request 8 — “Unable to fulfill. We do not carry A5 colored paper… Stock is insufficient for the full quantities requested.”; Request 14 — “Current stock… is insufficient for 5000, 2000, and 500 units respectively.”; Request 20 — “We do not produce tickets or the volume of flyers and posters requested.” So not all requests are fulfilled, and the response column clearly states reasons (item not carried, insufficient stock, or quantity not available).

---

## 3. Strengths of the Implemented System (with reference to test_results.csv)

- **Clear separation of roles**: The orchestrator delegates to Inventory, Quoting, and Sales agents. This is reflected in **test_results.csv** by consistent, task-appropriate responses: fulfilled orders state what was supplied and the total; unfulfilled ones explain missing items or stock limits (e.g. request 2’s “We do not carry balloons”, request 3’s “We do not stock A3 paper or reams”).

- **Full use of starter helpers**: All seven required helpers are used in tools (see Section 1). The evaluation output is consistent with that: cash balance and inventory value in **test_results.csv** evolve as sales and stock are applied (e.g. `inventory_value` decreases from about $12,450 to about $10,700 as orders are fulfilled), which would not occur without `create_transaction`, `get_stock_level`, and related helpers.

- **Consistent date handling**: `RequestContext.request_date` is used for all DB and delivery queries. The **test_results.csv** `request_date` column matches the sample (e.g. 2025-04-01 through 2025-04-17), and responses reference delivery dates (e.g. “Delivery by April 15, 2025”) in a coherent way.

- **Customer-facing behavior**: Responses in **test_results.csv** are professional and informative without exposing internals. Fulfilled orders state totals and discounts (e.g. request 5: “Total $222.80 with party-order discount”); unfulfilled ones give clear reasons (e.g. request 8: “We do not carry A5 colored paper… Stock is insufficient”) without revealing internal errors or PII.

- **Single submission file**: The entire multi-agent system lives in **project_starter.py**, and the same script produces the submitted **test_results.csv**, so evaluators can run the full sample and reproduce the results.

---

## 4. Suggestions for Further Improvement

1. **Item name normalization and matching**  
   Customers use varied wording (“A4 glossy paper”, “glossy A4”, “heavy cardstock (white)”). The agents rely on the LLM to map these to our catalog (e.g. “Glossy paper”, “A4 paper”, “Cardstock”). Adding a small **mapping layer** (e.g. synonyms or embeddings) between raw request text and our `item_name` list would make matching more reliable and reduce mis-quotes or “item not found” when we actually carry the product.

2. **Structured quote and order protocol**  
   Right now the Quoting and Sales agents output free text. Defining **structured outputs** (e.g. Pydantic models for “Quote” and “OrderResult”) would make it easier to:
   - Validate quotes (e.g. line items, total, delivery date) before showing to the customer.
   - Persist accepted quotes (e.g. into a `quotes` table) and link them to subsequent orders.
   - Improve evaluation by checking fields in **test_results.csv** (e.g. “quote_given”, “order_fulfilled”, “reason_declined”) instead of parsing prose.

3. **Reorder policy in the Inventory agent**  
   The Inventory agent can place reorders via `create_stock_order`, but the “when to reorder” rule is left to the LLM. Encoding an explicit **reorder policy** (e.g. compare `get_stock_level` to a threshold from the `inventory` table or a config) and exposing it in a tool would make reordering more predictable and testable (e.g. “after this request, reorder was triggered for item X”).

4. **Retries and error handling**  
   API or tool failures (e.g. transient network errors) are not retried. Adding **retries** for LLM and critical tools, and **clear error messages** (e.g. “We couldn’t process your request right now; please try again”) would improve robustness and customer experience.

---

## 5. Summary

The multi-agent system for Beaver’s Choice Paper Company uses one **orchestrator** and three **worker agents** (Inventory, Quoting, Sales), each with tools backed by the provided database helpers. The workflow diagram documents this design and the use of all seven required functions. The implementation is in a single file (**project_starter.py**), uses **pydantic-ai** with the Vocareum OpenAI endpoint, and is intended to meet the rubric for delegation, tool usage, evaluation (test_results.csv), and customer-facing behavior. The suggestions above aim to improve matching, structure, reorder logic, and reliability in a future iteration.
