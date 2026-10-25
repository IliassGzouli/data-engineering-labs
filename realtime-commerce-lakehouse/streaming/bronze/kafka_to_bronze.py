"""Lecture des messages Kafka vers une table Bronze Delta Lake."""

import logging
from pathlib import Path

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_PATH = PROJECT_ROOT / "data/bronze/commerce_events"
CHECKPOINT_PATH = PROJECT_ROOT / "data/checkpoints/bronze/commerce_events"

KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1"


def create_spark_session() -> SparkSession:
    builder = (
        SparkSession.builder
        .master("local[2]")
        .appName("commerce-kafka-to-bronze")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "2")
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )

    return configure_spark_with_delta_pip(
        builder,
        extra_packages=[KAFKA_PACKAGE],
    ).getOrCreate()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    query = None

    try:
        kafka_events = (
            spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "commerce.events")
            .option("startingOffsets", "earliest")
            .option("failOnDataLoss", "true")
            .option("maxOffsetsPerTrigger", 1000)
            .load()
        )

        bronze_events = kafka_events.select(
            col("key").cast("string").alias("message_key"),
            col("value").cast("string").alias("raw_event"),
            col("topic"),
            col("partition"),
            col("offset"),
            col("timestamp").alias("kafka_timestamp"),
            current_timestamp().alias("ingested_at"),
        )

        query = (
            bronze_events.writeStream
            .format("delta")
            .outputMode("append")
            .option("checkpointLocation", str(CHECKPOINT_PATH))
            .trigger(processingTime="5 seconds")
            .queryName("commerce_kafka_to_bronze")
            .start(str(BRONZE_PATH))
        )

        logger.info("Stream started: Kafka -> %s", BRONZE_PATH)
        logger.info("Checkpoint: %s", CHECKPOINT_PATH)

        while query.isActive:
            query.awaitTermination(timeout=1)

    except KeyboardInterrupt:
        logger.info("Stopping stream")

    finally:
        if query is not None:
            query.stop()
        spark.stop()


if __name__ == "__main__":
    main()