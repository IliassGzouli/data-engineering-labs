# E-commerce Analytics Warehouse

End-to-end analytics engineering project built from the **Brazilian E-Commerce Public Dataset by Olist**. It turns nine source CSV files into validated Parquet datasets, applies dataset-specific cleaning and enrichment with Polars, and builds a dimensional analytics layer in DuckDB with dbt Core.

The implemented data flow is:

```text
Raw CSV -> Bronze Parquet -> Silver Parquet -> DuckDB/dbt staging -> Gold marts -> Metabase
```

This project is maintained inside the [`data-engineering-labs`](https://github.com/IliassGzouli/data-engineering-labs) monorepo.

## Architecture

```text
Olist CSV files
      |
      v
Python + Polars
extract -> schema-based validation -> Parquet write
      |
      v
Bronze layer
validated, source-aligned Parquet files
      |
      v
Silver layer
standardization, quality flags, deduplication, derived fields
      |
      v
DuckDB + dbt
9 staging views -> 8 Gold tables
      |
      v
Metabase
executive analytics dashboard
```

| Layer | Location | Purpose |
| --- | --- | --- |
| Raw | `data/raw/` | Original Olist CSV files |
| Bronze | `data/bronze/` | Validated, source-aligned data stored as Parquet |
| Silver | `data/silver/` | Cleaned, standardized, flagged, or enriched Parquet datasets |
| Staging | `ecommerce_analytics/models/staging/` | dbt views over the Silver files |
| Gold | `ecommerce_analytics/models/marts/` | DuckDB tables designed for analytical use |
| BI | Metabase | Dashboard and interactive consumption layer over DuckDB |

The file-based stages are reproducible: rerunning a load writes the same dataset-specific Parquet path. dbt then rebuilds views and tables from those Silver inputs. The pipeline is batch-oriented and runs locally or in CI; it is not an orchestrated or incremental production pipeline.

## Technology Stack

- **Python 3.12** for pipeline code and automation
- **Polars** for CSV extraction, validation, and Silver transformations
- **Parquet** for Bronze and Silver storage
- **pytest** for Python unit and pipeline-component tests
- **DuckDB** as the local analytical database
- **dbt Core** and **dbt-duckdb** for SQL modeling, tests, documentation, and lineage
- **Docker** for a reproducible dbt build image
- **Git, GitHub, and GitHub Actions** for version control and continuous integration
- **Metabase** with the DuckDB driver for business intelligence

Dependency versions are pinned in `requirements.txt`; the current runtime includes Polars 1.43.2, pytest 9.0.1, DuckDB 1.5.5, dbt Core 1.12.0, and dbt-duckdb 1.11.0.

## Source Data and Bronze Ingestion

The ingestion package is split by responsibility:

- `ingestion/extract.py` checks that an input exists, is a file, has a `.csv` extension, contains rows, and can be parsed by Polars. Date parsing is attempted during extraction.
- `ingestion/schemas.py` defines the required, non-null, and unique-key columns for each supported file.
- `ingestion/validate.py` selects the schema from the source filename and applies generic structural and quality checks.
- `ingestion/load.py` creates the destination directory and writes the validated DataFrame as Parquet.
- `ingestion/pipeline.py` discovers all CSV files in a Raw directory and runs extract, validate, and load for each file.

Nine Olist datasets are supported:

1. customers
2. orders
3. order items
4. order payments
5. order reviews
6. products
7. sellers
8. geolocation
9. product category translation

The validation rules currently enforce:

- a non-empty DataFrame;
- all schema-required columns;
- no nulls in dataset-specific critical columns;
- uniqueness for configured single or composite keys;
- valid references to columns named by validation rules;
- a known schema for every processed filename.

Validation is fail-fast at dataset level. Invalid rows are not quarantined individually, and quality reports or rejected-record outputs are not implemented.

## Silver Transformations

All nine Bronze datasets have a corresponding callable pipeline in `transformation/pipeline.py`. Each function reads one Bronze Parquet file, applies its transformation, and writes a same-named Parquet file to the Silver directory.

| Dataset | Implemented transformation |
| --- | --- |
| Customers | Casts `customer_zip_code_prefix` to a string and left-pads it to five characters |
| Orders | Adds `has_delivery_date_anomaly` for delivered orders missing approval, carrier-delivery, or customer-delivery timestamps |
| Order items | Adds `item_total_value = price + freight_value` |
| Order payments | Flags non-positive values with `has_invalid_payment_value` and `not_defined` payment types with `has_undefined_payment_type` |
| Products | Flags missing descriptive metadata and missing/non-positive physical attributes |
| Sellers | Casts and left-pads `seller_zip_code_prefix` to five characters |
| Order reviews | Adds `has_duplicate_review_id` for repeated review identifiers |
| Category translation | Passes the already-clean translation mapping through unchanged |
| Geolocation | Standardizes ZIP prefixes and removes exact duplicate rows |

The transformation package exposes one function per dataset; it does not currently provide a single command-line entry point that runs all Silver pipelines together.

## DuckDB and dbt Gold Layer

The dbt project is located in `ecommerce_analytics/`. Its default profile writes to `dev.duckdb`, staging models are materialized as views, and marts are materialized as tables.

### Staging models

Each staging view reads its corresponding Silver Parquet file directly:

- `stg_customers`
- `stg_geolocation`
- `stg_order_items`
- `stg_order_payments`
- `stg_order_reviews`
- `stg_orders`
- `stg_product_category_translation`
- `stg_products`
- `stg_sellers`

### Dimensions and facts

| Model | Grain and role |
| --- | --- |
| `dim_customers` | One row per `customer_id`; customer identity and location attributes |
| `dim_products` | One row per `product_id`; product metadata, quality flags, and English category name from the translation mapping |
| `dim_sellers` | One row per `seller_id`; seller location attributes |
| `dim_geolocation` | One row per ZIP-code prefix; average coordinates plus the most frequent city and state |
| `fct_orders` | One row per `order_id`; status, lifecycle timestamps, delivery anomaly flag, item count, product value, freight, and total value |
| `fct_order_items` | One row per `(order_id, order_item_id)`; product, seller, shipping, price, freight, and item total. It is enriched from `dim_products` with `product_category_name_english` |
| `fct_payments` | One row per `(order_id, payment_sequential)`; payment method, installments, value, and Silver quality flags |
| `fct_reviews` | One row per source review record; order review content, score, timestamps, and duplicate-review flag |

`dim_geolocation` is available as a shared geographic lookup for ZIP-level analysis. The current marts do not physically join it into the customer or seller dimensions; BI queries can join it using the standardized ZIP prefix.

## Testing and Data Quality

### Python tests

The pytest suite covers CSV extraction errors, empty inputs, schema selection, required columns, null and duplicate detection, Bronze/Silver Parquet writes, each Silver transformation, and each dataset-specific Silver pipeline.

Current verified result:

```text
42 passed
```

### dbt tests

The dbt project contains 27 tests across 17 models:

- 11 `not_null` tests;
- 5 `unique` tests;
- 6 `relationships` tests;
- 1 `accepted_values` test for order status;
- 4 singular business tests covering non-negative payments, review-score range, unique order items, and unique payments.

The checked dbt run artifact records a successful `dbt build` of 44 nodes: 17 models and 27 tests, with no failures. These counts describe the current project and stored artifact; rerun `dbt build` after changing code or data.

## Business Intelligence

Metabase is used as the BI layer on top of the DuckDB warehouse. The locally configured **Ecommerce Executive Dashboard** contains:

- Total Orders
- Total Revenue
- Average Order Value
- Late Delivery Rate
- Revenue by Month
- Top 10 Product Categories by Revenue
- Orders by Status
- Top 10 Customer States by Revenue
- Customer Revenue Map
- Top 10 States by Average Delivery Time
- Review Score Distribution

The local `metabase/` workspace includes a DuckDB Metabase driver, but it is intentionally ignored by Git. The `dashboards/` directory currently contains no exported dashboard definition or screenshot, so dashboard provisioning is manual and the BI layer is not reproducible from version-controlled files alone.

## Docker

The image uses `python:3.12-slim`, installs Git and the pinned Python/dbt dependencies, copies the project, sets `DBT_PROFILES_DIR`, and starts in `/app/ecommerce_analytics`.

Build the image from this directory:

```bash
docker build -t ecommerce-dbt-analytics .
```

Run the container:

```bash
docker run --rm ecommerce-dbt-analytics
```

The container's default command is `dbt build`. It does not run Python ingestion, generate Silver data, start Metabase, or deploy an application. Because `.dockerignore` excludes DuckDB files but not `data/`, the build uses the Silver Parquet files present in the Docker build context.

## Continuous Integration

The monorepo workflow at `../.github/workflows/ci.yml` is triggered on pushes and pull requests that change this project or the workflow itself. It runs on Ubuntu with Python 3.12 and performs the following steps:

1. checks out the repository;
2. installs the pinned requirements with pip caching;
3. runs the 42 pytest tests;
4. generates all nine Bronze datasets from small version-controlled CI CSV fixtures;
5. generates all nine Silver datasets from those Bronze fixtures;
6. runs `dbt build` against the CI Silver directory;
7. builds the Docker image.

The workflow validates the project but does not publish an image, deploy infrastructure, or deploy the dashboard.

## Repository Structure

```text
data-engineering-labs/
├── .github/workflows/ci.yml              # Monorepo CI workflow
└── ecommerce-dbt-analytics-warehouse/
    ├── data/
    │   ├── raw/                          # 9 source CSV files (local/ignored)
    │   ├── bronze/                       # Validated Parquet (generated/ignored)
    │   └── silver/                       # Transformed Parquet (generated/ignored)
    ├── ingestion/                        # Extract, schemas, validation, Bronze load
    ├── transformation/                   # Silver rules, load, dataset pipelines
    ├── ecommerce_analytics/
    │   ├── models/
    │   │   ├── staging/                  # 9 Parquet-backed views
    │   │   └── marts/                    # 4 dimensions and 4 facts
    │   ├── tests/                        # 4 singular dbt tests
    │   ├── dbt_project.yml
    │   └── profiles.yml
    ├── tests/
    │   ├── fixtures/ci_raw/              # Small committed CI source datasets
    │   └── test_*.py                     # pytest suite
    ├── dashboards/                       # Reserved for versioned BI artifacts
    ├── metabase/                         # Local ignored Metabase driver/workspace
    ├── Dockerfile
    ├── .dockerignore
    ├── requirements.txt
    └── README.md
```

Generated databases, dbt targets/logs, caches, and local Metabase files are omitted from this simplified tree.

## Installation and Usage

### 1. Clone and install

```bash
git clone https://github.com/IliassGzouli/data-engineering-labs.git
cd data-engineering-labs/ecommerce-dbt-analytics-warehouse

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

The full Olist CSV files are not version-controlled. Place the nine files, with the exact filenames defined in `ingestion/schemas.py`, in `data/raw/` before running the local data pipeline.

### 2. Run tests

```bash
pytest -q
```

### 3. Build Bronze

```bash
python -m ingestion.pipeline
```

This is the only Python module with a direct CLI entry point. It processes every CSV found in `data/raw/`.

### 4. Build Silver

There is no all-datasets Silver CLI. The following Python snippet calls the nine implemented pipelines:

```bash
python - <<'PY'
from transformation import pipeline

bronze = "data/bronze"
silver = "data/silver"

jobs = [
    (pipeline.run_customers_silver_pipeline, "olist_customers_dataset.parquet"),
    (pipeline.run_orders_silver_pipeline, "olist_orders_dataset.parquet"),
    (pipeline.run_order_items_silver_pipeline, "olist_order_items_dataset.parquet"),
    (pipeline.run_order_payments_silver_pipeline, "olist_order_payments_dataset.parquet"),
    (pipeline.run_products_silver_pipeline, "olist_products_dataset.parquet"),
    (pipeline.run_sellers_silver_pipeline, "olist_sellers_dataset.parquet"),
    (pipeline.run_order_reviews_silver_pipeline, "olist_order_reviews_dataset.parquet"),
    (pipeline.run_product_category_translation_silver_pipeline, "product_category_name_translation.parquet"),
    (pipeline.run_geolocation_silver_pipeline, "olist_geolocation_dataset.parquet"),
]

for run, filename in jobs:
    run(f"{bronze}/{filename}", silver)
PY
```

### 5. Build and test the warehouse

```bash
cd ecommerce_analytics
dbt debug --profiles-dir .
dbt build --profiles-dir .
```

To generate and serve dbt documentation:

```bash
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Key Engineering Concepts Demonstrated

- layered Raw/Bronze/Silver/Gold/BI architecture;
- modular extract, validate, transform, and load components;
- centralized dataset schemas and fail-fast quality gates;
- columnar Parquet storage and direct analytical querying;
- dimensional and fact modeling with explicit grains;
- dbt lineage, documentation, generic tests, and business assertions;
- deterministic dataset paths and repeatable local/CI builds;
- containerized dbt execution;
- CI validation using compact, version-controlled fixtures;
- BI consumption through DuckDB and Metabase.

## Project Status

The local batch pipeline currently supports all nine source datasets from Raw through Silver. The dbt warehouse contains nine staging views and eight Gold marts, and the automated test suites cover both Python processing and analytical-model constraints. Docker and GitHub Actions are implemented. Metabase is used locally for the executive dashboard but is not provisioned from version control.

## Current Limitations

- Full source data and generated Raw/Bronze/Silver assets are local and ignored by Git; only compact Raw CI fixtures are committed.
- Ingestion stops on the first invalid dataset; row-level rejection and persisted quality reports are not available.
- Silver pipelines must be called individually and do not yet have a shared CLI/orchestrator.
- Processing is full-refresh and file-based; there is no incremental ingestion, scheduler, cloud storage, or production warehouse.
- The local dbt profile contains development and production target names, but both are local DuckDB files rather than deployed environments.
- Metabase configuration and the dashboard are not exported or reproducibly deployed from the repository.
- Python tests focus on ingestion and Silver components; CI provides the end-to-end integration path through dbt.

## Future Improvements / Roadmap

- Add an orchestrated all-datasets pipeline with structured run metadata and logging.
- Persist validation reports and quarantine invalid records instead of failing only at dataset level.
- Add incremental processing and source freshness checks.
- Version or provision the Metabase connection, dashboard, and visual assets.
- Add broader dbt column documentation and tests for remaining business measures and accepted domains.
- Publish the Docker image and add deployment only when a target runtime is defined.
- Evaluate object storage and a production analytical warehouse while retaining DuckDB for local development.

## Dataset

The project uses the **Brazilian E-Commerce Public Dataset by Olist**, a public dataset describing orders placed across Brazilian marketplaces. Its files cover customers, orders, line items, payments, reviews, products, sellers, geolocation, and Portuguese-to-English product category translations.

Download the dataset from its original distribution page and review the source terms before using or redistributing it. The repository intentionally excludes the full raw dataset from Git.
