import mojito
from pykrx import stock
from datetime import datetime, date
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random # 랜덤 딜레이용
# ㅈㄴ바보임? import DAG를 안해놓고 DAG에 안뜬다고 물어보냐........
from config import *



def get_broker():
    # mock=True는 모의투자, False는 실전투자입니다.
    # 실시간 시세를 받으려면 실전계좌(mock=False)가 필요할 수 있습니다.
    return mojito.KoreaInvestment(
        api_key=MOJITO_API_KEY,
        api_secret=MOJITO_API_SECRET,
        acc_no=MOJITO_ACC_NO,
        mock=True 
    )

def get_kospi_tickers():
    """코스피 전체 종목"""
    # 주말/공휴일에는 데이터가 안 올 수 있으므로 가장 최근 영업일 로직이 좋으나,
    # 일단 오늘 날짜로 시도합니다.
    today = datetime.now().strftime("%Y%m%d")
    try:
        tickers = stock.get_market_ticker_list(today, market="KOSPI")
    except:
        # 에러 발생 시(장 시작 전 등) 어제 날짜 등으로 fallback 하는 로직 추천
        # 여기서는 일단 빈 리스트 반환 방지
        tickers = stock.get_market_ticker_list(market="KOSPI")
    
    ticker_names = {}
    for ticker in tickers:
        try:
            ticker_names[ticker] = stock.get_market_ticker_name(ticker)
        except:
            ticker_names[ticker] = "Unknown"
    
    return ticker_names

def fetch_latest_bar(broker, ticker, name):
    """최신 1시간봉 조회"""
    # 스레드 안에서 딜레이
    time.sleep(random.uniform(0.1, 0.3)) 

    try:
        resp = broker.fetch_ohlcv(
            symbol=ticker,
            timeframe=TIMEFRAME, 
            adj_price=True
        )
        
        # 응답 검증 (딕셔너리 키 확인)
        # output2에 데이터 리스트가 들어옵니다.
        if resp and isinstance(resp, dict) and 'output2' in resp:
            data_list = resp['output2']
            
            if data_list and len(data_list) > 0:
                # 최신 데이터 (보통 0번 인덱스가 최신일 수 있으나 확인 필요, 여기선 시간 역순이라 가정하고 0번 가져옴)
                # 만약 시간 순서가 과거->미래라면 -1 (마지막)을 가져와야 함.
                # 한국투자증권 API는 보통 [0]이 가장 최근(오늘) 데이터입니다.
                latest = data_list[0] 
                
                # 날짜 처리 (형식: YYYYMMDD, HHMMSS)
                # output2의 날짜 키는 보통 'stck_bsop_date'(일봉) 또는 'stck_cntg_hour'(분봉) 등 다양함
                # 여기선 안전하게 현재 날짜로 처리하거나, 응답 키를 확인해야 함.
                
                return {
                    'symbol': ticker,
                    'trade_date': datetime.now().date(), # 일단 수집 시점 날짜 사용
                    'open': float(latest.get('stck_oprc', 0)), # 시가
                    'high': float(latest.get('stck_hgpr', 0)), # 고가
                    'low': float(latest.get('stck_lwpr', 0)),  # 저가
                    'close': float(latest.get('stck_prpr', 0)), # 종가 (현재가)
                    'volume': int(latest.get('cntg_vol', 0))   # 거래량
                }
            
    except Exception as e:
        # 너무 많은 에러 로그 방지를 위해 주석 처리하거나 필요시 출력
        # print(f"⚠️ Error {ticker} ({name}): {e}")
        pass
    
    return None

def collect_data():
    """수집 메인 함수"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] 1시간봉 수집 시작")
    print(f"{'='*60}\n")
    
    broker = get_broker()
    ticker_names = get_kospi_tickers()
    
    print(f"총 {len(ticker_names)}개 종목 수집 시작...")
    
    results = []
    
    # API 제한 고려: max_workers를 너무 높이지 마세요 (5~10 추천)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_latest_bar, broker, ticker, name): ticker
            for ticker, name in ticker_names.items()
        }
        
        for idx, future in enumerate(as_completed(futures), 1):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Thread Error: {e}")
            
            if idx % 50 == 0:
                print(f"  진행중: {idx}/{len(ticker_names)} (성공: {len(results)}건)")
    
    print(f"\n✅ 수집 완료: 총 {len(results)}개 데이터 준비됨")
    
    # ⭐ [핵심 수정] 반드시 데이터를 반환해야 합니다!
    return results