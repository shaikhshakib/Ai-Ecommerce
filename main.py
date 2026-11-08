import mysql.connector
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import chat_with_agent, input_messages as default_input_messages
from cart_tool import add_to_cart
from place_order_tool import place_order
from view_cart_tool import view_cart

load_dotenv()
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/products")
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products


@app.get("/products/filter")
def filter_products(max_price: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE price <= %s", (max_price,))
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products

@app.get("/products/category")
def get_products_by_category(category: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM products WHERE LOWER(category) = LOWER(%s)",
        (category,)
    )
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products
@app.get("/products/search")
def search_products(category: str, max_price: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM products WHERE LOWER(category) = LOWER(%s) AND price <= %s",
        (category, max_price)
    )
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.post("/products")
def add_product(name: str, category: str, price: float):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
        (name, category, price)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Product added successfully"}

@app.put("/products/{product_id}") 
def update_product(product_id: int, price: float): 
    connection = get_db_connection() 
    cursor = connection.cursor() 
    cursor.execute( "UPDATE products SET price = %s WHERE id = %s", (price, product_id) ) 
    connection.commit() 
    updated = cursor.rowcount 
    cursor.close() 
    connection.close() 
    return {"updated": updated}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    connection.commit()

    deleted = cursor.rowcount

    cursor.close()
    connection.close()

    return {"deleted": deleted}

class ChatRequest(BaseModel):
    message : str
    session_id : str

sessions = {}
pending_carts = {}
checkout_states = {}
@app.post("/chat")
def chat(request: ChatRequest):

    if request.session_id not in sessions:
        sessions[request.session_id] = default_input_messages.copy()

    pending_cart = pending_carts.setdefault(request.session_id, {})
    checkout = checkout_states.setdefault(request.session_id, {})

    user_message = request.message.strip()
    message_lower = user_message.lower()

    print("DEBUG SESSION:", request.session_id)
    print("DEBUG PENDING CART:", pending_cart)
    print("DEBUG CHECKOUT:", checkout)

    # Step 1: Handle pending cart confirmation
    if pending_cart:

        if message_lower in ["yes", "yes please", "confirm", "do it", "add it"]:

            result = add_to_cart(
                product_id=pending_cart["product_id"],
                quantity=pending_cart["quantity"],
                session_id=request.session_id,
                confirmed=True
            )

            pending_cart.clear()

            reply = (
                result.get("message")
                or result.get("error")
                or "Cart request processed."
            )

            sessions[request.session_id].append({
                "role": "user",
                "content": request.message
            })

            sessions[request.session_id].append({
                "role": "assistant",
                "content": reply
            })

            return {"reply": reply}

        elif message_lower in ["no", "no thanks", "cancel", "don't", "dont"]:

            pending_cart.clear()

            return {
                "reply": "No problem! Your product was not added to the cart."
            }

        else:
            pending_cart.clear()

    # Step 2: Start checkout
    if not checkout and message_lower in [
        "checkout",
        "i want to checkout",
        "proceed to checkout",
        "place my order"
    ]:

        cart = view_cart(request.session_id)

        if not cart["items"]:
            return {"reply": "Your cart is empty. Please add products before checkout."}

        checkout_states[request.session_id] = {
            "stage": "name"
        }

        return {
            "reply": "Great! Let's complete your order. Please enter your full name."
        }

    # Step 3: Handle checkout cancellation
    if checkout and message_lower in ["cancel", "cancel checkout", "stop"]:

        checkout_states.pop(request.session_id, None)

        return {
            "reply": "Checkout cancelled. Your cart is still safe."
        }

    # Step 4: Collect customer details
    if checkout:

        stage = checkout["stage"]

        # Collect customer name
        if stage == "name":

            if len(user_message) < 2:
                return {"reply": "Please enter a valid full name."}

            checkout["customer_name"] = user_message
            checkout["stage"] = "phone"

            return {
                "reply": "Thank you! Now please enter your 10-digit mobile number."
            }

        # Collect phone number
        elif stage == "phone":

            phone = "".join(
                character for character in user_message
                if character.isdigit()
            )

            if len(phone) != 10:
                return {
                    "reply": "Please enter a valid 10-digit mobile number."
                }

            checkout["phone"] = phone
            checkout["stage"] = "address"

            return {
                "reply": "Please enter your complete delivery address."
            }

        # Collect delivery address
        elif stage == "address":

            if len(user_message) < 10:
                return {
                    "reply": "Please enter a complete delivery address."
                }

            checkout["address"] = user_message

            # Fetch latest cart summary
            cart = view_cart(request.session_id)

            if not cart["items"]:
                checkout_states.pop(request.session_id, None)

                return {
                    "reply": "Your cart is empty. Please add products before checkout."
                }

            summary = "Your order summary:\n\n"

            for item in cart["items"]:

                summary += (
                    f"{item['name']} x {item['quantity']} "
                    f"= ₹{item['subtotal']:.2f}\n"
                )

            summary += f"\nTotal Amount: ₹{cart['total']:.2f}"

            summary += (
                "\n\nDelivery Details:"
                f"\nName: {checkout['customer_name']}"
                f"\nPhone: {checkout['phone']}"
                f"\nAddress: {checkout['address']}"
            )

            summary += "\n\nWould you like to confirm and place this order? (Yes/No)"

            checkout["stage"] = "confirmation"

            return {"reply": summary}

        # Step 5: Final order confirmation
        elif stage == "confirmation":

            if message_lower in [
                "yes",
                "yes please",
                "confirm",
                "place order",
                "place my order",
                "do it"
            ]:

                result = place_order(
                    session_id=request.session_id,
                    customer_name=checkout["customer_name"],
                    phone=checkout["phone"],
                    address=checkout["address"]
                )

                checkout_states.pop(request.session_id, None)

                if result["success"]:

                    return {
                        "reply": (
                            f"Your order has been placed successfully!\n\n"
                            f"Order ID: {result['order_id']}\n"
                            f"Customer: {result['customer_name']}\n"
                            f"Total Amount: ₹{result['total_amount']:.2f}\n\n"
                            "Thank you for shopping with Céleste Rosé!"
                        )
                    }

                return {
                    "reply": result["message"]
                }

            elif message_lower in ["no", "no thanks"]:

                checkout_states.pop(request.session_id, None)

                return {
                    "reply": "Your order was not placed. Your cart is still available."
                }

            else:

                return {
                    "reply": "Please confirm your order by replying Yes or No."
                }

    # Step 6: Normal AI conversation
    reply = chat_with_agent(
        request.message,
        sessions[request.session_id],
        pending_cart,
        request.session_id
    )

    return {"reply": reply}