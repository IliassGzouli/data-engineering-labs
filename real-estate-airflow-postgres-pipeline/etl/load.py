from sqlalchemy import create_engine

from config import DATABASE_URL, POSTGRES_TABLE_NAME

import logging


logger = logging.getLogger(__name__)


def load(df):
    logger.info("Starting data loading...")
    logger.info("DataFrame received successfully.")
    logger.info("Dataset shape: %s", df.shape)

    engine = create_engine(DATABASE_URL)

    try:
        df.to_sql(
            POSTGRES_TABLE_NAME,
            engine,
            if_exists="replace",
            index=False,
            chunksize=10000,
        )

        logger.info(
            "Data loaded successfully into PostgreSQL table: %s",
            POSTGRES_TABLE_NAME,
        )

    except Exception:
        logger.exception("Failed to load data into PostgreSQL.")
        raise

    finally:
        engine.dispose()
        logger.info("Database engine disposed.")