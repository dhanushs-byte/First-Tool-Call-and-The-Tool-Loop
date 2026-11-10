
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv(
        "OPENAI_BASE_URL",
        "https://openrouter.ai/api/v1"
    )
)

MODEL = os.getenv("OPENAI_MODEL")

if not MODEL:
    raise ValueError("OPENAI_MODEL is missing in .env")


# ==========================================
# 2. SAMPLE DATABASE
# ==========================================

orders = {
    "ORD101": {
        "status": "Shipped",
        "delivery": "12 November 2026"
    },
    "ORD102": {
        "status": "Processing",
        "delivery": "15 November 2026"
    },
    "ORD103": {
        "status": "Delivered",
        "delivery": "8 November 2026"
    }
}

customers = {
    "CUST001": {
        "name": "Arun",
        "email": "arun@example.com"
    },
    "CUST002": {
        "name": "Priya",
        "email": "priya@example.com"
    },
    "CUST003": {
        "name": "Rahul",
        "email": "rahul@example.com"
    }
}


# ==========================================
# 3. PYTHON TOOL FUNCTIONS
# ==========================================

def get_order_status(order_id):
    """Get order status and estimated delivery date."""

    return orders.get(
        order_id,
        {"error": f"Order {order_id} not found"}
    )


def get_customer(customer_id):
    """Get registered customer name and email."""

    return customers.get(
        customer_id,
        {"error": f"Customer {customer_id} not found"}
    )


def calculate_discount(amount, percent):
    """Calculate discount and final payable amount."""

    if amount < 0:
        return {"error": "Amount cannot be negative"}

    if not 0 <= percent <= 100:
        return {"error": "Discount must be between 0 and 100"}

    discount = amount * percent / 100

    return {
        "original_amount": amount,
        "discount_percent": percent,
        "discount_amount": round(discount, 2),
        "final_amount": round(amount - discount, 2)
    }


# ==========================================
# 4. TOOL REGISTRY
# ==========================================

tool_functions = {
    "get_order_status": get_order_status,
    "get_customer": get_customer,
    "calculate_discount": calculate_discount
}


# ==========================================
# 5. TOOL SCHEMAS
# ==========================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Use this tool when the user asks about an existing "
                "order, including its shipping status, processing "
                "status, or estimated delivery date. Returns the "
                "order status and delivery date. Requires an order ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID, such as ORD101"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": (
                "Use this tool when the user asks for details about "
                "a registered customer. Returns the customer's name "
                "and email address. Requires a customer ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID, such as CUST001"
                    }
                },
                "required": ["customer_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_discount",
            "description": (
                "Use this tool when the user asks to calculate a "
                "percentage discount on a monetary amount. Returns "
                "the original amount, discount amount and final "
                "payable amount. Requires amount and percent."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Original monetary amount"
                    },
                    "percent": {
                        "type": "number",
                        "description": "Discount percentage from 0 to 100"
                    }
                },
                "required": ["amount", "percent"],
                "additionalProperties": False
            }
        }
    }
]


# ==========================================
# 6. EXECUTE REQUESTED TOOLS
# ==========================================

def execute_tool(tool_call):

    function_name = tool_call.function.name

    try:
        arguments = json.loads(
            tool_call.function.arguments
        )

        print(
            f"\nTool requested: {function_name}"
            f"({json.dumps(arguments)})"
        )

        if function_name not in tool_functions:
            result = {"error": "Unknown tool"}

        else:
            result = tool_functions[function_name](
                **arguments
            )

    except (json.JSONDecodeError, TypeError, ValueError) as error:
        result = {"error": str(error)}

    print("Tool result:", result)

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
    }


# ==========================================
# 7. REUSABLE TOOL CALLING LOOP
# ==========================================

def run_tool_loop(question, max_rounds=5):

    print("\n" + "=" * 65)
    print("USER:", question)
    print("=" * 65)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer support assistant. "
                "Use the available tools whenever the user asks "
                "for order information, customer details, or "
                "discount calculations. Do not invent database "
                "results. For general knowledge questions, "
                "answer directly without calling tools."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # Maximum five model/tool rounds
    for round_number in range(1, max_rounds + 1):

        print(f"\n--- TOOL LOOP ROUND {round_number} ---")

        # Call LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Preserve assistant response in conversation
        messages.append(
            assistant_message.model_dump(
                exclude_none=True
            )
        )

        # Detect tool calls
        tool_calls = assistant_message.tool_calls

        # No tool call: final text response
        if not tool_calls:

            print("\nFINAL ANSWER:")
            print(assistant_message.content)

            break

        # Execute every requested tool
        for tool_call in tool_calls:

            tool_result = execute_tool(tool_call)

            messages.append(tool_result)

    else:
        print("\nMaximum tool rounds reached.")
        print("The model did not finish within the limit.")

    # ======================================
    # 8. PRINT COMPLETE MESSAGE HISTORY
    # ======================================

    print("\n" + "=" * 65)
    print("FULL CONVERSATION MESSAGE LIST")
    print("=" * 65)

    print(
        json.dumps(
            messages,
            indent=4,
            ensure_ascii=False
        )
    )

    return messages


# ==========================================
# 9. TEST FIVE QUESTIONS
# ==========================================

if __name__ == "__main__":

    questions = [
        "What is the status of order ORD101?",
        
        "Give me the details of customer CUST001.",

        "Calculate a 20% discount on 5000.",

        (
            "What is the status of order ORD102 "
            "and who is customer CUST002?"
        ),

        "Explain what a Large Language Model is."
    ]

    for question in questions:

        run_tool_loop(
            question=question,
            max_rounds=5
        )
