{{ config(
    materialized='table'
) }}

with order_items as (

    select *
    from {{ ref('stg_order_items') }}

),

products as (

    select
        product_id,
        product_category_name_english
    from {{ ref('dim_products') }}

)

select
    order_items.*,
    products.product_category_name_english
from order_items
left join products
    on order_items.product_id = products.product_id