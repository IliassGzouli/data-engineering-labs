with orders as (

    select *
    from {{ ref('stg_orders') }}

),

order_items as (

    select *
    from {{ ref('stg_order_items') }}

),

order_totals as (

    select
        order_id,
        count(*) as item_count,
        sum(price) as products_value,
        sum(freight_value) as freight_value,
        sum(item_total_value) as order_total_value
    from order_items
    group by order_id

)

select
    orders.order_id,
    orders.customer_id,
    orders.order_status,
    orders.order_purchase_timestamp,
    orders.order_approved_at,
    orders.order_delivered_carrier_date,
    orders.order_delivered_customer_date,
    orders.order_estimated_delivery_date,
    orders.has_delivery_date_anomaly,
    order_totals.item_count,
    order_totals.products_value,
    order_totals.freight_value,
    order_totals.order_total_value
from orders
left join order_totals
    on orders.order_id = order_totals.order_id