<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const code = route.params.code // URL에서 종목코드 획득

const summary = ref(null)
const chartData = ref([])
const posts = ref([])
const loading = ref(true)

// 차트 SVG 패스 생성
const chartPath = computed(() => {
  if (!chartData.value.length) return ''
  const data = chartData.value
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  return data.map((v, i) => {
    const x = (i / (data.length - 1)) * 800
    const y = 300 - ((v - min) / range) * 300
    return `${x},${y}`
  }).join(' ')
})

const fetchData = async () => {
  loading.value = true
  try {
    // 1. 요약
    const sumRes = await fetch(`/api/stock-prices/summary/?ticker=${code}`)
    if (sumRes.ok) summary.value = await sumRes.json()

    // 2. 30일 차트
    const chartRes = await fetch(`/api/stock-prices/chart/?ticker=${code}&days=30`)
    if (chartRes.ok) {
      const json = await chartRes.json()
      chartData.value = json.map(row => Number(row.close))
    }

    // 3. 종목 토론글
    const feedRes = await fetch(`/api/posts/feed/?ticker=${code}`)
    if (feedRes.ok) posts.value = await feedRes.json()

  } catch(e) { console.error(e) } 
  finally { loading.value = false }
}

onMounted(() => fetchData())
</script>

<template>
  <div class="detail-page">
    <div v-if="loading" class="loading">로딩 중...</div>
    <div v-else class="content">
      
      <div class="header">
        <button @click="router.back()" class="back-btn">←</button>
        <div>
          <h1 class="title">{{ summary?.name }} <span class="code">{{ code }}</span></h1>
          <div class="price" :class="summary?.change_rate >= 0 ? 'red' : 'blue'">
            {{ Number(summary?.last_price).toLocaleString() }}원
            <span class="change">{{ summary?.change_rate }}%</span>
          </div>
        </div>
      </div>

      <div class="chart-box">
        <svg viewBox="0 0 800 300" class="chart-svg">
          <polyline 
            :points="chartPath" 
            fill="none" 
            stroke="#3b82f6" 
            stroke-width="2" 
          />
        </svg>
      </div>

      <div class="feed-section">
        <h3>종목 토론방 ({{ posts.length }})</h3>
        <div v-if="posts.length === 0" class="empty">게시글이 없습니다.</div>
        <div v-else class="feed-list">
          <div v-for="post in posts" :key="post.id" class="feed-item">
            <div class="feed-head">
              <span class="author">{{ post.author_nickname || '익명' }}</span>
              <span class="date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
            </div>
            <div class="feed-body">{{ post.content }}</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.detail-page { max-width: 800px; margin: 0 auto; color: #f5f5f7; padding-bottom: 60px; }
.header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.back-btn { background: #1f2937; border: none; color: white; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 20px; }
.title { margin: 0; font-size: 24px; }
.code { font-size: 16px; color: #9ca3af; font-weight: normal; margin-left: 8px; }
.price { font-size: 28px; font-weight: 700; margin-top: 4px; }
.change { font-size: 16px; margin-left: 10px; }
.red { color: #ef4444; } .blue { color: #3b82f6; }

.chart-box { background: #141414; border: 1px solid #1f2937; border-radius: 16px; padding: 20px; margin-bottom: 30px; }
.chart-svg { width: 100%; height: auto; }

.feed-section h3 { border-bottom: 1px solid #1f2937; padding-bottom: 10px; margin-bottom: 16px; }
.feed-item { background: #141414; border: 1px solid #1f2937; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.feed-head { display: flex; justify-content: space-between; color: #9ca3af; font-size: 13px; margin-bottom: 8px; }
.empty { text-align: center; color: #6b7280; padding: 30px; }
</style>