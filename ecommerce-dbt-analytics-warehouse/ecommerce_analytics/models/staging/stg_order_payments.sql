select *
from read_parquet('{{ var("silver_data_path") }}/olist_order_payments_dataset.parquet')