from serpapi import GoogleSearch
import pandas as pd
from functools import reduce
import os
from dotenv import load_dotenv
from pathlib import Path

#API key
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

SERP_API_KEY = str(os.getenv("SERP_API_KEY"))

#directory for parquet output
BASE_DIR = Path(__file__).resolve().parents[2]
destination_path = BASE_DIR / "data" / "raw" / "serp_api"

#-----request data------
#labor market search data
layoffs_request = {
    "engine": "google_trends",
    "q": "layoffs",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

umplymt_benefits_request = {
    "engine": "google_trends",
    "q": "unemployment benefits",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

job_cuts_request = {
    "engine": "google_trends",
    "q": "job cuts",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

second_job_request = {
    "engine": "google_trends",
    "q": "second job",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

side_hustle_request = {
    "engine": "google_trends",
    "q": "side hustle",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

CCMP_request = {
    "engine": "google_trends",
    "q": "credit card minimum payment",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

#consumer spending search data
mortgage_request = {
    "engine": "google_trends",
    "q": "mortgage preapproval",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

car_request = {
    "engine": "google_trends",
    "q": "new car deals",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

flights_request = {
    "engine": "google_trends",
    "q": "flight deals",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

CCA_request = {
    "engine": "google_trends",
    "q": "credit card application",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

kitchen_request = {
    "engine": "google_trends",
    "q": "kitchen remodel",
    "date": "all",
    "data_type": "TIMESERIES",
    "api_key": SERP_API_KEY,
}

#------search and store results------
#function to search and return results as dict
def search_and_store(request):
    search = GoogleSearch(request)
    results = search.get_dict()
    return results
#labor market search data restults
layoffs_results = search_and_store(layoffs_request)
umplymt_benefits_results = search_and_store(umplymt_benefits_request)
job_cuts_results = search_and_store(job_cuts_request)
second_job_results = search_and_store(second_job_request)
side_hustle_results = search_and_store(side_hustle_request)
CCMP_results = search_and_store(CCMP_request)

#consumer spending search data results
mortgage_results = search_and_store(mortgage_request)
car_results = search_and_store(car_request)
flights_results = search_and_store(flights_request)
CCA_results = search_and_store(CCA_request)
kitchen_results = search_and_store(kitchen_request)
#cost of living shopping/search data


#-----function gets df from serpapi results------
def serpapi_to_df(results):
    IOT = results["interest_over_time"]
    timeline = IOT["timeline_data"]

    rows = []
    
    for point in timeline:
        #skip parial data
        if point.get("partial_data", False):
            continue
        #convert serpapi unix timestamp to datetime
        date = pd.to_datetime(
            int(point["timestamp"]),
            unit="s",
            utc = True
        ).tz_convert(None)
        #get info
        for v in point["values"]:
            rows.append({
                "date": date,
                "query": v["query"],
                "value": int(v["extracted_value"]),
            })

    return (
        pd.DataFrame(rows)
          .sort_values("date")
          .reset_index(drop=True)
    )

#-----merge dfs, convert df into long format, add category column, and write to parquet------
search_terms = [
    ("layoffs", layoffs_results),
    ("unemployment_benefits", umplymt_benefits_results),
    ("job_cuts", job_cuts_results),
    ("second_job", second_job_results),
    ("side_hustle", side_hustle_results),
    ("ccmp", CCMP_results),
    ("mortgage", mortgage_results),
    ("car", car_results),
    ("flights", flights_results),
    ("CCA", CCA_results),
    ("kitchen", kitchen_results),
]

search_dfs = []
for name, results in search_terms:
    results_df = serpapi_to_df(results)[["date", "query", "value"]]
    search_dfs.append(results_df)

serpAPI_search_data = pd.concat(search_dfs, ignore_index=True)
#define categories and map to cateogry column
categories = {
    "layoffs": "labor_market",
    "unemployment benefits": "labor_market",
    "job cuts": "labor_market",
    "second job": "labor_market",
    "side hustle": "labor_market",
    "credit card minimum payment": "labor_market",
    "mortgage preapproval": "consumer_spending",
    "new car deals": "consumer_spending",
    "flight deals": "consumer_spending",
    "credit card application": "consumer_spending",
    "kitchen remodel": "consumer_spending"
}

serpAPI_search_data["category"] = serpAPI_search_data["query"].map(categories)

#write to parquet
serpAPI_search_data.to_parquet(destination_path / "serp_raw.parquet", index=False)

print(serpAPI_search_data)
