CREATE OR REPLACE TABLE main_features AS
WITH base AS (
    SELECT
        date,
        value,
        query,
        category,
        source,
        (
            (value - AVG(value) OVER (
                PARTITION BY source, query, category
            ))
            / NULLIF(
                STDDEV_SAMP(value) OVER (
                    PARTITION BY source, query, category
                ),
                0
            )
        ) AS zscore
    FROM fact_observations
),
aggregated AS (
    SELECT
        date,

        AVG(
            CASE
                WHEN category = 'labor_market' AND source = 'serp'
                THEN 100.0 * (1.0 / (1.0 + exp(-1.7 * zscore)))
            END
        ) AS labor_search_sentiment,

        AVG(
            CASE
                WHEN category = 'consumer_spending' AND source = 'serp'
                THEN 100.0 * (1.0 / (1.0 + exp(-1.7 * zscore)))
            END
        ) AS spending_search_sentiment,

        AVG(
            CASE
                WHEN category = 'labor_market' AND source IN ('fred', 'bls')
                THEN 100.0 * (1.0 / (1.0 + exp(-1.7 * zscore)))
            END
        ) AS labor_reported_sentiment,

        AVG(
            CASE
                WHEN category = 'consumer_spending' AND source IN ('fred', 'bls')
                THEN 100.0 * (1.0 / (1.0 + exp(-1.7 * zscore)))
            END
        ) AS spending_reported_sentiment,

        MAX(
            CASE
                WHEN query = 'LNS14000000' THEN value
            END
        ) AS LNS14000000,

        MAX(
            CASE
                WHEN query = 'CES0500000002' THEN value
            END
        ) AS CES0500000002,

        MAX(
            CASE
                WHEN query = 'CES0000000001' THEN value
            END
        ) AS CES0000000001,

        MAX(
            CASE
                WHEN query = 'unemployment benefits' THEN value
            END
        ) AS unemployment_benefits,

        MAX(
            CASE
                WHEN query = 'second job' THEN value
            END
        ) AS second_job,

        MAX(
            CASE
                WHEN query = 'layoffs' THEN value
            END
        ) AS layoffs,


    FROM base
    GROUP BY date
)

SELECT
    date,
    labor_search_sentiment,
    spending_search_sentiment,
    labor_reported_sentiment,
    spending_reported_sentiment,
    labor_search_sentiment - labor_reported_sentiment AS labor_gap,
    spending_search_sentiment - spending_reported_sentiment AS spending_gap,
    LNS14000000,
    CES0500000002,
    CES0000000001,
    unemployment_benefits,
    second_job,
    layoffs
FROM aggregated
ORDER BY date;