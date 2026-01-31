with s as (
    select * from {{ ref('stg_contributions') }}
)
select
    s.declaration_id,
    md5(s.taxpayer_id || ':' || s.country) as taxpayer_key,
    s.event_date,
    s.amount,
    s.currency,
    s.contribution_type,
    s.status,
    s.country,
    s.ingestion_ts,
    s.source_file
from s
