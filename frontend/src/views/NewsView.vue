<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/ko' // 한국어 설정

// dayjs 플러그인 설정
dayjs.extend(relativeTime)
dayjs.locale('ko')

// --- 1. 상태 관리 변수들 ---
const newsItems = ref([])       // 실제 뉴스 데이터가 담길 곳
const loading = ref(false)      // 로딩 중 표시용
const searchQuery = ref('')     // 검색어
const page = ref(1)             // 페이지네이션
const activeCategory = ref('통합뉴스')
const activeTab = ref('최신뉴스')

// 사이드바 메뉴 (UI용)
const CATEGORIES = ['통합뉴스', '인기뉴스', '최신뉴스', '금융뉴스']

// --- 2. API 통신 함수 (Django에서 데이터 가져오기) ---
const fetchNews = async () => {
  loading.value = true
  try {
    // 🔹 Django API 호출 (localhost:8000)
    // params: 검색어(search)를 쿼리스트링으로 보냄
    const response = await axios.get('http://localhost:8000/api/latest-news/', {
      params: {
        search: searchQuery.value, 
      }
    })
    
    newsItems.value = response.data
    console.log('뉴스 데이터 로드 성공:', newsItems.value)

  } catch (error) {
    console.error('뉴스 불러오기 실패:', error)
  } finally {
    loading.value = false
  }
}

// --- 3. 이벤트 핸들러 및 유틸리티 ---

// 초기 로딩 시 실행
onMounted(() => {
  fetchNews()
})

// 검색어가 바뀌면 실행 (엔터키용 함수)
const onSearch = () => {
  fetchNews()
}

// 카테고리 선택 (UI용)
const selectCategory = (cat) => {
  activeCategory.value = cat
}

// 날짜 포맷팅 (예: "3시간 전")
const formatTime = (dateString) => {
  if (!dateString) return ''
  return dayjs(dateString).fromNow()
}

// 감성분석 색상 반환
const getSentimentColor = (sentiment) => {
  if (sentiment === 'positive') return 'green-accent-3' // 호재: 밝은 초록
  if (sentiment === 'negative') return 'red-accent-2'   // 악재: 밝은 빨강
  return 'grey'                                         // 중립: 회색
}

// 감성분석 텍스트 반환
const getSentimentText = (sentiment) => {
  if (sentiment === 'positive') return '호재'
  if (sentiment === 'negative') return '악재'
  return '중립'
}
</script>

<template>
  <v-container class="py-8" style="max-width: 1280px;">
    <v-row>
      
      <v-col cols="12" md="3">
        <v-card class="custom-card pa-4" variant="outlined" rounded="xl">
          <h2 class="text-h6 font-weight-bold mb-4 ml-2 text-white">뉴스 분류</h2>
          
          <v-list bg-color="transparent" class="pa-0">
            <v-list-item
              v-for="category in CATEGORIES"
              :key="category"
              @click="selectCategory(category)"
              rounded="lg"
              class="mb-1"
              :class="{ 'active-category': activeCategory === category }"
              link
            >
              <v-list-item-title :class="activeCategory === category ? 'text-white font-weight-bold' : 'text-grey'">
                {{ category }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="9">
        
        <div class="mb-6">
          <v-text-field
            v-model="searchQuery"
            placeholder="뉴스 키워드 검색 (종목명, 내용 등)"
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            rounded="xl"
            bg-color="#141414"
            color="primary"
            hide-details
            class="custom-input"
            @keyup.enter="onSearch"
          ></v-text-field>
        </div>

        <div class="d-flex gap-2 mb-6">
          <v-chip
            v-for="tab in ['최신뉴스', '인기뉴스']"
            :key="tab"
            :variant="activeTab === tab ? 'flat' : 'outlined'"
            :color="activeTab === tab ? 'white' : 'grey'"
            class="px-4"
            @click="activeTab = tab"
            link
          >
            <span :class="activeTab === tab ? 'text-black font-weight-bold' : 'text-grey-lighten-1'">
              {{ tab }}
            </span>
          </v-chip>
        </div>

        <div v-if="loading" class="d-flex justify-center my-10">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        </div>

        <div v-else-if="newsItems.length === 0" class="text-center text-grey my-10">
          <v-icon icon="mdi-newspaper-remove" size="64" class="mb-4"></v-icon>
          <h3 class="text-h6">표시할 뉴스가 없습니다.</h3>
          <p class="text-body-2 mt-2">검색어를 변경하거나 잠시 후 다시 시도해주세요.</p>
        </div>

        <div v-else class="d-flex flex-column gap-4">
          <v-card
            v-for="news in newsItems"
            :key="news.id"
            class="custom-card news-item-card"
            variant="outlined"
            rounded="xl"
            link
            :href="news.url"
            target="_blank"
          >
            <div class="d-flex pa-5">
              
              <div class="thumbnail-box rounded-lg mr-5 d-flex align-center justify-center bg-grey-darken-4 overflow-hidden border-subtle">
                <v-img
                  v-if="news.image_url"
                  :src="news.image_url"
                  cover
                  class="fill-height fill-width transition-swing"
                ></v-img>
                <v-icon 
                  v-else 
                  icon="mdi-newspaper-variant-outline" 
                  color="grey-darken-1" 
                  size="32"
                ></v-icon>
              </div>

              <div class="flex-grow-1 d-flex flex-column justify-space-between">
                
                <div>
                  <h3 class="text-subtitle-1 font-weight-bold text-white mb-2 text-truncate-2 title-hover">
                    {{ news.title }}
                  </h3>

                  <div class="d-flex flex-wrap gap-2 mb-2">
                    <v-chip
                      v-if="news.company_name"
                      size="x-small"
                      color="blue-lighten-1"
                      variant="tonal"
                      label
                      class="font-weight-bold"
                    >
                      {{ news.company_name }}
                    </v-chip>

                    <v-chip 
                      v-if="news.sentiment && news.sentiment !== 'neutral'"
                      size="x-small" 
                      :color="getSentimentColor(news.sentiment)" 
                      variant="tonal" 
                      label 
                      class="font-weight-bold"
                      prepend-icon="mdi-chart-line"
                    >
                      {{ getSentimentText(news.sentiment) }}
                    </v-chip>
                  </div>
                </div>

                <div class="d-flex align-center text-caption text-grey">
                  <span class="font-weight-medium text-grey-lighten-2">
                    {{ news.source || '인터넷뉴스' }}
                  </span>
                  <span class="mx-2">·</span>
                  <span>{{ formatTime(news.news_collection_date) }}</span>
                </div>

              </div>
            </div>
          </v-card>
        </div>

        <div class="mt-8 d-flex justify-center">
          <v-pagination
            v-model="page"
            :length="5"
            rounded="circle"
            active-color="primary"
            variant="flat"
            size="small"
          ></v-pagination>
        </div>

      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
/* 다크모드 전용 딥 블랙 배경 */
.custom-card {
  background-color: #141414 !important; /* 리액트 디자인의 그 색상 */
  border-color: #333 !important;
  transition: all 0.2s ease-in-out;
}

/* 호버 시 테두리와 그림자 효과 */
.custom-card:hover {
  border-color: #555 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

/* 활성화된 카테고리 */
.active-category {
  background-color: #2a2a2a !important;
}

/* 검색창 테두리 커스텀 */
.custom-input :deep(.v-field__outline__start),
.custom-input :deep(.v-field__outline__end),
.custom-input :deep(.v-field__outline__notch) {
  border-color: #333 !important;
}

/* 썸네일 박스 스타일 */
.thumbnail-box {
  width: 110px;    /* 크기 약간 키움 */
  height: 110px;
  flex-shrink: 0;
  border: 1px solid #333; /* 미세한 테두리 */
}

/* 텍스트 말줄임 (2줄) */
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

/* 제목 호버 효과 */
.news-item-card:hover .title-hover {
  text-decoration: underline;
  text-decoration-color: #666;
  text-underline-offset: 4px;
}

/* 간격 유틸리티 */
.gap-2 { gap: 8px; }
.gap-4 { gap: 16px; }

/* 미세 테두리 */
.border-subtle {
  border: 1px solid rgba(255,255,255,0.1);
}
</style>