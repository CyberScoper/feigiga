<template>
  <div>
    <section class="hero">
      <div class="container hero-inner">
        <div class="hero-content fade-up">
          <span class="eyebrow">REV.01 · FEI STU BRATISLAVA · CLASS OF 2030</span>
          <h1>
            Your <em>unfair</em> advantage<br/>
            at <em>FEI STU</em>.
          </h1>
          <p class="lead lead-editorial">
            Three modules. One companion. Explore <strong>9 bachelor programs</strong>,
            survive the <strong>first 30 days</strong>, match with <strong>16+ JobFair employers</strong>
            — all wired to a multilingual AI tutor.
          </p>
          <div class="cta-row">
            <NuxtLink to="/courses" class="btn btn-primary">
              Explore programs →
            </NuxtLink>
            <NuxtLink to="/freshman" class="btn btn-ghost">
              Freshman? Start here
            </NuxtLink>
          </div>
          <div class="stats">
            <div class="stat"><strong class="tabular">99%</strong><span class="unit">EMP-RATE</span><span>employment rate</span></div>
            <div class="stat"><strong class="tabular">2940</strong><span class="unit">EUR/MO</span><span>avg. salary (5y)</span></div>
            <div class="stat"><strong class="tabular">2368</strong><span class="unit">STUDENTS</span><span>active students</span></div>
            <div class="stat"><strong class="tabular">1951</strong><span class="unit">SINCE</span><span>since</span></div>
          </div>
        </div>
        <div class="hero-visual fade-up">
          <div class="scope">
            <header class="scope-top">
              <span class="dot rec"></span>
              <span class="t-label">FEI · SIGNAL ANALYZER</span>
              <span class="t-time mono">{{ scopeClock }}</span>
            </header>

            <svg class="scope-svg" viewBox="0 0 320 220" preserveAspectRatio="none" aria-hidden="true">
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(127,219,255,0.10)" stroke-width="0.5"/>
                </pattern>
                <pattern id="gridLg" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(127,219,255,0.20)" stroke-width="0.7"/>
                </pattern>
              </defs>

              <!-- Grid -->
              <rect x="0" y="0" width="320" height="220" fill="url(#grid)"/>
              <rect x="0" y="0" width="320" height="220" fill="url(#gridLg)"/>

              <!-- Center crosshairs -->
              <line x1="0" y1="110" x2="320" y2="110" stroke="rgba(127,219,255,0.35)" stroke-width="0.6" stroke-dasharray="2,4"/>
              <line x1="160" y1="0" x2="160" y2="220" stroke="rgba(127,219,255,0.35)" stroke-width="0.6" stroke-dasharray="2,4"/>

              <!-- Sine wave — CH1 (PROGRAMS) — cyan -->
              <path class="wave w1"
                    d="M0,110 Q40,70 80,110 T160,110 T240,110 T320,110"
                    fill="none" stroke="#7fdbff" stroke-width="1.6" stroke-linecap="round"/>

              <!-- Sine wave — CH2 (SURVIVAL) — orange, slower -->
              <path class="wave w2"
                    d="M0,110 Q30,140 60,110 T120,110 T180,110 T240,110 T320,110"
                    fill="none" stroke="#ff7a3d" stroke-width="1.4" stroke-linecap="round" opacity="0.85"/>

              <!-- Square wave — CH3 (JOBFAIR) — yellow -->
              <path class="wave w3"
                    d="M0,110 L20,110 L20,90 L60,90 L60,130 L100,130 L100,90 L140,90 L140,130 L180,130 L180,90 L220,90 L220,130 L260,130 L260,90 L300,90 L300,110 L320,110"
                    fill="none" stroke="#ffce4f" stroke-width="1.2" stroke-linecap="square" opacity="0.7"/>

              <!-- Sample points -->
              <g class="samples">
                <circle cx="40" cy="76" r="2.5" fill="#7fdbff"/>
                <circle cx="120" cy="76" r="2.5" fill="#7fdbff"/>
                <circle cx="200" cy="76" r="2.5" fill="#7fdbff"/>
                <circle cx="280" cy="76" r="2.5" fill="#7fdbff"/>
              </g>

              <!-- Axis labels -->
              <g font-family="JetBrains Mono" font-size="6" fill="#6d7d97">
                <text x="4" y="14">+1.0</text>
                <text x="4" y="114">  0</text>
                <text x="4" y="214">-1.0</text>
                <text x="296" y="216" text-anchor="end">t →</text>
              </g>

              <!-- Trigger marker -->
              <g transform="translate(40 6)">
                <path d="M0 0 L8 0 L4 6 Z" fill="#ff7a3d"/>
                <text x="12" y="6" font-family="JetBrains Mono" font-size="6" fill="#ff7a3d">TRIG</text>
              </g>

              <!-- Cursor marker (right side) -->
              <line x1="240" y1="0" x2="240" y2="220" stroke="#ff7a3d" stroke-width="0.6" stroke-dasharray="3,3"/>
              <g transform="translate(244 16)">
                <rect x="0" y="-9" width="56" height="11" fill="#0a1726" stroke="#ff7a3d" stroke-width="0.5"/>
                <text x="3" y="-1" font-family="JetBrains Mono" font-size="6" fill="#ff7a3d">CURSOR A</text>
              </g>
            </svg>

            <footer class="scope-channels">
              <NuxtLink to="/courses" class="ch ch-1 fade-up" :style="`animation-delay: ${0 * 80 + 350}ms`">
                <span class="ch-led"></span>
                <span class="ch-name">CH1</span>
                <span class="ch-sig">PROGRAMS · 9 / 9</span>
              </NuxtLink>
              <NuxtLink to="/freshman" class="ch ch-2 fade-up" :style="`animation-delay: ${1 * 80 + 350}ms`">
                <span class="ch-led"></span>
                <span class="ch-name">CH2</span>
                <span class="ch-sig">SURVIVAL · 30 d</span>
              </NuxtLink>
              <NuxtLink to="/jobfair" class="ch ch-3 fade-up" :style="`animation-delay: ${2 * 80 + 350}ms`">
                <span class="ch-led"></span>
                <span class="ch-name">CH3</span>
                <span class="ch-sig">JOBFAIR · 16</span>
              </NuxtLink>
            </footer>
          </div>
        </div>
      </div>
    </section>

    <section class="section pillars">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">SECTION 01 · THREE MODULES</span>
          <h2>Engineered for every stage of your <em>FEI</em> journey.</h2>
        </div>
        <div class="grid grid-3 stagger">
          <NuxtLink to="/courses" class="pillar pillar-blue">
            <div class="pillar-icon"><Icon name="lucide:compass" class="ico-xl ico-hazard" /></div>
            <h3>Course Explorer</h3>
            <p>Navigate all 9 bachelor programs. Filter by interest. AI-quiz to find the perfect fit.</p>
            <span class="pillar-arrow">Explore →</span>
          </NuxtLink>
          <NuxtLink to="/freshman" class="pillar pillar-cyan">
            <div class="pillar-icon"><Icon name="lucide:backpack" class="ico-xl ico-cyan" /></div>
            <h3>Freshman Survival Kit</h3>
            <p>Campus map, first-week to-do, Slovak survival phrases, emergency contacts.</p>
            <span class="pillar-arrow">Survive →</span>
          </NuxtLink>
          <NuxtLink to="/jobfair" class="pillar pillar-hot">
            <div class="pillar-icon"><Icon name="lucide:briefcase" class="ico-xl ico-warn" /></div>
            <h3>JobFair Match</h3>
            <p>Match your skills with employers from FEI JobFair. AI-powered career fit.</p>
            <span class="pillar-arrow">Match →</span>
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="section quick">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">SECTION 02 · QUICK ACCESS</span>
          <h2>Faculty essentials, <em>one click</em> away.</h2>
        </div>
        <div class="grid grid-4 stagger">
          <a href="https://is.stuba.sk/" target="_blank" rel="noopener" class="card link-card">
            <div class="lc-icon"><Icon name="lucide:key" class="ico-lg ico-hazard" /></div>
            <h3>AIS</h3>
            <p>Academic info system. Schedule, grades, registration.</p>
          </a>
          <a href="https://www.fei.stuba.sk/" target="_blank" rel="noopener" class="card link-card">
            <div class="lc-icon"><Icon name="lucide:globe" class="ico-lg ico-cyan" /></div>
            <h3>Faculty site</h3>
            <p>Official FEI STU news, events, announcements.</p>
          </a>
          <a href="https://www.fei.stuba.sk/sk/studenti/ubytovanie.html" target="_blank" rel="noopener" class="card link-card">
            <div class="lc-icon"><Icon name="lucide:house" class="ico-lg ico-signal" /></div>
            <h3>Accommodation</h3>
            <p>Dormitory info & application.</p>
          </a>
          <a href="https://www.office.com/" target="_blank" rel="noopener" class="card link-card">
            <div class="lc-icon"><Icon name="lucide:mail" class="ico-lg ico-muted" /></div>
            <h3>Webmail</h3>
            <p>STU Office 365 mail.</p>
          </a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const scopeClock = ref('00:00:00')
onMounted(() => {
  const tick = () => { scopeClock.value = new Date().toTimeString().slice(0, 8) }
  tick()
  const id = setInterval(tick, 1000)
  onBeforeUnmount(() => clearInterval(id))
})
useHead({
  title: 'FEI Companion — Ultimate Student Hub for FEI STU Bratislava',
  meta: [
    { name: 'description', content: 'Explore study programs, survive your first week, and match with JobFair employers. AI-powered companion for FEI STU students.' }
  ]
})
</script>

<style scoped>
.hero { padding: 60px 0 80px; }
.hero-inner {
  display: grid; grid-template-columns: 1.2fr 1fr; gap: 60px; align-items: center;
}
.hero-content .badge { margin-bottom: 22px; }
.lead { font-size: 1.2rem; color: var(--text-dim); margin: 22px 0 32px; max-width: 540px; }
.cta-row { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 50px; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; max-width: 580px; }
.stat strong {
  display: block; font-size: 1.7rem; font-weight: 800;
  color: var(--hazard);
  background: none;
  -webkit-text-fill-color: initial;
}
.stat .unit {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--text-muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  display: block;
  margin-top: 4px;
}
.tabular { font-variant-numeric: tabular-nums; }
.stat span { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

.hero-visual { display: flex; justify-content: center; align-items: center; min-height: 460px; }

.scope {
  width: 100%; max-width: 480px;
  background: linear-gradient(180deg, #0a1726 0%, #08131f 100%);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  padding: 18px;
  position: relative;
  box-shadow:
    inset 0 0 60px rgba(127, 219, 255, 0.04),
    0 30px 60px -20px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(127, 219, 255, 0.05);
}
.scope::before, .scope::after {
  content: ''; position: absolute; width: 18px; height: 18px;
  border: 1.5px solid var(--hazard);
  pointer-events: none;
}
.scope::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
.scope::after  { bottom: -1px; right: -1px; border-left: none; border-top: none; }

.scope-top {
  display: flex; align-items: center; gap: 12px;
  padding-bottom: 12px;
  margin-bottom: 6px;
  border-bottom: 1px dashed var(--line-strong);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  animation: fadeUp .8s .15s both;
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--rust);
  box-shadow: 0 0 8px var(--rust);
}
.dot.rec { animation: rec-blink 1.6s ease-in-out infinite; }
@keyframes rec-blink { 50% { opacity: 0.3; } }
.t-label { color: var(--text-dim); font-weight: 600; }
.t-time { margin-left: auto; color: var(--cyan); }

.scope-svg {
  width: 100%; height: auto; aspect-ratio: 320 / 220;
  display: block;
}
.wave { stroke-dasharray: 800; stroke-dashoffset: 800; }
.w1 { animation: draw 2.8s cubic-bezier(.4,0,.2,1) .2s forwards, drift 8s linear .4s infinite; }
.w2 { animation: draw 3.2s cubic-bezier(.4,0,.2,1) .5s forwards, drift 11s linear .8s infinite; }
.w3 { animation: draw 3.6s cubic-bezier(.4,0,.2,1) .8s forwards; }
@keyframes draw  { to { stroke-dashoffset: 0; } }
@keyframes drift {
  0%   { transform: translateX(0); }
  50%  { transform: translateX(-6px); }
  100% { transform: translateX(0); }
}
.samples circle { animation: blink 1.4s ease-in-out infinite alternate; }
.samples circle:nth-child(2) { animation-delay: .35s; }
.samples circle:nth-child(3) { animation-delay: .7s; }
.samples circle:nth-child(4) { animation-delay: 1.05s; }
@keyframes blink { 0% { opacity: 0.3; } 100% { opacity: 1; } }

.scope-channels {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px dashed var(--line-strong);
}
.ch {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 4px;
  text-decoration: none;
  transition: all .15s ease;
  background: rgba(15, 34, 58, 0.4);
}
.ch:hover { border-color: var(--cyan); transform: translateY(-2px); background: rgba(15, 34, 58, 0.7); }
.ch-led { width: 7px; height: 7px; border-radius: 50%; flex: 0 0 7px; }
.ch-1 .ch-led { background: var(--cyan); box-shadow: 0 0 6px var(--cyan); }
.ch-2 .ch-led { background: var(--hazard); box-shadow: 0 0 6px var(--hazard); }
.ch-3 .ch-led { background: var(--signal); box-shadow: 0 0 6px var(--signal); }
.ch-name { font-family: var(--font-mono); font-size: 0.78rem; font-weight: 700; color: var(--text); }
.ch-sig  { font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-muted); letter-spacing: 0.06em; }

.section-head { text-align: center; margin-bottom: 50px; }
.section-head .badge { margin-bottom: 14px; }

.pillar {
  display: block;
  padding: 36px 30px;
  border-radius: var(--radius-lg);
  background: linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--border);
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
  position: relative; overflow: hidden;
  color: var(--text);
}
.pillar::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 0% 0%, var(--primary-dim), transparent 50%);
  opacity: 0; transition: opacity .25s;
}
.pillar:hover { transform: translateY(-4px); border-color: var(--border-strong); box-shadow: var(--shadow-glow); }
.pillar:hover::before { opacity: 1; }
.pillar-icon { margin-bottom: 16px; }
.pillar h3 { font-size: 1.4rem; margin-bottom: 10px; }
.pillar p { color: var(--text-dim); margin-bottom: 20px; }
.pillar-arrow { color: var(--primary); font-weight: 600; font-size: 0.95rem; position: relative; z-index: 1; }
.pillar-cyan:hover { box-shadow: var(--shadow-glow-accent); }
.pillar-cyan .pillar-arrow { color: var(--accent); }
.pillar-hot:hover { box-shadow: 0 0 40px rgba(212, 75, 46, 0.22); }
.pillar-hot .pillar-arrow { color: var(--hot); }

.link-card { color: var(--text); display: block; }
.lc-icon { margin-bottom: 12px; }
.link-card h3 { margin-bottom: 8px; }
.link-card p { color: var(--text-dim); font-size: 0.92rem; }

@media (max-width: 900px) {
  .hero-inner { grid-template-columns: 1fr; gap: 36px; }
  .hero-visual { order: -1; min-height: auto; }
  .scope { max-width: 100%; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  .lead { font-size: 1.05rem; }
  .cta-row { flex-direction: column; gap: 10px; }
  .cta-row .btn { width: 100%; justify-content: center; }
}
@media (max-width: 560px) {
  .scope { padding: 12px; }
  .scope-top { font-size: 0.62rem; gap: 8px; flex-wrap: wrap; }
  .scope-channels { grid-template-columns: 1fr; gap: 6px; }
  .ch { padding: 10px 14px; min-height: 48px; }
  .ch-sig { font-size: 0.72rem; }
  .pillar { padding: 26px 22px; }
  .pillar h3 { font-size: 1.2rem; }
  .stat strong { font-size: 1.5rem; }
}
</style>
