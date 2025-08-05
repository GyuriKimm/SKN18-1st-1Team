import re

from bs4 import BeautifulSoup
from base_crawler import BaseCrawler


class chevroletFAQCrawler(BaseCrawler):
    company = "CHEVROLET"
    def extract_faq(self, soup: BeautifulSoup):
        """쉐보레 FAQ 페이지 구조에서 카테고리, 질문, 답변 추출"""
        faq_list = []
        # 카테고리별로 FAQ가 구분되어 있음
        groups = soup.find_all("div", class_="q-mod q-mod-expander q-expander q-expander-default q-closed-xs q-closed-sm q-closed-med q-closed-lg q-closed-xl")
        for group in groups:
            question_tag = group.find("h6", class_="q-button-text q-headline-text")
            answer_tag = group.find("div", class_="q-text q-body1 q-invert")
            question = question_tag.get_text(strip=True)
            paragraphs = answer_tag.find_all("p")
            answer = "\n".join(p.get_text(strip=True) for p in paragraphs)
            match = re.match(r'\[(.*?)\]\s*(.*)', question)
            if match:
                category = match.group(1)
                question = match.group(2)
            faq_list.append([category, question, answer])
        return faq_list
    
    def map_category(self, faq_list):
        """데이터베이스 카테고리와 홈페이지에 나와있는 카테고리를 맵핑"""
        mapped_faq_list = []
        for category, question, answer in faq_list:
            mapped_faq_list.append((self.company, category, question, answer))
        return mapped_faq_list

    def run(self):
        """실행함수"""
        try:
            # 쉐보레 FAQ 페이지를 로드
            self.load_page("https://www.chevrolet.co.kr/faq", "col-con")
            soup = self.get_parsed_soup()
            faq_list = self.extract_faq(soup)
            faq_list = self.map_category(faq_list)
            return faq_list
        except Exception as e:
            print(f"[FAQ 크롤링 실패] {e}")
        finally:
            self.quit()