"""Envoi d'événements e-commerce vers Kafka."""

import argparse
import json
import logging
import time

from confluent_kafka import Producer

from producer.generator import generate_event


logger = logging.getLogger(__name__)


def run_producer(count: int, interval: float) -> None:
    producer = Producer({
        "bootstrap.servers": "localhost:9092",
        "client.id": "commerce-python-producer",
        "enable.idempotence": True,
        "delivery.timeout.ms": 30000,
        "broker.address.family":"v4",
    })

    delivered = 0
    failed = 0
    queued = 0

    def on_delivery(err, msg) -> None:
        nonlocal delivered, failed

        if err is not None:
            failed += 1
            logger.error("Delivery failed: %s", err)
        else:
            delivered += 1
            logger.info(
                "Delivered: topic=%s partition=%s offset=%s",
                msg.topic(),
                msg.partition(),
                msg.offset(),
            )

    logger.info("Starting producer: count=%s interval=%ss", count, interval)

    try:
        for index in range(count):
            event = generate_event()

            producer.produce(
                topic="commerce.events",
                key=event["user_id"].encode("utf-8"),
                value=json.dumps(event, ensure_ascii=False).encode("utf-8"),
                on_delivery=on_delivery,
            )
            queued += 1

            # Traite les confirmations pendant l'attente.
            producer.poll(0)

            if index < count -1:
                time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Interrupted: waiting for pending messages")

    finally:
        remaining = producer.flush(timeout=35)
        logger.info(
            "Summary: queued=%s delivered=%s failed=%s pending=%s",
            queued,
            delivered,
            failed,
            remaining,
        )

    if failed or remaining:
        raise RuntimeError("Some messages were not confirmed as delivered")


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

    run_producer(count=args.count, interval=args.interval)


if __name__ == "__main__":
    main()