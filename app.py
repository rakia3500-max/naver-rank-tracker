import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="쇼핑 통합 관제 트렌드", layout="wide")
st.title("📈 키워드별 순위 트렌드 (1~100위 집중)")

file_name = "tracking_log.csv"

# 파일이 없을 때 예외 처리
if not os.path.exists(file_name):
    st.warning("아직 데이터 파일(tracking_log.csv)이 없습니다.")
    st.info("GitHub Actions가 실행될 때까지 기다리거나, 수동으로 실행해 주세요.")
    st.stop()

# 데이터 로드
df = pd.read_csv(file_name)
df['date'] = pd.to_datetime(df['date'])

# --- 사이드바 설정 ---
st.sidebar.header("🔍 필터 옵션")

# 1. 키워드 선택 (기본값: 데이터에 있는 첫 번째 키워드)
all_keywords = df['keyword'].unique()
if len(all_keywords) > 0:
    default_kw = [all_keywords[0]]
else:
    default_kw = []

selected_kws = st.sidebar.multiselect(
    "확인할 키워드 선택 (여러 개 가능)", 
    all_keywords, 
    default=default_kw
)

# 2. 기간 선택
period = st.sidebar.radio("조회 기간", ["최근 7일", "최근 30일", "전체"], index=1)

# --- 데이터 필터링 ---
# 날짜 필터
if period == "최근 7일":
    start_date = pd.Timestamp.now() - pd.Timedelta(days=7)
    df = df[df['date'] >= start_date]
elif period == "최근 30일":
    start_date = pd.Timestamp.now() - pd.Timedelta(days=30)
    df = df[df['date'] >= start_date]

# 키워드 필터
if selected_kws:
    plot_df = df[df['keyword'].isin(selected_kws)]
else:
    plot_df = pd.DataFrame() # 선택 안 하면 빈 화면

# --- 차트 그리기 ---
if not plot_df.empty:
    # 999위(순위 밖)인 데이터는 차트에서 보기 싫다면 아예 뺄 수도 있지만,
    # "순위 밖으로 밀려났다"는 걸 보여주기 위해 105위 정도로 치환해서 바닥에 깔아주는 게 좋습니다.
    # 여기서는 시각적 왜곡을 막기 위해 105위로 값을 임시 변경하여 그립니다.
    display_df = plot_df.copy()
    display_df.loc[display_df['rank'] > 100, 'rank'] = 105 

    fig = px.line(display_df, x='date', y='rank', color='keyword', markers=True,
                  title="일별 순위 변화 (1위 ~ 100위)",
                  hover_data={"rank": True, "date": True})

    # [핵심 수정] Y축 설정: 범위를 1~105로 고정하고, 눈금을 10단위로 설정
    fig.update_yaxes(
        range=[105, 0],       # 0이 맨 위, 105가 맨 아래 (역순)
        tickmode='linear',    # 눈금 간격 균등하게
        dtick=10,             # 10단위로 눈금 표시 (1, 11, 21...)
        title="순위 (낮을수록 상위권)"
    )
    
    # X축 날짜 형식 예쁘게
    fig.update_xaxes(
        dtick="D1",           # 하루 단위로 표시 (데이터가 많으면 자동 조정됨)
        tickformat="%m-%d",   # 월-일 형식
        title="날짜"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 상세 데이터 표 ---
    with st.expander("📊 상세 데이터 보기 (원본)"):
        # 표에서는 999위 그대로 보여줌 (팩트 확인용)
        st.dataframe(plot_df.sort_values(by=['date', 'keyword'], ascending=[False, True]))

else:
    st.info("👈 왼쪽 사이드바에서 키워드를 선택해 주세요.")
