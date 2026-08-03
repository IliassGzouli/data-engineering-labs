import os


SAMPLE_SIZE = 50000
RAW_DATA_PATH = "./data/raw/usa_real_estate.csv"
PROCESSED_DATA_PATH = "./data/processed/usa_real_estate_clean.csv"
POSTGRES_TABLE_NAME = "real_estate_listings"

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5434")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "real_estate_db")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/{POSTGRES_DB}"
)

