import requests
import pandas as pd
import datetime as dt
import time
import os
import streamlit as st

def get_rank(kw, cid, sec):
    """네이버 쇼핑 API 수집"""
    try:
        headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec}
        params = {"query": kw, "display": 100, "sort": "sim"}
        res = requests.get("https://openapi.naver.com/v1/search/shop.json", 
                           headers=headers, params=params, timeout=10)
        return res.json().get('items', []) if res.status_code == 200 else []
    except: return []

def run_automation():
    # 1. 시크릿에서 90개 키워드 및 API 키 로드
    try:
        naver_cid = st.secrets["NAVER_CLIENT_ID"]
        naver_csec = st.secrets["NAVER_CLIENT_SECRET"]
        raw_keywords = st.secrets["DEFAULT_KEYWORDS"]
        # 콤마나 줄바꿈으로 섞여있어도 잘 읽어오도록 처리
        keywords = [k.strip() for k in raw_keywords.replace('\n', ',').split(',') if k.strip()]
        
        brand1 = [x.strip() for x in st.secrets.get("MY_BRAND_1", "").split(',')]
        brand2 = [x.strip() for x in st.secrets.get("MY_BRAND_2", "").split(',')]
        my_brands = [b.replace(" ", "") for b in (brand1 + brand2) if b]
    except Exception as e:
        print(f"설정 로드 실패: {e}")
        return

    today = dt.date.today().isoformat()
    daily_results = []

    # 2. 90개 키워드 순회하며 조사
    print(f"🚀 {len(keywords)}개 키워드 조사 시작...")
    for idx, kw in enumerate(keywords):
        items = get_rank(kw, naver_cid, naver_csec)
        rank_found = 999 # 순위 밖 기본값
        
        if items:
            for r, item in enumerate(items, 1):
                mall_name = item['mallName'].replace(" ", "")
                if any(brand in mall_name for brand in my_brands):
                    rank_found = r
                    break
        
        daily_results.append({"date": today, "keyword": kw, "rank": rank_found})
        print(f"[{idx+1}/{len(keywords)}] {kw}: {rank_found}위")
        time.sleep(0.3) # API 차단 방지

    # 3. 기존 장부에 90개 결과 추가 저장
    file_name = "tracking_log.csv"
    new_df = pd.DataFrame(daily_results)
    
    if os.path.exists(file_name):
        old_df = pd.read_csv(file_name)
        # 예시 데이터(나의키워드)가 들어있는 기존 데이터는 삭제하고 새로 시작
        old_df = old_df[~old_df['keyword'].isin(["나의키워드1", "나의키워드2"])]
        final_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        final_df = new_df
    
    final_df.drop_duplicates(subset=['date', 'keyword'], keep='last', inplace=True)
    final_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print("✅ 모든 키워드 수집 완료!")

if __name__ == "__main__":
    run_automation()
