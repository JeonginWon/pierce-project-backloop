<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 이미지 및 로고 import
import dataAnalysisImg from '@/assets/stock_image.png'
import newsImg from '@/assets/ai_report_image.png'
import communityImg from '@/assets/community.png'
import portfolioImg from '@/assets/portfolio_image.png'
import logoImg from '@/assets/logo.png'

const router = useRouter()

const goDashboard = () => { router.push({ name: 'dashboard' }) }
const goSignup = () => { router.push({ name: 'signup' }) }

onMounted(() => {
  const observerOptions = { 
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
  }
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
      }
    })
  }, observerOptions)

  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el))
})
</script>

<template>
  <div class="landing-container">
    
    <section class="section hero animate-on-scroll">
      <div class="hero-content">
        <h1 class="main-title">
          주식, 과거부터 현재까지<br />
          <span class="highlight">BackLoop</span>에서
        </h1>
        <p class="sub-text">
          뉴스 데이터 기반의 AI 분석으로 실현하는 스마트한 투자 루프
        </p>
        <div class="btn-group">
          <button class="start-btn glow" @click="goDashboard">
            Start
          </button>
        </div>
      </div>
    </section>

    <section class="section features-list-section">
      <div class="feature-container">
        <div class="feature-row animate-on-scroll">
          <div class="text-side">
            <span class="badge analysis">Investment</span>
            <h2 class="feature-title">모의투자로<br/>투자감각 향상</h2>
            <p class="feature-desc">
              '백 마일리지' 시스템으로 실제 자산 손실 걱정 없이 투자 루틴을 연습하고 실력을 키워보세요.
            </p>
          </div>
          <div class="image-side">
            <div class="img-wrapper">
              <img :src="dataAnalysisImg" alt="모의투자" class="feature-img" />
            </div>
          </div>
        </div>

        <div class="feature-row reverse animate-on-scroll">
          <div class="text-side">
            <span class="badge insight">AI Insight</span>
            <h2 class="feature-title">뉴스 AI<br/>분석 리포트</h2>
            <p class="feature-desc">
              수많은 뉴스 속에 숨겨진 투자 신호를 AI가 포착합니다. 데이터 기반 객관적인 리포트를 확인하세요.
            </p>
          </div>
          <div class="image-side">
            <div class="img-wrapper">
              <img :src="newsImg" alt="AI 분석" class="feature-img" />
            </div>
          </div>
        </div>

        <div class="feature-row animate-on-scroll">
          <div class="text-side">
            <span class="badge community">Community</span>
            <h2 class="feature-title">함께 성장하는<br/>커뮤니티</h2>
            <p class="feature-desc">
              혼자 고민하지 마세요. 수만 명의 투자자들과 실시간으로 소통하며 시장을 읽는 통찰력을 공유할 수 있습니다.
            </p>
          </div>
          <div class="image-side">
            <div class="img-wrapper">
              <img :src="communityImg" alt="커뮤니티" class="feature-img" />
            </div>
          </div>
        </div>

        <div class="feature-row reverse animate-on-scroll">
          <div class="text-side">
            <span class="badge portfolio">Portfolio</span>
            <h2 class="feature-title">나만의 투자<br/>포트폴리오 관리</h2>
            <p class="feature-desc">
              내 투자 성향을 분석하고 포트폴리오를 최적화하세요. 3천만 백마일리지를 전략적으로 확장해보세요!
            </p>
          </div>
          <div class="image-side">
            <div class="img-wrapper">
              <img :src="portfolioImg" alt="포트폴리오" class="feature-img" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section footer-cta-section animate-on-scroll">
      <div class="cta-main-card">
        <div class="service-icon">
          <img :src="logoImg" alt="BackLoop 로고" class="cta-logo-img" />
        </div>
        <h2 class="cta-headline">
          투자의 흐름에 집중. 쓰기 좋게 맞춤.<br/>
          BackLoop
        </h2>
        <div class="cta-button-group">
          <button class="cta-sub-btn primary" @click="goDashboard">
            대시보드 바로가기 <span class="icon">↗</span>
          </button>
          <button class="cta-sub-btn outline" @click="goSignup">
            회원가입 바로가기 <span class="icon">→</span>
          </button>
        </div>
      </div>
    </section>

    <footer class="bottom-info-footer">
      <div class="footer-content">
        <div class="dev-team">
          <span class="team-name">Team 개미투자연구소</span>
          <div class="dev-links">
            <a href="https://github.com/pierce-pjt/pierce.git" target="_blank" class="dev-link">Github</a>
            <a href="mailto:mary010323@gmail.com" class="dev-link">Contact</a>
            <a href="#" class="dev-link">Privacy Policy</a>
          </div>
        </div>
        <p class="copyright">© 2025 BackLoop. All rights reserved. Designed for smarter investment.</p>
      </div>
    </footer>

  </div>
</template>

<style scoped>
/* --- 0. 폰트 및 배경 설정 (기존 유지) --- */
@font-face { font-family: 'HappinessSansTitle'; src: url('@/assets/fonts/Happiness-Sans-Title.ttf') format('truetype'); }
@font-face { font-family: 'HappinessSansBold'; src: url('@/assets/fonts/Happiness-Sans-Bold.ttf') format('truetype'); }

.landing-container {
  background: linear-gradient(125deg, #dcf1ff 0%, #ffffff 25%, #aacbff 50%, #f4f7ff 75%, #d1d5db 100%);
  background-size: 400% 400%;
  animation: fastMeshGradient 6s ease infinite;
  color: #1a1a1b;
  min-height: 100vh;
  overflow-x: hidden;
  font-family: 'HappinessSansBold', -apple-system, sans-serif;
}

@keyframes fastMeshGradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-on-scroll {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 1.2s cubic-bezier(0.2, 0.8, 0.2, 1), transform 1.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.animate-on-scroll.visible { opacity: 1; transform: translateY(0); }

.section {
  width: 100%; max-width: 1400px; margin: 0 auto;
  padding: 160px 40px;
}

/* Hero */
.hero { text-align: center; min-height: 70vh; display: flex; flex-direction: column; justify-content: center; }
.main-title { font-family: 'HappinessSansTitle', sans-serif; font-size: 5rem; font-weight: 900; line-height: 1.2; margin-bottom: 30px; }
.highlight { color: #2563eb; }
.sub-text { font-size: 1.6rem; color: #4b5563; margin-bottom: 50px; }
.start-btn { padding: 20px 60px; font-size: 1.4rem; font-weight: 800; border-radius: 100px; cursor: pointer; border: none; background: #7b97d3; color: #ffffff; transition: 0.4s; }
.start-btn:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.2); }

/* --- 2. Feature Grid (유지) --- */
.feature-container { display: flex; flex-direction: column; gap: 220px; }
.feature-row { display: flex; align-items: center; justify-content: space-between; gap: 80px; }
.feature-row.reverse { flex-direction: row-reverse; }

.text-side { flex: 1; min-width: 550px; flex-shrink: 0; }
.text-side > * { opacity: 0; transform: translateY(20px); transition: all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1); }
.visible .text-side > * { opacity: 1; transform: translateY(0); }

.badge { display: inline-flex; padding: 8px 16px; border-radius: 12px; font-size: 1rem; font-weight: 800; margin-bottom: 24px; }
.analysis { background: #eff6ff; color: #2563eb; }
.insight { background: #f5f3ff; color: #2563eb; }
.community { background: #ecfdf5; color: #2563eb; }
.portfolio { background: #fff7ed; color: #2563eb; }

.feature-title { 
  font-family: 'HappinessSansTitle', sans-serif; 
  font-size: 3.5rem; 
  font-weight: 900; 
  line-height: 1.25; 
  margin-bottom: 24px; 
  color: #111;
  white-space: nowrap; 
  word-break: keep-all; 
}
.feature-desc { font-size: 1.4rem; line-height: 1.7; color: #4b5563; word-break: keep-all; max-width: 520px; }

.image-side { flex: 1.1; display: flex; justify-content: center; opacity: 0; transform: scale(0.95); transition: all 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.2s; }
.visible .image-side { opacity: 1; transform: scale(1); }
.img-wrapper {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 40px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 580px;
}
.feature-img { width: 100%; height: auto; border-radius: 24px; display: block; }

/* --- 3. 푸터 CTA --- */
.footer-cta-section { padding: 80px 40px 60px; } /* 하단 여백 조정 */
.cta-main-card {
  background: #ffffff;
  border-radius: 40px;
  padding: 40px 60px;
  text-align: center;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.06);
  border: 1px solid #f1f5f9;
  max-width: 1100px;
  margin: 0 auto;
}

.cta-logo-img { width: 50px; margin-bottom: 20px; }
.cta-headline {
  font-family: 'HappinessSansTitle', sans-serif;
  font-size: 2.2rem;
  line-height: 1.3;
  margin-bottom: 35px;
  color: #1a1a1b;
}

.cta-button-group { display: flex; justify-content: center; gap: 15px; }
.cta-sub-btn {
  padding: 14px 28px;
  font-size: 1rem;
  font-weight: 800;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.cta-sub-btn.primary { background: #7b97d3; color: white; border: none; }
.cta-sub-btn.outline { background: transparent; color: #1a1a1b; border: 2px solid #e5e7eb; }

/* --- 신규 추가: 최하단 개발자 정보 스타일 --- */
.bottom-info-footer {
  padding: 40px 40px 60px;
  text-align: center;
  border-top: 1px solid rgba(0, 0, 0, 0.05); /* 상단 구분선 */
  margin-top: 20px;
}

.footer-content {
  max-width: 1100px;
  margin: 0 auto;
}

.dev-team {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.team-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: #374151;
}

.dev-links {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.dev-link {
  font-size: 0.9rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.2s;
}

.dev-link:hover {
  color: #2563eb;
}

.copyright {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-top: 10px;
}

@media (max-width: 1024px) {
  .cta-main-card { padding: 40px 30px; }
  .cta-headline { font-size: 1.8rem; }
  .feature-row { flex-direction: column; text-align: center; }
  .text-side { min-width: auto; }
  .feature-title { white-space: normal; }
  .dev-links { gap: 15px; }
}
</style>