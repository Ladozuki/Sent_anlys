
import requests
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from Sent_anlys.database.db_config import Session
from Sent_anlys.database.db_models import NewsSentiment

# NLTK downloads
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')
nltk.download('punkt')

# Initialize tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
sid = SentimentIntensityAnalyzer()

# Keywords for filtering
topics = [
    "freight rates", "global shipping demand",
    "MR or LR1 or Suezmax or Aframax or VLCC", "russia shipping", "Persian-Gulf",
    "Time Charter", "Spot Charter", "Black-sea shipping", "tanker shipping",  "GDP growth", "trade wars", 
    "sanctions", "crude oil ", "Middle-East oil", "LNG shipping", "Suez Canal",
    "port congestion", "autonomous shipping", "climate change shipping", "decarbonization in shipping",
    "bunkering", "maritime IOT", "baltic wet index", "global trade index", "North Sea shipping", "China shipping",
    "global supply chain", "Dangote refinery",  "MARPOL", "shipping emissions",
    "Cape of Good hope", "West Africa crude oil and gas shipping", 
    "Angola oil and gas exports", "FPSO operations Africa", "OPEC", 
    "IMO regulations", "maritime oil logistics Africa"
]

# Text Cleaning Function
def clean_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'\W', ' ', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words])
    return text

# Sentiment Analysis Function
def analyze_sentiment(text):
    sentiment_score = sid.polarity_scores(text)['compound']
    sentiment = 'positive' if sentiment_score > 0 else ('negative' if sentiment_score < 0 else 'neutral')
    return sentiment_score, sentiment

# Fetch News and Save to Database
def fetch_news(query, from_date, to_date, api_key):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "sortBy": "relevancy",
        "language": "en",
        "apiKey": api_key
    }
    session = Session()
    pstve_texts, ngtve_texts = [], []
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            for article in articles:
                raw_text = (article.get('title', '') + ' ' +
                            article.get('description', '') + ' ' +
                            article.get('content', '')).strip()
                cleaned_text = clean_text(raw_text)


                #Perform sentiment analysis
                sentiment_score, sentiment = analyze_sentiment(cleaned_text)
                if sentiment == 'positive':
                    pstve_texts.append(cleaned_text)
                elif sentiment == 'negative':
                    ngtve_texts.append(cleaned_text)

                #Add processed article to the database
                session.add(NewsSentiment(
                    topic=query,
                    source=article.get("source", {}).get("name"),
                    author=article.get("author"),
                    title=article.get("title", "No Title"),
                    description=article.get("description", "No Description"),
                    content=article.get("content", "No Content"),
                    date=article.get("publishedAt"),
                    url=article.get("url"),
                    sentiment_score=sentiment_score
                ))
            session.commit()
            print(f"News articles for '{query}' saved to database.")
        else:
            print(f"Error fetching news: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

# Main Process
if __name__ == "__main__":
    API_KEY = "18d81375ec4f465f83516fbaac3554d2"

    for keyword in topics:
        print(f"Fetching news for: {keyword}")
        fetch_news(keyword, "2024-12-15", "2025-01-02", API_KEY)






# Generate Word Cloud
# def generate_wordcloud(df, sentiment, output_path):
#     text = ' '.join(df.loc[df['sentiment'] == sentiment, 'cleaned_text'])
#     wordcloud = WordCloud(width=800, height=400).generate(text)
#     plt.figure(figsize=(10, 6))
#     plt.imshow(wordcloud, interpolation='bilinear')
#     plt.title(f'{sentiment.capitalize()} Sentiments Word Cloud')
#     plt.axis('off')
#     plt.savefig(output_path)
#     plt.close()
#     print(f"{sentiment.capitalize()} Word Cloud saved to {output_path}")



    # Generate and save word clouds for visualization
    # os.makedirs("../reports", exist_ok=True)
    # generate_wordcloud(all_articles, 'positive', "../reports/positive_wordcloud.png")
    # generate_wordcloud(all_articles, 'negative', "../reports/negative_wordcloud.png")

    





