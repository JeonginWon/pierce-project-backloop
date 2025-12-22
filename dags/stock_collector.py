import mojito
from pykrx import stock
from datetime import datetime
import time
import requests
import urllib3
from config import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_broker():
    return mojito.KoreaInvestment(
        api_key=MOJITO_API_KEY,
        api_secret=MOJITO_API_SECRET,
        acc_no=MOJITO_ACC_NO,
        mock=True 
    )

def get_all_tickers():
    """KOSPI + KOSDAQ 전체 종목"""
    today = datetime.now().strftime("%Y%m%d")
    ticker_names = {}
    
    # KOSPI
    try:
        kospi_tickers = stock.get_market_ticker_list(today, market="KOSPI")
    except:
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")
    
    print(f"📊 KOSPI 종목: {len(kospi_tickers)}개")
    
    for ticker in kospi_tickers:
        try:
            ticker_names[ticker] = stock.get_market_ticker_name(ticker)
        except:
            ticker_names[ticker] = "Unknown"
    
    # KOSDAQ
    try:
        kosdaq_tickers = stock.get_market_ticker_list(today, market="KOSDAQ")
    except:
        kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")
    
    print(f"📊 KOSDAQ 종목: {len(kosdaq_tickers)}개")
    
    for ticker in kosdaq_tickers:
        try:
            ticker_names[ticker] = stock.get_market_ticker_name(ticker)
        except:
            ticker_names[ticker] = "Unknown"
    
    print(f"📊 전체: {len(ticker_names)}개\n")
    
    return ticker_names

def fetch_latest_bar(broker, ticker, name):
    """최신 1시간봉 조회"""
    
    max_retries = 5
    
    for attempt in range(max_retries):
        time.sleep(1.1)

        try:
            resp = broker.fetch_ohlcv(
                symbol=ticker,
                timeframe=TIMEFRAME, 
                adj_price=True
            )
            
            if not isinstance(resp, dict):
                print(f"⚠️ 이상한 응답 [{ticker}]: {resp}")
                time.sleep(2.0)
                continue

            msg_cd = resp.get('msg_cd', '')
            if msg_cd == 'EGW00201':
                print(f"🔥 과부하 감지 [{ticker}]: 5초 대기 ({attempt+1}/{max_retries})")
                time.sleep(5.0) 
                continue

            if 'output2' in resp:
                data_list = resp['output2']
                if data_list and len(data_list) > 0:
                    latest = data_list[0] 
                    current_dt = datetime.now().replace(minute=0, second=0, microsecond=0)
                    
                    return {
                        'symbol': ticker,
                        'record_time': current_dt,
                        'open': float(latest.get('stck_oprc', 0)),
                        'high': float(latest.get('stck_hgpr', 0)),
                        'low': float(latest.get('stck_lwpr', 0)),
                        'close': float(latest.get('stck_clpr', 0)),
                        'volume': int(latest.get('acml_vol', 0))
                    }
                else:
                    return None 
            
            msg1 = resp.get('msg1')
            if msg1:
                print(f"⚠️ API 메시지 [{ticker}]: {msg1}")
                time.sleep(1.0)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ce:
            print(f"🚨 [서버 차단 감지] 1분 대기 (Zombie Mode)")
            time.sleep(60.0)
            
        except Exception as e:
            print(f"⚠️ 예외 발생 [{ticker}]: {e}")
            time.sleep(1.0)
    
    print(f"❌ 최종 실패 [{ticker}/{name}]")
    return None

def collect_data():
    """수집 메인 함수 - KOSPI + KOSDAQ"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] KOSPI + KOSDAQ 1시간봉 수집 시작")
    print(f"{'='*60}\n")
    
    broker = get_broker()
    ticker_names = get_all_tickers()  # 👈 KOSPI + KOSDAQ
    
    print(f"총 {len(ticker_names)}개 종목 수집 시작...\n")
    
    results = []
    
    for idx, (ticker, name) in enumerate(ticker_names.items(), 1):
        result = fetch_latest_bar(broker, ticker, name)
        
        if result:
            results.append(result)
        
        # 진행 상황 출력 (50개마다)
        if idx % 50 == 0:
            print(f"  진행: {idx}/{len(ticker_names)} (성공: {len(results)}건)")

    print(f"\n{'='*60}")
    print(f"✅ 수집 완료: 총 {len(results)}건")
    print(f"{'='*60}\n")
    
    return results