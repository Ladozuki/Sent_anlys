import requests
import pandas as pd
import re
import nltk
import os
import time
from datetime import datetime, timedelta
import logging
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_collection.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsSentimentCollector")

class NewsSentimentCollector:
    """
    Collects maritime shipping news and performs sentiment analysis.
    Focuses on routes related to Dangote refinery and West African shipping.
    """
    def __init__(self, api_key, output_dir="data"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.csv_file = os.path.join(output_dir, "news_sentiment.csv")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize NLTK components
        try:
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            logger.info("Downloading required NLTK data...")
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
        
        # Initialize NLP tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.sid = SentimentIntensityAnalyzer()
        
        # Topic lists
        self.topics = self.get_default_topics()
        self.route_dict = self.get_route_dict()
        
    def get_default_topics(self):
        """Return the default topics to query"""
        return [
            # Major Shipping Routes & Tanker Flows
            "Nigeria to Europe shipping", "Middle East to Europe refined products", 
            "Middle East to Africa oil", "North African crude to Europe", 
            "Rotterdam refined products", "Black Sea oil exports", 
            
            # Logistics, Infrastructure & Disruptions
            "Suez Canal", "port congestion", "bunker availability", 
            "shipping emissions", "decarbonization in shipping",
            
            # Newly Emerging Market Trends
            "autonomous shipping", "Cape of Good Hope diversions", 
            "maritime oil logistics Africa", "Dangote refinery"
        ]
    
    def get_route_dict(self):
        """Return mapping between route codes and descriptions"""
        return {
            "TD2": "Middle East Gulf to Singapore",
            "TD3C": "Middle East Gulf to China (VLCC)",
            "TD6": "Black Sea to Mediterranean (Suezmax)",
            "TD7": "North Sea to Continent (Aframax)",
            "TD8": "Kuwait to Singapore",
            "TD9": "Caribbean to US Gulf (LR1)",
            "TD15": "West Africa to China (VLCC)",
            "TD20": "West Africa to UK-Continent (Suezmax)",
            "TD22": "US Gulf to China",
            "TD25": "US Gulf to UK-Continent",
            "TD27": "Guyana to ARA",
            "TC5": "CPP Middle East Gulf to Japan (LR1)",
            "TC8": "CPP Middle East Gulf to UK-Continent (LR1)",
            "TC12": "Naphtha West Coast India to Japan (MR)",
            "TC15": "Naphtha Mediterranean to Far East (Aframax)",
            "TC16": "ARA to Offshore Lome (LR1)",
            "TC17": "CPP Jubail to Dar es Salaam (MR)",
            "TC18": "CPP US Gulf to Brazil (MR)",
            "TC19": "CPP Amsterdam to Lagos (MR)",
            "TC20": "CPP Middle East Gulf to UK-Continent (Aframax)"
        }
    
    def clean_text(self, text):
        """Clean and preprocess text for sentiment analysis"""
        if text is None:
            return ""
            
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
        text = re.sub(r'\W', ' ', text)  # Remove punctuation
        text = text.lower()  # Convert to lowercase
        text = ' '.join([self.lemmatizer.lemmatize(word) for word in text.split() if word not in self.stop_words])
        return text
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using VADER"""
        if not text:
            return 0.0
        sentiment_score = self.sid.polarity_scores(text)['compound']
        return sentiment_score
    
    def fetch_news(self, query, from_date, to_date, max_retries=3):
        """
        Fetch news for a specific query and time period
        
        Args:
            query: Search term
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            max_retries: Maximum number of retry attempts
        
        Returns:
            DataFrame with fetched news articles
        """
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "sortBy": "relevancy",
            "language": "en",
            "apiKey": self.api_key
        }
        
        # Add route code as tag if query matches a route description
        route_code = None
        for code, description in self.route_dict.items():
            if description.lower() in query.lower():
                route_code = code
                break
        
        retries = 0
        while retries < max_retries:
            try:
                logger.info(f"Fetching news for '{query}'...")
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    articles = response.json().get("articles", [])
                    data_list = []
                    
                    logger.info(f"Found {len(articles)} articles for '{query}'")
                    
                    for article in articles:
                        # Handle potential None values with null-coalescing
                        title = article.get('title', '') or ''
                        description = article.get('description', '') or ''
                        content = article.get('content', '') or ''
                        
                        raw_text = (title + ' ' + description + ' ' + content).strip()
                        cleaned_text = self.clean_text(raw_text)
                        
                        # Skip if cleaned text is too short
                        if len(cleaned_text) < 50:
                            continue
                        
                        # Perform sentiment analysis
                        sentiment_score = self.analyze_sentiment(cleaned_text)
                        
                        # Create topic with route tag if available
                        topic_with_tag = query
                        if route_code:
                            topic_with_tag = f"{query} @{route_code}"
                        
                        # Get source name safely
                        source = article.get("source", {})
                        source_name = source.get("name", "") if isinstance(source, dict) else ""
                        
                        # Ensure all fields are strings to prevent concatenation errors
                        author = article.get("author", "") or ""
                        publish_date = article.get("publishedAt", "") or ""
                        url = article.get("url", "") or ""
                        
                        # Store article data
                        data_list.append({
                            "topic": topic_with_tag,
                            "source": source_name,
                            "author": author,
                            "title": title,
                            "description": description,
                            "content": content,
                            "date": publish_date,
                            "url": url,
                            "sentiment_score": sentiment_score,
                            "clean_topic": route_code if route_code else ""
                        })
                    
                    # Convert to DataFrame
                    return pd.DataFrame(data_list)
                    
                elif response.status_code == 429:  # Rate limit error
                    retries += 1
                    wait_time = 2 ** retries  # Exponential backoff
                    logger.warning(f"Rate limit reached. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error fetching news: {response.status_code} - {response.text}")
                    return pd.DataFrame()
                    
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                retries += 1
                time.sleep(2)
        
        logger.error(f"Failed to fetch news for '{query}' after {max_retries} attempts")
        return pd.DataFrame()
    
    def map_news_to_routes(self, news_df):
        """Map news articles to route codes based on content"""
        if news_df.empty:
            return news_df
        
        # If clean_topic is already set, don't override
        mask = news_df["clean_topic"] == ""
        
        # Extract route codes from topic field
        news_df.loc[mask, "clean_topic"] = news_df.loc[mask, "topic"].str.extract(r"@(\w+)").fillna("")
        
        # For remaining unmapped articles, try to match route descriptions in content
        still_unmapped = (news_df["clean_topic"] == "")
        
        if still_unmapped.any():
            for idx, row in news_df[still_unmapped].iterrows():
                # Ensure title and description are strings
                title = str(row.get("title", "")) if row.get("title") is not None else ""
                description = str(row.get("description", "")) if row.get("description") is not None else ""
                content = (title + " " + description).lower()
                
                for code, description in self.route_dict.items():
                    # Extract key terms from route description
                    route_terms = description.lower().split()
                    # Check if key route terms appear in content
                    if any(term in content for term in route_terms if len(term) > 3):
                        news_df.at[idx, "clean_topic"] = code
                        break
        
        return news_df
    
    def collect_news(self, days_back=13, custom_topics=None):
        """
        Collect news for all topics over the specified time period
        
        Args:
            days_back: Number of days to look back
            custom_topics: Optional list of custom topics to query
        
        Returns:
            Path to the saved CSV file
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Use custom topics if provided, otherwise use defaults
        topics_to_query = custom_topics if custom_topics else self.topics
        
        logger.info(f"Collecting news from {from_date} to {to_date} for {len(topics_to_query)} topics")
        
        all_news = pd.DataFrame()
        
        for topic in topics_to_query:
            topic_news = self.fetch_news(topic, from_date, to_date)
            
            if not topic_news.empty:
                all_news = pd.concat([all_news, topic_news])
                
                # Add brief delay to avoid rate limits
                time.sleep(1)
        
        # Map news to routes
        if not all_news.empty:
            all_news = self.map_news_to_routes(all_news)
            
            # Save to CSV
            if os.path.exists(self.csv_file):
                # Add only new articles (based on URL)
                existing_df = pd.read_csv(self.csv_file)
                existing_urls = set(existing_df["url"]) if "url" in existing_df.columns else set()
                new_articles = all_news[~all_news["url"].isin(existing_urls)]
                
                if not new_articles.empty:
                    new_articles.to_csv(self.csv_file, mode='a', header=False, index=False)
                    logger.info(f"Added {len(new_articles)} new articles to {self.csv_file}")
                else:
                    logger.info("No new articles to add")
            else:
                all_news.to_csv(self.csv_file, index=False)
                logger.info(f"Saved {len(all_news)} articles to {self.csv_file}")
        else:
            logger.warning("No news articles collected")
            
        return self.csv_file
    
    def analyze_sentiment_distribution(self):
        """Analyze sentiment distribution by topic instead of route"""
        if not os.path.exists(self.csv_file):
            logger.warning(f"News data file not found: {self.csv_file}")
            return None
            
        df = pd.read_csv(self.csv_file)
        
        if df.empty:
            logger.warning("News data is empty")
            return None
        
        # Extract the base topic (without route tags)
        df["base_topic"] = df["topic"].str.split(" @").str[0]
        
        # Calculate sentiment stats by topic
        topic_sentiment = df.groupby("base_topic").agg({
            "sentiment_score": ["mean", "std", "count"],
            "date": ["min", "max"]  # Fixed: removed the minus sign
        })
        
        # Flatten the column names
        topic_sentiment.columns = ['_'.join(col).strip() for col in topic_sentiment.columns.values]
        topic_sentiment = topic_sentiment.reset_index()
        
        # Calculate positive vs negative article counts
        sentiment_counts = df.groupby("base_topic").apply(
            lambda x: pd.Series({
                "positive_count": (x["sentiment_score"] > 0.1).sum(),
                "neutral_count": ((x["sentiment_score"] >= -0.1) & (x["sentiment_score"] <= 0.1)).sum(),
                "negative_count": (x["sentiment_score"] < -0.1).sum()
            })
        ).reset_index()
        
        # Merge with sentiment stats
        result = pd.merge(topic_sentiment, sentiment_counts, on="base_topic", how="left")
        
        # Save analysis results
        analysis_file = os.path.join(self.output_dir, "sentiment_analysis.csv")
        result.to_csv(analysis_file, index=False)
        logger.info(f"Sentiment analysis saved to {analysis_file}")
        
        return result

# Example usage
if __name__ == "__main__":
    API_KEY = "18d81375ec4f465f83516fbaac3554d2"  # Replace with your actual key
    
    collector = NewsSentimentCollector(API_KEY)
    news_file = collector.collect_news(days_back=27)
    sentiment_analysis = collector.analyze_sentiment_distribution()
    
    if sentiment_analysis is not None:
        print("\nSentiment Analysis by Topic:")
        print(sentiment_analysis[["base_topic", "sentiment_score_mean", "sentiment_score_count"]])