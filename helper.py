from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# Load English stopwords (from NLTK)
english_stop_words = set(stopwords.words('english'))

# Load Hinglish stopwords from the local file "stop_hinglish.txt"
def load_hinglish_stopwords():
    try:
        with open("stop_hinglish.txt", "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

# Merge all stopword sources
stop_words = english_stop_words.union(load_hinglish_stopwords())

extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = [word for message in df['message'].fillna('') for word in message.split()]
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]
    links = [url for message in df['message'].fillna('') for url in extract.find_urls(message)]
    
    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    user_counts = df['user'].value_counts().head()
    user_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    user_percent.columns = ['name', 'percent']
    return user_counts, user_percent


def create_wordcloud(selected_user, df):
    """Generates a word cloud based on user messages"""
    if df.empty or 'message' not in df.columns:
        raise ValueError("No valid messages to generate a word cloud.")

    # Filter messages for selected user (if needed)
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    text = " ".join(df["message"].dropna())

    if not text.strip():
        raise ValueError("No meaningful text available for WordCloud.")

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color="white").generate(text)
    return wc


def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>')].copy()
    words = [word for message in temp['message'].fillna('') for word in message.lower().split() if word not in stop_words]

    return pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = [char for message in df['message'].fillna('') for char in message if emoji.is_emoji(char)]
    return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date').count()['message'].reset_index()

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts() if not df.empty else pd.Series()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts() if not df.empty else pd.Series()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()

    return df.pivot_table(index='day_name', columns='period_24hr', values='message', aggfunc='count').fillna(0)
