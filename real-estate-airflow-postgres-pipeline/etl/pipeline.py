from etl.extract import extract
from etl.transform import transform
from etl.load import load
from config import RAW_DATA_PATH
from etl.validate import validate_data
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline():
    try:
        logger.info("Starting ETL pipeline...")
        
        df_raw = extract(RAW_DATA_PATH)
        df_clean = transform(df_raw)
        validate_data(df_clean)
        load(df_clean)
        
        logger.info("ETL pipeline completed successfully.")

    except Exception as e:
        logger.exception("ETL pipeline failed.")
        logger.exception(f"Error: {e}")
        raise
    
if __name__ == "__main__":
    run_pipeline()