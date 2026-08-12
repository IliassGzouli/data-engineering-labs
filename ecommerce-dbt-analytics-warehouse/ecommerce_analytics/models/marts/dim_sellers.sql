{{ config(
    materialized='table'
) }}

with sellers as (

    select *
    from {{ ref('stg_sellers') }}

)

select *
from sellers