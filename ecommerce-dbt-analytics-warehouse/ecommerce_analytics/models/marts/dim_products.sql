{{ config(
    materialized='table'
) }}

with products as (

    select *
    from {{ ref('stg_products') }}

),

category_translation as (

    select *
    from {{ ref('stg_product_category_translation') }}

)

select
    products.*,
    category_translation.product_category_name_english
from products
left join category_translation
    on products.product_category_name = category_translation.product_category_name