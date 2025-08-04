import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import csv
import time
from datetime import datetime
import os
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CarNewsCrawler:
    def __init__(self, headless: bool = True, debug: bool = False):
        """
        Initialize the car news crawler
        
        Args:
            headless (bool): Run browser in headless mode
            debug (bool): Enable debug mode for troubleshooting
        """
        self.debug = debug
        self.setup_selenium(headless)
        self.news_data = []
        
    def setup_selenium(self, headless: bool):
        """Setup Selenium WebDriver with Chrome options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            if headless:
                chrome_options.add_argument("--headless")
                
            # Add user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            self.driver = None
            
    def debug_page_structure(self, url: str = "https://www.yna.co.kr/industry/automobile"):
        """
        Debug method to analyze page structure and content
        """
        try:
            logger.info(f"Debug: Analyzing page structure for {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get page title
            page_title = self.driver.title
            logger.info(f"Debug: Page title: {page_title}")
            
            # Find all links on the page
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"Debug: Found {len(all_links)} total links on page")
            
            # Analyze link texts and URLs - focus on news links
            news_links = []
            other_links = []
            
            for link in all_links[:30]:  # Check first 30 links
                try:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    
                    if text and href:
                        # Check if it's a news link
                        href_lower = href.lower()
                        text_lower = text.lower()
                        
                        # Look for news-related patterns
                        is_news_link = any(pattern in href_lower for pattern in ['/view/', '/news/', '/article/', '/automobile/']) or \
                                        any(pattern in text_lower for pattern in ['뉴스', '기사', 'news', 'article'])
                        
                        if is_news_link:
                            news_links.append((text, href))
                        else:
                            other_links.append((text, href))
                            
                except Exception as e:
                    continue
            
            logger.info(f"Debug: Found {len(news_links)} news-related links:")
            for text, href in news_links[:10]:
                logger.info(f"Debug: - {text[:50]} -> {href}")
            
            logger.info(f"Debug: Found {len(other_links)} other links:")
            for text, href in other_links[:10]:
                logger.info(f"Debug: - {text[:50]} -> {href}")
            
            # Check for specific CSS classes that might contain news
            common_selectors = [
                ".list-type01", ".list-type02", ".list-type03",
                ".news-list", ".article-list", ".list-news",
                ".news-item", "article", ".item"
            ]
            
            for selector in common_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Debug: Found {len(elements)} elements with selector '{selector}'")
                        if elements[0].text.strip():
                            logger.info(f"Debug: First element text: {elements[0].text[:100]}")
                            
                            # Check for dates in the first few elements
                            for i, element in enumerate(elements[:3]):
                                try:
                                    date_elements = element.find_elements(By.CSS_SELECTOR, "time, .date, .time, .published")
                                    if date_elements:
                                        logger.info(f"Debug: Element {i+1} has date: {date_elements[0].text}")
                                except:
                                    pass
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Debug: Error analyzing page structure: {e}")

    def crawl_korean_news(self, max_articles: int = 10) -> List[Dict]:
        """
        Crawl car news from Yonhap News (Korean)
        
        Args:
            max_articles (int): Maximum number of articles to crawl
            
        Returns:
            List[Dict]: List of news articles
        """
        articles = []
        try:
            logger.info("Starting to crawl Yonhap News...")
            self.driver.get("https://www.yna.co.kr/industry/automobile")
            
            # Wait for page to load - look for news content
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-type212 li")))
            except:
                # If specific selectors don't work, just wait for any content
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)  # Give extra time for dynamic content
            
            # Try different selectors for Korean news sites
            selectors_to_try = self.driver.find_elements(By.CSS_SELECTOR, "div.list-type212 li")
            
            article_elements = []
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Since URL is already automobile-specific, take all elements
                        article_elements = elements[:max_articles]
                        logger.info(f"Found {len(elements)} elements using selector: {selector}")
                        if self.debug:
                            logger.info(f"Debug: First element text: {elements[0].text[:100] if elements[0].text else 'No text'}")
                        break
                except Exception as e:
                    if self.debug:
                        logger.warning(f"Debug: Selector {selector} failed: {e}")
                    continue
            
            if not article_elements:
                # Fallback: try to find news links
                fallback_selectors = [
                    "a[href*='/view/']",  # Yonhap specific
                    "a[href*='/news/']",
                    "a[href*='/article/']",
                    "a[href*='/automobile/']"
                ]
                
                for fallback_selector in fallback_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, fallback_selector)
                        if elements:
                            article_elements = elements[:max_articles]
                            logger.info(f"Using fallback method, found {len(elements)} potential articles")
                            break
                    except:
                        continue
            
            for article in article_elements:
                try:
                    # Try different title selectors
                    title_selectors = [
                        "h3 a", "h2 a", "h4 a", "h1 a",  # Headers with links
                        "a",  # Any link
                        ".title a", ".headline a", ".news-title a",
                        "strong a", "b a"
                    ]
                    
                    title_element = None
                    for title_selector in title_selectors:
                        try:
                            title_element = article.find_element(By.CSS_SELECTOR, title_selector)
                            if title_element.text.strip():
                                break
                        except:
                            continue
                    
                    if not title_element:
                        # If no title found, try to get text from the article element itself
                        title_element = article
                    
                    title = title_element.text.strip()
                    if not title:
                        continue
                    
                    # Get link
                    if title_element.tag_name == "a":
                        link = title_element.get_attribute("href")
                    else:
                        # Try to find a link within the article
                        try:
                            link_element = article.find_element(By.CSS_SELECTOR, "a")
                            link = link_element.get_attribute("href")
                        except:
                            link = ""
                    
                    # Get summary if available
                    summary = ""
                    summary_selectors = [
                        "p", ".summary", ".description", ".content", ".text",
                        ".news-summary", ".article-summary"
                    ]
                    
                    for summary_selector in summary_selectors:
                        try:
                            summary_element = article.find_element(By.CSS_SELECTOR, summary_selector)
                            summary = summary_element.text.strip()
                            if summary and summary != title:
                                break
                        except:
                            continue
                    
                    # Get date if available - this is important for sorting by recency
                    date = datetime.now().isoformat()
                    date_selectors = [
                        "time", ".date", ".time", ".published", ".timestamp",
                        ".news-date", ".article-date", ".date-time"
                    ]
                    
                    for date_selector in date_selectors:
                        try:
                            date_element = article.find_element(By.CSS_SELECTOR, date_selector)
                            date_attr = date_element.get_attribute("datetime")
                            if date_attr:
                                date = date_attr
                                break
                            else:
                                date_text = date_element.text.strip()
                                if date_text:
                                    date = date_text
                                    break
                        except:
                            continue
                    
                    # Clean up the title (remove extra whitespace and newlines)
                    title = " ".join(title.split())
                    
                    article_data = {
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "date": date,
                        "source": "Yonhap News"
                    }
                    
                    articles.append(article_data)
                    logger.info(f"Extracted article: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"Failed to extract article from Yonhap News: {e}")
                    continue
            
            # Sort articles by date (newest first) if dates are available
            try:
                articles.sort(key=lambda x: x.get('date', ''), reverse=True)
                logger.info(f"Sorted {len(articles)} articles by date (newest first)")
            except:
                logger.warning("Could not sort articles by date")
                    
        except Exception as e:
            logger.error(f"Error crawling Yonhap News: {e}")
            
        return articles
    
    def crawl_all_sources(self, max_articles_per_source: int = 5) -> List[Dict]:
        """
        Crawl car news from all available sources
        
        Args:
            max_articles_per_source (int): Maximum articles per source
            
        Returns:
            List[Dict]: Combined list of news articles
        """
        all_articles = []
        
        # Crawl from different sources
        sources = [
            self.crawl_korean_news
        ]
        
        for source_func in sources:
            try:
                articles = source_func(max_articles_per_source)
                all_articles.extend(articles)
                logger.info(f"Successfully crawled {len(articles)} articles from {source_func.__name__}")
                time.sleep(2)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Failed to crawl from {source_func.__name__}: {e}")
                continue
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        self.news_data = all_articles
        logger.info(f"Total articles collected: {len(all_articles)}")
        
        return all_articles
    
    def save_to_json(self, filename: str = "car_news.json"):
        """
        Save news data to JSON file
        
        Args:
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "crawl_date": datetime.now().isoformat(),
                    "total_articles": len(self.news_data),
                    "articles": self.news_data
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"News data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")
    
    def save_to_csv(self, filename: str = "car_news.csv"):
        """
        Save news data to CSV file
        
        Args:
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if self.news_data:
                    writer = csv.DictWriter(f, fieldnames=self.news_data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.news_data)
            
            logger.info(f"News data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save CSV file: {e}")
    
    def save_to_txt(self, filename: str = "car_news.txt"):
        """
        Save news data to readable text file
        
        Args:
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"CAR NEWS REPORT\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Articles: {len(self.news_data)}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, article in enumerate(self.news_data, 1):
                    f.write(f"{i}. {article['title']}\n")
                    f.write(f"   Source: {article['source']}\n")
                    f.write(f"   Date: {article['date']}\n")
                    f.write(f"   Link: {article['link']}\n")
                    if article['summary']:
                        f.write(f"   Summary: {article['summary']}\n")
                    f.write("\n" + "-" * 80 + "\n\n")
            
            logger.info(f"News data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save text file: {e}")
    
    def display_news_summary(self):
        """Display a summary of collected news"""
        if not self.news_data:
            print("No news data available. Run crawl_all_sources() first.")
            return
        
        print(f"\n{'='*60}")
        print(f"CAR NEWS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Articles: {len(self.news_data)}")
        print(f"Sources: {set(article['source'] for article in self.news_data)}")
        print(f"Latest Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        for i, article in enumerate(self.news_data[:10], 1):  # Show first 10
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']} | Date: {article['date']}")
            if article['summary']:
                print(f"   {article['summary'][:100]}...")
            print()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            logger.info("WebDriver closed successfully")

def main():
    """Main function to run the car news crawler"""
    crawler = CarNewsCrawler(headless=True)
    
    try:
        # Crawl news from all sources
        print("Starting car news crawling...")
        articles = crawler.crawl_all_sources(max_articles_per_source=5)
        
        if articles:
            # Save to different formats
            crawler.save_to_json("car_news.json")
            crawler.save_to_csv("car_news.csv")
            crawler.save_to_txt("car_news.txt")
            
            # Display summary
            crawler.display_news_summary()
            
            print(f"\nCrawling completed! Found {len(articles)} articles.")
            print("Files created:")
            print("- car_news.json (JSON format)")
            print("- car_news.csv (CSV format)")
            print("- car_news.txt (Readable text format)")
        else:
            print("No articles were found.")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        
    finally:
        crawler.cleanup()

if __name__ == "__main__":
    main()