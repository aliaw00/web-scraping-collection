import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from analysis.trend_analyzer import TrendAnalyzer

# Set modern, minimalist page config
st.set_page_config(page_title="Reddit Trend Miner", page_icon="📊", layout="wide")

@st.cache_data(ttl=600) # Cache data for 10 minutes to prevent constant DB hits
def load_data():
    db = DatabaseManager("../reddit_data.db")
    return db.get_all_posts_df()

def run_dashboard():
    st.title("📊 Reddit Trend Miner")
    st.markdown("A lightweight tool monitoring subreddit trends and discussion topics.")
    
    # Load Data
    df = load_data()
    
    if df.empty:
        st.warning("No data found. Please run `main.py` to collect some Reddit posts first.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    available_subs = df['subreddit'].unique().tolist()
    selected_subs = st.sidebar.multiselect("Select Subreddits", available_subs, default=available_subs)
    
    # Apply filters
    filtered_df = df[df['subreddit'].isin(selected_subs)]

    # --- Top Level Metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Posts Analyzed", len(filtered_df))
    col2.metric("Total Subreddits", len(selected_subs))
    col3.metric("Highest Score", int(filtered_df['score'].max()))

    st.markdown("---")

    # --- Trend Analysis ---
    st.subheader("🔥 Trending Keywords")
    
    # Use our Analysis module
    trend_df = TrendAnalyzer.extract_top_keywords(filtered_df['title'])
    
    # Create a modern Plotly bar chart
    fig = px.bar(
        trend_df, 
        x='Mentions', 
        y='Keyword', 
        orientation='h',
        color='Mentions',
        color_continuous_scale='Blues',
        title="Most Mentioned Topics in Titles"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    # --- Raw Data Explorer ---
    st.subheader("Raw Data Explorer")
    st.dataframe(
        filtered_df[['subreddit', 'title', 'score', 'num_comments']].sort_values(by='score', ascending=False),
        use_container_width=True
    )

if __name__ == "__main__":
    run_dashboard()
