import streamlit as st
import time
import json
import pandas as pd
from datetime import datetime
import os
from news_module import CarNewsCrawler

# Page configuration
st.set_page_config(
    page_title="Car News Crawler",
    page_icon="🚗",
    layout="wide",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .news-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .source-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .date-text {
        color: #666;
        font-size: 0.9rem;
    }
    .summary-text {
        color: #333;
        font-style: italic;
        margin-top: 0.5rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">🚗 Car News Crawler</h1>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.header("📰 Latest Car News")
        #news crawl
        try:
            crawler = CarNewsCrawler(headless=True, debug=True)
            articles = crawler.crawl_all_sources(max_articles_per_source=5)
            crawler.cleanup()
                        
            if articles:
                # Save to files
                crawler.news_data = articles
                crawler.save_to_json("car_news.json")
                crawler.save_to_csv("car_news.csv")
                crawler.save_to_txt("car_news.txt")
                            
                st.success(f"✅ Successfully crawled {len(articles)} articles!")
                st.session_state.articles = articles
                st.session_state.last_crawl = datetime.now()
            else:
                st.error("❌ No articles found. Please try again.")
                            
        except Exception as e:
            st.error(f"❌ Error during crawling: {str(e)}")  

        if "articles" in st.session_state and st.session_state.articles:
            articles = st.session_state.articles

            # Filter options
            st.subheader("🔍 Filter Options")
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                search_term = st.text_input("Search in titles", "")
            
            with col_filter2:
                sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Title A-Z", "Title Z-A"])
            
            # Filter articles
            filtered_articles = articles
            
            if search_term:
                filtered_articles = [a for a in filtered_articles if search_term.lower() in a['title'].lower()]

            # Sort articles
            if sort_by == "Date (Newest)":
                filtered_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
            elif sort_by == "Date (Oldest)":
                filtered_articles.sort(key=lambda x: x.get('date', ''))
            elif sort_by == "Title A-Z":
                filtered_articles.sort(key=lambda x: x['title'])
            elif sort_by == "Title Z-A":
                filtered_articles.sort(key=lambda x: x['title'], reverse=True)
            
            # Display articles
            st.write(f"Showing {len(filtered_articles)} of {len(articles)} articles")
            
            for i, article in enumerate(filtered_articles):
                with st.container():
                    st.markdown(f"""
                    <div class="news-card">
                        <h3>{article['title']}</h3>
                        <span class="source-badge">{article['source']}</span>
                        <div class="date-text">📅 {article['date']}</div>
                        <a href="{article['link']}" target="_blank">🔗 Read Article</a>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.info("ℹ️ No news data available. Press the button to crawl news or load saved data.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        🚗 Car News Crawler | Last updated: {time.strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()