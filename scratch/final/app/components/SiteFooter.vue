<template>
  <footer class="footer">
    <div class="container footer-inner">
      <div class="col">
        <div class="brand">FEI Companion</div>
        <p class="muted">Ultimate hub for FEI STU Bratislava students. Not affiliated with FEI STU.</p>
      </div>
      <div class="col">
        <h4>Faculty links</h4>
        <a href="https://www.fei.stuba.sk/" target="_blank" rel="noopener">fei.stuba.sk</a>
        <a href="https://is.stuba.sk/" target="_blank" rel="noopener">AIS</a>
        <a href="https://www.fei.stuba.sk/sk/studium.html" target="_blank" rel="noopener">Štúdium</a>
      </div>
      <div class="col">
        <h4>App</h4>
        <NuxtLink to="/courses">Programs</NuxtLink>
        <NuxtLink to="/freshman">Survival Kit</NuxtLink>
        <NuxtLink to="/tutor">Math+Phys Tutor</NuxtLink>
        <NuxtLink to="/jobfair">JobFair</NuxtLink>
      </div>
      <div class="col">
        <h4>Built for</h4>
        <p class="muted">Master of VibeCoding 2026<br/>FEI STU × UMIKT × PosAm</p>
      </div>
    </div>
    <div class="container bottom">
      <span class="muted">© 2026 fei.murzin.digital</span>
      <span class="mono accent">v1.0</span>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: 80px;
  border-top: 1px solid var(--border);
  background: linear-gradient(180deg, transparent, rgba(0,0,0,0.3));
  padding: 60px 0 30px;
}
.footer-inner {
  display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr; gap: 40px;
}
.col h4 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 14px; }
.col a { display: block; color: var(--text-dim); padding: 4px 0; font-size: 0.92rem; }
.col a:hover { color: var(--primary); }
.brand { font-weight: 800; font-size: 1.2rem; margin-bottom: 10px; color: var(--text); letter-spacing: -0.015em; }
.brand::after { content: ' /'; color: var(--hazard); font-family: var(--font-mono); font-weight: 400; }
.muted { color: var(--text-muted); font-size: 0.88rem; }
.bottom { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 0.85rem; }
.accent { color: var(--accent); }
@media (max-width: 760px) {
  .footer-inner { grid-template-columns: 1fr 1fr; gap: 30px; }
}
</style>
