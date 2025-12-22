<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import VueApexCharts from 'vue3-apexcharts'

const router = useRouter()
const authStore = useAuthStore()

const popularStocks = ref([])
const stocks = ref([])
const watchlist = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const loading = ref(false)
let pollingTimer = null

const API_BASE = '/api'
const PAGE_SIZE = 15

// 시장 지수 데이터
const marketIndices = ref([
  { name: 'KOSPI', value: 2580.45, change_rate: 0.45, series: [{ data: [30, 40, 35, 50, 49, 60] }] },
  { name: 'KOSDAQ', value: 865.12, change_rate: -0.12, series: [{ data: [50, 40, 45, 30, 35, 20] }] }
])

const sparklineOptions = {
  chart: { sparkline: { enabled: true }, animations: { enabled: false } },
  stroke: { curve: 'smooth', width: 2 },
  colors: ['#3182f6'],
  tooltip: { enabled: false }
}

// --- 기능 로직 ---

const isWatched = (code) => watchlist.value.includes(code)

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

const fetchWatchlist = async () => {
  if (!authStore.isAuthenticated) return
  try {
    const res = await fetch(`${API_BASE}/watchlist/`, { credentials: 'include' })
    
    if (res.ok) {
      const data = await res.json()
      const items = data.results || data 

      if (Array.isArray(items)) {
        watchlist.value = items.map(item => item.ticker)
      } else {
        console.warn("예상치 못한 데이터 형식입니다.", data)
      }
    }
  } catch (e) {
    console.error("관심종목 로드 실패", e)
  }
}

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
      const chartSeries = [{ data: [30, 40, 35, 50, 49, 60] }]

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

const startPolling = () => {
  pollingTimer = setInterval(() => {
    fetchPopularStocks(); fetchStocks();
  }, 10000)
}

watch(() => authStore.isAuthenticated, (newVal) => {
  if (newVal) fetchWatchlist()
}, { immediate: true })

watch(searchQuery, () => { currentPage.value = 1; fetchStocks() })
watch(currentPage, fetchStocks)

onMounted(() => {
  if (authStore.isAuthenticated) fetchWatchlist()
  fetchPopularStocks(); fetchStocks(); startPolling()
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
            <span class="index-val">{{ index.value }}</span>
            <span :class="index.change_rate >= 0 ? 'red' : 'blue'" class="index-rate">
              {{ index.change_rate >= 0 ? '+' : '' }}{{ index.change_rate }}%
            </span>
          </div>
        </div>
        <div class="index-mini-chart">
          <VueApexCharts type="line" height="40" width="80" :options="sparklineOptions" :series="index.series" />
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
.dashboard-wrapper { background: #000; color: #fff; min-height: 100vh; padding-bottom: 50px; }
.red { color: #f04452; }
.blue { color: #3182f6; }

/* 레이아웃 */
.market-header { display: flex; gap: 15px; padding: 20px; max-width: 1200px; margin: 0 auto; border-bottom: 1px solid #1a1a1b; }
.index-card { background: #1a1a1b; padding: 15px 20px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; flex: 1; }
.main-content { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
.section-title { font-size: 18px; font-weight: 700; margin-bottom: 15px; }

/* 인기 종목 그리드 */
.popular-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 12px; margin-bottom: 40px; }
.pop-card { background: #1a1a1b; padding: 12px 16px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: background 0.2s; }
.pop-card:hover { background: #252526; }
.pop-left { display: flex; align-items: center; gap: 10px; }
.rank { font-size: 14px; font-weight: bold; color: #666; width: 15px; }
.stock-logo-fixed { width: 40px; height: 40px; border-radius: 50%; }

/* 전체 주식 테이블 */
.stock-table-header { display: grid; grid-template-columns: 100px 1.5fr 100px 120px 100px 100px 100px; padding: 10px 20px; font-size: 12px; color: #666; border-bottom: 1px solid #1a1a1b; }
.stock-table-row { display: grid; grid-template-columns: 100px 1.5fr 100px 120px 100px 100px 100px; align-items: center; padding: 15px 20px; border-bottom: 1px solid #1a1a1b; cursor: pointer; }
.stock-table-row:hover { background: #1a1a1b; }
.flex-items { display: flex; align-items: center; gap: 10px; }
.text-right { text-align: right; }
.font-bold { font-weight: 600; }
.text-gray { color: #919193; font-size: 13px; }

/* UI 요소 */
.star-btn { background: none; border: none; color: #ff9d00; font-size: 18px; cursor: pointer; }   
.num { color: #919193; font-weight: bold; width: 20px; text-align: center; }
.stock-logo-sm { width: 32px; height: 32px; border-radius: 50%; }
.ratio-bar-mini { width: 60px; height: 4px; background: #3182f6; border-radius: 2px; overflow: hidden; margin-left: auto; }
.buy-part { background: #f04452; height: 100%; }
.ratio-text { font-size: 10px; color: #666; margin-top: 4px; display: block; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 30px; }
.pagination button { background: #1a1a1b; border: none; color: #fff; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
.pagination button:disabled { opacity: 0.3; }
</style>