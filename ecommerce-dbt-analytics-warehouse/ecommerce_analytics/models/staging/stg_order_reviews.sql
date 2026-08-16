select *
from read_parquet('{{ var("silver_data_path") }}/olist_order_reviews_dataset.parquet')