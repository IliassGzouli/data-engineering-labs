{{ config(
    materialized='table'
)}}

with payments as (
    
    select *
    from {{ ref('stg_order_payments')}}
)

select *
from payments