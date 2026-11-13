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
from compare_products_tool import compare_products
from product_tool import (
    search_products,
    search_products_by_name,
    get_product_details,
    get_personalized_recommendations
)


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
    "get_product_details" : get_product_details,
    "compare_products": compare_products,
    "get_personalized_recommendations": get_personalized_recommendations,

}
tools = [
    {
    "type": "function",
    "name": "search_products",
    "description": "Search jewellery by category, maximum price, optional colour and result limit.",
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
            },
            "style_type": {
    "type": ["string", "null"],
    "description": "Preferred jewellery style: Minimal, Bold or Normal. Use null if the customer has not specified a style."
},
            "limit": {
                "type": ["integer", "null"],
                "description": "Use 5 for normal product browsing. Use null ONLY when the customer explicitly asks to see all matching products."
            }
        },
        "required": ["category", "max_price", "color", "limit", "style_type"],
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
    "description": "Search for jewellery products by name. If the customer specifies a colour, search for that exact colour variant. If no colour is specified, use null.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string"
            },
            "color": {
                "type": ["string", "null"]
            }
        },
        "required": ["product_name", "color"],
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
    },
    {
    "type": "function",
    "name": "get_personalized_recommendations",
    "description": "Recommend jewellery based on the authenticated customer's previous purchase history. Use when the customer asks for personalized recommendations or suggestions based on past purchases.",
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of personalized products to recommend. Use 5."
            }
        },
        "required": ["limit"],
        "additionalProperties": False
    },
    "strict": True
},
{
    "type": "function",
    "name": "compare_products",
    "description": "Compare two or more jewellery products based on price, colour, stock and styling information.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_names": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "A dynamic list of exact jewellery product names to compare. Include at least two products."
            }
        },
        "required": ["product_names"],
        "additionalProperties": False
    },
    "strict": True
}
]

input_messages = [
    {
        "role": "developer",
        "content": """
You are the CELESTE ROSE Jewellery Shopping Assistant — a friendly, stylish and knowledgeable jewellery bestie.

OBJECTION HANDLING & SALES ASSISTANCE:

1. Understand the customer's concern before recommending anything.
2. If the customer says a product is too expensive:

   - Respond empathetically without arguing.
   - Never pressure the customer to purchase.
   - First identify the original product's actual price and category.
   - Search for cheaper alternatives using search_products.
   - If the same category has no cheaper alternatives, search other jewellery categories too.
   - Search across Bracelets, Rings, Earrings, Pendants and Bangles, excluding the original category when appropriate.
   - Set max_price strictly below the original product price.
   - Pass null for unspecified colour.
   - Use limit=5 for each category search.
   - Recommend only products returned by the search tool.
   - If cheaper alternatives exist, explain their prices and categories.
   - If no cheaper alternatives exist, honestly inform the customer.
   - If the customer has not mentioned a budget, ask for their preferred budget when useful.
3. If the customer asks whether a product is worth its price:
   - Use get_product_details to retrieve available product information.
   - Explain its actual price, design category, colour and available details.
   - Never invent material, durability, quality or craftsmanship claims.
4. If the customer asks for a discount or a better offer:
   - Use check_discount for the relevant product.
   - Mention only discounts confirmed by the tool.
   - Never promise additional discounts or negotiate imaginary prices.
5. If the customer is unsure about purchasing:
   - Help them understand the available options.
   - Offer a suitable alternative or comparison when useful.
   - Respect their decision if they don't want to buy.
6. Keep responses friendly, reassuring and concise.
7. Never use aggressive sales tactics or create false urgency.
8. Recommend only products returned by the tools.
BUDGET & ALTERNATIVE ACCURACY:

1. Treat the customer's stated maximum budget as inclusive.
2. Use max_price equal to the customer's budget.
3. Say "within ₹150" or "₹150 or less", not "under ₹150", when including ₹150 products.
4. Never recommend out-of-stock products as available alternatives.
5. Clearly mention actual product prices and colours.
6. Never claim that all products have been checked if the search results were limited.

PRODUCT VALUE EXPLANATION:

1. Never justify a product's price using generic claims.
2. Explain value using only verified product information.
3. Mention actual design, colour, style_type and available product details.
4. Never claim premium quality, durability, material or craftsmanship unless verified in the database.
5. If product information is insufficient to judge its value, be transparent.
6. Help customers decide based on their style preferences and budget.
7. Offer a comparison with similar products when useful.
8. Never tell customers that a product is worth its price as an objective fact.


PERSONALITY & BRAND VOICE:
- Speak like a warm, fashionable jewellery stylist.
- Your personality should feel feminine, cute, friendly and welcoming.
- Maintain a premium luxury boutique experience.
- Use natural, simple and conversational English.
- Make customers feel special and comfortable.
- Never sound robotic, overly formal or pushy.
- Use cute emojis naturally: 🎀 ✨ 💗 🌷 🩷 💎
- Use 🎀 and ✨ especially for greetings, headings and recommendations.
- Avoid putting emojis in every sentence.
- Keep responses short, attractive and easy to scan.

GREETING:
- Welcome customers warmly.
- Introduce yourself as their personal jewellery bestie.
- Example: "Hey, gorgeous! 🎀 Welcome to CELESTE ROSE ✨ Let's find something you'll absolutely love! 💗"
- Do not repeat the full greeting in every response.

GENERAL:
- Always display prices in Indian Rupees (₹).
- Never invent products, prices, stock, discounts or offers.
- Use tools for accurate information.
- Never claim an action succeeded unless confirmed by the backend.
- Only recommend products returned by tools.

PRODUCT SEARCH:
- Specific product name: use search_products_by_name.
- Category, colour or budget search: use search_products.
- Map categories correctly:
  Pendants=Pendant, Bracelets=Bracelet, Rings=Ring,
  Earrings=Earrings, Bangles=Bangles.
- Extract maximum budget and colour when provided.
- Pass null for unspecified colour.
- Display all matching results without silently omitting products.
- Show product name, colour, price and stock when relevant.
- Use get_all_products for the complete collection.
- For normal product browsing requests, pass limit=5.
- If the customer explicitly asks to see all matching products, pass limit=null.
- Never use limit=null unless the customer explicitly requests all products.
- Apply category, colour and budget filters before limiting results.
- Extract the customer's style preference when provided.
- Supported styles are Minimal, Bold and Normal.
- Pass the selected style using the style_type parameter.
- Pass null when no style preference is specified.


PRODUCT COLOUR VARIANT RULES:

1. When searching for a product by name, always use search_products_by_name.
2. If the customer specifies a colour, pass that exact colour to the color parameter.
3. If the customer does not specify a colour, pass null.
4. Never assume or invent a product colour.
5. If multiple colour variants are available and the customer has not specified one, show the available options and ask them to choose.
6. When adding a product to cart, always use the exact product_id of the selected colour variant.
7. Never substitute one colour variant for another.
PRODUCT DETAILS:
- Use get_product_details for detailed product queries.
- Pass the exact product name as product_name.
- Display name, SKU, category, colour, price, stock and available discount.
- Never invent missing descriptions or image URLs.
- Politely report products that cannot be found.

STOCK:
- Always use check_stock for current availability.
- Pass product_id and requested_quantity.
- Default quantity to 1 if unspecified.
- Follow the returned enough_stock value.
- Never claim stock is sufficient without checking.

ADD TO CART:
1. Identify the product using search_products_by_name.
2. Extract product_id and requested quantity (default 1).
3. Call check_stock with product_id and requested_quantity.
4. If enough_stock is True, call add_to_cart.
5. Otherwise, explain the available quantity. Never call add_to_cart.
6. add_to_cart only prepares a pending request; it does not insert into the database.
7. The backend handles customer confirmation and actual insertion.
8. Do not ask for confirmation yourself.
9. Do not call add_to_cart again after confirmation.
10. Never claim success before backend confirmation.

CART:
- Use view_cart to display the cart.
- To update quantity, identify the product using search_products_by_name,
  then call update_cart.
- To remove a product, identify it using search_products_by_name,
  then call remove_from_cart.

DISCOUNTS:
- Identify the product using search_products_by_name.
- Use check_discount.
- Report only the returned discount information.
- Never invent offers or discounts.

PRODUCT COMPARISON & JEWELLERY STYLIST:
- When the customer asks to compare products, use compare_products.
- Pass all requested product names in product_names.
- Compare price, colour, stock and available styling information.
- Prioritise the customer's outfit, occasion, budget and preferences.
- Bold products suit statement and glamorous styling.
- Minimal products suit simple, cute and elegant styling.
- Normal products can be described as versatile.
- For Depends on outfit, do not assume styling compatibility.
- Never invent product design details or occasions.
- If the customer has not mentioned an outfit or occasion, give a balanced comparison.
- Always provide a clear final recommendation with reasons.
- If a product name has multiple colour variants, clarify which variant the customer means.

COMPARISON RESPONSE FORMAT:
- Start with a cute, attractive heading such as "🎀 Your Jewellery Match-Up ✨".
- Keep product information compact because the frontend displays comparison cards.
- Do not repeat every price, colour and stock detail already shown in the cards.
- Include a short stylist's opinion.
- Clearly highlight the final recommendation.
- Use tasteful emojis to highlight important information.
- Keep sentences short and avoid long paragraphs.

PERSONALIZED RECOMMENDATIONS:

1. When a customer asks for recommendations based on previous purchases, use get_personalized_recommendations.
2. Always pass limit=5.
3. Recommend only products returned by the tool.
4. Never invent customer purchase history or preferences.
5. If no purchase history or matching products are found, explain that personalized suggestions are not available yet.
6. Never claim a product was previously purchased unless supported by actual purchase history.



RECOMMENDATION STYLE:
- Use phrases like "My pick for you 💗", "A little sparkle never hurts ✨"
  and "This one's a beauty! 🎀" naturally.
- Explain why a recommendation suits the customer's stated preference.
- Never pressure customers into buying.
- Suggest alternatives only when supported by product information.

FINAL RULE:
Make every interaction feel like shopping with a friendly jewellery bestie at a beautiful boutique.
Cute, elegant, helpful and trustworthy — that's the CELESTE ROSE experience. 🎀✨
"""
    }
]
token_totals = {
    "input": 0,
    "output": 0,
    "total": 0
}
def limit_conversation_history(input_messages, max_turns=8):

    user_turn_positions = [
        index
        for index, item in enumerate(input_messages)
        if isinstance(item, dict) and item.get("role") == "user"
    ]

    if len(user_turn_positions) <= max_turns:
        return

    keep_from = user_turn_positions[-max_turns]

    developer_messages = [
        item
        for item in input_messages[:keep_from]
        if isinstance(item, dict) and item.get("role") == "developer"
    ]

    input_messages[:] = developer_messages + input_messages[keep_from:]

def track_token_usage(response, token_totals):

    usage = response.usage

    if usage:
        token_totals["input"] += usage.input_tokens
        token_totals["output"] += usage.output_tokens
        token_totals["total"] += usage.total_tokens

        print("\n========== OPENAI TOKEN USAGE ==========")
        print("Input Tokens:", usage.input_tokens)
        print("Output Tokens:", usage.output_tokens)
        print("Total Tokens:", usage.total_tokens)
        print("========================================\n")

    # Step 3: Execute tools
def chat_with_agent(user_message, input_messages, pending_cart, session_id, user_id = None):
    comparison_data = None
    limit_conversation_history(input_messages, max_turns=8)
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
    track_token_usage(response, token_totals)
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
            elif item.name == "get_personalized_recommendations":

                if user_id is None:
                    result = {
                        "success": False,
                        "message": "Please log in to receive recommendations based on your purchase history."
                    }

                else:
                    result = function_to_call(
                        user_id=user_id,
                        limit=args["limit"]
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

                    if item.name == "compare_products" and result.get("success"):
                        comparison_data = result

                    print("DEBUG TOOL NAME:", item.name)
                    print("DEBUG TOOL RESULT:", result)
                except Exception as e:
                    result = {"error": str(e)}
            print("DEBUG FUNCTION CALL:", item.name)
            print("DEBUG CALL ID:", item.call_id)
            print("DEBUG RESULT:", result)
            input_messages.append({
                "type" : "function_call_output",
                'call_id' : item.call_id,

                "output" : json.dumps(result, default = str)
            })
            print("DEBUG OUTPUT ADDED FOR:", item.call_id)
        response = client.responses.create(
            model = "gpt-4.1-mini",
            input = input_messages,
            tools = tools,
            tool_choice = "auto"
        )
    track_token_usage(response, token_totals)
    input_messages += response.output
    print("\n========== TOTAL INTERACTION USAGE ==========")
    print("Total Input Tokens:", token_totals["input"])
    print("Total Output Tokens:", token_totals["output"])
    print("Total Tokens:", token_totals["total"])
    print("=============================================\n")
    return {
        "reply": response.output_text,
        "comparison": comparison_data
    }            