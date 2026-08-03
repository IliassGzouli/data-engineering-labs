# Real Estate Airflow PostgreSQL Pipeline

End-to-end data engineering project that extracts, transforms, validates, and loads a large real estate dataset into PostgreSQL. The pipeline is containerized with Docker, orchestrated with Apache Airflow, and tested with Pytest.

## Project overview

This project was developed to practice the main stages of a modern data engineering workflow:

- extracting data from a CSV file;
- cleaning and transforming data with Pandas;
- validating data quality;
- loading processed data into PostgreSQL;
- orchestrating the ETL pipeline with Apache Airflow;
- containerizing services with Docker;
- testing pipeline components with Pytest and mocks.

## ETL architecture

```text
Raw CSV dataset
        |
        v
    Extract
        |
        v
   Transform
        |
        v
    Validate
        |
        v
Load into PostgreSQL
        |
        v
Orchestrate with Airflow
```

## Pipeline stages

### 1. Extract

The extraction step reads the raw real estate CSV dataset with Pandas.

The function supports an optional `nrows` parameter, which can be used to process a smaller sample during development.

Raw dataset size:

```text
2,226,382 rows
12 columns
```

### 2. Transform

The transformation step:

- selects the required columns;
- removes rows with missing required values;
- removes rows with non-positive prices;
- removes rows with non-positive house sizes;
- normalizes text columns;
- calculates the `price_per_sqft` column;
- prepares the data for validation and loading.

The final columns are:

```text
status
price
bed
bath
acre_lot
city
state
zip_code
house_size
prev_sold_date
price_per_sqft
```

Transformed dataset size:

```text
1,656,256 rows
11 columns
```

### 3. Validate

The validation step verifies that:

- the DataFrame is not empty;
- all required columns exist;
- required columns do not contain null values;
- prices are positive;
- house sizes are positive;
- calculated price-per-square-foot values are positive.

If a validation rule fails, the pipeline raises an exception and stops before loading invalid data into PostgreSQL.

### 4. Load

The loading step writes the validated DataFrame into PostgreSQL using Pandas and SQLAlchemy.

The destination table is:

```text
real_estate_listings
```

The data is loaded with:

```python
if_exists="replace"
index=False
chunksize=10000
```

The SQLAlchemy engine is disposed after the loading operation, whether the operation succeeds or fails.

### 5. Orchestration

Apache Airflow orchestrates the complete ETL pipeline through the following DAG:

```text
real_estate_etl_dag
```

The main Airflow task is:

```text
run_extract_transform_load
```

The task uses a `PythonOperator` to execute the pipeline.

The final manual Airflow execution completed successfully.

## Technologies

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Psycopg2
- Apache Airflow
- Docker
- Docker Compose
- Pytest
- Git
- GitHub

## Project structure

```text
real-estate-airflow-postgres-pipeline/
├── dags/
│   └── real_estate_etl_dag.py
├── data/
│   ├── raw/
│   └── processed/
├── etl/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   ├── pipeline.py
│   └── quality_checks.py
├── logs/
├── sql/
│   └── create_tables.sql
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_validate.py
│   ├── test_load.py
│   └── test_pipeline.py
├── .gitignore
├── config.py
├── docker-compose.yml
├── main.py
├── README.md
└── requirements.txt
```

## Requirements

Before running the project, make sure the following tools are installed:

- Python 3.12 or later
- Docker
- Docker Compose
- Git

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

The project uses configuration values defined in `config.py`.

The local PostgreSQL connection uses:

```text
Host: localhost
Port: 5434
Database: real_estate_db
User: postgres
```

The host port `5434` is mapped to PostgreSQL port `5432` inside the Docker container.

Example Docker port mapping:

```yaml
ports:
  - "5434:5432"
```

## Run the project

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/data-engineering-labs.git
```

Enter the project directory:

```bash
cd data-engineering-labs/real-estate-airflow-postgres-pipeline
```

### 2. Start Docker services

```bash
docker compose up -d
```

Check the service status:

```bash
docker compose ps
```

### 3. Run the ETL pipeline locally

```bash
PYTHONPATH=. python main.py
```

Expected final logs:

```text
Data validation completed successfully.
Data loaded successfully into PostgreSQL table: real_estate_listings
Database engine disposed.
ETL pipeline completed successfully.
```

## Run the tests

Run the complete test suite:

```bash
PYTHONPATH=. pytest -v
```

Current result:

```text
17 tests passed
```

The test suite covers:

- CSV extraction;
- extraction failure handling;
- expected transformation columns;
- `price_per_sqft` calculation;
- text normalization;
- removal of missing required values;
- removal of non-positive values;
- validation of valid and invalid DataFrames;
- PostgreSQL loading with mocks;
- database write failure handling;
- SQLAlchemy engine disposal;
- complete pipeline execution with mocks;
- prevention of loading when validation fails.

## Unit testing strategy

The tests follow the AAA structure:

```text
Arrange
Act
Assert
```

- `Arrange`: prepare data, mocks, and expected values;
- `Act`: execute the function being tested;
- `Assert`: verify the result or expected behavior.

Mocks are used for external operations such as:

- reading CSV files;
- creating a SQLAlchemy engine;
- writing data into PostgreSQL.

This keeps unit tests fast and prevents them from depending on external services.

## PostgreSQL verification

Connect to PostgreSQL:

```bash
docker exec -it real_estate_postgres \
  psql -U postgres -d real_estate_db
```

Verify the number of loaded rows:

```sql
SELECT COUNT(*)
FROM real_estate_listings;
```

Expected result:

```text
1656256
```

Display sample rows:

```sql
SELECT *
FROM real_estate_listings
LIMIT 5;
```

Run a final data-quality check:

```sql
SELECT COUNT(*)
FROM real_estate_listings
WHERE price <= 0
   OR house_size <= 0
   OR price_per_sqft <= 0
   OR state IS NULL;
```

Expected result:

```text
0
```

Exit PostgreSQL:

```sql
\q
```

## Airflow

After starting the Docker services, open the Airflow web interface and locate:

```text
real_estate_etl_dag
```

Enable the DAG and trigger it manually.

The task:

```text
run_extract_transform_load
```

should finish with the following status:

```text
success
```

The successful Airflow execution confirms that the complete ETL pipeline can be orchestrated automatically.

## Final results

```text
Raw rows:                 2,226,382
Clean rows:               1,656,256
Final columns:            11
Invalid required rows:    0
Pytest tests:             17 passed
PostgreSQL loading:       successful
Airflow execution:        successful
```

## Key learning outcomes

This project demonstrates practical experience with:

- ETL pipeline design;
- large CSV dataset processing;
- Pandas transformations;
- data-quality validation;
- PostgreSQL integration;
- SQLAlchemy database connections;
- Dockerized data infrastructure;
- Apache Airflow orchestration;
- unit testing and mocking;
- logging and error handling;
- Git and GitHub project organization.

## Author

**Iliass Gzouli**  

- Email: [iliassgzouli@gmail.com](mailto:ton-email@example.com)
- LinkedIn: [linkedin.com/in/Iliass Gzouli](https://www.linkedin.com/in/iliass-gzouli-b0615a324)
- GitHub: [github.com/Iliass Gzouli](https://github.com/IliassGzouli)