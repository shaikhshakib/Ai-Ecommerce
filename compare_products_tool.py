import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def compare_products(product_names):

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = connection.cursor(dictionary=True)

        matched_products = []
        not_found = []

        for product_name in product_names:

            query = """
                SELECT
                    id,
                    name,
                    category,
                    price,
                    color,
                    stock,
                    style_type,
                    occasion,
                    outfit_compatibility
                FROM products
                WHERE LOWER(name) = LOWER(%s)
            """

            cursor.execute(query, (product_name,))
            products = cursor.fetchall()

            if products:
                for product in products:
                    product["price"] = float(product["price"])

                matched_products.extend(products)

            else:
                not_found.append(product_name)

        return {
            "success": True,
            "products": matched_products,
            "not_found": not_found
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()