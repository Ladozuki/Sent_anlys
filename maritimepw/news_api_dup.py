
import requests
import pandas as pd
import re
import nltk
import sys
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# NLTK downloads
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')
nltk.download('punkt')

# Initialize tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
sid = SentimentIntensityAnalyzer()


csv_file = "news_sentiment.csv"

topics = [
    # **Dangote & West Africa Market Impact**
   

    # **Major Shipping Routes & Tanker Flows**
    "Nigeria to Europe shipping", "Middle East to Europe refined products", "Middle East to Africa oil",
    "North African crude to Europe", "Rotterdam refined products", "Black Sea oil exports", 

    # **Logistics, Infrastructure & Disruptions**
    "Suez Canal", "port congestion", "bunker availability", "shipping emissions", "decarbonization in shipping",

    # **Newly Emerging Market Trends**
    "autonomous shipping", "Cape of Good Hope diversions", "maritime oil logistics Africa"
]

# Keywords for filtering
keywords = [
    # Core African Routes
    "Dangote refinery", "West Africa refined products", "Nigeria oil exports", "intra-African trade",
    "Nigeria to Europe shipping", "Rotterdam refined products", "Dangote Europe crude", "diesel exports to Europe",
    "West Africa crude to China", "Nigeria crude to China",
    "West Africa to UK-Continent", "Bonny to Rotterdam crude","West African oil exports",
    "Dangote to East Africa", "refined products exports East Africa", "Dar es Salaam imports", "Nigeria refined products",

    # Global Routes for Context
    "Middle East to East Asia crude", "Singapore oil imports", "China crude imports",
    "Middle East to Europe refined products", "Middle East Gulf to UK", "refined product flows",
    "Middle East to Africa oil", "Middle East refined products Africa", "bunker price", "import reductions Africa", 
    "North African crude to Europe", "Black Sea oil exports", "CPC to Augusta",
    "Caribbean oil exports", "refined product flows America",

    # General Supporting Context
    "global oil prices", "freight rates", "maritime logistics Africa", "shipping emissions",
    "spot prices", "time charter rates", "bunker availability", "Suez Canal", "port congestion",
    "GDP growth", "OPEC announcements", "trade wars", "sanctions impact on shipping",

    # Newly Added Topics
    "Frontline crude oil shipping", "Golar LNG", "lpg shipping"
    "BP refinery", "Shell crude exports", "decarbonization shipping", "green shipping", "vlsfo",
    "Scorpio Tankers spot rates", "Navios fleet expansion",
    "Euronav Middle East routes", "Star Bulk rates",
    "Golden Ocean charter trends", "Danaos shipping updates",
    "Capital Product Partners tankers", "Teekay Aframax operations", "maritime IOT", "baltic wet index", "North Sea shipping",
]

list =  [ 
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
    pstve_texts, ngtve_texts = [], []
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            data_list = []
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
                 # Store in list
                data_list.append({
                    "topic": query,
                    "source": article.get("source", {}).get("name"),
                    "author": article.get("author"),
                    "title": article.get("title", "No Title"),
                    "description": article.get("description", "No Description"),
                    "content": article.get("content", "No Content"),
                    "date": article.get("publishedAt"),
                    "url": article.get("url"),
                    "sentiment_score": sentiment_score
                })
            
            # Convert list to DataFrame
            df = pd.DataFrame(data_list)

            # Append or create CSV
            if os.path.exists(csv_file):
                df.to_csv(csv_file, mode='a', header=False, index=False)
            else:
                df.to_csv(csv_file, index=False)

            print(f"News articles for '{query}' saved to CSV.")
        else:
            print(f"Error fetching news: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

# Main Process
if __name__ == "__main__":
    API_KEY = "18d81375ec4f465f83516fbaac3554d2"

    for keyword in topics:
        print(f"Fetching news for: {keyword}")
        fetch_news(keyword, "2025-01-13", "2025-02-13", API_KEY)
                

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

    





