# Week 5 – Day 2: LLM Application Development
## Function Calling / Tool Use – Tool Schemas and Tool Loop

## Project Overview

This project demonstrates function calling (tool use) in Large Language Model applications using Python and the OpenRouter API.

The application enables an LLM to select and execute predefined Python functions based on user questions. It implements tool schemas, function execution, tool responses, and a reusable tool-calling loop.

**API Provider:** OpenRouter  
**SDK:** OpenAI Python SDK  
**Language:** Python

## Project Structure

```text
Week5_Day2/
│
├── task1_first_tool_call.py
├── task2_tool_loop.py
├── task2_output.txt
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Technologies Used

- Python
- OpenRouter API
- OpenAI Python SDK
- JSON
- JSON Schema
- Python-dotenv

---

# Task 1 – First Tool Call

### Objectives

- Create a Python function `get_weather(city)`.
- Define a function tool schema with name, description and JSON parameters.
- Send the question: "Is it raining in Chennai?"
- Detect `tool_calls` in the model response.
- Extract function names and arguments.
- Execute the requested Python function.
- Append the result as a tool message.
- Call the model again to generate the final response.

### Tool Implemented

**Function:** `get_weather(city)`

Sample weather database:

| City | Temperature | Condition |
|---|---:|---|
| Chennai | 31°C | Light rain |
| Bangalore | 24°C | Cloudy |
| Mumbai | 29°C | Sunny |

### Execution Output

```text
USER: Is it raining in Chennai?

Tool requested: get_weather({"city": "Chennai"})

Tool result:
{'temperature': 31, 'condition': 'light rain'}

Final:
It is 31 C with light rain in Chennai.
```

### Key Learning

The LLM does not execute Python functions directly. It generates a structured tool-call request, and the application executes the requested function and returns the result to the model.

---

# Task 2 – The Tool Loop

### Objectives

- Implement three Python tools.
- Define detailed tool descriptions and JSON schemas.
- Build a reusable tool-calling loop.
- Execute requested functions dynamically.
- Append tool results to conversation messages.
- Continue calling the LLM until it returns a text response.
- Set a maximum of five rounds.
- Handle multiple tool calls.
- Print the complete conversation message history.

### Tools Implemented

| Function | Description |
|---|---|
| `get_order_status(order_id)` | Retrieves order status and estimated delivery date. |
| `get_customer(customer_id)` | Retrieves customer name and email. |
| `calculate_discount(amount, percent)` | Calculates discount and final payable amount. |

### Sample Database

**Orders**

| Order ID | Status | Delivery |
|---|---|---|
| ORD101 | Shipped | 12 November 2026 |
| ORD102 | Processing | 15 November 2026 |
| ORD103 | Delivered | 8 November 2026 |

**Customers**

| Customer ID | Name | Email |
|---|---|---|
| CUST001 | Arun | arun@example.com |
| CUST002 | Priya | priya@example.com |
| CUST003 | Rahul | rahul@example.com |

### Five Test Questions

1. What is the status of order ORD101?
2. Give me the details of customer CUST001.
3. Calculate a 20% discount on 5000.
4. What is the status of order ORD102 and who is customer CUST002?
5. Explain what a Large Language Model is.

### Representative Execution Results

**Question 1 – Order Status**

```text
Tool requested: get_order_status
Order ID: ORD101

Result:
Status: Shipped
Delivery: 12 November 2026
```

**Question 2 – Customer Details**

```text
Tool requested: get_customer
Customer ID: CUST001

Result:
Name: Arun
Email: arun@example.com
```

**Question 3 – Discount Calculation**

```text
Tool requested: calculate_discount

Original Amount: 5000
Discount Percentage: 20%
Discount Amount: 1000
Final Amount: 4000
```

**Question 4 – Multiple Tool Calls**

```text
Tool requested: get_order_status
Tool requested: get_customer

Result:
Order Status: Processing
Customer Name: Priya
Email: priya@example.com
```

**Question 5 – No Tool Required**

```text
USER: Explain what a Large Language Model is.

No tool required.

FINAL ANSWER:
A Large Language Model is an AI model
trained on large amounts of text to understand
and generate human language.
```

*Note: These are representative results. The actual model-generated wording and tool-call order may vary. The complete execution log is saved separately in task2_output.txt.*

---

# Bonus Challenge – Tool Description Improvement

Tested how tool descriptions influence model tool selection.

**Vague description:**

```python
"description": "Gets information about something."
```

**Improved description:**

```python
"description": (
    "Use this tool when the user asks about an existing "
    "order's shipping status, processing status or "
    "estimated delivery date. Requires an order ID."
)
```

### Learning

Clear and specific tool descriptions help the model identify the correct function and its required parameters.

---

# Concepts Learned

| Concept | Description |
|---|---|
| Function Calling | Model requests application-defined functions. |
| Tool Schema | Defines function name, description and parameters. |
| JSON Schema | Defines valid function inputs. |
| Tool Calls | Structured function requests from the model. |
| Tool Message | Returns the function execution result. |
| Tool Registry | Maps function names to Python functions. |
| Tool Loop | Repeats LLM calls and tool execution. |
| Multiple Tool Calls | Executes multiple functions in a single response. |
| Maximum Rounds | Prevents unlimited tool execution. |

---

# Installation and Execution

### 1. Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Week5_Day2
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=your_supported_model
```

Never upload API keys to GitHub.

### 5. Run Task 1

```bash
python task1_first_tool_call.py
```

### 6. Run Task 2

```bash
python task2_tool_loop.py
```

### 7. Save Execution Output

```powershell
python task2_tool_loop.py > task2_output.txt 2>&1
```

---

# Security

- API credentials are stored in `.env`.
- `.env` is excluded using `.gitignore`.
- No API keys are included in source code.
- The application uses predefined sample databases for demonstration.

# Conclusion

This project demonstrates how Large Language Models interact with external Python functions through structured function calling.

Task 1 implements a weather lookup tool, while Task 2 implements a reusable tool-calling loop with order tracking, customer lookup and discount calculation.

The project provides practical experience in building LLM-powered applications using OpenRouter, function schemas, JSON arguments and dynamic tool execution.