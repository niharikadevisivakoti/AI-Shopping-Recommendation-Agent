from pathlib import Path
import sys

from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from recommendation_engine.recommender import RecommendationEngine

engine = RecommendationEngine(ROOT / "data" / "products.csv")

mcp = FastMCP("Product Recommendation Agent")


@mcp.tool
def search_products(query: str) -> list:
    """Search products by name, category, description, or tags."""
    return engine.products(query, None)


@mcp.tool
def get_products_by_category(category: str) -> list:
    """Get products belonging to a category."""
    return engine.products(None, category)


@mcp.tool
def filter_products_by_price(max_price: float) -> list:
    """Find products under the given maximum price."""
    result = engine.products(None, None)
    products = result.get("products", [])

    return [
        product
        for product in products
        if product.get("price", 0) <= max_price
    ]

@mcp.tool
def get_similar_products(product_id: int, limit: int = 6) -> list:
    """Get products similar to a specific product."""
    return engine.similar(product_id, limit)


@mcp.tool
def get_recommendations(
    viewed_product_ids: list[int],
    category: str | None = None,
    limit: int = 6,
) -> list:
    """Get personalized product recommendations."""
    return engine.personalized(
        viewed_product_ids,
        category,
        limit,
    )


if __name__ == "__main__":
    mcp.run()