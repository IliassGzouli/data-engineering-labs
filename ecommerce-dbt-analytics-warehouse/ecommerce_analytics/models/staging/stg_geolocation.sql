select *
from read_parquet('{{ var("silver_data_path")}}/olist_geolocation_dataset.parquet')