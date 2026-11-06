import json
from openai import OpenAI
from dotenv import load_dotenv
from product_tool import search_products, search_products_by_name
from stock_tool import check_stock
from cart_tool import add_to_cart
load_dotenv()

client = OpenAI()
tool_functions = {
    "search_products": search_products,
    "search_products_by_name" : search_products_by_name,
    "check_stock" : check_stock,
    "add_to_cart" : add_to_cart

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
    },
{
    "type" : "function",
    "name" : "check_stock",
    "description" : "Check available stock of jewellery product using product ID.",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "product_id" : {"type" : "integer"}
        },
        "required" : ["product_id"],
        "additionalProperties" : False
    },
    "strict" : True
},
{
    "type": "function",
    "name": "add_to_cart",
    "description": "Add a product to cart only after explicit customer confirmation.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {"type": "integer"},
            "quantity": {"type": "integer"}
        },
        "required": ["product_id", "quantity"],
        "additionalProperties": False
    },
    "strict": True
},
{
    "type": "function",
    "name": "search_products_by_name",
    "description": "Find a jewellery product using its name and return its product ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {"type": "string"}
        },
        "required": ["product_name"],
        "additionalProperties": False
    },
    "strict": True
}
]

input_messages = [
    {
        "role" : "developer",
        "content" : """
        You are Celeste Rose's Jewellery Shopping assistant.
        Use search_products to find products.
        use check_stock to check inventory.

        Never add products to add unless the customer explicitly confirms the action.

        If stock is insufficient, inform the customer.
        Never claim an action succeeded unless the tool confirms it. 
        When a customer wants to add a product to cart:

        1. First use search_product_by_name to identify the product.
        2. If multiple products match, ask the customer to choose.
        3. Use check_stock to verify availability.
        4. Ask the customer for confirmation before adding to cart.
        5. Only after confirmation, use add_to_cart.
        6. Never assume the customer's confirmation.
        You are Céleste Rosé's jewellery shopping assistant.

        Rules:
        1. Always display prices in Indian Rupees (₹).
        2. When the customer asks about availability, use check_stock.
        3. When the customer wants to add a product to cart, first identify the product using search_product_by_name.
        4. Then use check_stock to verify inventory.
        5. Ask for explicit confirmation before adding to cart.
        6. Execute add_to_cart only after confirmation.
        7. Never claim an action succeeded unless the tool confirms it.
        """
    },
    {
        "role": "user",
        "content": "Is Golden Pendant available? Check its current stock."
    }
]

response = client.responses.create(
    model="gpt-4.1-mini",
    input=input_messages,
    tools=tools,
    tool_choice="auto"
)

while True:

    function_calls = [
        item for item in response.output
        if item.type == "function_call"
    ]

    if not function_calls:
        break

    input_messages += response.output

    for item in function_calls:

        print("Tool called:", item.name)

        function_to_call = tool_functions.get(item.name)

        args = json.loads(item.arguments)

        if function_to_call is None:

            result = {"error": "Unknown tool requested"}

        else:

            try:
                result = function_to_call(**args)

            except Exception as e:
                result = {"error": str(e)}

        print("Tool Result:", result)

        input_messages.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result, default=str)
        })

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=input_messages,
        tools=tools,
        tool_choice="auto"
    )

print("\nAI Final Answer:")
print(response.output_text)


