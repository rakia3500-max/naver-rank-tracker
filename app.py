import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 네이버 순위 트렌드")

try:
    df = pd.read_csv("tracking_log.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    kws = st.multiselect("키워드 선택", df['keyword'].unique(), default=df['keyword'].unique()[0])
    filtered = df[df['keyword'].isin(kws)]
    
    fig = px.line(filtered, x='date', y='rank', color='keyword', markers=True)
    fig.update_yaxes(autorange="reversed", title="순위") # 1위가 위로 가게
    st.plotly_chart(fig, use_container_width=True)
except:
    st.write("아직 데이터가 없습니다. 내일 아침에 다시 확인하세요!")
