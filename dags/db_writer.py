import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from config import DJANGO_DB

def save_to_db(data_list):
    """PostgreSQL에 직접 저장"""
    if not data_list:
        return 0, 0
    
    conn = psycopg2.connect(**DJANGO_DB)
    cur = conn.cursor()
    
    saved = 0
    updated = 0
    
    try:
        for data in data_list:
            # UPSERT 쿼리
            cur.execute("""
                INSERT INTO rag_stockdailyprice 
                    (symbol, trade_date, open, high, low, close, volume, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, trade_date) 
                DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
                RETURNING (xmax = 0) AS inserted
            """, (
                data['symbol'],
                data['trade_date'],
                data['open'],
                data['high'],
                data['low'],
                data['close'],
                data['volume'],
                datetime.now()
            ))
            
            result = cur.fetchone()
            if result and result[0]:
                saved += 1
            else:
                updated += 1
        
        conn.commit()
        print(f"✅ DB 저장: 신규 {saved}개, 업데이트 {updated}개")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ DB 저장 실패: {e}")
        raise
    finally:
        cur.close()
        conn.close()
    
    return saved, updated