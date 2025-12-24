<template>
  <v-container class="py-10" style="max-width: 1000px;">
    
    <!-- 로딩 상태 -->
    <div v-if="loading" class="d-flex justify-center my-10">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <!-- 게시글 상세 -->
    <div v-else-if="selectedPost">
      <!-- 뒤로가기 버튼 -->
      <v-btn 
        variant="text" 
        prepend-icon="mdi-arrow-left" 
        class="mb-4 text-grey"
        @click="goBack"
      >
        목록으로
      </v-btn>

      <!-- 메인 카드 -->
      <v-card class="transparent-card" rounded="xl" variant="outlined">
        <v-card-text class="pa-8">
          
          <!-- 헤더: 작성자 정보 + 수정/삭제 버튼 -->
          <div class="d-flex justify-space-between align-center mb-6">
            <button 
              type="button" 
              class="user-info-btn d-flex align-center gap-3"
              @click.stop="goToUserProfile(selectedPost.author.id)"
            >
              <v-avatar size="48">
                <img 
                  :src="selectedPost.author.profile_image_url || '/default-profile.png'" 
                  style="width: 100%; height: 100%; object-fit: cover;"
                />
              </v-avatar>
              <div>
                <div class="text-white font-weight-bold text-body-1">
                  {{ selectedPost.author.nickname }}
                </div>
                <div class="d-flex align-center gap-2 text-caption">
                  <span 
                    :class="selectedPost.author.total_return_rate > 0 ? 'text-red-accent-2' : 'text-blue-accent-2'"
                    class="font-weight-bold"
                  >
                    {{ selectedPost.author.total_return_rate > 0 ? '+' : '' }}{{ selectedPost.author.total_return_rate }}%
                  </span>
                  <span class="text-grey">|</span>
                  <span class="text-grey">{{ formatDate(selectedPost.created_at) }}</span>
                </div>
              </div>
            </button>

            <!-- 작성자에게만 보이는 수정/삭제 버튼 -->
            <div v-if="isAuthor && !isEditing" class="d-flex gap-2">
              <v-btn 
                color="primary" 
                variant="tonal" 
                size="small"
                prepend-icon="mdi-pencil"
                @click="startEdit"
              >
                수정
              </v-btn>
              <v-btn 
                color="error" 
                variant="tonal" 
                size="small"
                prepend-icon="mdi-delete"
                @click="deletePost"
              >
                삭제
              </v-btn>
            </div>
          </div>

          <!-- 수정 모드 -->
          <div v-if="isEditing" class="edit-form">
            <v-text-field
              v-model="editTicker"
              label="티커 (선택사항)"
              placeholder="예: AAPL"
              variant="outlined"
              bg-color="#1E1E1E"
              color="primary"
              class="mb-3"
            ></v-text-field>
            
            <v-text-field
              v-model="editTitle"
              label="제목"
              placeholder="제목을 입력하세요"
              variant="outlined"
              bg-color="#1E1E1E"
              color="primary"
              class="mb-3"
            ></v-text-field>
            
            <v-textarea
              v-model="editContent"
              label="내용"
              placeholder="내용을 입력하세요"
              variant="outlined"
              bg-color="#1E1E1E"
              color="primary"
              rows="10"
              class="mb-3"
            ></v-textarea>

            <div class="d-flex gap-2 justify-end">
              <v-btn 
                color="grey" 
                variant="text"
                @click="cancelEdit"
              >
                취소
              </v-btn>
              <v-btn 
                color="primary" 
                variant="flat"
                @click="saveEdit"
              >
                저장
              </v-btn>
            </div>
          </div>

          <!-- 일반 보기 모드 -->
          <div v-else>
            <!-- 제목 -->
            <h1 class="text-h4 font-weight-bold text-white mb-4">
              <v-chip 
                v-if="selectedPost.ticker" 
                color="primary" 
                variant="tonal" 
                size="small" 
                class="mr-2"
              >
                {{ selectedPost.ticker }}
              </v-chip>
              {{ selectedPost.title }}
            </h1>

            <!-- 본문 -->
            <div class="post-content mb-6">
              <p class="text-grey-lighten-1 text-body-1" style="white-space: pre-wrap; line-height: 1.8;">
                {{ selectedPost.content }}
              </p>
              <v-img 
                v-if="selectedPost.image_url" 
                :src="selectedPost.image_url" 
                class="mt-4 rounded-lg"
                cover
              ></v-img>
            </div>

            <!-- 좋아요 버튼 -->
            <div class="d-flex gap-2">
              <v-btn
                :color="selectedPost.is_liked ? 'red-accent-2' : 'grey'"
                :variant="selectedPost.is_liked ? 'tonal' : 'outlined'"
                @click.stop="toggleLike"
              >
                <v-icon :icon="selectedPost.is_liked ? 'mdi-heart' : 'mdi-heart-outline'" class="mr-1"></v-icon>
                좋아요 {{ selectedPost.like_count }}
              </v-btn>
            </div>
          </div>

          <v-divider class="my-8 border-opacity-25"></v-divider>

          <!-- 댓글 섹션 -->
          <div class="comments-section">
            <h3 class="text-h6 text-white font-weight-bold mb-4">
              💬 댓글 {{ comments.length }}
            </h3>

            <!-- 댓글 리스트 -->
            <div class="comment-list mb-6">
              <v-card
                v-for="cmt in comments"
                :key="cmt.id"
                class="comment-item transparent-card mb-3 pa-4"
                rounded="lg"
                variant="outlined"
              >
                <div class="d-flex justify-space-between align-start mb-2">
                  <button
                    type="button"
                    class="cmt-author-btn text-primary font-weight-bold"
                    @click.stop="goToUserProfile(cmt.author.id)"
                  >
                    {{ cmt.author.nickname }}
                  </button>
                  
                  <v-btn
                    v-if="authStore.user?.id === cmt.author.id"
                    icon="mdi-delete"
                    variant="text"
                    size="x-small"
                    color="error"
                    @click="deleteComment(cmt.id)"
                  ></v-btn>
                </div>
                
                <p class="text-grey-lighten-1 text-body-2 mb-0">
                  {{ cmt.content }}
                </p>
              </v-card>

              <div v-if="comments.length === 0" class="text-center py-8 text-grey">
                <v-icon icon="mdi-comment-outline" size="48" class="mb-2"></v-icon>
                <div>첫 댓글을 남겨보세요!</div>
              </div>
            </div>

            <!-- 댓글 입력 -->
            <div class="comment-input-area">
              <v-text-field
                v-model="newComment"
                placeholder="댓글을 남겨보세요..."
                variant="outlined"
                bg-color="#1E1E1E"
                color="primary"
                hide-details
                @keyup.enter="addComment"
              >
                <template v-slot:append-inner>
                  <v-btn
                    color="primary"
                    variant="flat"
                    size="small"
                    @click="addComment"
                  >
                    등록
                  </v-btn>
                </template>
              </v-text-field>
            </div>
          </div>

        </v-card-text>
      </v-card>
    </div>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const selectedPost = ref(null)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)

// 수정 모드 관련
const isEditing = ref(false)
const editTitle = ref('')
const editContent = ref('')
const editTicker = ref('')

const API_BASE = '/api'

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const postId = computed(() => route.params.id)

// 작성자 본인 확인
const isAuthor = computed(() => {
  return authStore.isAuthenticated && 
         selectedPost.value && 
         authStore.user?.id === selectedPost.value.author.id
})

const fetchPostDetail = async () => {
  loading.value = true
  try {
    const postRes = await fetch(`${API_BASE}/posts/${postId.value}/`)
    if (postRes.ok) {
      selectedPost.value = await postRes.json()
    } else {
      alert('게시글을 찾을 수 없습니다.')
      router.push('/community')
      return
    }

    const commentsRes = await fetch(`${API_BASE}/posts/${postId.value}/comments/`)
    if (commentsRes.ok) {
      comments.value = await commentsRes.json()
    }
  } catch (e) {
    console.error('데이터 로드 실패:', e)
  } finally {
    loading.value = false
  }
}

const goToUserProfile = (userId) => {
  if (!userId) return
  router.push(`/user/${userId}`)
}

const addComment = async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  if (!newComment.value.trim()) return

  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/comments/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
      body: JSON.stringify({ content: newComment.value })
    })

    if (res.ok) {
      const created = await res.json()
      comments.value.push(created)
      newComment.value = ''
      if (selectedPost.value) selectedPost.value.comment_count++
    }
  } catch (e) {
    console.error('댓글 등록 실패:', e)
  }
}

const toggleLike = async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/like/`, { 
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })
    if (res.ok) {
      const data = await res.json()
      selectedPost.value.is_liked = data.liked
      selectedPost.value.like_count = data.like_count
    }
  } catch (e) {
    console.error('좋아요 실패:', e)
  }
}

// 수정 모드 시작
const startEdit = () => {
  editTitle.value = selectedPost.value.title
  editContent.value = selectedPost.value.content
  editTicker.value = selectedPost.value.ticker || ''
  isEditing.value = true
}

// 수정 취소
const cancelEdit = () => {
  isEditing.value = false
}

// 수정 저장
const saveEdit = async () => {
  if (!editTitle.value.trim() || !editContent.value.trim()) {
    alert('제목과 내용을 입력해주세요.')
    return
  }

  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
      body: JSON.stringify({
        title: editTitle.value,
        content: editContent.value,
        ticker: editTicker.value
      })
    })

    if (res.ok) {
      const updated = await res.json()
      selectedPost.value.title = updated.title
      selectedPost.value.content = updated.content
      selectedPost.value.ticker = updated.ticker
      isEditing.value = false
      alert('수정되었습니다.')
    } else {
      alert('수정에 실패했습니다.')
    }
  } catch (e) {
    console.error('수정 실패:', e)
    alert('수정에 실패했습니다.')
  }
}

// 게시글 삭제
const deletePost = async () => {
  if (!confirm('정말 삭제하시겠습니까?')) return

  try {
    const res = await fetch(`${API_BASE}/posts/${postId.value}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })

    if (res.ok || res.status === 204) {
      alert('삭제되었습니다.')
      router.push('/community')
    } else {
      alert('삭제에 실패했습니다.')
    }
  } catch (e) {
    console.error('삭제 실패:', e)
    alert('삭제에 실패했습니다.')
  }
}

// 댓글 삭제
const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return

  try {
    const res = await fetch(`${API_BASE}/posts/comments/${commentId}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      credentials: 'include',
    })

    if (res.ok || res.status === 204) {
      comments.value = comments.value.filter(c => c.id !== commentId)
      if (selectedPost.value) selectedPost.value.comment_count--
    } else {
      alert('댓글 삭제에 실패했습니다.')
    }
  } catch (e) {
    console.error('댓글 삭제 실패:', e)
    alert('댓글 삭제에 실패했습니다.')
  }
}

const goBack = () => {
  router.back()
}

const formatDate = (date) => dayjs(date).format('YYYY.MM.DD HH:mm')

onMounted(() => {
  fetchPostDetail()
})
</script>

<style scoped>
/* 메인 대시보드 카드 스타일: 배경 투명 */
.transparent-card {
  background-color: transparent !important;
  border-color: #524f4fff !important;
  box-shadow: none !important;
}

.gap-3 { gap: 0.75rem; }
.gap-2 { gap: 0.5rem; }

.user-info-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 12px;
  transition: background 0.2s;
}

.user-info-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.cmt-author-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: opacity 0.2s;
}

.cmt-author-btn:hover {
  opacity: 0.8;
}

.comment-item {
  transition: all 0.2s;
}

.comment-item:hover {
  background: rgba(255, 255, 255, 0.02) !important;
}
</style>