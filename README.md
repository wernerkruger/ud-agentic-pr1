# Munder Difflin Multi-Agent System Project

Welcome to the starter code repository for the **Munder Difflin Paper Company Multi-Agent System Project**! This repository contains the starter code and tools you will need to design, build, and test a multi-agent system that supports core business operations at a fictional paper manufacturing company.

## Project Context

You’ve been hired as an AI consultant by Munder Difflin Paper Company, a fictional enterprise looking to modernize their workflows. They need a smart, modular **multi-agent system** to automate:

- **Inventory checks** and restocking decisions
- **Quote generation** for incoming sales inquiries
- **Order fulfillment** including supplier logistics and transactions

Your solution must use a maximum of **5 agents** and process inputs and outputs entirely via **text-based communication**.

This project challenges your ability to orchestrate agents using modern Python frameworks like `smolagents`, `pydantic-ai`, or `npcsh`, and combine that with real data tools like `sqlite3`, `pandas`, and LLM prompt engineering.

---

## What’s Included

From the `project.zip` starter archive, you will find:

- `project_starter.py`: The main Python script you will modify to implement your agent system
- `quotes.csv`: Historical quote data used for reference by quoting agents
- `quote_requests.csv`: Incoming customer requests used to build quoting logic
- `quote_requests_sample.csv`: A set of simulated test cases to evaluate your system

---

## Workspace Instructions

All the files have been provided in the VS Code workspace on the Udacity platform. Please install the agent orchestration framework of your choice.

## Local setup instructions

1. Install dependencies

Make sure you have Python 3.8+ installed.

You can install all required packages using the provided requirements.txt file:

`pip install -r requirements.txt`

If you're using smolagents, install it separately:

`pip install smolagents`

For other options like pydantic-ai or npcsh[lite], refer to their documentation.

2. Create .env File

Add your OpenAI-compatible API key:

`UDACITY_OPENAI_API_KEY=your_openai_key_here`

This project uses a custom OpenAI-compatible proxy hosted at https://openai.vocareum.com/v1.

## How to Run the Project

The multi-agent system is implemented in the `"YOUR MULTI AGENT STARTS HERE"` section inside `project_starter.py`. To run:

1. Run the `run_test_scenarios()` function at the bottom of the script.
2. This will simulate a series of customer requests.
3. Your system should respond by coordinating inventory checks, generating quotes, and processing orders.

Output will include:

- Agent responses
- Cash and inventory updates
- Final financial report
- A `test_results.csv` file with all interaction logs

---

## Tips for Success

- Start by sketching a **flow diagram** to visualize agent responsibilities and interactions.
- Test individual agent tools before full orchestration.
- Always include **dates** in customer requests when passing data between agents.
- Ensure every quote includes **bulk discounts** and uses past data when available.
- Use the **exact item names** from the database to avoid transaction failures.

---

## This Implementation

- **Framework**: pydantic-ai with Vocareum OpenAI-compatible endpoint.
- **Agents**: Orchestrator (delegates), Inventory (stock + reorders), Quoting (quotes + history), Sales (fulfillment).
- **Run evaluation**: `python project_starter.py` — initializes DB, processes `quote_requests_sample.csv`, writes `test_results.csv`.
- **Workflow diagram**: See `workflow_diagram.md` (Mermaid). Export to PNG (e.g. via [Mermaid Live](https://mermaid.live)) as `workflow_diagram.png` for submission.
- **Reflection**: See `REFLECTION_REPORT.md` for architecture, evaluation notes, and improvement suggestions.

## Submission Checklist

**Include all of the following in your submission:**

1. **project_starter.py** — completed implementation with all agent logic
2. **workflow_diagram.png** — workflow diagram (export from `workflow_diagram.md` via [Mermaid Live](https://mermaid.live) if needed)
3. **REFLECTION_REPORT.md** — reflection report that explains the system and **discusses evaluation results from test_results.csv** (specific request IDs, cash balance changes, fulfilled vs unfulfilled, and reasons from the response column)
4. **test_results.csv** — **required.** Generate it by running `python project_starter.py` (after `pip install -r requirements.txt` and with `UDACITY_OPENAI_API_KEY` set). The file must show: at least three requests with a change to cash balance, at least three quote/order requests successfully fulfilled, and some requests not fulfilled with reasons in the response column.

---