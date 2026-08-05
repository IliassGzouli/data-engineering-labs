ORDERS_SCHEMA ={
    "required_columns":{
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    },
    "unique_columns": ["order_id"],
    "non_null_columns": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
    ], 
}

CUSTOMERS_SCHEMA = {
    "required_columns": {
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    },
    "unique_columns": ["customer_id"],
    "non_null_columns": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
}

ORDER_ITEMS_SCHEMA = {
    "required_columns": {
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    },
    "unique_columns": ["order_id", "order_item_id"],
    "non_null_columns": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
}

ORDER_PAYMENTS_SCHEMA = {
    "required_columns": {
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    },
    "unique_columns": ["order_id", "payment_sequential"],
    "non_null_columns": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
}

ORDER_REVIEWS_SCHEMA = {
    "required_columns": {
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    },
    "unique_columns": ["review_id", "order_id"],
    "non_null_columns": [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp",
    ],
}

PRODUCTS_SCHEMA = {
    "required_columns": {
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    },
    "unique_columns": ["product_id"],
    "non_null_columns": [
        "product_id",
    ],
}

SELLERS_SCHEMA = {
    "required_columns": {
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    },
    "unique_columns": ["seller_id"],
    "non_null_columns": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
}

CATEGORY_TRANSLATION_SCHEMA = {
    "required_columns": {
        "product_category_name",
        "product_category_name_english",
    },
    "unique_columns": ["product_category_name"],
    "non_null_columns": [
        "product_category_name",
        "product_category_name_english",
    ],
}

GEOLOCATION_SCHEMA = {
    "required_columns": {
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    },
    "unique_columns": None,
    "non_null_columns": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ],
}

DATASET_SCHEMAS = {
    "olist_orders_dataset.csv": ORDERS_SCHEMA,
    "olist_customers_dataset.csv": CUSTOMERS_SCHEMA,
    "olist_order_items_dataset.csv": ORDER_ITEMS_SCHEMA,
    "olist_order_payments_dataset.csv": ORDER_PAYMENTS_SCHEMA,
    "olist_order_reviews_dataset.csv": ORDER_REVIEWS_SCHEMA,
    "olist_products_dataset.csv": PRODUCTS_SCHEMA,
    "olist_sellers_dataset.csv": SELLERS_SCHEMA,
    "product_category_name_translation.csv": CATEGORY_TRANSLATION_SCHEMA,
    "olist_geolocation_dataset.csv": GEOLOCATION_SCHEMA,
}

