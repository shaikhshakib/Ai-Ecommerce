import json
from openai import OpenAI
from dotenv import load_dotenv
from product_tool import search_products

load_dotenv()

client = OpenAI()

tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Search jewellery by category and maximum price.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "max_price": {"type": "number"}
            },
            "required": ["category", "max_price"],
            "additionalProperties": False
        },
        "strict": True
    }
]

input_messages = [
    {
        "role": "user",
        "content": "Find pendants under 800 rupees."
    }
]

response = client.responses.create(
    model="gpt-4.1-mini",
    input=input_messages,
    tools=tools,
    tool_choice="required"
)

input_messages += response.output

for item in response.output:
    if item.type == "function_call":
        print("Tool called:", item.name)
        print("Arguments:", item.arguments)

        args = json.loads(item.arguments)

        products = search_products(
            args["category"],
            args["max_price"]
        )

        print("Database results:", products)

        input_messages.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(products, default=str)
        })

response = client.responses.create(
    model="gpt-4.1-mini",
    input=input_messages,
    tools=tools,
    tool_choice="none"
)

print("\nAI Final Answer:")
print(repr(response.output_text))