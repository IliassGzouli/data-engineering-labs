import pandas as pd

from etl.transform import transform


def test_transform_returns_expected_columns():
    df_raw = pd.DataFrame({
        "status": ["for_sale"],
        "price": [200000],
        "bed": [3],
        "bath": [2],
        "acre_lot": [0.25],
        "city": ["Rabat"],
        "state": ["MA"],
        "zip_code": ["10000"],
        "house_size": [1000],
        "prev_sold_date": ["2024-01-01"],
    })

    df_clean = transform(df_raw)

    expected_columns = [
        "status",
        "price",
        "bed",
        "bath",
        "acre_lot",
        "city",
        "state",
        "zip_code",
        "house_size",
        "prev_sold_date",
        "price_per_sqft",
    ]

    assert list(df_clean.columns) == expected_columns

def test_transform_calculates_price_per_sqft():
    df_raw = pd.DataFrame({
        "status": ["for_sale"],
        "price": [200000],
        "bed": [3],
        "bath": [2],
        "acre_lot": [0.25],
        "city": ["Rabat"],
        "state": ["MA"],
        "zip_code": ["10000"],
        "house_size": [1000],
        "prev_sold_date": ["2024-01-01"],
    })

    df_clean = transform(df_raw)

    assert df_clean.iloc[0]["price_per_sqft"] == 200


def test_transform_normalizes_text_columns():
    df_raw = pd.DataFrame({
        "status": ["  FOR_SALE  "],
        "price": [200000],
        "bed": [3],
        "bath": [2],
        "acre_lot": [0.25],
        "city": ["  Rabat  "],
        "state": ["  MA  "],
        "zip_code": ["10000"],
        "house_size": [1000],
        "prev_sold_date": ["2024-01-01"],
    })

    df_clean = transform(df_raw)

    assert df_clean.iloc[0]["status"] == "for_sale"
    assert df_clean.iloc[0]["city"] == "rabat"
    assert df_clean.iloc[0]["state"] == "ma"

def test_transform_removes_rows_with_missing_price():
    df_raw = pd.DataFrame({
        "status": ["for_sale", "for_sale"],
        "price": [200000, None],
        "bed": [3, 2],
        "bath": [2, 1],
        "acre_lot": [0.25, 0.15],
        "city": ["Rabat", "Casablanca"],
        "state": ["MA", "MA"],
        "zip_code": ["10000", "20000"],
        "house_size": [1000, 800],
        "prev_sold_date": ["2024-01-01", "2023-06-15"],
    })

    df_clean = transform(df_raw)

    assert len(df_clean) == 1
    assert df_clean.iloc[0]["price"] == 200000


def test_transform_removes_rows_with_missing_house_size():
    df_raw = pd.DataFrame({
        "status": ["for_sale", "for_sale"],
        "price": [200000, 150000],
        "bed": [3, 2],
        "bath": [2, 1],
        "acre_lot": [0.25, 0.15],
        "city": ["Rabat", "Casablanca"],
        "state": ["MA", "MA"],
        "zip_code": ["10000", "20000"],
        "house_size": [1000, None],
        "prev_sold_date": ["2024-01-01", "2023-06-15"],
    })

    df_clean = transform(df_raw)

    assert len(df_clean) == 1
    assert df_clean.iloc[0]["house_size"] == 1000

def test_transform_removes_rows_with_non_positive_values():
        df_raw = pd.DataFrame({
        "status": ["for_sale", "for_sale", "for_sale"],
        "price": [200000, 0, 150000],
        "bed": [3, 2, 2],
        "bath": [2, 1, 1],
        "acre_lot": [0.25, 0.15, 0.20],
        "city": ["Rabat", "Casablanca", "Marrakech"],
        "state": ["MA", "MA", "MA"],
        "zip_code": ["10000", "20000", "40000"],
        "house_size": [1000, 800, 0],
        "prev_sold_date": [
            "2024-01-01",
            "2023-06-15",
            "2022-10-10",
        ],
    })

        df_clean = transform(df_raw)

        assert len(df_clean) == 1
        assert df_clean.iloc[0]["price"] == 200000
        assert df_clean.iloc[0]["house_size"] == 1000