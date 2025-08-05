from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from typing import List, Dict
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
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            logger.info("WebDriver closed successfully")