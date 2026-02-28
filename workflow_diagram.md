# Beaver's Choice Paper Company – Multi-Agent Workflow Diagram

## Architecture (max 5 agents)

```mermaid
flowchart TB
    subgraph Customer
        A[Customer Request]
    end

    subgraph Orchestrator
        O[Orchestrator Agent]
        O --- T1[get_financial_summary<br/>uses: generate_financial_report]
        O --- T2[delegate_to_inventory]
        O --- T3[delegate_to_quoting]
        O --- T4[delegate_to_sales]
    end

    subgraph InventoryAgent[Inventory Agent]
        I[Inventory Agent]
        I --- I1[get_all_inventory_tool<br/>uses: get_all_inventory]
        I --- I2[get_stock_level_tool<br/>uses: get_stock_level]
        I --- I3[create_stock_order<br/>uses: create_transaction]
    end

    subgraph QuotingAgent[Quoting Agent]
        Q[Quoting Agent]
        Q --- Q1[search_quote_history_tool<br/>uses: search_quote_history]
        Q --- Q2[get_stock_for_quote<br/>uses: get_stock_level]
        Q --- Q3[get_delivery_estimate<br/>uses: get_supplier_delivery_date]
        Q --- Q4[get_cash_balance_tool<br/>uses: get_cash_balance]
        Q --- Q5[get_financial_report_for_quote<br/>uses: generate_financial_report]
    end

    subgraph SalesAgent[Sales Agent]
        S[Sales Agent]
        S --- S1[get_stock_for_sales<br/>uses: get_stock_level]
        S --- S2[fulfill_order<br/>uses: create_transaction]
        S --- S3[get_delivery_estimate_sales<br/>uses: get_supplier_delivery_date]
        S --- S4[get_cash_balance_sales<br/>uses: get_cash_balance]
    end

    A --> O
    T2 --> I
    T3 --> Q
    T4 --> S
```

## Data flow

1. **Customer request** (text) enters the **Orchestrator** with a request date (for DB queries).
2. Orchestrator may call **get_financial_summary** (uses `generate_financial_report`) for an overview.
3. For inventory questions or reorders → **delegate_to_inventory** → **Inventory Agent** uses:
   - `get_all_inventory`, `get_stock_level`, `create_transaction` (stock_orders).
4. For quote requests → **delegate_to_quoting** → **Quoting Agent** uses:
   - `search_quote_history`, `get_stock_level`, `get_supplier_delivery_date`, `get_cash_balance`, `generate_financial_report`.
5. For order fulfillment → **delegate_to_sales** → **Sales Agent** uses:
   - `get_stock_level`, `create_transaction` (sales), `get_supplier_delivery_date`, `get_cash_balance`.
6. Orchestrator returns a single, customer-facing response (with rationale, no sensitive internals).

Export this Mermaid from [Mermaid Live](https://mermaid.live) or Diagrams.net to produce `workflow_diagram.png` for submission.
