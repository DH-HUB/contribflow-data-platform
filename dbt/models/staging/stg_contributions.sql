with src as (
    select
        declaration_id,
        taxpayer_id,
        event_date::date as event_date,
        amount::numeric(18,2) as amount,
        currency,
        contribution_type,
        status,
        country,
        ingestion_ts,
        source_file
    from raw.contributions_raw
)
select * from src
