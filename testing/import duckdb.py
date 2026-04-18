import duckdb

con = duckdb.connect("/Users/gregoryjoshua/Desktop/Projects/Sentiment-Reporting-Gap/data/database/analytics.duckdb")

df = con.execute("""
SELECT *
FROM fact_observations
WHERE category = 'labor_market' AND source = 'serp'
ORDER BY date
""").df()

print(df)