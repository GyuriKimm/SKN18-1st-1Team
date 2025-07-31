import sys
import os
import json

# 현재 파일 기준 상위 디렉토리 (sources/)를 import 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pymysql
import pandas as pd

from database import Database

# 설정파일 가져오는 함수
def get_config():
    with open("../config.json", encoding="UTF-8") as f:
        config = json.load(f)
    return config

# 데이터베이스에서 데이터 읽어오는 함수
def fetch_faq_data():
    config = get_config()
    database_ins = Database(**config["database"])
    database_ins.connect()
    result = database_ins.read_data()
    database_ins.close_connection()
    return pd.DataFrame(result)

def show_banner(faq_brand):
    # 브랜드별 배너 이미지 매핑
    banner_map = {
        "INFINITI FAQ": "./image/infiniti.png",
        "GENESIS FAQ": "./image/genesis.png"
    }
    # 배너 이미지 출력
    st.image(banner_map.get(faq_brand, "./image/infiniti.png"))

# ✅ 랜덤 FAQ 보여주는 함수
def show_random_faq(faq_df):
    st.markdown("### 🔀 추천 질문")
    if len(faq_df) > 0:
        sample_df = faq_df.sample(n=min(10, len(faq_df))) # 무작위로 일부 행을 가져옴
        for _, row in sample_df.iterrows(): # sample_df의 각 행을 순회하며 실행
            with st.expander(f"❓ {row[0]}"): # 질문
                st.write(f"💬 {row[1]}") # 답변
    else: # FAQ 데이터가 없을때
        st.warning("FAQ 데이터가 없습니다.")

# ✅ 카테고리 기반 FAQ 보여주는 함수
def show_category_faq(faq_df, selected_category):
    st.markdown(f"### 📌 '{selected_category}' 관련 질문")

    filtered_df = faq_df[faq_df[2] == selected_category]

    if filtered_df.empty:
        st.info("선택한 카테고리에 대한 질문이 없습니다.")
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"❓ {row[0]}"):
                st.write(f"💬 {row[1]}")
    

if __name__=="__main__":
    # Streamlit 설정
    st.set_page_config(layout="wide", page_title="FAQ")
    st.sidebar.title("❓ FAQ")

    # 브랜드 선택
    faq_brand = st.sidebar.selectbox("브랜드를 선택하세요", ["INFINITI FAQ", "GENESIS FAQ"])
    show_banner(faq_brand)

    # 전체 FAQ 데이터 가져오기
    faq_df = fetch_faq_data()

    # 🔎 선택된 브랜드에 해당하는 데이터만 필터링
    company_name = faq_brand.split()[0].upper()  # 'INFINITI FAQ' -> 'INFINITI'
    faq_df = faq_df[faq_df[3].str.upper() == company_name]

    # 페이지 제목 출력
    st.title(f"❓ {faq_brand}")

    # 카테고리 목록 만들기 (중복 제거)
    all_categories = faq_df[2].dropna().unique().tolist()
    selected_category = st.selectbox(" 카테고리를 선택하세요: ", ["카테고리를 선택하세요"] + all_categories)
    st.markdown("---")
    
    # 카테고리 선택 분기
    if selected_category == "카테고리를 선택하세요":
        show_random_faq(faq_df)
    else:
        show_category_faq(faq_df, selected_category)