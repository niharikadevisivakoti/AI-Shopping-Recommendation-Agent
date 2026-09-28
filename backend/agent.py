import json
import ollama

from backend.mcp_server import (
    search_products,
    get_products_by_category,
    filter_products_by_price,
    get_similar_products,
    get_recommendations,
)

MODEL = "llama3.2:3b"
USD_TO_INR = 96


def ask_llama(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are a shopping recommendation assistant.

Understand the user's shopping request and choose the correct action.

Return ONLY valid JSON.

Available actions:

1. search
{"action":"search","query":"running shoes"}

2. category
{"action":"category","category":"Footwear"}

3. price
{"action":"price","max_price":31.25}

4. search_and_price
{"action":"search_and_price","query":"running shoes","max_price":31.25}

5. similar
{"action":"similar","product_id":1}

6. recommendations
{"action":"recommendations"}

7. none
{"action":"none"}

For Indian rupees:
1 USD = 96 INR.

Example:
"I need running shoes under 3000 rupees"

Return:
{"action":"search_and_price","query":"running shoes","max_price":31.25}
""",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response["message"]["content"]


def run_tool(decision: dict):
    action = decision.get("action")

    if action == "search":
        return search_products(
            decision.get("query", "")
        )

    if action == "category":
        return get_products_by_category(
            decision.get("category", "")
        )

    if action == "price":
        return filter_products_by_price(
            float(decision.get("max_price", 0))
        )

    if action == "search_and_price":
        search_result = search_products(
            decision.get("query", "")
        )

        products = search_result.get("products", [])

        max_price = float(
            decision.get("max_price", 0)
        )

        filtered_products = [
            product
            for product in products
            if product.get("price", 0) <= max_price
        ]

        return {
            "products": filtered_products,
            "available_matches": products,
            "max_price": max_price,
        }

    if action == "similar":
        return get_similar_products(
            int(decision.get("product_id", 0))
        )

    if action == "recommendations":
        return get_recommendations([])

    return None


def create_response(user_message: str, decision: dict, result):
    action = decision.get("action")

    if action == "search_and_price":
        products = result.get("products", [])
        alternatives = result.get("available_matches", [])
        max_price = result.get("max_price", 0)

        budget_inr = round(max_price * USD_TO_INR)

        if products:
            lines = [
                f"Here are the products I found under ₹{budget_inr}:"
            ]

            for product in products[:5]:
                price_inr = round(
                    product.get("price", 0) * USD_TO_INR
                )

                lines.append(
                    f"- {product.get('name')} — ₹{price_inr:,}"
                )

            return "\n".join(lines)

        if alternatives:
            lines = [
                f"I couldn't find any matching products under ₹{budget_inr}."
            ]

            lines.append("The available matching product is:")

            for product in alternatives[:3]:
                price_inr = round(
                    product.get("price", 0) * USD_TO_INR
                )

                lines.append(
                    f"- {product.get('name')} — ₹{price_inr:,}"
                )

            lines.append(
                "Would you like me to look for alternatives within your budget?"
            )

            return "\n".join(lines)

        return (
            f"I couldn't find any products matching "
            f"'{decision.get('query', '')}' under ₹{budget_inr}."
        )

    if action == "search":
        products = result.get("products", [])

        if not products:
            return "I couldn't find any matching products."

        lines = ["Here are the products I found:"]

        for product in products[:5]:
            price_inr = round(
                product.get("price", 0) * USD_TO_INR
            )

            lines.append(
                f"- {product.get('name')} — ₹{price_inr:,}"
            )

        return "\n".join(lines)

    if action == "category":
        products = result.get("products", [])

        if not products:
            return "I couldn't find products in that category."

        lines = ["Here are some products from that category:"]

        for product in products[:5]:
            price_inr = round(
                product.get("price", 0) * USD_TO_INR
            )

            lines.append(
                f"- {product.get('name')} — ₹{price_inr:,}"
            )

        return "\n".join(lines)

    if action == "price":
        products = result.get("products", [])

        if not products:
            return "I couldn't find products within that price range."

        lines = ["Here are some products within your budget:"]

        for product in products[:5]:
            price_inr = round(
                product.get("price", 0) * USD_TO_INR
            )

            lines.append(
                f"- {product.get('name')} — ₹{price_inr:,}"
            )

        return "\n".join(lines)

    if action == "similar":
        products = result.get("products", [])

        if not products:
            return "I couldn't find similar products."

        lines = ["Here are some similar products:"]

        for product in products[:5]:
            price_inr = round(
                product.get("price", 0) * USD_TO_INR
            )

            lines.append(
                f"- {product.get('name')} — ₹{price_inr:,}"
            )

        return "\n".join(lines)

    if action == "recommendations":
        products = result.get("products", [])

        if not products:
            return "I couldn't generate recommendations yet."

        lines = ["Here are some recommendations:"]

        for product in products[:5]:
            price_inr = round(
                product.get("price", 0) * USD_TO_INR
            )

            lines.append(
                f"- {product.get('name')} — ₹{price_inr:,}"
            )

        return "\n".join(lines)

    return "I couldn't understand that shopping request."


def agent_chat(user_message: str):
    decision_text = ask_llama(user_message)

    try:
        decision = json.loads(decision_text)
    except json.JSONDecodeError:
        return {
            "message": "I couldn't understand your request.",
            "decision": {},
            "products": [],
        }

    result = run_tool(decision)

    message = create_response(
        user_message,
        decision,
        result,
    )

    return {
        "message": message,
        "decision": decision,
        "products": result,
    }