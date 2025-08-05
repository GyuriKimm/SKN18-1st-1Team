import json
import sys
import os

# 현재 파일 기준 상위 디렉토리 (sources/)를 import 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database
from infiniti_FAQ import InfinitiFAQCrawler
from genesis_FAQ import GenesisFAQCrawler
from chevrolet_FAQ import ChevroletFAQCrawler


def get_config():
    with open("../config.json", encoding="UTF-8") as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    # 설정파일 가져오기
    config = get_config()

    ## Infiniti
    db_ins = Database(**config["database"])
    db_ins.connect()
    faq_crawler_ins = InfinitiFAQCrawler()
    infiniti_FAQ = faq_crawler_ins.run()
    db_ins.insert(infiniti_FAQ)
    db_ins.close_connection()

    ## Genesis
    db_ins = Database(**config["database"])
    genesis_ins = GenesisFAQCrawler()
    genesis_FAQ = genesis_ins.run()
    db_ins.connect()
    db_ins.insert(genesis_FAQ)
    db_ins.close_connection()

    ## CHEVROLET
    db_ins = Database(**config["database"])
    chevrolet_ins = ChevroletFAQCrawler()
    chevrolet_FAQ = chevrolet_ins.run()
    db_ins.connect()
    db_ins.insert(chevrolet_FAQ)
    db_ins.close_connection()
