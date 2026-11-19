"""Customer support agent powered by Groq API."""

import json
from groq import Groq

from app.config import GROQ_API_KEY as DEFAULT_GROQ_API_KEY, MODEL_NAME
from app.tools import run_tool

SYSTEM_INSTRUCTION = """
You are an intelligent, friendly, professional, and efficient
AI Customer Support Agent.

Your primary responsibility is to help customers with their
accounts, orders, deliveries, support tickets, and refund requests.

You must provide accurate, helpful, concise, and personalized
customer support using the available backend tools.

========================
1. CUSTOMER IDENTIFICATION
========================

- Always ask for the customer's registered email address before
  accessing or looking up their account.
- Do not retrieve customer information, orders, or tickets
  until the customer provides their email address.
- Validate that the email address is in a reasonable format.
- Once provided, use the appropriate customer lookup tool.
- Never assume the customer's identity.
- If the customer has no registered account, politely explain this.

========================
2. TOOL USAGE AND DATA ACCURACY
========================

- Use available Python backend tools whenever real customer,
  order, delivery, or ticket information is required.
- Never invent, assume, or guess customer details.
- Never fabricate order IDs, prices, delivery dates,
  refund amounts, or ticket statuses.
- Only communicate information returned by the backend tools.
- If a tool returns no results, clearly inform the customer.
- If a tool fails, apologize and explain that the information
  is temporarily unavailable.
- Never claim an action was completed unless the tool
  successfully confirms it.

========================
3. ORDER MANAGEMENT
========================

You can help customers with:
- Order status and shipping updates
- Order history and details
- Delivery issues or delays

========================
4. SUPPORT TICKETS
========================

You can help customers with:
- Creating a support ticket for issues
- Viewing existing tickets and statuses

========================
5. PRIMARY OBJECTIVE
========================

Your goal is to resolve customer issues accurately,
efficiently, and professionally.
"""

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up a customer record by their email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The customer's email address.",
                    }
                },
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_orders",
            "description": "Retrieve all past and present orders placed by a customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The unique ID of the customer.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Check the details and delivery status of a specific order by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The unique ID of the order.",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a new support ticket for a customer issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The unique ID of the customer.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Brief topic or title of the issue.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the support request.",
                    },
                },
                "required": ["customer_id", "subject", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tickets",
            "description": "Retrieve all support tickets opened by a specific customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The unique ID of the customer.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
]

MAX_TOOL_ROUNDS = 5


def new_chat():
    """Start a new chat session history.

    Returns:
        list: A list of chat messages seeded with the system instruction.
    """
    return [{"role": "system", "content": SYSTEM_INSTRUCTION}]


def ask_agent(chat_messages: list, user_message: str, api_key: str = None) -> str:
    """Send a user message, execute automatic function calls, and return the reply.

    Args:
        chat_messages: Conversation message list from new_chat().
        user_message (str): The customer's message.
        api_key (str, optional): User-provided Groq API key (falls back to .env key).

    Returns:
        str: The agent's final text reply.
    """
    effective_key = (api_key or "").strip() or DEFAULT_GROQ_API_KEY
    if not effective_key:
        raise ValueError("No Groq API key provided. Please enter your Groq API key in the sidebar.")

    client = Groq(api_key=effective_key)
    chat_messages.append({"role": "user", "content": user_message})

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_messages,
            tools=GROQ_TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        tool_calls = msg.tool_calls

        # If model didn't call any tools, it's the final reply
        if not tool_calls:
            reply_text = msg.content or ""
            chat_messages.append({"role": "assistant", "content": reply_text})
            return reply_text

        # Record assistant tool call in history
        chat_messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        # Execute each tool call and append tool response
        for tc in tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            result = run_tool(tool_name, args)

            chat_messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tool_name,
                "content": json.dumps(result),
            })

    # Fallback if loop exceeded max rounds
    return "I apologize, but I was unable to complete your request. Please try again."
