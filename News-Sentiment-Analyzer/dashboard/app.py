import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import re
from collections import Counter

# Set page config at the very beginning
st.set_page_config(page_title="News Sentiment Analyzer", page_icon="📰", layout="wide")

# Add the parent directory to the path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import database
from main import run_pipeline

# Stop Words for keyword analysis
STOP_WORDS = {
    'the', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 
    'for', 'on', 'are', 'as', 'with', 'his', 'they', 'of', 'and', 'at',
    'this', 'how', 'what', 'why', 'can', 'do', 'my', 'we', 'from', 'about',
    'an', 'by', 'or', 'be', 'has', 'have', 'from', 'but', 'not', 'their',
    'will', 'says', 'after', 'new', 'more', 'first', 'over', 'out', 'us', 
    'who', 'her', 'she', 'him', 'its', 'about', 'just', 'more', 'into', 'than',
    'would', 'could', 'should', 'been', 'were', 'also', 'some', 'them', 'their'
}

def extract_keywords(df, sentiment_label=None, top_n=10):
    """Tokenizes headlines and extracts top keywords."""
    if sentiment_label:
        titles = df[df['sentiment_label'] == sentiment_label]['title']
    else:
        titles = df['title']
        
    words = []
    for title in titles:
        # Match only alphabetical characters with length >= 3
        cleaned = re.findall(r'\b[a-z]{3,}\b', str(title).lower())
        words.extend([w for w in cleaned if w not in STOP_WORDS])
    
    counter = Counter(words)
    return pd.DataFrame(counter.most_common(top_n), columns=['Keyword', 'Frequency'])

@st.cache_data(ttl=60)
def load_data():
    """Fetches articles from the SQLite database."""
    # Ensure tables are created
    database.init_db()
    return database.get_articles_df()

# Custom CSS styling for premium look
st.markdown("""
<style>
    /* Gradient Banner */
    .banner {
        background: linear-gradient(135deg, #0e1e38 0%, #1e3a60 100%);
        padding: 40px;
        border-radius: 16px;
        text-align: center;
        color: #ffffff;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .banner h1 {
        font-family: 'Inter', sans-serif;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin: 0;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #00d2ff 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .banner p {
        font-size: 1.15rem;
        color: #a0aec0;
        margin-top: 10px;
        margin-bottom: 0;
    }
    
    /* Premium HTML Metrics Boxes */
    .metric-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    .metric-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
    }
    .metric-value {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Pill Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-align: center;
    }
    .badge-positive {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.3);
    }
    .badge-negative {
        background-color: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    .badge-neutral {
        background-color: rgba(160, 174, 192, 0.15);
        color: #a0aec0;
        border: 1px solid rgba(160, 174, 192, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 1. Gradient Header Banner
st.markdown("""
<div class="banner">
    <h1>📰 Global News Sentiment Analyzer</h1>
    <p>Automated pipeline scraping international feeds, scoring headline polarity, and mining macro-trends.</p>
</div>
""", unsafe_allow_html=True)

# Load data
df = load_data()

# 2. Check if database has entries
if df.empty:
    st.info("No scraped articles found in the database. Click the button below to execute the scraper pipeline.")
    if st.button("🚀 Trigger First Pipeline Run", use_container_width=True):
        with st.spinner("Scraping feeds, resolving content, and scoring sentiments..."):
            run_pipeline()
            st.cache_data.clear()
            st.rerun()
else:
    # Sidebar control panel
    st.sidebar.header("🕹️ Controls & Filters")
    
    # Manual Scraping Control
    if st.sidebar.button("🔄 Sync & Rescrape Latest News", use_container_width=True):
        with st.spinner("Scraping and analyzing latest headlines..."):
            run_pipeline()
            st.cache_data.clear()
            st.success("Successfully synchronized database!")
            st.rerun()
            
    st.sidebar.markdown("---")
    
    # Filtering parameters
    search_query = st.sidebar.text_input("🔍 Search Headlines", "")
    
    sources = df['source'].unique().tolist()
    selected_sources = st.sidebar.multiselect("Select News Sources", sources, default=sources)
    
    sentiment_options = ['Positive', 'Negative', 'Neutral']
    selected_sentiments = st.sidebar.multiselect("Filter Sentiment", sentiment_options, default=sentiment_options)
    
    # Apply filtering criteria
    filtered_df = df[
        (df['source'].isin(selected_sources)) &
        (df['sentiment_label'].isin(selected_sentiments))
    ]
    
    if search_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, case=False, na=False)]

    # 3. High-Fidelity Metrics Grid
    total_articles = len(filtered_df)
    avg_score = filtered_df['sentiment_score'].mean() if total_articles > 0 else 0.0
    
    # Color coding average score
    score_color = "#95a5a6"
    if avg_score >= 0.05:
        score_color = "#2ecc71"
    elif avg_score <= -0.05:
        score_color = "#e74c3c"
        
    pos_count = len(filtered_df[filtered_df['sentiment_label'] == 'Positive'])
    neg_count = len(filtered_df[filtered_df['sentiment_label'] == 'Negative'])
    neu_count = len(filtered_df[filtered_df['sentiment_label'] == 'Neutral'])
    
    # Custom HTML metrics injection
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-value" style="color: #00d2ff;">{total_articles}</div>
            <div class="metric-label">Articles Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: {score_color};">{avg_score:+.3f}</div>
            <div class="metric-label">Average Sentiment (Compound)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #2ecc71;">{pos_count}</div>
            <div class="metric-label">Positive Headlines</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #e74c3c;">{neg_count}</div>
            <div class="metric-label">Negative Headlines</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # If no records match filters, short-circuit visualizations
    if filtered_df.empty:
        st.warning("No records matched the selected filter criteria. Try adjusting the sidebar options.")
    else:
        # 4. Visualizations Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Sentiment Polarity Distribution")
            donut_fig = go.Figure(data=[go.Pie(
                labels=['Positive', 'Neutral', 'Negative'],
                values=[pos_count, neu_count, neg_count],
                hole=.45,
                marker=dict(colors=['#2ecc71', '#95a5a6', '#e74c3c']),
                hoverinfo="label+percent+value",
                textinfo="label+percent"
            )])
            donut_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=300
            )
            st.plotly_chart(donut_fig, use_container_width=True)
            
        with col2:
            st.subheader("🏢 Source Sentiment Breakdown")
            # Grouped bar chart comparing counts of sentiment per news source
            source_summary = filtered_df.groupby(['source', 'sentiment_label']).size().reset_index(name='count')
            bar_fig = px.bar(
                source_summary,
                x='source',
                y='count',
                color='sentiment_label',
                color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'},
                barmode='group',
                labels={'count': 'Number of Articles', 'source': 'Source', 'sentiment_label': 'Sentiment'}
            )
            bar_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                margin=dict(t=20, b=20, l=10, r=10),
                height=300,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(bar_fig, use_container_width=True)
            
        st.markdown("---")
        
        # 5. Visualizations Row 2 (Sentiment Trends Over Time)
        st.subheader("📈 Sentiment Value Over Time")
        
        # Parse published_at as datetime (extract just date portion or hours)
        filtered_df = filtered_df.copy()
        filtered_df['parsed_date'] = pd.to_datetime(filtered_df['published_at'], errors='coerce')
        filtered_df = filtered_df.dropna(subset=['parsed_date'])
        
        if not filtered_df.empty:
            # Resample daily or hourly depending on span
            trend_df = filtered_df.set_index('parsed_date').resample('H' if len(filtered_df) < 100 else 'D')['sentiment_score'].mean().reset_index()
            
            trend_fig = px.area(
                trend_df,
                x='parsed_date',
                y='sentiment_score',
                labels={'sentiment_score': 'Avg Compound Score', 'parsed_date': 'Timestamp'},
            )
            
            # Highlight positive/negative regions dynamically using line colors
            trend_fig.update_traces(
                line_color='#00d2ff',
                fillcolor='rgba(0, 210, 255, 0.15)'
            )
            trend_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                margin=dict(t=10, b=20, l=10, r=10),
                height=300
            )
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("Insufficient timestamp data to render sentiment trend lines.")
            
        st.markdown("---")
        
        # 6. Visualizations Row 3: Keyword Analysis (Positive vs Negative Vocabulary)
        st.subheader("🏷️ Vocabulary & Topic Extraction")
        col_pos_word, col_neg_word = st.columns(2)
        
        with col_pos_word:
            st.markdown("<h4 style='color:#2ecc71; text-align:center;'>Top Keywords in Positive Headlines</h4>", unsafe_allow_html=True)
            pos_kw = extract_keywords(filtered_df, sentiment_label='Positive')
            if not pos_kw.empty:
                pos_kw_fig = px.bar(
                    pos_kw,
                    x='Frequency',
                    y='Keyword',
                    orientation='h',
                    color_continuous_scale='Greens',
                    color='Frequency'
                )
                pos_kw_fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    coloraxis_showscale=False,
                    yaxis={'categoryorder': 'total ascending', 'showgrid': False},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.05)'},
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=280
                )
                st.plotly_chart(pos_kw_fig, use_container_width=True)
            else:
                st.write("No positive keywords resolved.")
                
        with col_neg_word:
            st.markdown("<h4 style='color:#e74c3c; text-align:center;'>Top Keywords in Negative Headlines</h4>", unsafe_allow_html=True)
            neg_kw = extract_keywords(filtered_df, sentiment_label='Negative')
            if not neg_kw.empty:
                neg_kw_fig = px.bar(
                    neg_kw,
                    x='Frequency',
                    y='Keyword',
                    orientation='h',
                    color_continuous_scale='Reds',
                    color='Frequency'
                )
                neg_kw_fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    coloraxis_showscale=False,
                    yaxis={'categoryorder': 'total ascending', 'showgrid': False},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.05)'},
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=280
                )
                st.plotly_chart(neg_kw_fig, use_container_width=True)
            else:
                st.write("No negative keywords resolved.")
                
        st.markdown("---")
        
        # 7. Feed Explorer & List view
        st.subheader("🔎 Document Feed Explorer")
        
        # We construct an interactive table displaying custom HTML badges for sentiment label
        display_df = filtered_df.copy()
        
        # Format links and badges
        def make_clickable(row):
            return f'<a href="{row["url"]}" target="_blank" style="color: #00d2ff; text-decoration: none; font-weight:500;">🔗 Link</a>'
            
        def make_sentiment_badge(row):
            lbl = row['sentiment_label']
            if lbl == 'Positive':
                return '<span class="badge badge-positive">Positive</span>'
            elif lbl == 'Negative':
                return '<span class="badge badge-negative">Negative</span>'
            else:
                return '<span class="badge badge-neutral">Neutral</span>'

        display_df['Source'] = display_df['source']
        display_df['Headline'] = display_df['title']
        display_df['Score'] = display_df['sentiment_score'].apply(lambda x: f"{x:+.3f}")
        display_df['Sentiment'] = display_df.apply(make_sentiment_badge, axis=1)
        display_df['Published At'] = display_df['published_at'].apply(lambda x: str(x)[:16].replace('T', ' '))
        display_df['Link'] = display_df.apply(make_clickable, axis=1)
        
        # Display as Markdown / HTML table for premium formatting
        html_table = display_df[['Source', 'Headline', 'Published At', 'Score', 'Sentiment', 'Link']].to_html(
            escape=False, index=False, classes="dataframe"
        )
        
        # Add table border radius and row highlight styling
        st.markdown(f"""
        <style>
            table.dataframe {{
                width: 100%;
                border-collapse: collapse;
                background-color: rgba(255,255,255,0.02);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            table.dataframe th {{
                background-color: rgba(255,255,255,0.08);
                color: #ffffff;
                font-weight: 600;
                text-align: left;
                padding: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            table.dataframe td {{
                padding: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                color: #e2e8f0;
            }}
            table.dataframe tr:hover td {{
                background-color: rgba(255,255,255,0.04);
            }}
        </style>
        {html_table}
        """, unsafe_allow_html=True)
