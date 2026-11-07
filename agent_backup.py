import json
from openai import OpenAI
from dotenv import load_dotenv
from product_tool import search_products, search_products_by_name
from stock_tool import check_stock
from cart_tool import add_to_cart
from discount_tool import check_discount
from get_all_products_tool import get_all_products
load_dotenv()

client = OpenAI()
tool_functions = {
    "search_products": search_products,
    "search_products_by_name" : search_products_by_name,
    "check_stock" : check_stock,
    "add_to_cart" : add_to_cart,
    "check_discount" : check_discount,
    "get_all_products" : get_all_products

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
},
{
    "type" : "function",
    "name" : 'check_discount',
    "description" : "Check the discount percentage and final discounted price  of a product using its product ID.",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "product_id" : {
                "type" : "integer"
            }
        },
        "required" : ["product_id"],
        "additionalProperties" : False
    },
    "strict" : True
},
{
    "type" : "function",
    "name" : "get_all_products",
    "description" : "Get the complete list of products available in the jewellery store , including product ID, name, category,price and stock",
    "parameters" : {
        "type" : "object",           
        "properties" : {},
        "required" : [],
        "additionalProperties" : False
    },
    "strict" : True
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

        1. First use search_products_by_name to identify the product.
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

        IMPORTANT TOOL RULES:

        1. When a customer asks whether a product is available or asks for current stock, you MUST call check_stock.

        2. First identify the product using search_products_by_name.

        3. Extract the product ID from the search result.

        4. Then call check_stock using that product ID.

        5. Do not answer stock availability using search results alone.

        6. Always display prices in Indian Rupees (₹).

        DISCOUNT AND OFFER RULES:

        1. Never invent discounts, offers, or promotional codes.
        2. Never claim that you checked discounts because no discount tool exists.
        3. If a customer asks about discounts, clearly explain that discount information is currently unavailable.
        4. Never promise to check offers in the future.
        5. Only provide information returned by available tools or explicitly provided in the developer instructions.

        - When a customer asks about a discount or offer on a product:
        1. Identify the product using search_products_by_name.
        2. Get its product ID.
        3. Call check_discount using that product ID.
        4. Tell the customer the original price, discount percentage, and final discounted price.
        5. Never invent or assume discounts. Only report values returned by the tool.
        6. If no discount is available, clearly tell the customer.

        - When a customer asks to see all products or the complete jewellery collection:
        1. Call get_all_products.
        2. Display the products with their names, categories and prices.
        3. Mention stock availability when relevant.
        4. Do not invent products, prices or stock.
        5. Only show information returned by the tool.
        """
    },
]
while True:

    # Step 1: Get customer message
    user_message = input("\nYou: ")

    if user_message.lower().strip() == "exit":
        print("Chat ended.")
        break

    input_messages.append({
        "role": "user",
        "content": user_message
    })

    # Step 2: Get AI response
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=input_messages,
        tools=tools,
        tool_choice="auto"
    )

    # Step 3: Execute tools
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

                    if item.name == "add_to_cart":

                        confirmation = input(
                            "Confirm adding this product to cart? (yes/no): "
                        )

                        if confirmation.lower().strip() == "yes":

                            result = function_to_call(
                                **args,
                                confirmed=True
                            )

                        else:

                            result = {
                                "success": False,
                                "message": "Customer cancelled the cart operation"
                            }

                    else:

                        result = function_to_call(**args)

                except Exception as e:

                    result = {"error": str(e)}

            print("Tool Result:", result)

            input_messages.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result, default=str)
            })

        # Step 4: Send tool results back to AI
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=input_messages,
            tools=tools,
            tool_choice="auto"
        )

    # Step 5: Display final answer
    print("\nAI:", response.output_text)

    # Step 6: Save AI response in conversation history
    input_messages += response.output

