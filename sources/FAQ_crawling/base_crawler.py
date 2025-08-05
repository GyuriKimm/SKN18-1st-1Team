from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class BaseCrawler:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def load_page(self, url: str, wait_class: str, timeout: int = 10):
        """URL을 로드하고 특정 클래스가 등장할 때까지 기다림"""
        self.driver.get(url)
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, wait_class))
        )

    def get_parsed_soup(self) -> BeautifulSoup:
        """현재 페이지의 HTML을 BeautifulSoup 객체로 반환"""
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def quit(self):
        self.driver.quit()
