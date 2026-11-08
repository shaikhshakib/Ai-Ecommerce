import json
from openai import OpenAI
from dotenv import load_dotenv
from product_tool import search_products, search_products_by_name, get_product_details
from stock_tool import check_stock
from cart_tool import add_to_cart
from discount_tool import check_discount
from get_all_products_tool import get_all_products
from view_cart_tool import view_cart
from update_cart_tool import update_cart
from remove_from_cart_tool import remove_from_cart

load_dotenv()

client = OpenAI()
tool_functions = {
    "search_products": search_products,
    "search_products_by_name" : search_products_by_name,
    "check_stock" : check_stock,
    "add_to_cart" : add_to_cart,
    "check_discount" : check_discount,
    "get_all_products" : get_all_products,
    "view_cart" : view_cart,
    "update_cart": update_cart,
    "remove_from_cart": remove_from_cart,
    "get_product_details" : get_product_details

}
tools = [
    {
    "type": "function",
    "name": "search_products",
    "description": "Search jewellery by category, maximum price and optional colour.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Product category such as Pendant, Bracelet, Ring, Earrings or Bangles."
            },
            "max_price": {
                "type": ["number", "null"],
                "description": "Maximum product price in INR. Use null if customer has not specified a budget."
            },
            "color": {
                "type": ["string", "null"],
                "description": "Optional product colour such as Gold or Silver. Use null if not specified."
            }
        },
        "required": ["category", "max_price", "color"],
        "additionalProperties": False
    },
    "strict": True
},
{
    "type": "function",
    "name": "check_stock",
    "description": "Check available stock of a jewellery product and verify whether the requested quantity is available.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {"type": "integer"},
            "requested_quantity": {"type": "integer"}
        },
        "required": ["product_id", "requested_quantity"],
        "additionalProperties": False
    },
    "strict": True
},
{
    "type": "function",
    "name": "add_to_cart",
    "description": "Prepare a pending cart request for a product. Do not insert anything into the database. The backend will ask the customer for confirmation and handle the actual cart insertion.",
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
    "type": "function",
    "name": "get_product_details",
    "description": "Get complete details of a specific jewellery product.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Exact name of the product."
            }
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
    },
    {
        "type": "function",
        "name": "view_cart",
        "description": "View all products in the customer's shopping cart.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "update_cart",
        "description": "Update the quantity of an existing product in the customer's shopping cart.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "ID of the product to update."
                },
                "quantity": {
                    "type": "integer",
                    "description": "New quantity requested by the customer."
                }
            },
            "required": ["product_id", "quantity"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "remove_from_cart",
        "description": "Remove a product from the customer's shopping cart when requested.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "ID of the product to remove."
                }
            },
            "required": ["product_id"],
            "additionalProperties": False
        },
        "strict": True
    }
]

input_messages = [
    {
        "role": "developer",
        "content": """
You are Céleste Rosé's Jewellery Shopping Assistant.

GENERAL RULES:
1. Always display prices in Indian Rupees (₹).
2. Never invent products, prices, stock or discounts.
3. Use available tools to retrieve accurate information.
4. Never claim an action succeeded unless the tool confirms it.

PRODUCT SEARCH:
1. Use search_products_by_name when customers mention a specific product name.
2. Use search_products for category, price and colour-based searches.
3. Identify the correct category from the customer's request:
   - Pendants = Pendant
   - Bracelets = Bracelet
   - Rings = Ring
   - Earrings = Earrings
   - Bangles = Bangles
4. Extract the maximum budget when the customer mentions a price limit.
5. Extract the colour when the customer mentions Gold, Silver or another colour.
6. If the customer does not mention a colour, pass null.
7. Never invent product details. Only recommend products returned by the tools.
8. Use get_all_products when customers ask to see the complete collection.
9. Use check_stock when customers ask about product availability or stock.
10. Display product name, colour, price and available stock when relevant.
11. Display every matching product returned by search_products. Never silently omit matching products.
12. Preserve the exact product name, colour, price and stock returned by the tool.

PRODUCT DETAILS:
1. When a customer asks for detailed information about a specific product, use get_product_details.
2. Pass the exact product name as product_name.
3. Display the product name, SKU, category, colour, price and available stock.
4. Display discount information when applicable.
5. If description or image_url is missing, do not invent information.
6. If the product is not found, politely inform the customer that the product is unavailable.
7. Never invent product details.

ADD TO CART:
1. When a customer wants to add a product, identify it using search_products_by_name.
2. Extract the product_id and requested quantity from the search result and customer message.
3. If the customer does not mention a quantity, use requested_quantity = 1.
4. ALWAYS call check_stock before calling add_to_cart.
5. Pass both product_id and requested_quantity to check_stock.
6. Check the enough_stock value returned by check_stock.
7. If enough_stock is True, call add_to_cart with the product_id and requested quantity.
8. If enough_stock is False, DO NOT call add_to_cart.
9. Inform the customer about the available stock and explain that the requested quantity is unavailable.
10. The add_to_cart tool only prepares a pending request. It does not insert anything into the database.
11. The backend will ask the customer for confirmation after the pending request is prepared.
12. Do not ask for confirmation yourself.
13. Do not call add_to_cart again after the customer confirms.
14. The backend handles Yes and No responses.
15. Never claim a product was added until the backend confirms success.

STOCK:
1. Always use check_stock for current stock availability.
2. Pass product_id and requested_quantity to check_stock.
3. If the customer does not mention a quantity, use requested_quantity = 1.
4. Use enough_stock to determine whether the requested quantity is available.
5. Never claim sufficient stock without checking the tool result.

VIEW CART:
Use view_cart when the customer asks to see their cart.

UPDATE CART:
Use search_products_by_name to identify the product, then update_cart to change its quantity.

REMOVE FROM CART:
Use search_products_by_name to identify the product, then remove_from_cart to remove it.

DISCOUNTS:
1. Use search_products_by_name to identify the product.
2. Use check_discount to retrieve discount information.
3. Report only the values returned by the tool.
4. Never invent discounts or offers.

"""
    }
]
    # Step 3: Execute tools
def chat_with_agent(user_message, input_messages, pending_cart, session_id):
    input_messages.append({
        "role" : "user",
        "content" : user_message
    })

    response = client.responses.create(
        model = "gpt-4.1-mini",
        input = input_messages,
        tools = tools,
        tool_choice = "auto"
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

            function_to_call = tool_functions.get(item.name)
            args = json.loads(item.arguments)

            if function_to_call is None:
                result = {"error": "Unknown tool requested"}
            elif item.name == "view_cart":
                result = view_cart(session_id)
            elif item.name == "update_cart":
                result = update_cart(
                    product_id=args["product_id"],
                    quantity=args["quantity"],
                    session_id=session_id
                )
            elif item.name == "remove_from_cart":
                result = remove_from_cart(
                    product_id=args["product_id"],
                    session_id=session_id
                )
            elif item.name == "add_to_cart":
                pending_cart.update(args)
                print("DEBUG PENDING CART AFTER ADD:", pending_cart)
                result = {
                    "success": False,
                    "pending_confirmation": True,
                    "message": "Product is ready. Ask the customer for confirmation. Do not add it yet."
                }

            else:
                try:
                    result = function_to_call(**args)
                    print("DEBUG TOOL NAME:", item.name)
                    print("DEBUG TOOL RESULT:", result)
                except Exception as e:
                    result = {"error": str(e)}

            input_messages.append({
                "type" : "function_call_output",
                'call_id' : item.call_id,

                "output" : json.dumps(result, default = str)
            })
            if pending_cart:
                confirmation_message = "Your product is ready. Would you like me to add it to your cart? Please confirm."

                input_messages.append({
                    "role": "assistant",
                    "content": confirmation_message
                })

                return confirmation_message
        response = client.responses.create(
            model = "gpt-4.1-mini",
            input = input_messages,
            tools = tools,
            tool_choice = "auto"
        )

    input_messages += response.output

    return response.output_text               