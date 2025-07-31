from bs4 import BeautifulSoup
from base_crawler import BaseCrawler


class InfinitiFAQCrawler(BaseCrawler):
    company = "INFINITI"
    def extract_faq(self, soup: BeautifulSoup):
        """페이지 구조에서 카테고리, 질문, 답변 추출"""
        faq_list = []
        groups = soup.find_all("div", class_="contentZone section")
        for group in groups:
            # 카테고리 추출
            category = "None"
            heading_tag = group.find("div", class_="heliostext section")
            if heading_tag:
                # class 속성이 없는 span 태그만 필터링
                category_span = next(
                    (span for span in heading_tag.find_all("span") if span.has_attr("class")),
                    None
                )
                if category_span:
                    category = category_span.get_text(strip=True)

            # ✅ FAQ 항목들 순회
            faq_items = group.find_all("div", class_="accordion-group")
            for item in faq_items:
                question_tag = item.find("h2", class_="accordion-title")
                answer_tag = item.find("div", class_="accordion-panel")

                if question_tag and answer_tag:
                    question = question_tag.get_text(strip=True)
                    paragraphs = answer_tag.find_all("p")
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
            # 페이지를 로드
            self.load_page("https://www.infiniti.com/regions/ko-kr/faqs.html", "accordion-title")
            # 페이지의 구조를 가져옴
            soup = self.get_parsed_soup()
            # 페이지 구조에서 카테고리, 질문, 답변 추출
            faq_list = self.extract_faq(soup)
            faq_list = self.map_category(faq_list)
            return faq_list
        except Exception as e:
            print(f"[FAQ 크롤링 실패] {e}")
        finally:
            self.quit()
