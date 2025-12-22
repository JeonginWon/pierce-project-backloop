<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import VueApexCharts from 'vue3-apexcharts'

const router = useRouter()
const authStore = useAuthStore()

const popularStocks = ref([])
const stocks = ref([])
const watchlist = ref([]) // 관심종목 ticker 문자열 배열
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const loading = ref(false)
let pollingTimer = null

const API_BASE = '/api'
const PAGE_SIZE = 15

// --- 시장 지수 데이터 상태 ---
const marketIndices = ref([
  { name: 'KOSPI', value: 0, change_rate: 0, series: [{ data: [] }] },
  { name: 'KOSDAQ', value: 0, change_rate: 0, series: [{ data: [] }] }
])

const sparklineOptions = {
  chart: { sparkline: { enabled: true }, animations: { enabled: false } },
  stroke: { curve: 'smooth', width: 2 },
  colors: ['#3182f6'],
  tooltip: { enabled: false }
}

// --- 기능 로직 ---

const isWatched = (code) => watchlist.value.includes(code)

// 시장 지수 패칭 (백엔드 MarketIndexViewSet 호출)
const fetchMarketIndices = async () => {
  try {
    const res = await fetch(`${API_BASE}/market-indices/`)
    if (res.ok) {
      const data = await res.json()
      marketIndices.value = data
    }
  } catch (e) {
    console.error("지수 로드 실패:", e)
  }
}

// 관심종목 토글
const toggleWatchlist = async (event, stock) => {
  event.stopPropagation()
  if (!authStore.isAuthenticated) return alert('로그인이 필요합니다.')

  try {
    const res = await fetch(`${API_BASE}/watchlist/toggle/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ ticker: stock.code })
    })
    
    if (res.ok) {
      const result = await res.json()
      if (result.added) {
        if (!watchlist.value.includes(stock.code)) watchlist.value.push(stock.code)
      } else {
        watchlist.value = watchlist.value.filter(c => c !== stock.code)
      }
    }
  } catch (e) { console.error("관심종목 토글 실패", e) }
}

// 관심종목 리스트 불러오기
const fetchWatchlist = async () => {
  if (!authStore.isAuthenticated) return
  try {
    const res = await fetch(`${API_BASE}/watchlist/`, { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      const items = data.results || data 
      if (Array.isArray(items)) {
        watchlist.value = items.map(item => item.ticker)
      }
    }
  } catch (e) { console.error("관심종목 로드 실패", e) }
}

// 인기 종목 불러오기
const fetchPopularStocks = async () => {
  const TRENDING_TICKERS = [
    { code: '005930', name: '삼성전자' },
    { code: '000660', name: 'SK하이닉스' },
    { code: '373220', name: 'LG에너지솔루션' },
    { code: '035720', name: '카카오' },
    { code: '005380', name: '현대차' },
    { code: '035420', name: 'NAVER' }
  ]
  try {
    const results = await Promise.all(TRENDING_TICKERS.map(async (item) => {
      const res = await fetch(`${API_BASE}/stock-prices/summary/?ticker=${item.code}`)
      const summary = res.ok ? await res.json() : { last_price: 0, change_rate: 0 }
      return { ...item, ...summary }
    }))
    popularStocks.value = results
  } catch (e) { console.error(e) }
}

const formatTradingValue = (value) => {
  if (value >= 1) {
    return `${value}억원`
  } else if (value > 0) {
    return '1억 이하'
  } else {
    return '1억 이하'
  }
}

// 전체 주식 리스트 불러오기
const fetchStocks = async () => {
  if (currentPage.value === 1) loading.value = true
  try {
    let url = `${API_BASE}/companies/?page=${currentPage.value}`
    if (searchQuery.value) url += `&search=${encodeURIComponent(searchQuery.value)}`
    const res = await fetch(url)
    const data = await res.json()
    const companyList = data.results || data
    totalPages.value = Math.ceil((data.count || 1) / PAGE_SIZE)

    const fetchedStocks = await Promise.all(companyList.map(async (company) => {
      const sumRes = await fetch(`${API_BASE}/stock-prices/summary/?ticker=${company.code}`)
      const summary = sumRes.ok ? await sumRes.json() : { last_price: 0, change_rate: 0, volume: 0 }
      
      // 거래대금 계산 (숫자 타입 보장)
      const volume = Number(summary.volume) || 0
      const price = Number(summary.last_price) || 0
      const tradingValue = Math.floor((volume * price) / 100000000)
      
      const buyRatio = summary.buy_ratio || Math.floor(Math.random() * 40) + 30 
      const chartSeries = [{ data: [30, 40, 35, 50, 49, 60] }] // 임시 차트 데이터

      return { ...company, ...summary, tradingValue, buyRatio, chartSeries }
    }))

    // 👇 정렬 로직 강화
    stocks.value = fetchedStocks.sort((a, b) => {
      const valA = Number(a.tradingValue) || 0
      const valB = Number(b.tradingValue) || 0
      
      // 1. 거래대금 내림차순 정렬
      if (valB !== valA) {
        return valB - valA
      }
      // 2. 거래대금이 같으면 이름순 정렬 (순서 고정을 위해)
      return a.name.localeCompare(b.name)
    })
    
  } catch (e) {
    console.error("데이터 로드 실패", e)
  } finally {
    loading.value = false
  }
}

// 실시간 폴링 (10초 주기)
const startPolling = () => {
  pollingTimer = setInterval(() => {
    fetchMarketIndices(); 
    fetchPopularStocks(); 
    fetchStocks();
  }, 10000)
}

// 인증 상태 변화 감시
watch(() => authStore.isAuthenticated, (newVal) => {
  if (newVal) fetchWatchlist()
}, { immediate: true })

watch(searchQuery, () => { currentPage.value = 1; fetchStocks() })
watch(currentPage, fetchStocks)

onMounted(() => {
  if (authStore.isAuthenticated) fetchWatchlist()
  fetchMarketIndices()
  fetchPopularStocks()
  fetchStocks()
  startPolling()
})

onUnmounted(() => { if (pollingTimer) clearInterval(pollingTimer) })
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="market-header">
      <div v-for="index in marketIndices" :key="index.name" class="index-card">
        <div class="index-info">
          <span class="index-name">{{ index.name }}</span>
          <div class="index-val-row">
            <span class="index-val">{{ index.value.toLocaleString() }}</span>
            <span :class="index.change_rate >= 0 ? 'red' : 'blue'" class="index-rate">
              {{ index.change_rate >= 0 ? '+' : '' }}{{ index.change_rate }}%
            </span>
          </div>
        </div>
        <div class="index-mini-chart">
          <VueApexCharts 
            v-if="index.series[0].data.length > 0"
            type="line" height="40" width="80" 
            :options="sparklineOptions" :series="index.series" 
          />
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="popular-section">
        <h3 class="section-title">지금 뜨는 인기 종목</h3>
        <div class="popular-grid">
          <div v-for="(stock, idx) in popularStocks" :key="stock.code" class="pop-card" @click="router.push(`/stock/${stock.code}`)">
            <div class="pop-left">
              <span class="rank">{{ idx + 1 }}</span>
              <button class="star-btn" @click="toggleWatchlist($event, stock)">
                {{ isWatched(stock.code) ? '★' : '☆' }}
              </button>
              <img :src="`https://static.toss.im/png-icons/securities/icn-sec-fill-${stock.code}.png`" class="stock-logo-fixed" />
              <div class="stock-name-box">
                <span class="name">{{ stock.name }}</span>
                <span class="price">{{ Number(stock.last_price || 0).toLocaleString() }}원</span>
              </div>
            </div>
            <div class="pop-right">
              <span :class="['rate-text', stock.change_rate >= 0 ? 'red' : 'blue']">
                {{ stock.change_rate > 0 ? '+' : '' }}{{ stock.change_rate }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <section class="all-stocks-section">
        <div class="list-header">
          <h3 class="section-title">전체 주식</h3>
          <input v-model="searchQuery" placeholder="종목명 검색" class="search-input" />
        </div>

        <div class="stock-table-header">
          <span class="col-rank">순위</span>
          <span class="col-name">종목</span>
          <span class="col-chart text-center">차트</span>
          <span class="col-price text-right">현재가</span>
          <span class="col-rate text-right">등락률</span>
          <span class="col-value text-right">거래대금</span>
          <span class="col-ratio text-right">매수비율</span>
        </div>
        
        <div class="stock-list-container shadow-sm">
          <div v-for="(stock, idx) in stocks" :key="stock.code" class="stock-table-row" @click="router.push(`/stock/${stock.code}`)">
            <div class="col-rank flex-items">
              <button class="star-btn" @click="toggleWatchlist($event, stock)">{{ isWatched(stock.code) ? '★' : '☆' }}</button>
              <span class="num">{{ (currentPage - 1) * PAGE_SIZE + idx + 1 }}</span>
            </div>
            <div class="col-name flex-items">
              <img :src="`https://static.toss.im/png-icons/securities/icn-sec-fill-${stock.code}.png`" class="stock-logo-sm" />
              <!-- 👇 기업명만 표시 (ticker 제거) -->
              <div class="name-box">
                <span class="name">{{ stock.name }}</span>
              </div>
            </div>
            <div class="col-chart">
              <VueApexCharts type="line" height="30" width="80" :options="sparklineOptions" :series="stock.chartSeries" />
            </div>
            <div class="col-price text-right font-bold">{{ Number(stock.last_price || 0).toLocaleString() }}원</div>
            <div class="col-rate text-right" :class="stock.change_rate >= 0 ? 'red' : 'blue'">{{ stock.change_rate > 0 ? '+' : '' }}{{ stock.change_rate }}%</div>
            <!-- 👇 포맷 함수 적용 -->
            <div class="col-value text-right text-gray">{{ formatTradingValue(stock.tradingValue) }}</div>
            <div class="col-ratio flex-column text-right">
              <div class="ratio-bar-mini"><div class="buy-part" :style="{ width: stock.buyRatio + '%' }"></div></div>
              <span class="ratio-text">{{ stock.buyRatio }} : {{ 100 - stock.buyRatio }}</span>
            </div>
          </div>
        </div>

        <div class="pagination">
          <button @click="currentPage--" :disabled="currentPage === 1">이전</button>
          <span class="page-num">{{ currentPage }} / {{ totalPages }}</span>
          <button @click="currentPage++" :disabled="currentPage === totalPages">다음</button>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dashboard-wrapper { background: #000; color: #fff; min-height: 100vh; padding-bottom: 50px; font-family: sans-serif; }
.red { color: #f04452; }
.blue { color: #3182f6; }

/* 지수 영역 */
.market-header { display: flex; gap: 15px; padding: 20px; max-width: 1200px; margin: 0 auto; border-bottom: 1px solid #1a1a1b; }
.index-card { background: #1a1a1b; padding: 15px 20px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; flex: 1; border: 1px solid #222; }
.index-name { color: #919193; font-size: 14px; font-weight: bold; }
.index-val { font-size: 20px; font-weight: 800; display: block; margin-top: 4px; }
.index-rate { font-size: 14px; font-weight: bold; }

.main-content { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
.section-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; }

/* 인기 종목 그리드 */
.popular-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 12px; margin-bottom: 40px; }
.pop-card { background: #1a1a1b; padding: 16px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: 0.2s; border: 1px solid #222; }
.pop-card:hover { background: #252526; }
.pop-left { display: flex; align-items: center; gap: 12px; }
.rank { font-size: 15px; font-weight: bold; color: #666; width: 15px; }
.stock-logo-fixed { width: 44px; height: 44px; border-radius: 50%; }
.stock-name-box .name { display: block; font-weight: bold; font-size: 16px; }
.stock-name-box .price { color: #919193; font-size: 13px; }
.rate-text { font-weight: bold; font-size: 16px; }

/* 전체 주식 리스트 */
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.search-input { background: #1a1a1b; border: 1px solid #333; color: #fff; padding: 10px 16px; border-radius: 12px; width: 250px; }
.stock-table-header { display: grid; grid-template-columns: 100px 1.5fr 100px 120px 100px 100px 100px; padding: 10px 20px; font-size: 12px; color: #666; }
.stock-table-row { display: grid; grid-template-columns: 100px 1.5fr 100px 120px 100px 100px 100px; align-items: center; padding: 18px 20px; border-bottom: 1px solid #1a1a1b; cursor: pointer; transition: 0.2s; }
.stock-table-row:hover { background: #111; }

.flex-items { display: flex; align-items: center; gap: 10px; }
.text-right { text-align: right; }
.font-bold { font-weight: 600; }
.text-gray { color: #919193; font-size: 13px; }

/* UI 요소 */
.star-btn { background: none; border: none; color: #ff9d00; font-size: 18px; cursor: pointer; }   
.num { color: #919193; font-weight: bold; width: 20px; text-align: center; }
.stock-logo-sm { width: 32px; height: 32px; border-radius: 50%; }
.ratio-bar-mini { width: 60px; height: 4px; background: #3182f6; border-radius: 2px; overflow: hidden; margin-left: auto; }
.col-ratio { display: flex; flex-direction: column; align-items: flex-end; }
.ratio-bar-mini { width: 60px; height: 4px; background: #3182f6; border-radius: 2px; overflow: hidden; margin-bottom: 4px; }
.buy-part { background: #f04452; height: 100%; }
.ratio-text { font-size: 10px; color: #666; }

/* 공통 UI */
.star-btn { background: none; border: none; color: #ff9d00; font-size: 20px; cursor: pointer; transition: transform 0.2s; }
.star-btn:hover { transform: scale(1.2); }
.stock-logo-sm { width: 36px; height: 36px; border-radius: 50%; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 40px; }
.pagination button { background: #1a1a1b; border: 1px solid #333; color: #fff; padding: 10px 20px; border-radius: 12px; cursor: pointer; font-weight: bold; }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }

@media (max-width: 768px) {
  .popular-grid { grid-template-columns: 1fr; }
  .stock-table-header, .stock-table-row { grid-template-columns: 80px 1fr 100px; }
  .col-chart, .col-value, .col-ratio { display: none; }
}
</style>