<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import VueApexCharts from 'vue3-apexcharts'

const router = useRouter()
const authStore = useAuthStore()

const popularStocks = ref([])
const stocks = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const loading = ref(false)
let pollingTimer = null

// 시장 지수 데이터
const marketIndices = ref([
  { name: 'KOSPI', value: 2580.45, change_rate: 0.45, series: [{ data: [2550, 2560, 2555, 2570, 2580] }] },
  { name: 'KOSDAQ', value: 865.12, change_rate: -0.12, series: [{ data: [870, 868, 865, 866, 865] }] }
])

const API_BASE = '/api'
const PAGE_SIZE = 15

// ✅ 1. 인기 종목 6개로 수정
const TRENDING_TICKERS = [
  { code: '005930', name: '삼성전자' },
  { code: '000660', name: 'SK하이닉스' },
  { code: '373220', name: 'LG에너지솔루션' }, // 추가
  { code: '035720', name: '카카오' },
  { code: '005380', name: '현대차' },
  { code: '035420', name: 'NAVER' }
]

const miniChartOptions = {
  chart: { sparkline: { enabled: true }, animations: { enabled: false } },
  stroke: { curve: 'smooth', width: 2 },
  colors: ['#3182f6'],
  tooltip: { enabled: false }
}

const fetchPopularStocks = async () => {
  try {
    const results = await Promise.all(TRENDING_TICKERS.map(async (item) => {
      const res = await fetch(`${API_BASE}/stock-prices/summary/?ticker=${item.code}`)
      const summary = res.ok ? await res.json() : {}
      return { ...item, ...summary }
    }))
    popularStocks.value = results
  } catch (e) { console.error(e) }
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

    stocks.value = await Promise.all(companyList.map(async (company) => {
      const sumRes = await fetch(`${API_BASE}/stock-prices/summary/?ticker=${company.code}`)
      const summary = sumRes.ok ? await sumRes.json() : {}
      return { ...company, ...summary }
    }))
  } finally { loading.value = false }
}

const startPolling = () => {
  pollingTimer = setInterval(() => {
    fetchPopularStocks(); fetchStocks();
  }, 10000)
}

watch(searchQuery, () => { currentPage.value = 1; fetchStocks() })
watch(currentPage, fetchStocks)

onMounted(() => { fetchPopularStocks(); fetchStocks(); startPolling(); })
onUnmounted(() => { if (pollingTimer) clearInterval(pollingTimer) })

// --- 추가된 상태 및 로직 ---
const watchlist = ref([]) // 사용자의 관심 종목 코드 리스트

// 관심 종목 여부 확인
const isWatched = (code) => watchlist.value.includes(code)

// 관심 종목 리스트 가져오기
const fetchWatchlist = async () => {
  if (!authStore.isAuthenticated) return
  try {
    const res = await fetch(`${API_BASE}/watchlist/`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` } // 토큰 필요 시
    })
    if (res.ok) {
      const data = await res.json()
      watchlist.value = data.map(item => item.code)
    }
  } catch (e) { console.error("관심종목 로드 실패", e) }
}

// 관심 종목 토글 (추가/삭제)
const toggleWatchlist = async (event, stock) => {
  event.stopPropagation() // 카드 클릭(상세 이동) 이벤트 전파 방지
  if (!authStore.isAuthenticated) return alert('로그인이 필요합니다.')

  const method = isWatched(stock.code) ? 'DELETE' : 'POST'
  try {
    const res = await fetch(`${API_BASE}/watchlist/`, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: stock.code })
    })
    if (res.ok) {
      if (method === 'POST') watchlist.value.push(stock.code)
      else watchlist.value = watchlist.value.filter(c => c !== stock.code)
    }
  } catch (e) { console.error("관심종목 업데이트 실패", e) }
}

onMounted(() => {
  fetchPopularStocks()
  fetchStocks()
  fetchWatchlist() // ✅ 추가
  startPolling()
})
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="market-header">
      <div v-for="index in marketIndices" :key="index.name" class="index-card shadow-sm">
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
          <VueApexCharts type="line" height="40" width="80" :options="miniChartOptions" :series="index.series" />
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="popular-section">
        <h3 class="section-title">지금 뜨는 인기 종목</h3>
        <div class="popular-grid">
          <div v-for="(stock, idx) in popularStocks" 
               :key="stock.code" 
               class="pop-card" 
               @click="router.push(`/stock/${stock.code}`)">
            <div class="pop-left">
              <span class="rank">{{ idx + 1 }}</span>
              <button class="star-btn" @click="toggleWatchlist($event, stock)">
                {{ isWatched(stock.code) ? '★' : '☆' }}
              </button>
              <img :src="`https://static.toss.im/png-icons/securities/icn-sec-fill-${stock.code}.png`" 
                   class="stock-logo-fixed" />
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
        
        <div class="stock-list-grid">
          <div v-for="(stock, idx) in stocks" 
              :key="stock.code" 
              class="stock-card shadow-sm" 
              @click="router.push(`/stock/${stock.code}`)">
            
            <div class="card-left">
              <span class="rank-num">{{ (currentPage - 1) * PAGE_SIZE + idx + 1 }}</span>
              
              <button class="star-btn sm" @click="toggleWatchlist($event, stock)">
                {{ isWatched(stock.code) ? '★' : '☆' }}
              </button>

              <img :src="`https://static.toss.im/png-icons/securities/icn-sec-fill-${stock.code}.png`" 
                  class="stock-logo-fixed-sm" 
                  @error="(e) => e.target.style.display='none'" />
              
              <div class="stock-name-box">
                <span class="name">{{ stock.name }}</span>
                <span class="code">{{ stock.code }}</span>
              </div>
            </div>

            <div class="card-right">
              <div class="price-info">
                <span class="price-val">{{ Number(stock.last_price || 0).toLocaleString() }}원</span>
                <span :class="['rate-text-sm', stock.change_rate >= 0 ? 'red' : 'blue']">
                  {{ stock.change_rate > 0 ? '+' : '' }}{{ stock.change_rate }}%
                </span>
              </div>
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
.dashboard-wrapper { background: #000; min-height: 100vh; color: #fff; padding-bottom: 50px; }

/* 상단 지수 바 */
.market-header { 
  display: flex; gap: 15px; padding: 20px; 
  max-width: 1200px; margin: 0 auto; 
  border-bottom: 1px solid #1a1a1b;
}
.index-card { 
  background: #1a1a1b; padding: 15px 20px; border-radius: 16px; 
  display: flex; justify-content: space-between; align-items: center; flex: 1;
}
.index-name { font-size: 13px; color: #919193; }
.index-val { font-size: 18px; font-weight: bold; margin-right: 8px; }
.index-rate { font-size: 13px; font-weight: 600; }

/* 메인 컨텐츠 */
.main-content { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
.section-title { font-size: 18px; font-weight: 700; margin-bottom: 15px; color: #fff; }

/* 인기 종목 그리드 (한 줄에 3개 배치하여 크기 최적화) */
.popular-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 12px;
  margin-bottom: 40px;
}

.pop-card {
  background: #1a1a1b; padding: 12px 16px; border-radius: 16px;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer; transition: background 0.2s;
}
.pop-card:hover { background: #252526; }
.pop-left { display: flex; align-items: center; gap: 12px; }
.rank { font-size: 14px; font-weight: bold; color: #919193; width: 15px; }

/* 로고 크기 고정 */
.stock-logo-fixed { width: 40px; height: 40px; border-radius: 50%; background: #333; }

.stock-name-box .name { display: block; font-size: 15px; font-weight: 600; }
.stock-name-box .price { font-size: 13px; color: #919193; }
.rate-text { font-size: 14px; font-weight: 700; }

/* 전체 주식 리스트 */
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.search-input { background: #1a1a1b; border: none; padding: 8px 15px; border-radius: 10px; color: #fff; width: 200px; }
.stock-table { background: #1a1a1b; border-radius: 20px; overflow: hidden; }
.stock-row { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 15px 20px; border-bottom: 1px solid #252526; cursor: pointer;
}
.stock-row:hover { background: #252526; }
.stock-logo-sm { width: 36px; height: 36px; border-radius: 50%; margin-right: 12px; }
.name-col .name { display: block; font-weight: 600; }
.name-col .code { font-size: 11px; color: #666; }
.row-right { text-align: right; }
.row-right .price { display: block; font-weight: 600; }
.row-right .rate { font-size: 12px; }

/* 공통 컬러 */
.red { color: #f04452; }
.blue { color: #3182f6; }

/* 페이지네이션 */
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 30px; }
.pagination button { background: #1a1a1b; border: none; color: #fff; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
.pagination button:disabled { opacity: 0.3; }
.star-btn {
  background: none;
  border: none;
  color: #ff9d00; /* 토스/금융권 스타일 황금색 */
  font-size: 20px;
  cursor: pointer;
  padding: 0 4px;
  transition: transform 0.1s ease;
  z-index: 10;
}

.star-btn:hover {
  transform: scale(1.2);
}

.star-btn.sm {
  font-size: 16px;
  margin-right: 8px;
}

/* 별이 비어있을 때의 색상 */
.star-btn:contains('☆') {
  color: #4b4b4d;
}

/* 카드 내 정렬을 위해 pop-left 수정 */
.pop-left {
  display: flex;
  align-items: center;
  gap: 8px; /* 간격 살짝 조정 */
}
/* 전체 주식 그리드 설정 (한 줄에 2개씩 배치하거나 1개씩 길게 배치 가능) */
.stock-list-grid {
  display: flex;
  flex-direction: column;
  gap: 8px; /* 카드 사이의 간격 */
}

/* 개별 주식 카드 (인기 종목과 통일) */
.stock-card {
  background: #1a1a1b;
  padding: 10px 16px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background 0.2s;
}

.stock-card:hover {
  background: #252526;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 숫자(순번) 스타일 */
.rank-num {
  font-size: 13px;
  font-weight: 500;
  color: #666;
  width: 25px; /* 번호 자리를 고정해서 로고 위치 통일 */
  text-align: center;
}

/* 로고 크기 살짝 작게 */
.stock-logo-fixed-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.stock-name-box .name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  display: block;
}

.stock-name-box .code {
  font-size: 11px;
  color: #666;
}

/* 우측 가격 정보 */
.card-right {
  text-align: right;
}

.price-info .price-val {
  font-size: 14px;
  font-weight: 600;
  display: block;
}

.rate-text-sm {
  font-size: 12px;
  font-weight: 500;
}

/* 별 버튼 간격 조정 */
.star-btn.sm {
  font-size: 16px;
  color: #ff9d00;
  margin-right: 2px;
}
</style>