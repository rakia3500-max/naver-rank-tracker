import requests
import pandas as pd
import random
import time
from datetime import datetime

# 수집 설정
KEYWORDS = ["나의키워드1", "나의키워드2"] # 조사하고 싶은 키워드
TARGET_MID = "12345678" # 내 상품의 mid 번호

def get_rank(keyword):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    time.sleep(random.uniform(2, 5)) # 차단 방지용 휴식
    # 실제 수집 로직 (간소화 버전)
    rank = random.randint(1, 50) # 실제로는 여기서 네이버 페이지를 분석함
    return rank

def run():
    today = datetime.now().strftime("%Y-%m-%d")
    new_results = []
    for kw in KEYWORDS:
        r = get_rank(kw)
        new_results.append({"date": today, "keyword": kw, "rank": r})
    
    # 장부(CSV) 업데이트
    filename = "tracking_log.csv"
    try:
        df = pd.read_csv(filename)
        df = pd.concat([df, pd.DataFrame(new_results)])
    except:
        df = pd.DataFrame(new_results)
    
    df.drop_duplicates(subset=['date', 'keyword'], keep='last', inplace=True)
    df.to_csv(filename, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run()
