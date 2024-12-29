import requests
from Sent_anlys.database.db_config import Session
# from Sent_anlys.models import MacroData
# from Sent_anlys.utils.freight_rates import fetch_freight_rates
from Sent_anlys.utils.news_api import fetch_news
from Sent_anlys.utils.macro_data import fetch_oil_prices, fetch_gdp_growth, fetch_trade_volumes, fetch_inflation_rates, fetch_industrial_production


NEWS_API_KEY = "18d81375ec4f465f83516fbaac3554d2"
ALPHA_VANTAGE_KEY = "1UGCGOW5V20L24UB"
    
def fetch_macro_data():
    print("Fetching oil prices...")
    fetch_oil_prices(ALPHA_VANTAGE_KEY)

    print("Fetching GDP growth data...")
    fetch_gdp_growth(ALPHA_VANTAGE_KEY)

    print("Fetching trade volume data...")
    fetch_trade_volumes(ALPHA_VANTAGE_KEY)

    print("Fetching inflation rate data...")
    fetch_inflation_rates(ALPHA_VANTAGE_KEY)

    print("Fetching industrial production data...")
    fetch_industrial_production(ALPHA_VANTAGE_KEY)

    fetch_oil_prices(ALPHA_VANTAGE_KEY)

if __name__ == "__main__":
    topics = [
        "freight rates", "global shipping demand", "container shipping",
        "dry bulk shipping", "tanker shipping", "oil price fluctuations",
        "GDP growth", "trade wars", "sanctions", "Ukraine War",
        "crude oil supply", "LNG shipping", "Suez Canal disruption",
        "port congestion", "autonomous shipping", "climate change shipping",
        "IMO regulations", "supply chain logistics", "tanker", "Medium Range",
        "Long range", "Aframax", "VLCC", "Panamax", "ULCC"
    ]
    
    for topic in topics:
        fetch_news(topic, "2024-11-28", "2024-12-28", NEWS_API_KEY)

    print("Fetching macroeconomic data...")
    fetch_macro_data()

        # print(f"Fetching news for topic: {topic}")
        # articles = fetch_news(topic, from_date, to_date, api_key)
        # # Add the topic to each article for context
        # for article in articles:
        #     article["topic"] = topic
        # all_articles.extend(articles)
        # time.sleep(1)  # Add delay to avoid hitting rate limits
