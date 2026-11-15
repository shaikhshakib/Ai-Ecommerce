from mcp.server import MCPServer
from product_tool import search_products, get_product_details
from stock_tool import check_stock
from discount_tool import check_discount

# Create MCP server
mcp = MCPServer("CELESTE ROSE")

@mcp.tool()
def search_jewellery_products(
    category: str,
    max_price : float | None = None,
    color: str | None = None,
    limit: int = 5,
    style_type : str | None = None
) -> list[dict]:

    """Search CELESTE ROSE jewellery products by category, price, colour and 
    style."""

    return search_products(
        category = category,
        max_price = max_price,
        color = color,
        limit = limit,
        style_type = style_type
    )

@mcp.tool()
def get_jewellery_product_details(product_name: str) -> dict | None:
    """Get complete details of a CELESTE ROSE jewellery product by its exact name."""
    return get_product_details(product_name)

@mcp.tool()
def check_jewellery_stock(product_id : int,
                          requested_quantity: int = 1
                          )-> dict:
    """Check available stock for a CELESTE ROSE jewellery product."""

    return check_stock(
        product_id = product_id,
        requested_quantity= requested_quantity
    )

@mcp.tool()
def check_jewellery_discount(product_id : int)-> dict:
    """Check the discounted price of a CELESTE ROSE product."""
    return check_discount(product_id)

if __name__ == "__main__":
    mcp.run()