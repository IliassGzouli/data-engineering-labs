"""Génération d'événements e-commerce synthétiques."""

import argparse
import json
import logging
import random
import time
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

logger = logging.getLogger(__name__)

PRODUCTS = (
    {"product_id": "P001", "name": "Keyboard", "price": "49.90"},
    {"product_id": "P002", "name": "Mouse", "price": "24.90"},
    {"product_id": "P003", "name": "Headphones", "price": "79.00"},
    {"product_id": "P004", "name": "Monitor", "price": "249.00"},
    {"product_id": "P005", "name": "USB-C cable", "price": "12.50"},
)

EVENT_TYPES = ("product_view", "add_to_cart", "order_created")
EVENT_WEIGHTS = (70, 20, 10)

def generate_event() -> dict:
    """Crée un événement indépendant portant sur un produit."""

    product = random.choice(PRODUCTS)

    event_type = random.choices(
        EVENT_TYPES,
        weights = EVENT_WEIGHTS,
        k=1,
    )[0]

    quantity = 1 if event_type == "product_view" else random.randint(1, 3)
    unit_price = Decimal(product["price"])
    total_amount = unit_price * quantity

    return {
        "schema_version": 1,
        "event_id": str(uuid4()),
        "event_time": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "user_id": f"U{random.randint(1, 100):03d}",
        "product_id": product["product_id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": str(unit_price),
        "total_amount": str(total_amount),
        "currency": "EUR",
        "order_id": str(uuid4()) if event_type == "order_created" else None,
    }


def run_generator(count: int, interval: float) -> None:
    """Affiche un événement JSON par ligne."""
    logger.info("Starting generator: count=%s interval=%ss", count, interval)

    try:
        for index in range(count):
            event = generate_event()
            print(json.dumps(event, ensure_ascii=False), flush=True)

            if index < count - 1:
                time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Generator stopped by user")
        return

    logger.info("Generation completed: %s events", count)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    if args.count <= 0:
        parser.error("--count must be greater than 0")
    if args.interval < 0:
        parser.error("--interval must be greater than or equal to 0")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    run_generator(count=args.count, interval=args.interval)


if __name__ == "__main__":
    main()