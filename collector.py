import requests
import pandas as pd
import datetime as dt
import time
import os
import streamlit as st

# --- 환경 변수 vs 시크릿 자동 선택 함수 ---
def get_secret(key):
    # 1. GitHub Actions (환경 변수)에서 먼저 찾기
    value = os.environ.get(key)
    if value:
        return value
    # 2. 없으면 Streamlit Cloud (시크릿)에서 찾기
    if key in st.secrets:
        return st.secrets[key]
    return None

def get_rank(kw, cid, sec):
    try:
        headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec}
        params = {"query": kw, "display": 100, "sort": "sim"}
        res = requests.get("https://openapi.naver.com/v1/search/shop.json", 
                           headers=headers, params=params, timeout=10)
        return res.json().get('items', []) if res.status_code == 200 else []
    except: return []

def run_automation():
    # 1. 설정값 로드 (개선된 방식)
    naver_cid = get_secret("NAVER_CLIENT_ID")
    naver_csec = get_secret("NAVER_CLIENT_SECRET")
    raw_keywords = get_secret("DEFAULT_KEYWORDS")
    
    brand1_raw = get_secret("MY_BRAND_1")
    brand2_raw = get_secret("MY_BRAND_2")

    # 설정값이 없으면 중단 (에러 방지)
    if not (naver_cid and raw_keywords):
        print("❌ 설정값을 찾을 수 없습니다. (Secrets/Env 확인 필요)")
        return

    # 키워드 및 브랜드 리스트 변환
    keywords = [k.strip() for k in raw_keywords.replace('\n', ',').split(',') if k.strip()]
    
    brand1 = [x.strip() for x in (brand1_raw or "").split(',')]
    brand2 = [x.strip() for x in (brand2_raw or "").split(',')]
    my_brands = [b.replace(" ", "") for b in (brand1 + brand2) if b]

    today = dt.date.today().isoformat()
    daily_results = []

    print(f"🚀 {len(keywords)}개 키워드 조사 시작...")

    # 2. 수집 루프
    for idx, kw in enumerate(keywords):
        items = get_rank(kw, naver_cid, naver_csec)
        rank_found = 999
        
        if items:
            for r, item in enumerate(items, 1):
                mall_name = item['mallName'].replace(" ", "")
                if any(brand in mall_name for brand in my_brands):
                    rank_found = r
                    break
        
        daily_results.append({"date": today, "keyword": kw, "rank": rank_found})
        # 로그에 진행 상황 출력
        print(f"[{idx+1}/{len(keywords)}] {kw}: {rank_found}위")
        time.sleep(0.3)

    # 3. 파일 저장 (파일이 없으면 새로 생성)
    file_name = "tracking_log.csv"
    new_df = pd.DataFrame(daily_results)
    
    # 기존 파일이 있으면 합치고, 없으면 새로 만듦
    if os.path.exists(file_name):
        try:
            old_df = pd.read_csv(file_name)
            final_df = pd.concat([old_df, new_df], ignore_index=True)
        except:
            final_df = new_df
    else:
        final_df = new_df
    
    final_df.drop_duplicates(subset=['date', 'keyword'], keep='last', inplace=True)
    final_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"✅ 수집 완료! {file_name} 저장됨.")

if __name__ == "__main__":
    run_automation()
