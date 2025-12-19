<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const code = route.params.code

const summary = ref(null)
const posts = ref([])
const loading = ref(true)
const tradeLogs = ref([]) // ✅ [추가] 실시간 거래 내역 상태

// 📈 차트 설정 고도화 (Y축 스케일 최적화)
const fullChartData = ref([]) 
const chartSeries = ref([])   
const activeRange = ref('1M') 

const chartOptions = ref({
  chart: { 
    type: 'candlestick', 
    background: 'transparent', 
    toolbar: { show: false },
    animations: { enabled: false } // 성능을 위해 첫 로딩 후 끔
  },
  theme: { mode: 'dark' },
  xaxis: { type: 'datetime', labels: { style: { colors: '#666' } } },
  yaxis: {
    opposite: true,
    labels: { 
      style: { colors: '#666' },
      formatter: (val) => val?.toLocaleString() 
    },
    // ✅ [핵심] Y축이 0부터 시작하지 않고 데이터 범위에 맞춰서 확대됨
    forceNiceScale: true,
    tooltip: { enabled: true }
  },
  grid: { borderColor: '#1a1a1b', strokeDashArray: 4 },
  plotOptions: {
    candlestick: { colors: { upward: '#f04452', downward: '#3182f6' } }
  }
})

const updateChartRange = (range) => {
  activeRange.value = range
  if (!fullChartData.value.length) return
  const now = new Date().getTime()
  let diff = 30 * 24 * 60 * 60 * 1000 // 1M default
  if (range === '1W') diff = 7 * 24 * 60 * 60 * 1000
  else if (range === '1Y') diff = 365 * 24 * 60 * 60 * 1000
  
  const filtered = fullChartData.value.filter(d => d.x >= (now - diff))
  chartSeries.value = [{ name: '주가', data: filtered }]
}

// ✅ [추가] 내 실시간 거래 내역 가져오기
const fetchMyTransactions = async () => {
  try {
    const res = await fetch(`/api/transactions/`) // 실제 API 엔드포인트에 맞게 수정
    if (res.ok) {
      const data = await res.json()
      tradeLogs.value = data.slice(0, 10) // 최근 10개만
    }
  } catch (e) { console.error(e) }
}

const fetchData = async () => {
  try {
    const sumRes = await fetch(`/api/stock-prices/summary/?ticker=${code}`)
    if (sumRes.ok) summary.value = await sumRes.json()

    if (!fullChartData.value.length) {
      const chartRes = await fetch(`/api/stock-prices/chart/?ticker=${code}&days=365`)
      if (chartRes.ok) {
        const json = await chartRes.json()
        fullChartData.value = json.map(row => ({
          x: new Date(row.date).getTime(),
          y: [row.open, row.high, row.low, row.close]
        }))
        updateChartRange('1M')
      }
    }
    const feedRes = await fetch(`/api/posts/feed/?ticker=${code}`)
    if (feedRes.ok) posts.value = await feedRes.json()
    fetchMyTransactions() // 거래 내역 갱신
  } catch(e) { console.error(e) } 
  finally { loading.value = false }
}

// 모의투자 로직 (기존 유지)
const showTradeModal = ref(false)
const tradeType = ref('BUY')
const tradeQuantity = ref(0)
const openTradeModal = (type) => {
  if(!authStore.isAuthenticated) return alert('로그인이 필요합니다.')
  tradeType.value = type; tradeQuantity.value = 0; showTradeModal.value = true
}

const executeTrade = async () => {
  if (tradeQuantity.value <= 0) return alert('수량을 입력해주세요.')
  try {
    const res = await fetch('/api/transactions/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company: code, type: tradeType.value, price: summary.value.last_price, quantity: tradeQuantity.value })
    })
    if(res.ok) {
      alert('주문이 체결되었습니다!'); 
      await authStore.fetchUser(); 
      showTradeModal.value = false;
      fetchData(); // 내역 즉시 갱신
    }
  } catch (e) { console.error(e) }
}

let polling = null
onMounted(() => { fetchData(); polling = setInterval(fetchData, 5000); })
onUnmounted(() => { if (polling) clearInterval(polling) })
</script>

<template>
  <div class="dashboard-detail">
    <header class="detail-header">
      <div class="header-left">
        <button @click="router.back()" class="back-btn">〈</button>
        <h1 class="stock-title">{{ summary?.name }} <span class="stock-code">{{ code }}</span></h1>
      </div>
      <div class="header-right" v-if="authStore.isAuthenticated">
        <div class="mileage-badge">💎 {{ Number(authStore.user?.mileage || 0).toLocaleString() }} M</div>
        <div class="action-btns">
          <button @click="openTradeModal('BUY')" class="btn buy">매수</button>
          <button @click="openTradeModal('SELL')" class="btn sell">매도</button>
        </div>
      </div>
    </header>

    <div class="main-grid">
      <div class="content-left">
        <section class="chart-section shadow-card">
          <div class="chart-top">
            <div class="current-price-box">
              <span class="main-price">{{ Number(summary?.last_price).toLocaleString() }}원</span>
              <span :class="summary?.change_rate >= 0 ? 'red' : 'blue'" class="main-rate">
                {{ summary?.change_rate >= 0 ? '+' : '' }}{{ summary?.change_rate }}%
              </span>
            </div>
            <div class="range-tabs">
              <button v-for="r in ['1W', '1M', '1Y']" :key="r" @click="updateChartRange(r)" :class="{ active: activeRange === r }">{{ r }}</button>
            </div>
          </div>
          <VueApexCharts type="candlestick" height="350" :options="chartOptions" :series="chartSeries" />
        </section>

        <section class="feed-section shadow-card">
          <h3>종목 토론방</h3>
          <div v-if="posts.length === 0" class="empty">첫 게시글을 작성해보세요.</div>
          <div v-for="post in posts" :key="post.id" class="post-item">
            <div class="post-meta">
              <span class="user">{{ post.author.nickname || '익명' }}</span>
              <span class="time">{{ new Date(post.created_at).toLocaleDateString() }}</span>
            </div>
            <p class="post-text">{{ post.content }}</p>
          </div>
        </section>
      </div>

      <aside class="content-right">
        <section class="log-section shadow-card">
          <div class="log-header">
            <h3>실시간 나의 거래</h3>
            <span class="live-dot"></span>
          </div>
          <div class="log-list">
            <div v-if="tradeLogs.length === 0" class="empty-log">거래 내역이 없습니다.</div>
            <div v-for="log in tradeLogs" :key="log.id" class="log-item">
              <div class="log-info">
                <span :class="log.type === 'BUY' ? 'tag-buy' : 'tag-sell'">{{ log.type === 'BUY' ? '매수' : '매도' }}</span>
                <span class="log-time">{{ log.time || '방금 전' }}</span>
              </div>
              <div class="log-details">
                <span class="log-amt">{{ log.quantity }}주</span>
                <span class="log-prc">{{ Number(log.price).toLocaleString() }}원</span>
              </div>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <div v-if="showTradeModal" class="modal-overlay" @click.self="showTradeModal = false">
      <div class="modal-content">
        <h2>{{ tradeType === 'BUY' ? '매수하기' : '매도하기' }}</h2>
        <div class="modal-body">
          <p>현재가: <strong>{{ Number(summary?.last_price).toLocaleString() }}원</strong></p>
          <div class="input-row">
            <label>수량</label>
            <input type="number" v-model.number="tradeQuantity" min="1" />
          </div>
          <div class="total-row">
            <span>예상 결제 금액</span>
            <strong>{{ Number(summary?.last_price * tradeQuantity).toLocaleString() }} M</strong>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showTradeModal = false" class="btn-cancel">취소</button>
          <button @click="executeTrade" :class="['btn-submit', tradeType === 'BUY' ? 'buy' : 'sell']">주문 확정</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-detail { background: #000; min-height: 100vh; color: #fff; padding: 0 20px 40px; }
.detail-header { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 25px 0; }
.header-left { display: flex; align-items: center; gap: 15px; }
.back-btn { background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; }
.stock-title { font-size: 24px; font-weight: bold; }
.stock-code { color: #666; font-size: 16px; font-weight: normal; }

.header-right { display: flex; align-items: center; gap: 20px; }
.mileage-badge { background: #1a1a1b; padding: 8px 15px; border-radius: 10px; color: #fbbf24; font-weight: bold; }
.action-btns { display: flex; gap: 10px; }
.btn { padding: 10px 25px; border-radius: 12px; border: none; font-weight: bold; cursor: pointer; color: #fff; }
.btn.buy { background: #f04452; } .btn.sell { background: #3182f6; }

.main-grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 8fr 4fr; gap: 25px; }

.shadow-card { background: #1a1a1b; border-radius: 24px; padding: 25px; }
.chart-top { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }
.main-price { font-size: 32px; font-weight: bold; margin-right: 10px; }
.main-rate { font-size: 18px; font-weight: bold; }

.range-tabs { display: flex; background: #000; padding: 4px; border-radius: 10px; }
.range-tabs button { background: none; border: none; color: #666; padding: 6px 12px; border-radius: 8px; cursor: pointer; }
.range-tabs button.active { background: #1a1a1b; color: #fff; font-weight: bold; }

/* 거래 로그 스타일 */
.log-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.live-dot { width: 8px; height: 8px; background: #00ff00; border-radius: 50%; box-shadow: 0 0 8px #00ff00; animation: pulse 2s infinite; }
.log-list { display: flex; flex-direction: column; gap: 15px; }
.log-item { background: #000; padding: 15px; border-radius: 16px; display: flex; justify-content: space-between; }
.tag-buy { color: #f04452; font-size: 12px; font-weight: bold; }
.tag-sell { color: #3182f6; font-size: 12px; font-weight: bold; }
.log-time { font-size: 11px; color: #666; margin-left: 8px; }
.log-details { text-align: right; }
.log-amt { display: block; font-weight: bold; }
.log-prc { font-size: 12px; color: #919193; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-content { background: #1a1a1b; padding: 30px; border-radius: 28px; width: 400px; }
.input-row { margin: 20px 0; display: flex; flex-direction: column; gap: 10px; }
.input-row input { background: #000; border: 1px solid #333; padding: 12px; border-radius: 12px; color: #fff; font-size: 18px; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
@media (max-width: 1024px) { .main-grid { grid-template-columns: 1fr; } }
</style>