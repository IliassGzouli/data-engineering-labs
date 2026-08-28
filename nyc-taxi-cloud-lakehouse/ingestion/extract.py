import logging
from pathlib import Path

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
RAW_DATA_DIR = Path("data/raw")
CHUNK_SIZE = 1024*1024
REQUEST_TIMEOUT = 60


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

def build_filename(year: int, month: int) -> str:
    if year < 2009:
        raise ValueError(
            "year must be greater than or equal to 2009"
        )
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")
    
    return f"yellow_tripdata_{year}-{month:02d}.parquet"

def download_yellow_taxi_data(
        year: int, 
        month: int, 
        raw_data_dir : Path = RAW_DATA_DIR
) -> Path:

    filename = build_filename(year, month)

    url = f"{BASE_URL}/{filename}"

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / filename

    if output_path.exists():
        logger.info("File already exists, skipping download: %s", output_path)
        return output_path
    #Log du début
    logger.info(f"Dowloading %s from %s", filename, url)

    #Faire la requête HTTP
    try:
        with requests.get(
            url, stream=True, timeout=REQUEST_TIMEOUT,
        ) as response:
            #Vérifier le statut HTTP
            response.raise_for_status()

            #Écriture par chunks
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)

    #Gestion des erreurs réseau
    except RequestException as exc:
        output_path.unlink(missing_ok=True)

        logger.error("Download failed for %s: %s", filename, exc)

        raise 
    except OSError as exc:
        output_path.unlink(missing_ok=True)
        
        logger.error("Failed to write file %s: %s", output_path, exc)

        raise

    logger.info("Download completed succesfully: %s", output_path)

    return output_path


if __name__ == "__main__":
    configure_logging()
    download_yellow_taxi_data(
        year=2026,
        month=1
    )