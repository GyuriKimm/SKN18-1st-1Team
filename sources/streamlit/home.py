import streamlit as st

# st.set_page_config(layout="wide", page_title="자동차 등록 현황")

st.sidebar.title("🚗 자동차 등록 현황")
category = st.sidebar.selectbox("카테고리를 선택하세요", ["홈", "그래프"])

if category == "홈":
    st.markdown("## 🚗 자동차 등록 현황")
    st.markdown("자동차 등록 관련 정보를 카테고리별로 확인할 수 있습니다.")
    st.markdown("- 연도별 등록 추이")
    st.markdown("- 지역별 등록 현황")
    st.markdown("- 차종별 비율 등")

elif category == "그래프":
    st.markdown("## 🚗 자동차 등록 현황 - 그래프 보기")

    st.markdown("### 📅 기간 선택 (년/월)")
    col1, col2 = st.columns(2)
    col1.text_input("시작", "202406")
    col2.text_input("종료", "202506")
    st.button("조회")

    st.markdown("### 📊 연도별 차량 등록 대수")
    st.line_chart(data=None)  # 더미 차트

    st.markdown("### 🗺️ 시도별 차량 등록 분포")
    st.map(data=None)  # 더미 지도
