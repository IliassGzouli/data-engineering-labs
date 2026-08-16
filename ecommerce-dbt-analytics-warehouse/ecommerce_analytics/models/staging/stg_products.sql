select *
from read_parquet('{{ var("silver_data_path") }}/olist_products_dataset.parquet')