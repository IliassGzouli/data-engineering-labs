from pathlib import Path
import polars as pl

def load_to_silver(
        dataframe: pl.DataFrame,
        source_file_path: str | Path,
        silver_data_dir: str | Path,
)->Path:
    """
    Save a transformed DataFrame as a Parquet file in the Silver layer.
    """

    source_file_path = Path(source_file_path)
    silver_data_dir = Path(silver_data_dir)

    silver_data_dir.mkdir(parents=True, exist_ok=True)

    output_file_path = silver_data_dir / source_file_path.name

    dataframe.write_parquet(output_file_path)
    return output_file_path

