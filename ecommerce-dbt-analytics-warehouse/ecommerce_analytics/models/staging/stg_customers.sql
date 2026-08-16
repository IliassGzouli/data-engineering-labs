select *
from read_parquet('{{ var("silver_data_path")}}/olist_customers_dataset.parquet')