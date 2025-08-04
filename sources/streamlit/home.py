import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
from plotly.subplots import make_subplots
import json
import datetime
import requests


API_KEY = "HZXgpAiQBEp9H9gcEzePi/qvWpMqa2Vav8W9Jaounr+S2hvMRYMdBlOqdWrVp81amfnm6W0B1IhPD+t9DyQAfQ=="

def get_dbconfig():
    with open("../config.json", encoding="UTF-8") as f:
        config = json.load(f)
    return config["database"]

def get_connection():
    db_config = get_dbconfig()
    return pymysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["db"],
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )

def run_query(query, params=None):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
    conn.close()
    return df

# 날씨 API 호출 함수
def get_weather():
    now = datetime.datetime.now()
    base_date = now.strftime('%Y%m%d')
    base_time = (now - datetime.timedelta(hours=1)).strftime('%H') + "00"
    nx, ny = 58, 125  # 서울 금천구

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    params = {
        'serviceKey': API_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny
    }

    response = requests.get(url, params=params)
    items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    data = {}

    for item in items:
        cat = item.get('category')
        val = item.get('obsrValue')
        if cat == 'T1H':
            data['기온'] = f"{val}°C"
        elif cat == 'REH':
            data['습도'] = f"{val}%"
        elif cat == 'WSD':
            data['풍속'] = f"{val} m/s"
        elif cat == 'RN1':
            data['강수량'] = f"{val} mm"

    return data

# -- CSS 스타일 --
st.markdown("""
    <style>
    h2 {
        color: #003366;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 0.3em;
    }
    h3 {
        color: #005599;
    }
    .dataframe {
        border: 2px solid #005599 !important;
        border-radius: 8px;
        padding: 8px;
    }
    .stat-box {
        background-color: #eaf3ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stat-label {
        font-weight: 600;
        color: #004080;
        margin-bottom: 5px;
    }
    .stat-value {
        font-size: 1.8rem;
        color: #002050;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout="wide")
st.sidebar.title("🚗 자동차 등록 현황")
category = st.sidebar.selectbox("카테고리를 선택하세요", ["홈", "시도별/차종별/용도별 분석", "전기차/충전소 분석"])


if category == "홈":
    st.title("🏠 메인 대시보드")
    st.markdown("---")
    col_news, col_weather = st.columns([1, 1])
    # 📰 자동차 관련 뉴스
    with col_news:
        st.markdown("### 📰 자동차 관련 뉴스")
        st.markdown("#### 대통령실 '자동차 관세 15%…쌀·소고기 시장 추가 개방 않기로'")
        st.write("미국과 한국 간 관세 협상에서 상호 관세를 25%에서 15%로 낮추기로 합의했습니다. "
                "8월 1일부터 적용되며, 자동차가 주요 수출 품목으로 포함되었습니다.")

    # 🌤️ 오늘의 날씨
    with col_weather:
        st.markdown("### 🌤️ 오늘의 날씨")
        st.markdown("**금천구 가산동**")
        
        try:
            weather = get_weather()
            with st.container():
                st.markdown(f"""
                    - 기온: {weather.get('기온', '정보 없음')}
                    - 습도: {weather.get('습도', '-')}
                    - 풍속: {weather.get('풍속', '-')}
                    - 강수량: {weather.get('강수량', '-')}
                    """)
        except Exception as e:
            st.warning(f"날씨 데이터를 불러오는 데 실패했습니다: {e}")
        
    st.markdown("---")
    st.markdown("## 🚘 대한민국 자동차 데이터 요약")
    # 📊 최신 전체 차량 등록 수
    car_query = """
        SELECT year, SUM(registered_cars) AS total
        FROM car_registration_by_region
        GROUP BY year
        ORDER BY year DESC
        LIMIT 2
    """
    car_df = run_query(car_query)
    car_latest = car_df.iloc[0]['total']
    car_prev = car_df.iloc[1]['total']
    car_delta = round(((car_latest - car_prev) / car_prev) * 100, 2)

    # ⚡ 전기차 등록 수
    ev_query = """
        SELECT date_recorded, sum_total
        FROM elec_car_registration_by_region
        ORDER BY date_recorded DESC
        LIMIT 2
    """
    ev_df = run_query(ev_query)
    ev_latest = ev_df.iloc[0]['sum_total']
    ev_prev = ev_df.iloc[1]['sum_total']
    ev_delta = round(((ev_latest - ev_prev) / ev_prev) * 100, 2)

    # 🔌 충전소 수
    charger_query = """
        SELECT date_recorded, SUM(sum_total) AS total
        FROM charging_station_by_region
        GROUP BY date_recorded
        ORDER BY date_recorded DESC
        LIMIT 2
    """
    chg_df = run_query(charger_query)
    chg_latest = chg_df.iloc[0]['total']
    chg_prev = chg_df.iloc[1]['total']
    chg_delta = round(((chg_latest - chg_prev) / chg_prev) * 100, 2)
    
    # 📊 메트릭 박스 표시
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="전체 등록 차량 수", value=f"{car_latest:,} 만대", delta=f"{car_delta:+.1f}% YoY")
        ev_per_charger = round(chg_latest / ev_latest, 2)
        st.metric("전기차 1기당 충전소 수", value=f"{ev_per_charger} 대/기")
    with col2:
        st.metric(label="전기차 등록 수", value=f"{ev_latest:,} 대", delta=f"{ev_delta:+.1f}% YoY")
        
    with col3:
        st.metric(label="충전소 수", value=f"{chg_latest:,} 기", delta=f"{chg_delta:+.1f}% YoY")

    st.markdown("""
    ---
    ### 🧭 **요약 인사이트**

    - 대한민국에는 현재 **{:,}대의 자동차**가 등록되어 있습니다.
    - 이 중 전기차 비중은 약 {:.1f}%**에 불과하며, 최근 **{:+.1f}% 증가**했습니다.
    - 충전소도 함께 증가하고 있지만 **지역 편차**가 큽니다.
    ---
    """.format(car_latest, (ev_latest / (car_latest*10000)) * 100, ev_delta))


elif category == "시도별/차종별/용도별 분석":
    st.markdown("## 🚗 자동차 등록 현황 - 그래프 보기")
    years = list(range(2000, 2025))
    col1, col2, _ = st.columns([1, 1, 6])  # 총 8 너비 중 앞 2개만 사용
    with col1:
        start_year = st.selectbox("시작 연도", options=years, index=years.index(2023))
    with col2:
        end_year = st.selectbox("종료 연도", options=years, index=years.index(2024))

    if start_year >= end_year:
        st.error("⚠ 종료 연도는 시작 연도보다 작을 수 없습니다.")

    tab1, tab2, tab3 = st.tabs(["📍 지역별", "🚙 차종별", "🛠️ 용도별"])

    #################
    # 📍 지역별 탭
    #################
    with tab1:
        st.subheader("📍 시도별 차량 등록 대수")

        region_query = """
            SELECT r.name AS region, cr.year, cr.registered_cars
            FROM car_registration_by_region cr
            JOIN region r ON cr.region_id = r.region_id
            WHERE cr.year BETWEEN %s AND %s
        """
        df = run_query(region_query, (start_year, end_year))

        yearly_sum_query = """
            SELECT year, SUM(registered_cars) AS total_registered
            FROM car_registration_by_region
            WHERE year BETWEEN %s AND %s
            GROUP BY year
            ORDER BY year
        """
        yearly_sum_df = run_query(yearly_sum_query, (start_year, end_year))

        if not df.empty and not yearly_sum_df.empty:
            df['registered_cars'] = pd.to_numeric(df['registered_cars'], errors='coerce')
            df['year'] = pd.to_numeric(df['year'], errors='coerce')

            pivot = df.pivot_table(index="year", columns="region", values="registered_cars", aggfunc='sum')

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown("### 📊 지역별 등록 대수")
                fig = px.line(pivot, x=pivot.index, y=pivot.columns,
                              labels={'value': '등록 대수', 'year': '연도'},
                              title='시도별 연도별 차량 등록 대수')
                fig.update_layout(legend_title_text='지역', hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📈 연도별 등록 차량 총합")
                fig_sum = px.line(yearly_sum_df, x='year', y='total_registered',
                                  labels={'total_registered': '총 등록 대수', 'year': '연도'},
                                  title='연도별 등록 차량 총합')
                st.plotly_chart(fig_sum, use_container_width=True)

                with st.expander("📋 원본 데이터 보기"):
                    st.dataframe(df.reset_index(drop=True))
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv,
                        file_name="car_by_region.csv",
                        mime="text/csv"
                    )

            with col2:
                st.markdown("### 📊 통계")
                total_cars = int(df['registered_cars'].sum())
                avg_length = round(df.groupby('year')['registered_cars'].sum().mean())
                max_value = int(df['registered_cars'].max())
                max_year = int(df.loc[df['registered_cars'].idxmax(), 'year'])

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">총 등록 차량 수</div>
                    <div class="stat-value">{total_cars:,} 만대</div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">연도별 평균 등록 수</div>
                    <div class="stat-value">{avg_length:,} 만대</div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">최대 등록 대수</div>
                    <div class="stat-value">{max_value:,} 만대 ({max_year}년)</div>
                </div>""", unsafe_allow_html=True)

        else:
            st.info("해당 기간에 데이터가 없습니다.")

    #################
    # 🚙 차종별 탭
    #################
    with tab2:
        st.subheader("🚘 차종별 차량 등록 대수")

        type_query = """
            SELECT year, passenger_car, van_car, truck_car, special_car
            FROM car_type_registration
            WHERE year BETWEEN %s AND %s
        """
        df = run_query(type_query, (start_year, end_year))

        yearly_sum_query = """
            SELECT year, 
                (passenger_car + van_car + truck_car + special_car) AS total_registered
            FROM car_type_registration
            WHERE year BETWEEN %s AND %s
            ORDER BY year
        """
        yearly_sum_df = run_query(yearly_sum_query, (start_year, end_year))

        if not df.empty and not yearly_sum_df.empty:
            df.set_index("year", inplace=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                fig = px.line(df, x=df.index, y=df.columns,
                              labels={'value': '등록 대수', 'year': '연도'},
                              title='차종별 차량 등록 대수 추이')
                fig.update_layout(legend_title_text='차종', hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📈 연도별 등록 차량 총합")
                fig_sum = px.line(yearly_sum_df, x='year', y='total_registered',
                                  labels={'total_registered': '총 등록 대수', 'year': '연도'},
                                  title='연도별 등록 차량 총합')
                st.plotly_chart(fig_sum, use_container_width=True)

                with st.expander("📋 원본 데이터 보기"):
                    st.dataframe(df.reset_index(drop=True))
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv,
                        file_name="car_by_type.csv",
                        mime="text/csv"
                    )

            with col2:
                st.markdown("### 📊 통계")
                total_cars = int(df.sum().sum())
                avg_cars = round(df.sum(axis=1).mean())
                max_value = int(df.sum(axis=1).max())
                max_year = int(df.sum(axis=1).idxmax())

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">총 등록 차량 수</div>
                    <div class="stat-value">{total_cars:,} 만대</div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">연도별 평균 등록 수</div>
                    <div class="stat-value">{avg_cars:,} 만대</div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">최대 등록 대수</div>
                    <div class="stat-value">{max_value:,} 만대 ({max_year}년)</div>
                </div>""", unsafe_allow_html=True)

        else:
            st.info("데이터가 없습니다.")

    #################
    # 🛠️ 용도별 탭
    #################
    with tab3:
        st.subheader("🔧 용도별 차량 등록 대수")

        usage_query = """
            SELECT year, official, private, business
            FROM car_use_type_registration
            WHERE year BETWEEN %s AND %s
        """
        df = run_query(usage_query, (start_year, end_year))

        yearly_sum_query = """
            SELECT year, (official + private + business) AS total_registered
            FROM car_use_type_registration
            WHERE year BETWEEN %s AND %s
            ORDER BY year
        """
        yearly_sum_df = run_query(yearly_sum_query, (start_year, end_year))

        if not df.empty and not yearly_sum_df.empty:
            df.set_index("year", inplace=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                fig = px.line(df, x=df.index, y=df.columns,
                              labels={'value': '등록 대수', 'year': '연도'},
                              title='용도별 차량 등록 대수 추이')
                fig.update_layout(legend_title_text='용도', hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📈 연도별 등록 차량 총합")
                fig_sum = px.line(yearly_sum_df, x='year', y='total_registered',
                                  labels={'total_registered': '총 등록 대수', 'year': '연도'},
                                  title='연도별 등록 차량 총합')
                st.plotly_chart(fig_sum, use_container_width=True)

                with st.expander("📋 원본 데이터 보기"):
                    st.dataframe(df.reset_index(drop=True))
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv,
                        file_name="car_by_use.csv",
                        mime="text/csv"
                    )

            with col2:
                st.markdown("### 📊 통계")
                total_cars = int(df.sum().sum())
                avg_cars = round(df.sum(axis=1).mean())
                max_value = int(df.sum(axis=1).max())
                max_year = int(df.sum(axis=1).idxmax())

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">총 등록 차량 수</div>
                    <div class="stat-value">{total_cars:,} 만대</div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">연도별 평균 등록 수</div>
                    <div class="stat-value">{avg_cars:,} 만대</div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="stat-box">
                    <div class="stat-label">최대 등록 대수</div>
                    <div class="stat-value">{max_value:,} 만대 ({max_year}년)</div>
                </div>""", unsafe_allow_html=True)

        else:
            st.info("데이터가 없습니다.")
elif category == "전기차/충전소 분석":

    st.subheader("⚡ 전기차 & 충전소 데이터 분석")

    years = list(range(2017, 2026))
    col1, col2, _ = st.columns([1, 1, 6])  # 총 8 너비 중 앞 2개만 사용
    with col1:
        start_year = st.selectbox("시작 연도", options=years, index=years.index(2023))
    with col2:
        end_year = st.selectbox("종료 연도", options=years, index=years.index(2024))

    if start_year >= end_year:
        st.error("⚠ 종료 연도는 시작 연도보다 작을 수 없습니다.")
    tab1, tab2, tab3 = st.tabs(["🚗 전기차 등록 추이", "🔌 충전소 구축 추이", "📊 지역별 전기차/충전소 비율"])

    # 🚗 전기차 등록 추이
    with tab1:
        query = """
            SELECT date_recorded, sum_total
            FROM elec_car_registration_by_region
            WHERE YEAR(date_recorded) BETWEEN %s AND %s
            ORDER BY date_recorded
        """
        df_ev = run_query(query, (start_year, end_year))

        if not df_ev.empty:
            df_ev['year'] = pd.to_datetime(df_ev['date_recorded']).dt.year
            df_ev = df_ev.groupby('year')['sum_total'].sum().reset_index()

            fig = px.line(df_ev, x='year', y='sum_total',
                        title="🚗연도별 전기차 등록 추이",
                        labels={'sum_total': '전기차 등록 수', 'year': '연도'})
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📋 원본 데이터 보기"):
                st.dataframe(df_ev)
        else:
            st.warning("전기차 등록 데이터를 불러올 수 없습니다.")

    # 🔌 충전소 구축 추이
    with tab2:
        query = """
            SELECT date_recorded, charging_speed, sum_total
            FROM charging_station_by_region
            WHERE YEAR(date_recorded) BETWEEN %s AND %s
        """
        df_chg = run_query(query, (start_year, end_year))

        if not df_chg.empty:
            df_chg['year'] = pd.to_datetime(df_chg['date_recorded']).dt.year
            df_chg_sum = df_chg.groupby(['year', 'charging_speed'])['sum_total'].sum().reset_index()

            fig = px.line(df_chg_sum, x='year', y='sum_total', color='charging_speed',
                        title="🔌충전속도별 충전소 구축 추이",
                        labels={'sum_total': '충전기 수', 'year': '연도', 'charging_speed': '충전속도'})
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📋 원본 데이터 보기"):
                st.dataframe(df_chg_sum)
        else:
            st.warning("충전소 데이터를 불러올 수 없습니다.")
    # 📊 지역별 전기차/충전소 비율
    with tab3:

        # 📅 연도 기준 날짜 변환
        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        # 전기차 데이터 가져오기
        ev_query = """
            SELECT * FROM elec_car_registration_by_region
            WHERE date_recorded BETWEEN %s AND %s
        """
        ev_df = run_query(ev_query, (start_date, end_date))

        # 충전소 데이터 가져오기
        chg_query = """
            SELECT * FROM charging_station_by_region
            WHERE date_recorded BETWEEN %s AND %s
        """
        chg_df = run_query(chg_query, (start_date, end_date))

        if not ev_df.empty and not chg_df.empty:
            latest_ev = ev_df.sort_values("date_recorded", ascending=False).iloc[0]
            latest_chg = chg_df.sort_values("date_recorded", ascending=False).iloc[0]

            ev_regions = set(ev_df.columns) - {"id", "date_recorded", "sum_total", "created_at"}
            chg_regions = set(chg_df.columns) - {"id", "date_recorded", "charging_speed", "sum_total", "created_at"}
            common_regions = sorted(ev_regions & chg_regions)

            # 최신 비율 계산
            ratio_data = []
            for region in common_regions:
                ev_count = latest_ev.get(region, 0)
                chg_count = latest_chg.get(region, 0)
                if chg_count and ev_count is not None:
                    ratio = round(ev_count / chg_count, 2)
                    ratio_data.append({
                        "지역": region,
                        "전기차 수": int(ev_count),
                        "충전소 수": int(chg_count),
                        "전기차/충전소 비율": ratio
                    })

            df_ratio = pd.DataFrame(ratio_data)

            # 연도별 충전소 비율 계산
            chg_percent_query = f"""
                SELECT date_recorded, {', '.join(common_regions)}, sum_total
                FROM charging_station_by_region
                WHERE YEAR(date_recorded) BETWEEN %s AND %s
            """
            percent_df = run_query(chg_percent_query, (start_year, end_year))

            if not percent_df.empty:
                percent_df['year'] = pd.to_datetime(percent_df['date_recorded']).dt.year

                yearly_ratios = []
                for year, group in percent_df.groupby("year"):
                    total = group[common_regions].sum().sum()
                    year_data = {"year": year}
                    for region in common_regions:
                        region_sum = group[region].sum()
                        ratio = round((region_sum / total) * 100, 2) if total else 0
                        year_data[region] = ratio
                    yearly_ratios.append(year_data)

                df_yearly_ratio = pd.DataFrame(yearly_ratios).sort_values("year")
                df_ratio_melted = df_yearly_ratio.melt(id_vars="year", var_name="지역", value_name="충전소 비율(%)")

                # ---- 📊 통합 subplot ----
                fig_combined = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=False,
                    vertical_spacing=0.15,
                    subplot_titles=[
                        "① 최신 지역별 전기차/충전소 비율 (대/기)",
                        "② 연도별 지역 충전소 비율 변화 (%)"
                    ]
                )

                # (1) 상단: 막대그래프
                fig_bar = px.bar(df_ratio, x="지역", y="전기차/충전소 비율")
                for trace in fig_bar.data:
                    fig_combined.add_trace(trace, row=1, col=1)

                # (2) 하단: 선그래프
                fig_line = px.line(df_ratio_melted, x="year", y="충전소 비율(%)", color="지역", markers=True)
                for trace in fig_line.data:
                    fig_combined.add_trace(trace, row=2, col=1)

                # 레이아웃 설정
                fig_combined.update_layout(
                    height=800,
                    title_text="📊 지역별 전기차 충전소 비율 통합 분석",
                    showlegend=True,
                    hovermode="x unified"
                )

                # 출력
                st.plotly_chart(fig_combined, use_container_width=True)

                # 데이터 보기
                with st.expander("📋 원본 데이터 보기"):
                    st.markdown("#### ✅ 최신 비율 데이터")
                    st.dataframe(df_ratio)
                    st.markdown("#### 📈 연도별 비율 데이터")
                    st.dataframe(df_yearly_ratio)
            else:
                st.warning("연도별 충전소 비율 데이터를 가져오지 못했습니다.")
        else:
            st.warning("선택한 기간에 해당하는 데이터가 부족합니다.")



