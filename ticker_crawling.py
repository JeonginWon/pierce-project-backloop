import FinanceDataReader as fdr

# KOSPI, KOSDAQ, KONEX 모두 포함된 KRX 전체 리스트
df = fdr.StockListing('KRX')

# 저장
df.to_csv('krx_ticker_list.csv', encoding='utf-8-sig')
print("저장 완료!")