#import pandas as pd
from sqlalchemy import create_engine
from config import POSTGRES_TABLE_NAME, DATABASE_URL
import logging

logger = logging.getLogger(__name__)

def load(df):
    logger.info("Starting data loading...")

    # Load the processed data from CSV
    #df = pd.read_csv(PROCESSED_DATA_PATH)

    logger.info("DataFrame received successfully.")
    logger.info("Dataset shape: %s", df.shape)

    engine = create_engine(DATABASE_URL)

    df.to_sql(POSTGRES_TABLE_NAME, engine, if_exists='replace', index=False, chunksize=10000)

    logger.info("Data loaded successfully into PostgreSQL table: %s", POSTGRES_TABLE_NAME)

