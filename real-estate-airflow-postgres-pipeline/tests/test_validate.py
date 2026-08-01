import pandas as pd
import pytest

from etl.validate import validate_data

def test_validate_data_with_valid_dataframe():
    df = pd.DataFrame(
        {
            "status": ["for_sale"],
            "price": [200000],
            "bed": [3],
            "bath": [2],
            "acre_lot": [0.5],
            "city": ["miami"],
            "state": ["florida"],
            "zip_code": [33101],
            "house_size": [1500],
            "prev_sold_date": [None],
            "price_per_sqft": [133.33],
        }
    )

    validate_data(df)  # Should not raise any exceptions


def test_validate_data_with_empty_dataframe():
    df = pd.DataFrame()
    
    with pytest.raises(ValueError):
        validate_data(df)  # Should raise ValueError for empty DataFrame


def test_validate_data_with_negative_values():
    df = pd.DataFrame({
        "price" : [-100000],
        "house_size": [1200],
        "price_per_sqft": [-83.33]
    })

    with pytest.raises(ValueError):
        validate_data(df)


def test_validate_data_with_missing_required_columns():
    df = pd.DataFrame(
        {
            "status": ["for_sale"],
            "price": [200000],
            # city est absente
            "state": ["florida"],
            "zip_code": [33101],
            "house_size": [1500],
            "price_per_sqft": [133.33],
        }
    )

    with pytest.raises(ValueError, match="Missing required columns.*city"):
        validate_data(df)

def test_validate_data_with_null_required_values():
    df = pd.DataFrame(
        {
            "status": ["for_sale"],
            "price": [200000],
            "city": [None],
            "state": ["florida"],
            "zip_code": [33101],
            "house_size": [1500],
            "price_per_sqft": [133.33],
        }
    )

    with pytest.raises(ValueError):
        validate_data(df)