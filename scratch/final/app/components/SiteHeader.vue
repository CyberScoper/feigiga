<template>
  <header class="header">
    <div class="container header-inner">
      <NuxtLink to="/" class="logo">
        <span class="logo-mark">
          <svg viewBox="0 0 32 32" width="32" height="32" aria-hidden="true">
            <defs>
              <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#ff7a3d" />
                <stop offset="100%" stop-color="#ffce4f" />
              </linearGradient>
            </defs>
            <rect x="2" y="2" width="28" height="28" rx="5" fill="#060e1a" stroke="url(#lg)" stroke-width="1.5"/>
            <path d="M5 5 L5 8 M5 5 L8 5" stroke="#ff7a3d" stroke-width="1.2" stroke-linecap="round" fill="none"/>
            <path d="M27 27 L27 24 M27 27 L24 27" stroke="#ff7a3d" stroke-width="1.2" stroke-linecap="round" fill="none"/>
            <path d="M9 9h14M9 16h10M9 23h12" stroke="url(#lg)" stroke-width="2.5" stroke-linecap="round" fill="none"/>
          </svg>
        </span>
        <span class="logo-text">
          <strong>FEI</strong><span class="logo-sub">Companion</span>
        </span>
      </NuxtLink>

      <nav class="nav" :class="{ open: menuOpen }">
        <NuxtLink to="/courses" @click="menuOpen=false">Programs</NuxtLink>
        <NuxtLink to="/freshman" @click="menuOpen=false">Survival</NuxtLink>
        <NuxtLink to="/tutor" @click="menuOpen=false" class="hot-link">Tutor<span class="new-dot"></span></NuxtLink>
        <NuxtLink to="/jobfair" @click="menuOpen=false">JobFair</NuxtLink>
        <a href="https://is.stuba.sk/" target="_blank" rel="noopener" class="ext">AIS ↗</a>
      </nav>

      <button class="burger" @click="menuOpen=!menuOpen" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
</template>

<script setup>
const menuOpen = ref(false)
</script>

<style scoped>
.header {
  position: sticky; top: 0; z-index: 50;
  backdrop-filter: blur(14px);
  background: rgba(6, 13, 26, 0.7);
  border-bottom: 1px solid var(--border);
}
.header-inner {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 24px;
}
.logo { display: flex; align-items: center; gap: 12px; color: var(--text); }
.logo-mark { display: inline-flex; }
.logo-text strong { font-weight: 800; letter-spacing: -0.02em; font-size: 1.1rem; }
.logo-sub { color: var(--text-dim); margin-left: 6px; font-size: 0.95rem; }
.nav { display: flex; align-items: center; gap: 28px; }
.nav a {
  color: var(--text-dim); font-weight: 500; font-size: 0.95rem;
  padding: 6px 0; position: relative;
}
.nav a:hover { color: var(--text); }
.nav a.router-link-active::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: -4px;
  height: 2px; background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 2px;
}
.nav .ext { color: var(--accent); }
.hot-link { position: relative; }
.new-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--hazard, #ff7a3d); box-shadow: 0 0 6px var(--hazard, #ff7a3d);
  display: inline-block; margin-left: 4px; vertical-align: super;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 50% { opacity: 0.35; } }

.burger { display: none; flex-direction: column; gap: 5px; padding: 12px; width: 44px; height: 44px; align-items: center; justify-content: center; }
.burger span { width: 22px; height: 2px; background: var(--text); border-radius: 1px; }

@media (max-width: 760px) {
  .nav {
    position: absolute; top: 100%; left: 0; right: 0;
    flex-direction: column; align-items: flex-start;
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 16px 24px; gap: 4px;
    transform: translateY(-10px); opacity: 0; pointer-events: none;
    transition: all .2s ease;
  }
  .nav a { padding: 14px 0; width: 100%; min-height: 44px; display: flex; align-items: center; }
  .nav.open { transform: translateY(0); opacity: 1; pointer-events: auto; }
  .burger { display: flex; }
}
</style>
