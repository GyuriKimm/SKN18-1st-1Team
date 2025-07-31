import streamlit as st
import pymysql
import pandas as pd

# DB 연결 함수
def get_faq_data():
    connection = pymysql.connect(
        host='localhost',
        user='urstory',
        password='1234',
        database='examplesdb',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT question, answer, category, company FROM companyFAQ")
        result = cursor.fetchall()
    connection.close()
    return pd.DataFrame(result)


# Streamlit 설정
st.set_page_config(layout="wide", page_title="FAQ")
st.sidebar.title("❓ FAQ")

# 브랜드별 배너 이미지 매핑
banner_map = {
    "INFINITI FAQ": "./image/infiniti.png",
    "GENESIS FAQ": "./image/genesis.png"
}

# 브랜드 선택
faq_brand = st.sidebar.selectbox("브랜드를 선택하세요", ["INFINITI FAQ", "GENESIS FAQ"])

# 배너 이미지 출력
st.image(banner_map.get(faq_brand, "./image/infiniti.png"))

# 전체 FAQ 데이터 가져오기
faq_df = get_faq_data()

# 🔎 선택된 브랜드에 해당하는 데이터만 필터링
company_name = faq_brand.split()[0].upper()  # 'INFINITI FAQ' -> 'INFINITI'
faq_df = faq_df[faq_df['company'].str.upper() == company_name]

# 페이지 제목 출력
st.title(f"❓ {faq_brand}")

# 카테고리 목록 만들기 (중복 제거)
all_categories = faq_df['category'].dropna().unique().tolist()
selected_category = st.selectbox(" 카테고리를 선택하세요: ", ["카테고리를 선택하세요"] + all_categories)
st.markdown("---")

# 카테고리 선택 분기
if selected_category == "카테고리를 선택하세요":
    st.markdown("### 🔀 추천 질문")

    if len(faq_df) > 0:
        sample_df = faq_df.sample(n=min(10, len(faq_df))) # 무작위로 일부 행을 가져옴
        for _, row in sample_df.iterrows(): # sample_df의 각 행을 순회하며 실행
            with st.expander(f"❓ {row['question']}"): # 질문
                st.write(f"💬 {row['answer']}") # 답변
    else: # FAQ 데이터가 없을때
        st.warning("FAQ 데이터가 없습니다.")
else:
    st.markdown(f"### 📌 '{selected_category}' 관련 질문")

    filtered_df = faq_df[faq_df['category'] == selected_category]

    if filtered_df.empty:
        st.info("선택한 카테고리에 대한 질문이 없습니다.")
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"❓ {row['question']}"):
                st.write(f"💬 {row['answer']}")
