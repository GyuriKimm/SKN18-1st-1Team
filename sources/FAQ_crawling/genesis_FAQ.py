from bs4 import BeautifulSoup
from base_crawler import BaseCrawler


class GenesisFAQCrawler(BaseCrawler):
    company = "GENESIS"
    def extract_faq(self, soup: BeautifulSoup):
        """페이지 구조에서 카테고리, 질문, 답변 추출"""
        faq_list = []
        groups = soup.find_all("div", class_="cp-faq__accordion-item")
        for group in groups:
            category_tag = group.find("strong", class_= "accordion-label")
            question_tag = group.find("p", class_= "accordion-title")
            answer_tag = group.find("div", class_ = "accordion-panel-inner")
            category = category_tag.get_text(strip=True)
            question = question_tag.get_text(strip=True)
            paragraphs =answer_tag.find_all("p")
            answer = "\n".join(p.get_text(strip=True) for p in paragraphs)
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
            self.load_page("https://www.genesis.com/kr/ko/support/faq.html", "cp-faq__accordion")
            soup = self.get_parsed_soup()
            faq_list = self.extract_faq(soup)
            faq_list = self.map_category(faq_list)
            return faq_list
        except Exception as e:
            print(f"[FAQ 크롤링 실패] {e}")
        finally:
            self.quit()