<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 이미지 및 로고 import
import dataAnalysisImg from '@/assets/data_image.jpeg'
import communityImg from '@/assets/community_image.jpeg'
import logoImg from '@/assets/logo.png' 

const router = useRouter()

const goDashboard = () => {
  router.push({ name: 'dashboard' })
}

const goSignup = () => {
  router.push({ name: 'signup' }) 
}

// 스크롤 등장 애니메이션 (2초)
onMounted(() => {
  const observerOptions = { threshold: 0.1 }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('appear')
      }
    })
  }, observerOptions)

  document.querySelectorAll('.section').forEach(el => observer.observe(el))
})
</script>

<template>
  <div class="landing-container">
    
    <section class="section hero">
      <div class="hero-content">
        <h1 class="main-title">
          주식, 과거부터 현재까지<br />
          <span class="highlight">BackLoop</span>에서
        </h1>
        <p class="sub-text">
          데이터 기반의 알고리즘 분석으로 실현하는 스마트한 투자 루프
        </p>
        <div class="btn-group">
          <button class="start-btn glow" @click="goDashboard">
            무료로 시작하기
          </button>
        </div>
      </div>
    </section>

    <section class="section feature">
      <div class="feature-card glass">
        <div class="card-image-wrapper">
          <img :src="dataAnalysisImg" alt="데이터 분석" class="card-image" />
        </div>
        <div class="card-text">
          <span class="badge">Analysis</span>
          <h2>데이터 기반 주식 추천</h2>
          <p>
            단순한 차트를 넘어, 과거의 유사 패턴과 심층 데이터를 분석합니다. 
            합리적인 투자 지표를 통해 당신만의 전략을 완성하세요.
          </p>
        </div>
      </div>
    </section>

    <section class="section feature">
      <div class="feature-card glass reverse">
        <div class="card-image-wrapper">
          <img :src="communityImg" alt="커뮤니티" class="card-image" />
        </div>
        <div class="card-text">
          <span class="badge">Community</span>
          <h2>커뮤니티와 함께 성장</h2>
          <p>
            지식은 나눌 때 가치가 커집니다. 수만 명의 투자자들과 
            실시간으로 소통하며 시장을 읽는 통찰력을 공유하세요.
          </p>
        </div>
      </div>
    </section>

    <section class="section footer-cta-section">
      <div class="cta-main-card">
        <div class="service-icon">
          <img :src="logoImg" alt="BackLoop 로고" class="cta-logo-img" />
        </div>
        <h2 class="cta-headline">
          투자의 흐름에 집중. 쓰기 좋게 맞춤.<br/>
          BackLoop
        </h2>
        <div class="cta-button-group">
          <button class="cta-sub-btn dark" @click="goDashboard">
            대시보드 바로가기 <span class="icon">↗</span>
          </button>
          <button class="cta-sub-btn dark" @click="goSignup">
            회원가입 바로가기 <span class="icon">→</span>
          </button>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
/* --- 0. 폰트 설정 --- */

/* 타이틀 전용 폰트 (Title) */
@font-face {
  font-family: 'HappinessSansTitle';
  src: url('@/assets/fonts/Happiness-Sans-Title.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

/* 본문 및 버튼용 폰트 (Bold) */
@font-face {
  font-family: 'HappinessSansBold';
  src: url('@/assets/fonts/Happiness-Sans-Bold.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

/* --- 1. 배경: 초고속 메쉬 그라디언트 (6초) --- */
.landing-container {
  background: linear-gradient(
    125deg, 
    #dcf1ff 0%, 
    #ffffff 25%, 
    #aacbff 50%, 
    #f4f7ff 75%, 
    #d1d5db 100%
  );
  background-size: 400% 400%;
  animation: fastMeshGradient 6s ease infinite;
  color: #1a1a1b;
  min-height: 100vh;
  overflow-x: hidden;
  /* 기본 폰트를 Bold로 설정 */
  font-family: 'HappinessSansBold', -apple-system, sans-serif;
}

@keyframes fastMeshGradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* --- 2. 섹션 애니메이션 (2초) --- */
.section {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 80px 40px;
  opacity: 0;
  transform: translateY(80px);
  transition: all 2s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform, opacity;
}

.section.appear {
  opacity: 1;
  transform: translateY(0);
}

/* --- 타이틀 스타일 (Title 폰트 적용) --- */
.main-title { 
  font-family: 'HappinessSansTitle', sans-serif;
  font-size: 5rem; 
  font-weight: 900; 
  line-height: 1.15; 
  margin-bottom: 30px; 
  word-break: keep-all; 
}

.highlight { color: #2563eb; }

/* --- 본문 스타일 (Bold 폰트 적용) --- */
.sub-text { 
  font-size: 1.6rem; 
  color: #4b5563; 
  margin-bottom: 50px; 
  word-break: keep-all; 
}

/* 피처 카드 */
.feature-card { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; width: 100%; align-items: center; }
.feature-card.reverse .card-image-wrapper { order: 2; }
.glass {
  background: rgba(255, 255, 255, 0.25); 
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 80px;
  border-radius: 60px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
}

.badge { display: inline-block; padding: 6px 16px; background: rgba(37, 99, 235, 0.1); color: #2563eb; border-radius: 20px; font-weight: 700; margin-bottom: 20px; }
.card-text h2 { font-size: 3.5rem; font-weight: 800; margin-bottom: 30px; word-break: keep-all; }
.card-text p { font-size: 1.4rem; line-height: 1.8; color: #374151; word-break: keep-all; }
.card-image-wrapper { width: 100%; height: 500px; border-radius: 40px; overflow: hidden; box-shadow: 0 30px 60px rgba(0,0,0,0.1); }
.card-image { width: 100%; height: 100%; object-fit: cover; transition: transform 0.8s ease; }
.feature-card:hover .card-image { transform: scale(1.08); }

/* --- 버튼 디자인 (Bold 폰트 적용) --- */
.start-btn { 
  font-family: 'HappinessSansBold', sans-serif;
  padding: 20px 50px; 
  font-size: 1.3rem; 
  font-weight: 800; 
  border-radius: 100px; 
  cursor: pointer; 
  border: none; 
  transition: all 0.4s ease; 
}
.start-btn.glow { background: #111; color: #fff; }
.start-btn.glow:hover { transform: translateY(-8px) scale(1.05); box-shadow: 0 20px 40px rgba(0,0,0,0.2), 0 0 20px rgba(37, 99, 235, 0.3); }

/* 하단 CTA */
.footer-cta-section { min-height: auto; padding-bottom: 120px; }
.cta-main-card { width: 100%; max-width: 1200px; background-color: #f9f9f9; border-radius: 40px; padding: 80px 40px; text-align: center; display: flex; flex-direction: column; align-items: center; }
.cta-logo-img { width: 120px; height: auto; border-radius: 24px; }
.cta-headline { font-size: 2.8rem; font-weight: 700; line-height: 1.4; margin-bottom: 40px; word-break: keep-all; color: #111; }
.cta-button-group { display: flex; gap: 20px; }

.cta-sub-btn { 
  font-family: 'HappinessSansBold', sans-serif;
  padding: 20px 40px; 
  font-size: 1.2rem; 
  font-weight: 700; 
  border-radius: 16px; 
  cursor: pointer; 
  border: none; 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  transition: all 0.3s ease; 
}
.cta-sub-btn.dark { background-color: #111; color: white; }
.cta-sub-btn:hover { background-color: #333; transform: translateY(-4px); }

/* 반응형 */
@media (max-width: 1200px) {
  .main-title { font-size: 3.5rem; }
  .feature-card, .feature-card.reverse { grid-template-columns: 1fr; padding: 40px; text-align: center; }
  .feature-card.reverse .card-image-wrapper { order: 0; }
}
</style>