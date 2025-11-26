import mojito
from pykrx import stock
from datetime import datetime
import time
# import random  <-- 고정 딜레이를 쓸 거라 random은 이제 필요 없습니다.
from config import *

def get_broker():
    return mojito.KoreaInvestment(
        api_key=MOJITO_API_KEY,
        api_secret=MOJITO_API_SECRET,
        acc_no=MOJITO_ACC_NO,
        mock=True 
    )

def get_kospi_tickers():
    """코스피 전체 종목"""
    today = datetime.now().strftime("%Y%m%d")
    try:
        tickers = stock.get_market_ticker_list(today, market="KOSPI")
    except:
        tickers = stock.get_market_ticker_list(market="KOSPI")
    
    ticker_names = {}
    for ticker in tickers:
        try:
            ticker_names[ticker] = stock.get_market_ticker_name(ticker)
        except:
            ticker_names[ticker] = "Unknown"
    
    return ticker_names

def fetch_latest_bar(broker, ticker, name):
    """최신 1시간봉 조회 (재시도 로직 포함)"""
    
    max_retries = 3  # 최대 3번까지 재시도
    
    for attempt in range(max_retries):
        # ⚠️ [핵심 수정 1] 딜레이 설정
        # 초당 2건 제한 -> 1건당 최소 0.5초 필요. 안전하게 0.6초 대기.
        time.sleep(0.6)

        try:
            resp = broker.fetch_ohlcv(
                symbol=ticker,
                timeframe=TIMEFRAME, 
                adj_price=True
            )
            
            # ⚠️ [핵심 수정 2] API 제한 에러(EGW00201) 발생 시 재시도
            if isinstance(resp, dict):
                msg_cd = resp.get('msg_cd', '')
                if msg_cd == 'EGW00201':
                    print(f"⏳ 제한 걸림 [{ticker}]: 1초 대기 후 재시도 ({attempt+1}/{max_retries})...")
                    time.sleep(1.0) # 벌칙 시간: 1초 쉬고 다시 시도
                    continue # 다음 loop로 넘어감 (재시도)

            # 정상 데이터 처리
            if resp and isinstance(resp, dict) and 'output2' in resp:
                data_list = resp['output2']
                
                if data_list and len(data_list) > 0:
                    latest = data_list[0] 
                    return {
                        'symbol': ticker,
                        'trade_date': datetime.now().date(),
                        'open': float(latest.get('stck_oprc', 0)),
                        'high': float(latest.get('stck_hgpr', 0)),
                        'low': float(latest.get('stck_lwpr', 0)),
                        'close': float(latest.get('stck_prpr', 0)),
                        'volume': int(latest.get('cntg_vol', 0))
                    }
                else:
                    # 데이터가 비어있으면(정상이지만 거래 없는 등) 재시도 할 필요 없음
                    return None 
            
        except Exception as e:
            print(f"⚠️ 실패 [{ticker}/{name}]: {e}")
            # 네트워크 에러 등은 재시도 해볼만 함
            time.sleep(1.0)
    
    return None

def collect_data():
    """수집 메인 함수"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] 1시간봉 수집 시작 (초당 2건 제한 모드)")
    print(f"{'='*60}\n")
    
    broker = get_broker()
    ticker_names = get_kospi_tickers()
    
    print(f"총 {len(ticker_names)}개 종목 수집 시작...")
    
    results = []
    
    for idx, (ticker, name) in enumerate(ticker_names.items(), 1):
        
        result = fetch_latest_bar(broker, ticker, name)
        
        if result:
            results.append(result)
        
        if idx % 50 == 0:
            print(f"  진행중: {idx}/{len(ticker_names)} (성공: {len(results)}건)")

    print(f"\n✅ 수집 완료: 총 {len(results)}개 데이터 준비됨")
    
    return results