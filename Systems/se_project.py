

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Al Jazeera Middle East News URL
url = "https://www.aljazeera.com/news/middle-east/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract headline elements
headlines = soup.find_all("h3", class_="gc__title")

# Parse into a list of dictionaries
news_data = []
for h in headlines[:15]:  # Get top 15
    title = h.text.strip()
    relative_link = h.find("a")["href"]
    full_link = "https://www.aljazeera.com" + relative_link
    news_data.append({"headline": title, "url": full_link})

# Convert to DataFrame
df = pd.DataFrame(news_data)

# Save to CSV
df.to_csv("middle_east_headlines.csv", index=False)

print("✅ Headlines saved to middle_east_headlines.csv")

#pip install nltk
import nltk
nltk.download('vader_lexicon')

import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

# Load your headline CSV
df_scrape = pd.read_csv("middle_east_headlines.csv")

# Initialize VADER
sia = SentimentIntensityAnalyzer()

# Run VADER on each headline
def analyze_sentiment(text):
    score = sia.polarity_scores(text)
    return score['compound']  # compound ranges from -1 to +1

# Add sentiment score
df_scrape["sentiment_score"] = df_scrape["headline"].apply(analyze_sentiment)

# Categorize score
df_scrape["sentiment_label"] = df_scrape["sentiment_score"].apply(
    lambda x: "positive" if x >= 0.2 else ("negative" if x <= -0.2 else "neutral")
)

# Preview and save
print(df_scrape[["headline", "sentiment_score", "sentiment_label"]])
df_scrape.to_csv("middle_east_headlines_sentiment.csv", index=False)

print("✅ VADER sentiment analysis complete and saved.")

df_scrape
###########Now using newapi.org to put more data into DF######
#pip install newsapi-python
from newsapi import NewsApiClient
import pandas as pd

api = NewsApiClient(api_key='7b5410e492fb467b8e5eb0698fd55124')

# Search for Middle East headlines
res = api.get_everything(q='Middle East conflict', language='en', sort_by='publishedAt', page_size=20)

# Convert to DataFrame
articles = res['articles']
df_newsapi = pd.DataFrame([{
    "headline": a["title"],
    "url": a["url"],
    "source": a["source"]["name"],
    "published_at": a["publishedAt"]
} for a in articles])

print(df_newsapi.head())

df_newsapi




######Now I am merging the two Together#####
scraped_df = pd.read_csv("middle_east_headlines_sentiment.csv")
df_newsapi
# If already in memory
df_newsapi["sentiment_score"] = df_newsapi["headline"].apply(lambda h: sia.polarity_scores(h)["compound"])
df_newsapi["sentiment_label"] = df_newsapi["sentiment_score"].apply(
    lambda s: "positive" if s >= 0.2 else "negative" if s <= -0.2 else "neutral"
)
df_newsapi


scraped_df.columns
# ['headline', 'url', 'sentiment_score', 'sentiment_label', 'source']
df_newsapi.columns
# ['headline', 'url', 'source', 'published_at', 'sentiment_score', 'sentiment_label']
# Add missing columns to match structure
if "published_at" not in scraped_df.columns:
    scraped_df["published_at"] = pd.NaT

combined_df = pd.concat([scraped_df, df_newsapi], ignore_index=True)

scraped_df["source_type"] = "scraped"
df_newsapi["source_type"] = "newsapi"



combined_df = combined_df.drop_duplicates(subset="url", keep="first")



combined_df.to_csv("combined_headlines_sentiment.csv", index=False)
print(f"✅ Combined dataset saved with {len(combined_df)} unique headlines.")
 
combined_df


######Pulling in even more data from Relief.Web API#####
import requests
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime, timezone

sia = SentimentIntensityAnalyzer()

def sentimentify(text):
    score = sia.polarity_scores(text)['compound']
    label = 'positive' if score >= 0.2 else 'negative' if score <= -0.2 else 'neutral'
    return score, label

def fetch_reliefweb(limit=20, keyword=None):
    url = "https://api.reliefweb.int/v1/reports"
    params = {
        "appname": "conflict-tracker",
        "limit": limit,
        "profile": "minimal"
    }

    if keyword:
        params["query[value]"] = keyword
        params["query[operator]"] = "AND"

    response = requests.get(url, params=params)
    data = response.json().get("data", [])

    results = []
    for item in data:
        fields = item.get("fields", {})
        title = fields.get("title", "No Title")
        url = item.get("href", "MISSING_URL")  # ✅ Correct ReliefWeb URL
        date = fields.get("date", {}).get("created", datetime.now(timezone.utc).isoformat())

        score, label = sentimentify(title)
        results.append({
            "headline": title,
            "url": url,
            "published_at": date,
            "source": "ReliefWeb",
            "sentiment_score": score,
            "sentiment_label": label,
            "source_type": "ReliefWeb"
        })

    return pd.DataFrame(results)

# 🔁 Run test call




df_relief = fetch_reliefweb(limit=15, keyword= ['Middle East','conflict','Israel','Yemen','Gaza'])
print(f"✅ ReliefWeb returned {len(df_relief)} articles.")
print(df_relief[['headline', 'source', 'published_at']].head())

df_relief

###Merging with the other two####
combined_df = pd.concat([combined_df, df_relief], ignore_index=True)
combined_df.drop_duplicates(subset=["headline", "source"], inplace=True)
combined_df.to_csv("combined_conflict_news.csv", index=False)
print(f"✅ Combined dataset now has {len(combined_df)} unique headlines.")


combined_df

### Streamlit dashboard on anothrer file####

####assigning coordinates to headlines####
import pandas as pd

df = pd.read_csv("combined_conflict_news.csv")
print(df.columns)
print(df[['headline', 'latitude', 'longitude']].dropna().head())

import pandas as pd

# Step 1: Load your data
df = pd.read_csv("combined_conflict_news.csv")

# Step 2: Country-to-coordinates dictionary
country_coords = {
    "Syria": (34.8021, 38.9968),
    "Iraq": (33.3152, 44.3661),
    "Iran": (32.4279, 53.6880),
    "Israel": (31.0461, 34.8516),
    "Palestine": (31.9522, 35.2332),
    "Lebanon": (33.8547, 35.8623),
    "Jordan": (30.5852, 36.2384),
    "Saudi Arabia": (23.8859, 45.0792),
    "Yemen": (15.5527, 48.5164),
    "United Arab Emirates": (23.4241, 53.8478),
    "Qatar": (25.276987, 51.520008),
    "Oman": (21.5126, 55.9233),
    "Bahrain": (26.0667, 50.5577),
    "Kuwait": (29.3759, 47.9774)
}
# Step 3: Add a function to tag lat/lon based on headline
def find_country_coords(headline):
    for country, (lat, lon) in country_coords.items():
        if country.lower() in str(headline).lower():
            return pd.Series([lat, lon, country])
    return pd.Series([None, None, None])

# Step 4: Apply function
df[['latitude', 'longitude', 'country']] = df['headline'].apply(find_country_coords)

# Step 5: Save a preview
print(df[['headline', 'country', 'latitude', 'longitude']].dropna().head())


#pip install folium
import folium
from folium.plugins import HeatMap

# Filter rows with coordinates
geo_df = df.dropna(subset=["latitude", "longitude"])

# Create base map centered on the Middle East
m = folium.Map(location=[30.0, 40.0], zoom_start=5, tiles='CartoDB positron')

# Add heatmap
heat_data = geo_df[["latitude", "longitude"]].values.tolist()
HeatMap(heat_data, radius=15).add_to(m)

# Save to HTML
m.save("middle_east_map.html")
print("✅ Saved map to 'middle_east_map.html'")
