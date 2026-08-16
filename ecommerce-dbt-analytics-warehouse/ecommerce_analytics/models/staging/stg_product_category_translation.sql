select *
from read_parquet('{{ var("silver_data_path") }}/product_category_name_translation.parquet')