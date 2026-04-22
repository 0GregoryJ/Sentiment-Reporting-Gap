SELECT
    date,
    spending_search_sentiment,
    spending_reported_sentiment,
    spending_gap,
    credit_card_application,
    kitchen_remodel,
    flight_deals
FROM main_features
WHERE date >= ?
ORDER BY date;