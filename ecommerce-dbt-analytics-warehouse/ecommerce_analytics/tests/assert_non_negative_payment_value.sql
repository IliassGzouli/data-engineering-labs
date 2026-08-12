select *
from {{ ref('fct_payments') }}
where payment_value < 0