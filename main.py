import mysql.connector
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import chat_with_agent, input_messages as default_input_messages
from cart_tool import add_to_cart
from place_order_tool import place_order
from view_cart_tool import view_cart
from auth import hash_password, verify_password, create_access_token
import re
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_access_token


load_dotenv()


# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# FastAPI application
app = FastAPI()

# JWT authentication security
security = HTTPBearer()


# Get currently logged-in user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, full_name, email, phone
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found."
            )

        return user

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

# Optional authentication for chatbot
optional_security = HTTPBearer(auto_error=False)


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security)
):

    if credentials is None:
        return None

    token = credentials.credentials

    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, full_name, email, phone
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found."
            )

        return user

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

# CORS Configuration
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
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_optional_current_user)
):

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
    "check out",
    "i want to checkout",
    "i want to check out",
    "proceed to checkout",
    "proceed to check out",
    "place my order"
]:

        if not current_user:
            return {
                "reply": "Please log in to your CELESTE ROSE account before placing an order."
            }

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
                    address=checkout["address"],
                    user_id=current_user["id"]
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

class ChatRequest(BaseModel):
    message: str
    session_id: str

class RegisterRequest(BaseModel):
    full_name : str
    email : str
    phone : str
    password : str


@app.post("/auth/register")
def register_user(request: RegisterRequest):

    full_name = request.full_name.strip()
    email= request.email.strip().lower()
    phone = request.phone.strip()
    password = request.password

    if len(full_name) < 2:
        raise HTTPException(status_code=400, detail="Enter a valid name.")

    if "@" not in email or"." not in email:
        raise HTTPException(status_code=400, detail='Enter a valid email')

    if len(phone) != 10 or not phone.isdigit():
        raise HTTPException(status_code=40, detail= "Enter a valid 10-digit number")

    if len(password) < 8:
        raise HTTPException(status_code= 400, detail="Password must contain atleast 8 charachters")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code= 400,
            detail="Password must contain atleast one uppercase letter"
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail= "Password should contain atleast one lowercase letter"
        )
    
    if not re.search(r"[0-9]", password):
        raise HTTPException(
            status_code=40,
            detail="Password must contain atleast one number"
        )
    if not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special charachter"
        )


    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_coide = 400,
                detail = "Email is already registered."
            )

        hashed_password = hash_password(password)


        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, phone, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (full_name, email, phone, hashed_password)
        )

        connection.commit()

        user_id = cursor.lastrowid

        return{
            "success" : True,
            "message" : "Registration successful!",
            "user" : {
                "id" : "user_id",
                "full_name" : full_name,
                "email" : email,
                "phone" : phone                    
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        if connection:
            connection.rollback()

        print("Registration error: ", e)

        raise HTTPException(
            status_code = 500,
            detail = "Registration failed. Please Try Again."
        )
    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


class LoginRequest(BaseModel):
    email: str
    password : str

@app.post("/auth/login")
def login_user(request: LoginRequest):

    email = request.email.strip().lower()
    password = request.password

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary= True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail = "Invalid email or password."
            )

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=401,
                detail = "Invalid email or password."
            )

        access_token = create_access_token(
            {"sub": str(user["id"])
             })

        return {
            "success" : True,
            "message" : 'Login Successful!',
            "access_token" : access_token,
            "token_type" : "bearer",
            "user" : {
                "id" : user["id"],
                "full_name" : user["full_name"],
                "email" : user["email"],
                "phone" : user["phone"]
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Login Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Login Failed. Please Try Again."
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.get("/auth/me")
def get_my_account(
    current_user: dict = Depends(get_current_user)
):
    return{
        "success" : True,
        "message" : 'Account details fetched successfully!',
        "user" : current_user
    }

@app.get("/orders/my")
def get_my_orders(
    current_user: dict = Depends(get_current_user)
):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                o.id AS order_id,
                o.created_at,
                o.total_amount,
                o.order_status,
                oi.product_id,
                p.name AS product_name,
                oi.quantity,
                oi.price
            FROM orders o
            LEFT JOIN order_items oi
                ON o.id = oi.order_id
            LEFT JOIN products p
                ON oi.product_id = p.id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
        """, (current_user["id"],))

        rows = cursor.fetchall()

        orders_dict = {}

        for row in rows:

            order_id = row["order_id"]

            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    "id": order_id,
                    "created_at": row["created_at"],
                    "total_amount": float(row["total_amount"]),
                    "order_status": row["order_status"],
                    "products": []
                }

            if row["product_id"] is not None:
                orders_dict[order_id]["products"].append({
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "quantity": row["quantity"],
                    "price": float(row["price"])
                })

        return {
            "success": True,
            "orders": list(orders_dict.values())
        }

    except Exception as e:
        print("My Orders Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Unable to fetch your orders."
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()