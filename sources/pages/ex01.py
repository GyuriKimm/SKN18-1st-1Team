import streamlit as st
import pandas as pd

# 앱 제목
st.title("🚗 현대자동차 정보 조회 시스템")

# 사이드바 메뉴
menu = st.sidebar.selectbox(
    "메뉴를 선택하세요",
    ["홈", "등록 현황 조회", "기업 FAQ 보기"]
)

# 홈
if menu == "홈":
    st.subheader("📌 사용 안내")
    st.write("""
    이 시스템은 현대자동차의 등록 현황 및 자주 묻는 질문(FAQ)을 간단하게 확인할 수 있는 웹 앱입니다.
    
    좌측 메뉴에서 기능을 선택하세요.
    """)

# 등록 현황
elif menu == "등록 현황 조회":
    st.subheader("📊 등록 현황")
    st.metric("전체 등록 차량 수", "5,200,000대")
    st.metric("전기차 등록 수", "400,000대")
    st.metric("수소차 등록 수", "15,000대")
    
    st.divider()

    st.subheader("📈 연도별 등록 차량 수 (가상 데이터)")
    
    # 예시용 데이터프레임
    data = pd.DataFrame({
        '연도': [2019, 2020, 2021, 2022, 2023, 2024],
        '전체': [4200000, 4400000, 4700000, 4900000, 5100000, 5200000],
        '전기차': [100000, 150000, 220000, 300000, 370000, 400000],
        '수소차': [5000, 7000, 9000, 12000, 14000, 15000],
    }).set_index('연도')

    st.line_chart(data)

# 기업 FAQ
elif menu == "기업 FAQ 보기":
    st.subheader("❓ 현대자동차 기업 FAQ")
    
    with st.expander("Q1. 현대차는 어떤 차종을 생산하나요?"):
        st.write("A1. SUV, 세단, 전기차, 수소차 등 다양한 차종을 생산합니다.")
        
    with st.expander("Q2. 현대차의 본사는 어디인가요?"):
        st.write("A2. 서울시 서초구 양재동에 위치해 있습니다.")
        
    with st.expander("Q3. 전기차 배터리 수명은 어떻게 되나요?"):
        st.write("A3. 약 8년 또는 160,000km까지 보증됩니다.")