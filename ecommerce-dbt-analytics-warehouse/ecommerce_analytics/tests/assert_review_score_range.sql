select *
from {{ ref('fct_reviews') }}
where review_score < 1
   or review_score > 5