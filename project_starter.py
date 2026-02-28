import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################

# Load environment and set up Vocareum OpenAI-compatible client
dotenv.load_dotenv()
API_KEY = os.getenv("UDACITY_OPENAI_API_KEY") or (open("mykey.txt").read().strip() if os.path.exists("mykey.txt") else None)
if not API_KEY:
    raise ValueError("Set UDACITY_OPENAI_API_KEY in .env or provide mykey.txt")

from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
# Support both older (OpenAIModel) and newer (OpenAIChatModel) pydantic-ai API
try:
    from pydantic_ai.models.openai import OpenAIChatModel as _OpenAIModelCls
except ImportError:
    from pydantic_ai.models.openai import OpenAIModel as _OpenAIModelCls
from pydantic_ai.providers.openai import OpenAIProvider

# Vocareum OpenAI-compatible endpoint
_openai_provider = OpenAIProvider(
    base_url="https://openai.vocareum.com/v1",
    api_key=API_KEY,
)
_llm = _OpenAIModelCls("gpt-4o-mini", provider=_openai_provider)


@dataclass
class RequestContext:
    """Context passed to all agents: request date for DB queries."""
    request_date: str


# ---------------------------------------------------------------------------
# Inventory Agent: check stock, reorder when needed
# Uses: get_all_inventory, get_stock_level, create_transaction (stock_orders)
# ---------------------------------------------------------------------------

inventory_agent = Agent(
    _llm,
    deps_type=RequestContext,
    instructions="""You are the inventory manager for Beaver's Choice Paper Company.
Your job is to: (1) answer questions about current stock levels for paper types,
(2) check if any items are below reorder threshold and need reordering,
(3) place stock orders when needed using create_stock_order.
Use the request_date from context for all date-based queries.
When reordering, use create_stock_order with the item name, quantity to order, and unit price.
Be concise and factual. Do not reveal internal cost details to customers.""",
)


@inventory_agent.tool
def get_all_inventory_tool(ctx: RunContext[RequestContext]) -> str:
    """Get current inventory snapshot (all items and their stock levels) as of the request date. Uses get_all_inventory."""
    inv = get_all_inventory(ctx.deps.request_date)
    if not inv:
        return "No inventory on record."
    lines = [f"{name}: {qty} units" for name, qty in sorted(inv.items())]
    return "\n".join(lines)


@inventory_agent.tool
def get_stock_level_tool(ctx: RunContext[RequestContext], item_name: str) -> str:
    """Get stock level for a specific item as of the request date. Uses get_stock_level."""
    df = get_stock_level(item_name, ctx.deps.request_date)
    if df.empty or df["current_stock"].iloc[0] == 0:
        return f"{item_name}: 0 in stock."
    return f"{item_name}: {int(df['current_stock'].iloc[0])} units in stock."


@inventory_agent.tool
def get_inventory_reference(ctx: RunContext[RequestContext]) -> str:
    """Get reference list of items we stock with min_stock_level and unit_price (from inventory table). Use to decide when to reorder."""
    df = pd.read_sql("SELECT item_name, min_stock_level, unit_price FROM inventory", db_engine)
    if df.empty:
        return "No inventory reference."
    lines = [f"{row['item_name']}: min_stock={int(row['min_stock_level'])}, unit_price=${row['unit_price']:.2f}" for _, row in df.iterrows()]
    return "\n".join(lines)


@inventory_agent.tool
def create_stock_order(ctx: RunContext[RequestContext], item_name: str, quantity: int, unit_price: float) -> str:
    """Place a stock order (reorder) from supplier. Uses create_transaction with transaction_type 'stock_orders'."""
    try:
        total = quantity * unit_price
        tid = create_transaction(
            item_name=item_name,
            transaction_type="stock_orders",
            quantity=quantity,
            price=total,
            date=ctx.deps.request_date,
        )
        return f"Stock order recorded (id={tid}): {quantity} units of {item_name}, total ${total:.2f}."
    except Exception as e:
        return f"Failed to create stock order: {e}"


# ---------------------------------------------------------------------------
# Quoting Agent: historical quotes, pricing, delivery estimates
# Uses: search_quote_history, get_stock_level, get_supplier_delivery_date, get_cash_balance, generate_financial_report
# ---------------------------------------------------------------------------

quoting_agent = Agent(
    _llm,
    deps_type=RequestContext,
    instructions="""You are the quoting specialist for Beaver's Choice Paper Company.
Your job is to: (1) look up similar past quotes for pricing guidance,
(2) check current stock and unit prices via generate_financial_report and get_stock_level,
(3) estimate supplier delivery with get_supplier_delivery_date,
(4) provide a clear, customer-friendly quote with a brief justification (e.g. bulk discount).
Use request_date for all date-based calls. Round totals to sensible amounts. Do not expose internal margins.""",
)


@quoting_agent.tool
def search_quote_history_tool(ctx: RunContext[RequestContext], search_terms: str, limit: int = 5) -> str:
    """Search historical quotes by keywords (comma-separated). Uses search_quote_history."""
    terms = [t.strip() for t in search_terms.split(",") if t.strip()]
    if not terms:
        return "No search terms provided."
    results = search_quote_history(terms, limit=limit)
    if not results:
        return "No matching historical quotes found."
    lines = []
    for r in results:
        lines.append(f"Request: {r.get('original_request', '')[:80]}... | Amount: ${r.get('total_amount')} | {r.get('quote_explanation', '')[:100]}...")
    return "\n".join(lines)


@quoting_agent.tool
def get_stock_for_quote(ctx: RunContext[RequestContext], item_name: str) -> str:
    """Get stock level for an item (for quoting). Uses get_stock_level."""
    df = get_stock_level(item_name, ctx.deps.request_date)
    if df.empty:
        return f"{item_name}: 0 in stock."
    return f"{item_name}: {int(df['current_stock'].iloc[0])} units in stock."


@quoting_agent.tool
def get_delivery_estimate(ctx: RunContext[RequestContext], quantity: int) -> str:
    """Get estimated supplier delivery date for a given quantity. Uses get_supplier_delivery_date."""
    date_str = get_supplier_delivery_date(ctx.deps.request_date, quantity)
    return f"Estimated delivery: {date_str} (for quantity {quantity})."


@quoting_agent.tool
def get_cash_balance_tool(ctx: RunContext[RequestContext]) -> str:
    """Get company cash balance as of request date. Uses get_cash_balance."""
    bal = get_cash_balance(ctx.deps.request_date)
    return f"Cash balance as of {ctx.deps.request_date}: ${bal:.2f}"


@quoting_agent.tool
def get_financial_report_for_quote(ctx: RunContext[RequestContext]) -> str:
    """Get financial report including inventory summary (unit prices and stock). Uses generate_financial_report."""
    report = generate_financial_report(ctx.deps.request_date)
    summary = report.get("inventory_summary", [])
    lines = [f"{s['item_name']}: stock={s['stock']}, unit_price=${s['unit_price']:.2f}" for s in summary[:30]]
    return "Inventory (unit prices):\n" + "\n".join(lines) if lines else "No inventory data."


# ---------------------------------------------------------------------------
# Sales Agent: fulfill orders, update DB
# Uses: get_stock_level, create_transaction (sales), get_supplier_delivery_date, get_cash_balance
# ---------------------------------------------------------------------------

sales_agent = Agent(
    _llm,
    deps_type=RequestContext,
    instructions="""You are the sales fulfillment agent for Beaver's Choice Paper Company.
Your job is to: (1) check stock with get_stock_level before fulfilling,
(2) fulfill orders by recording a sale with fulfill_order (item_name, quantity, total_price),
(3) provide delivery estimates with get_delivery_estimate when relevant.
Only fulfill orders when stock is sufficient. Use request_date for all transactions.
If stock is insufficient, say so clearly and do not call fulfill_order.""",
)


@sales_agent.tool
def get_stock_for_sales(ctx: RunContext[RequestContext], item_name: str) -> str:
    """Check stock level for an item before fulfilling. Uses get_stock_level."""
    df = get_stock_level(item_name, ctx.deps.request_date)
    if df.empty:
        return f"{item_name}: 0 in stock."
    return f"{item_name}: {int(df['current_stock'].iloc[0])} units in stock."


@sales_agent.tool
def fulfill_order(ctx: RunContext[RequestContext], item_name: str, quantity: int, total_price: float) -> str:
    """Record a sale (fulfill order). Uses create_transaction with transaction_type 'sales'."""
    try:
        tid = create_transaction(
            item_name=item_name,
            transaction_type="sales",
            quantity=quantity,
            price=total_price,
            date=ctx.deps.request_date,
        )
        return f"Order fulfilled (transaction id={tid}): {quantity} units of {item_name}, total ${total_price:.2f}."
    except Exception as e:
        return f"Failed to fulfill order: {e}"


@sales_agent.tool
def get_delivery_estimate_sales(ctx: RunContext[RequestContext], quantity: int) -> str:
    """Get supplier delivery estimate. Uses get_supplier_delivery_date."""
    date_str = get_supplier_delivery_date(ctx.deps.request_date, quantity)
    return f"Estimated delivery: {date_str}."


@sales_agent.tool
def get_cash_balance_sales(ctx: RunContext[RequestContext]) -> str:
    """Get current cash balance. Uses get_cash_balance."""
    bal = get_cash_balance(ctx.deps.request_date)
    return f"Cash balance: ${bal:.2f}"


# ---------------------------------------------------------------------------
# Orchestrator Agent: delegates to inventory, quoting, and sales
# ---------------------------------------------------------------------------

orchestrator_agent = Agent(
    _llm,
    deps_type=RequestContext,
    instructions="""You are the orchestrator for Beaver's Choice Paper Company.
You receive customer requests (inquiries, quote requests, or orders). Your job is to:
1. For inventory questions: call delegate_to_inventory with the question.
2. For quote requests: call delegate_to_quoting with the request details.
3. For order fulfillment: first ensure we have a quote and stock, then call delegate_to_sales with the order details.
4. Optionally use get_financial_summary to get an overview before or after handling the request.
Always respond to the customer in a clear, professional way. Summarize the outcome and explain key decisions (e.g. why a quote has a certain price, why an order could not be fulfilled). Do not expose internal system details or PII.""",
)


def _run_inventory(task: str, ctx: RequestContext) -> str:
    result = inventory_agent.run_sync(task, deps=ctx)
    return result.output if result.output else str(result.data)


def _run_quoting(task: str, ctx: RequestContext) -> str:
    result = quoting_agent.run_sync(task, deps=ctx)
    return result.output if result.output else str(result.data)


def _run_sales(task: str, ctx: RequestContext) -> str:
    result = sales_agent.run_sync(task, deps=ctx)
    return result.output if result.output else str(result.data)


@orchestrator_agent.tool
def delegate_to_inventory(ctx: RunContext[RequestContext], task_description: str) -> str:
    """Delegate an inventory-related task (check stock, reorder) to the inventory agent."""
    return _run_inventory(task_description, ctx.deps)


@orchestrator_agent.tool
def delegate_to_quoting(ctx: RunContext[RequestContext], task_description: str) -> str:
    """Delegate a quote request to the quoting agent."""
    return _run_quoting(task_description, ctx.deps)


@orchestrator_agent.tool
def delegate_to_sales(ctx: RunContext[RequestContext], task_description: str) -> str:
    """Delegate order fulfillment to the sales agent."""
    return _run_sales(task_description, ctx.deps)


@orchestrator_agent.tool
def get_financial_summary(ctx: RunContext[RequestContext]) -> str:
    """Get a high-level financial summary (cash, inventory value). Uses generate_financial_report."""
    report = generate_financial_report(ctx.deps.request_date)
    return (
        f"As of {report['as_of_date']}: Cash ${report['cash_balance']:.2f}, "
        f"Inventory value ${report['inventory_value']:.2f}, Total assets ${report['total_assets']:.2f}."
    )


def process_customer_request(request_text: str, request_date: str) -> str:
    """Process a single customer request through the orchestrator. Returns customer-facing response."""
    ctx = RequestContext(request_date=request_date)
    result = orchestrator_agent.run_sync(request_text, deps=ctx)
    return result.output if result.output else (str(result.data) if result.data else "No response generated.")


# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():
    print("Initializing Database...")
    init_database(db_engine)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request through the multi-agent system
        request_with_date = f"{row['request']} (Date of request: {request_date})"
        response = process_customer_request(request_with_date, request_date)

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
