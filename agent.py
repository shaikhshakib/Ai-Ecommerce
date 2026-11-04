import json
from openai import OpenAI
from dotenv import load_dotenv
from product_tool import search_products

load_dotenv()

client = OpenAI()
tool_functions = {
    "search_products": search_products
}
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

        tool_name = item.name

        function_to_call = tool_functions.get(tool_name)

        args = json.loads(item.arguments)

        if function_to_call is None:

            result = {"error": "Unknown tool requested"}

        else:

            try:
                result = function_to_call(**args)

            except Exception as e:
                result = {"error": str(e)}

        print("Database results:", result)

        input_messages.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result, default=str)
        })

response = client.responses.create(
    model="gpt-4.1-mini",
    input=input_messages,
    tools=tools,
    tool_choice="none"
)

print("\nAI Final Answer:")
print(repr(response.output_text))


