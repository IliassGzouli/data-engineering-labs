{{ config(
    materialized='table'
) }}

with geolocation as (

    select *
    from {{ ref('stg_geolocation') }}

),

coordinates_by_zip as (

    select
        geolocation_zip_code_prefix,
        avg(geolocation_lat) as geolocation_lat,
        avg(geolocation_lng) as geolocation_lng
    from geolocation
    group by geolocation_zip_code_prefix

),

city_counts as (

    select
        geolocation_zip_code_prefix,
        geolocation_city,
        count(*) as city_count
    from geolocation
    group by
        geolocation_zip_code_prefix,
        geolocation_city

),

city_by_zip as (

    select
        geolocation_zip_code_prefix,
        geolocation_city
    from (
        select
            geolocation_zip_code_prefix,
            geolocation_city,
            row_number() over (
                partition by geolocation_zip_code_prefix
                order by city_count desc, geolocation_city
            ) as row_num
        from city_counts
    )
    where row_num = 1

),

state_counts as (

    select
        geolocation_zip_code_prefix,
        geolocation_state,
        count(*) as state_count
    from geolocation
    group by
        geolocation_zip_code_prefix,
        geolocation_state

),

state_by_zip as (

    select
        geolocation_zip_code_prefix,
        geolocation_state
    from (
        select
            geolocation_zip_code_prefix,
            geolocation_state,
            row_number() over (
                partition by geolocation_zip_code_prefix
                order by state_count desc, geolocation_state
            ) as row_num
        from state_counts
    )
    where row_num = 1

)

select
    coordinates_by_zip.geolocation_zip_code_prefix,
    coordinates_by_zip.geolocation_lat,
    coordinates_by_zip.geolocation_lng,
    city_by_zip.geolocation_city,
    state_by_zip.geolocation_state
from coordinates_by_zip
left join city_by_zip
    on coordinates_by_zip.geolocation_zip_code_prefix = city_by_zip.geolocation_zip_code_prefix
left join state_by_zip
    on coordinates_by_zip.geolocation_zip_code_prefix = state_by_zip.geolocation_zip_code_prefix