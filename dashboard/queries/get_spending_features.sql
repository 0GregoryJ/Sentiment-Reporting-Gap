SELECT
    date,
    spending_search_sentiment,
    spending_reported_sentiment,
    spending_gap,
FROM main_features
WHERE date >= ?
ORDER BY date;