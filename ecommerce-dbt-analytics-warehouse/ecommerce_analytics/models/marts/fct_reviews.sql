{{ config(
    materialized='table'
) }}

with reviews as (

    select *
    from {{ ref('stg_order_reviews') }}

)

select *
from reviews