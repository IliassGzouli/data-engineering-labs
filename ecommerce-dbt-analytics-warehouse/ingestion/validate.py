import logging
import polars as pl

logger = logging.getLogger(__name__)

def validate_dataframe(
        dataframe: pl.DataFrame,
        required_columns: set[str],
        unique_columns: list[str] | None = None,
        non_null_columns: list[str] | None = None,
) -> None:

    """
    Validate the structure and basic quality of a Polars DataFrame.

    Args:
        dataframe: DataFrame to validate.
        required_columns: Columns that must exist.
        unique_columns: Columns whose combined values must be unique.
        non_null_columns: Columns that must not contain null values.

    Raises:
        ValueError: If a quality rule is violated.
    """

    logger.info(
        "Starting validation: rows=%s, columns=%d",
        dataframe.height,
        dataframe.width,
    )

    if dataframe.is_empty():
        raise ValueError("DatFrame is empty")

    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        missing_columns = ",".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_columns}") 

    unique_columns = unique_columns or []
    non_null_columns = non_null_columns or []

    validation_columns = set(unique_columns + non_null_columns)
    unknown_columns = validation_columns - set(dataframe.columns)

    if unknown_columns:
        unknown_names = ",".join(sorted(unknown_columns))
        raise ValueError(f"validation columns not found: {unknown_names}")
    
    #vérifier les valeurs nulles
    for column in non_null_columns:
        null_count = dataframe[column].null_count()

        if null_count > 0:
            raise ValueError(
                f"Column '{column}' contains {null_count} null value(s)"
            )

        #vérifier les doublons
    if unique_columns:
        duplicate_count = (
            dataframe
            .group_by(unique_columns)
            .len()
            .filter(pl.col("len") > 1)
            .select(pl.col("len").sum() - pl.len())
            .item()
        )

        if duplicate_count > 0:
            columns = ", ".join(unique_columns)
            raise ValueError(
                f"Found {duplicate_count} duplicate row(s) "
                f"for unique columns: {columns}"
            )

    logger.info("Validation completd succesfully")