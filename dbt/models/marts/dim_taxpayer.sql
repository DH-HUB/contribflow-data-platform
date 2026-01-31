-- Dimension contribuable pseudo-anonymisée (hash)
with base as (
    select distinct
        taxpayer_id,
        country
    from {{ ref('stg_contributions') }}
),
hashed as (
    select
        md5(taxpayer_id || ':' || country) as taxpayer_key,
        country
    from base
)
select * from hashed
