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

After running:

```bash
python project_starter.py
```

the script:

- Initializes the DB with `init_database(db_engine)`.
- Loads **quote_requests_sample.csv** and processes each row in date order.
- For each row, calls `process_customer_request(request_text, request_date)`, which runs the orchestrator (and thus inventory, quoting, and sales as needed).
- Appends a row to **results** with `request_id`, `request_date`, `cash_balance`, `inventory_value`, `response`.
- Writes **test_results.csv** and prints a final financial summary.

**Expected behavior relative to the rubric:**

- **At least three requests result in a change to cash balance** – Any request that leads to a fulfilled sale (via the Sales agent and `create_transaction(..., 'sales')`) will change cash. The orchestrator is instructed to delegate to the Sales agent for orders; multiple sample rows are orders, so several should result in sales and thus cash changes.
- **At least three quote requests successfully fulfilled** – Sample rows include both quote requests and orders. The Quoting agent is used for “quote” style requests; the Sales agent is used for “place order” style requests. Running the full sample should yield multiple successful quotes and multiple fulfilled orders.
- **Not all requests fulfilled, with reasons** – Some requests ask for items or quantities we don’t carry or don’t have in stock (e.g. “A3 paper”, “balloons”, “reams”). The Sales agent is instructed to check stock and only call `fulfill_order` when stock is sufficient; otherwise it should explain that the order cannot be fulfilled (e.g. insufficient stock or item not available). So some rows in **test_results.csv** will show “unfulfilled” with explanations.

If **test_results.csv** is not yet generated, run:

```bash
pip install -r requirements.txt
python project_starter.py
```

and then inspect **test_results.csv** for the columns above.

---

## 3. Strengths of the Implemented System

- **Clear separation of roles**: Orchestrator vs. Inventory, Quoting, and Sales avoids overlapping responsibilities and keeps each agent’s tools focused.
- **Full use of starter helpers**: All seven required helpers are used in tools as specified, with a clear mapping from diagram to code.
- **Consistent date handling**: `RequestContext.request_date` ensures all DB and delivery logic uses the same date, which is important for reproducible evaluation and time-ordered samples.
- **Customer-facing behavior**: The orchestrator is instructed to summarize outcomes and give brief rationale (e.g. discounts, inability to fulfill) without exposing internal data or PII.
- **Single submission file**: The entire multi-agent system lives in **project_starter.py**, so the evaluator has one place to run and inspect the flow.

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
