import requests
import pandas as pd
import time

API_KEY = "18d81375ec4f465f83516fbaac3554d2"

def fetch_news(query, from_date, to_date, api_key):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "sortBy": "relevancy",
        "language": "en",
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return articles
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def save_news_to_csv(all_articles, output_file):
    data = []
    for article in all_articles:
        data.append({
            "topic": article.get("topic"),
            "source": article["source"]["name"],
            "author": article["author"],
            "title": article["title"],
            "description": article["description"],
            "content": article["content"],
            "published_at": article["publishedAt"],
            "url": article["url"]
        })

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"News data saved to {output_file}")

if __name__ == "__main__":
    topics = [
        "freight rates", "global shipping demand", "container shipping",
        "dry bulk shipping", "tanker shipping", "oil price fluctuations",
        "GDP growth", "trade wars", "sanctions", "Ukraine War",
        "crude oil supply", "LNG shipping", "Suez Canal disruption",
        "port congestion", "autonomous shipping", "climate change shipping",
        "IMO regulations", "supply chain logistics"
    ]
    from_date = "2024-11-24"
    to_date = "2024-12-22"
    api_key = "YOUR_NEWSAPI_KEY"
    all_articles = []

    for topic in topics:
        print(f"Fetching news for topic: {topic}")
        articles = fetch_news(topic, from_date, to_date, api_key)
        # Add the topic to each article for context
        for article in articles:
            article["topic"] = topic
        all_articles.extend(articles)
        time.sleep(1)  # Add delay to avoid hitting rate limits

output_file = "news_topics_debug.csv"  # Static filename for debugging
save_news_to_csv(all_articles, output_file)

