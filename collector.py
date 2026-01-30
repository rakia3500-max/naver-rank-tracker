import requests
import pandas as pd
import datetime as dt
import time
import os
import streamlit as st

def get_rank(kw, cid, sec):
    """네이버 쇼핑 API를 통해 검색 결과 100개를 가져옵니다."""
    try:
        headers = {
            "X-Naver-Client-Id": cid,
            "X-Naver-Client-Secret": sec
        }
        params = {"query": kw, "display": 100, "sort": "sim"}
        res = requests.get("https://openapi.naver.com/v1/search/shop.json", 
                           headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            print(f"API Error ({kw}): {res.status_code}")
            return []
    except Exception as e:
        print(f"Network Error ({kw}): {e}")
        return []

def run_automation():
    # 1. 시크릿 설정값 로드
    try:
        naver_cid = st.secrets["NAVER_CLIENT_ID"]
        naver_csec = st.secrets["NAVER_CLIENT_SECRET"]
        
        # 90개 키워드 리스트 생성
        raw_keywords = st.secrets["DEFAULT_KEYWORDS"]
        keywords = [k.strip() for k in raw_keywords.replace('\n', ',').split(',') if k.strip()]
        
        # 브랜드 판별 리스트 (공백 제거하여 준비)
        brand1 = [x.strip().replace(" ", "") for x in st.secrets.get("MY_BRAND_1", "").split(',')]
        brand2 = [x.strip().replace(" ", "") for x in st.secrets.get("MY_BRAND_2", "").split(',')]
        my_brands = brand1 + brand2
        
    except Exception as e:
        print(f"시크릿 로드 실패: {e}")
        return

    today = dt.date.today().isoformat()
    daily_results = []

    print(f"🚀 {today} 순위 수집 시작 (총 {len(keywords)}개 키워드)")

    # 2. 키워드별 순위 추적
    for idx, kw in enumerate(keywords):
        items = get_rank(kw, naver_cid, naver_csec)
        rank_found = 999  # 기본값 (순위 밖)
        
        if items:
            for r, item in enumerate(items, 1):
                mall_name = item['mallName'].replace(" ", "")
                # 내 브랜드가 몰 이름에 포함되어 있는지 확인
                if any(brand in mall_name for brand in my_brands if brand):
                    rank_found = r
                    break
        
        daily_results.append({"date": today, "keyword": kw, "rank": rank_found})
        print(f"[{idx+1}/{len(keywords)}] {kw}: {rank_found}위")
        
        # API 과부하 방지 및 차단 회피를 위한 미세 지연
        time.sleep(0.2)

    # 3. 데이터 저장 (CSV 누적)
    file_name = "tracking_log.csv"
    new_df = pd.DataFrame(daily_results)
    
    if os.path.exists(file_name):
        try:
            old_df = pd.read_csv(file_name)
            final_df = pd.concat([old_df, new_df], ignore_index=True)
        except:
            final_df = new_df
    else:
        final_df = new_df
    
    # 중복 제거 (날짜와 키워드가 같은 데이터는 최신본 유지)
    final_df.drop_duplicates(subset=['date', 'keyword'], keep='last', inplace=True)
    
    # 저장 (Excel 호환을 위한 utf-8-sig)
    final_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"✅ 수집 완료 및 {file_name} 저장 성공")

if __name__ == "__main__":
    run_automation()
