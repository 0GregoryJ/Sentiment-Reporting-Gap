CREATE OR REPLACE TABLE fact_observations AS
SELECT
    date,
    query,
    category,
    value,
    'fred' AS source
FROM stg_fred

UNION ALL

SELECT
    date,
    query,
    category,
    value,
    'bls' AS source
FROM stg_bls

UNION ALL

SELECT
    date,
    query,
    category,
    value,
    'serp' AS source
FROM stg_serp;