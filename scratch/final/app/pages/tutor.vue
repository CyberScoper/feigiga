<template>
  <div class="tutor">
    <section class="page-hero">
      <div class="container">
        <span class="eyebrow">MODULE 04 / FRESHMAN TUTOR · B-MAT1 + B-FYZ1</span>
        <h1>The <em>two killers</em> of first year — <em>tamed.</em></h1>
        <p class="lead lead-editorial">~50 % of first-years fail Matematika 1 or Fyzika 1. This is your console: real syllabus, real PDFs from Marko/Chlpík, and a Gemini-powered tutor that explains step-by-step with rendered KaTeX. Multilingual (SK/EN/RU).</p>

        <div class="subj-switch" role="tablist">
          <button v-for="s in subjects" :key="s.id"
                  :class="{ sw: true, active: subject === s.id }"
                  @click="switchSubject(s.id)" role="tab" :aria-selected="subject === s.id">
            <Icon v-if="emojiToLucide(s.icon)" :name="emojiToLucide(s.icon)" class="sw-icon-svg" />
            <span v-else class="sw-icon">{{ s.icon }}</span>
            <div class="sw-body">
              <strong>{{ s.code }}</strong>
              <span>{{ s.name }}</span>
            </div>
          </button>
        </div>
      </div>
    </section>

    <section class="container tutor-grid">
      <!-- Sidebar -->
      <aside class="sidebar" v-if="data" :key="'sb-' + subject">
        <div class="card bracket meta">
          <h3>{{ data.name_sk }}</h3>
          <p class="muted-en">{{ data.name_en }} · {{ data.code }}</p>
          <dl class="kvs">
            <div><dt>Semester</dt><dd>{{ data.semester }}</dd></div>
            <div v-if="data.format"><dt>Formát</dt><dd>{{ data.format }}</dd></div>
            <div v-if="data.lecturer"><dt>Prednáša</dt><dd>{{ data.lecturer }}</dd></div>
            <div v-if="data.guarantor"><dt>Garant</dt><dd>{{ data.guarantor }}</dd></div>
          </dl>
        </div>

        <div class="card grading">
          <h4 class="spec-mark">Hodnotenie</h4>
          <p class="g-split">{{ data.grading.split }}</p>
          <p class="g-min"><span class="dot-w"></span> Minimum: {{ data.grading.min_admit }}</p>
          <p v-if="data.grading.passing_grade_E" class="g-pass"><span class="dot-c"></span> Prejdeš na E: {{ data.grading.passing_grade_E }}</p>
          <p class="g-rule"><Icon name="lucide:triangle-alert" class="ico-sm ico-warn" /> {{ data.grading.rule }}</p>
        </div>

        <div v-if="data.key_dates_2026?.length" class="card">
          <h4 class="spec-mark">Kontrolky 2026</h4>
          <div v-for="k in data.key_dates_2026" :key="k.date" class="date-row">
            <span class="d-date mono">{{ formatDate(k.date) }}</span>
            <div>
              <strong>{{ k.label.split('—')[0] }}</strong>
              <p class="muted">{{ k.label.split('—').slice(1).join('—').trim() }}</p>
              <span class="d-weight">{{ k.weight }}</span>
            </div>
          </div>
        </div>

        <div v-if="data.parallels?.length" class="card">
          <h4 class="spec-mark">Paralelky</h4>
          <ul class="plain">
            <li v-for="p in data.parallels" :key="p.id">
              <strong>{{ p.id }}</strong> — {{ p.name.replace(p.id + ' — ', '') }}
              <span class="muted block">{{ p.lecturer }}</span>
            </li>
          </ul>
        </div>

        <div class="card">
          <h4 class="spec-mark">Témy semestra</h4>
          <ol class="topics-list">
            <li v-for="t in data.topics" :key="t.id"
                :class="{ active: selectedTopic?.id === t.id }"
                @click="selectedTopic = t">
              <span class="t-num mono">{{ String(t.n).padStart(2, '0') }}</span>
              <div><strong>{{ t.title }}</strong>
                <p>{{ t.summary }}</p>
              </div>
            </li>
          </ol>
        </div>

        <div class="card danger">
          <h4 class="spec-mark danger-h"><Icon name="lucide:triangle-alert" class="ico-xs" /> Kde to padá</h4>
          <ul class="plain danger-list">
            <li v-for="d in data.danger_zones" :key="d">{{ d }}</li>
          </ul>
        </div>

        <div class="card">
          <h4 class="spec-mark"><Icon name="lucide:file-text" class="ico-xs" /> Skriptá & PDF</h4>
          <ul class="plain pdfs">
            <li v-for="p in data.pdfs" :key="p.url">
              <a :href="p.url" target="_blank" rel="noopener">→ {{ p.title }} ↗</a>
            </li>
          </ul>
        </div>
      </aside>

      <!-- Console -->
      <main class="console" :key="'cn-' + subject">
        <div class="console-frame bracket">
          <header class="cf-top">
            <span class="dot rec"></span>
            <span class="cf-title mono">FEI TUTOR · {{ data?.code }} <span v-if="selectedTopic" class="cf-topic">// {{ selectedTopic.title }}</span></span>
            <button v-if="messages.length" class="cf-reset" @click="resetChat" title="Reset">↺ RESET</button>
          </header>

          <div class="messages" ref="msgsEl">
            <div v-if="!messages.length" class="empty">
              <Icon v-if="emojiToLucide(data?.icon)" :name="emojiToLucide(data?.icon)" class="big-icon" />
              <p v-else class="big-emoji">{{ data?.icon }}</p>
              <p class="m-title">Pýtaj sa. Vlož úlohu v slovenčine, angličtine alebo s LaTeX-om.</p>
              <p class="m-sub">Príklady: <button class="ex" v-for="ex in examples" :key="ex" @click="problem = ex">{{ ex.slice(0, 60) }}{{ ex.length > 60 ? '…' : '' }}</button></p>
            </div>

            <article v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
              <div class="m-head">
                <span class="m-role">{{ m.role === 'user' ? 'YOU' : 'TUTOR' }}</span>
                <span class="m-meta mono" v-if="m.role === 'assistant'">gemini-2.5-flash</span>
              </div>
              <div class="m-body">
                <KatexRender v-if="m.role === 'assistant'" :text="m.content" />
                <pre v-else class="user-text">{{ m.content }}</pre>
              </div>
            </article>

            <div v-if="loading" class="loading">
              <div class="bars"><span></span><span></span><span></span></div>
              <span class="l-text">FEI Tutor počíta… <em>(typicky 3-7 s pre Gemini)</em></span>
            </div>
          </div>

          <form class="composer" @submit.prevent="ask">
            <textarea v-model="problem"
                      :placeholder="placeholder"
                      rows="3"
                      @keydown.enter.exact.prevent="ask"
                      @keydown.shift.enter="newline"
                      :disabled="loading"></textarea>
            <div class="composer-row">
              <span class="hint mono">Enter = odoslať · Shift+Enter = riadok · $...$ pre formuly</span>
              <button type="submit" class="btn btn-primary" :disabled="loading || !problem.trim()">
                {{ loading ? '...' : 'Vyriešiť →' }}
              </button>
            </div>
          </form>
        </div>
      </main>
    </section>
  </div>
</template>

<script setup>
useHead({
  title: 'Math 1 + Physics 1 Tutor — FEI Companion',
  meta: [{ name: 'description', content: 'Step-by-step Gemini-powered tutor for B-MAT1 (Matematika 1) and B-FYZ1 (Fyzika 1) at FEI STU. Renders KaTeX, cites Marko/Chlpík PDFs.' }]
})

const subjects = [
  { id: 'math1', icon: '📐', code: 'B-MAT1', name: 'Matematika 1' },
  { id: 'fyz1',  icon: '🧲', code: 'B-FYZ1', name: 'Fyzika 1' }
]
const subject = ref('math1')

const { data: math1Data } = await useFetch('/data/math1.json')
const { data: fyz1Data }  = await useFetch('/data/fyz1.json')
const data = computed(() => subject.value === 'math1' ? math1Data.value : fyz1Data.value)

const selectedTopic = ref(null)
const messages = ref([])
const problem = ref('')
const loading = ref(false)
const msgsEl = ref(null)

const placeholder = computed(() =>
  subject.value === 'math1'
    ? 'Vypočítaj $\\lim_{x\\to 0} \\frac{\\sin 2x}{x}$ — alebo vlož aj fotku z prednášky popisom slovami.'
    : 'Spočítaj moment zotrvačnosti tyče dĺžky $L$ a hmotnosti $m$ okolo osi cez okraj.'
)

const examples = computed(() => subject.value === 'math1'
  ? [
      'Vypočítaj $\\lim_{x\\to 0} \\frac{\\sin 2x}{\\ln(1+3x)}$',
      'Nájdi inverznú maticu k $\\begin{pmatrix} 2 & 1 \\\\ 5 & 3 \\end{pmatrix}$',
      'Rozhodni o konvergencii radu $\\sum_{n=1}^\\infty \\frac{n!}{n^n}$',
      'Rozvinˇ funkciu $\\sin x$ do Taylorovho radu do 5. rádu okolo $x_0 = 0$.'
    ]
  : [
      'Auto sa rozbieha s konštantným zrýchlením $a = 2 \\, \\mathrm{m/s^2}$. Aká je rýchlosť po 10 s a prejdená dráha?',
      'Pružina s tuhosťou $k = 200 \\, \\mathrm{N/m}$ a hmotnosťou $m = 0{,}5 \\, \\mathrm{kg}$ — vlastná frekvencia?',
      'Tyč dĺžky $L$, hmotnosti $m$ — moment zotrvačnosti k osi cez koniec (použi Steinerovu vetu).',
      'V plne ponorenom telese $V = 0{,}1 \\, \\mathrm{m^3}$ — aká je vztlaková sila vo vode?'
    ]
)

function switchSubject(s) {
  if (s === subject.value) return
  subject.value = s
  selectedTopic.value = null
  // Keep messages separately per subject in sessionStorage
  loadHistory()
}

watch(subject, () => loadHistory(), { immediate: false })

function newline() { problem.value += '\n' }

function scroll() {
  nextTick(() => { if (msgsEl.value) msgsEl.value.scrollTop = msgsEl.value.scrollHeight })
}

async function ask() {
  const p = problem.value.trim()
  if (!p || loading.value) return
  messages.value.push({ role: 'user', content: p })
  problem.value = ''
  loading.value = true
  scroll()
  try {
    const res = await $fetch('/api/tutor', {
      method: 'POST',
      body: {
        subject: subject.value,
        topic: selectedTopic.value?.title,
        problem: p,
        history: messages.value.slice(-7, -1)
      }
    })
    if (res?.reply) {
      messages.value.push({ role: 'assistant', content: res.reply })
    } else {
      messages.value.push({ role: 'assistant', content: `⚠ ${res?.error || 'Nepodarilo sa získať odpoveď.'} — skús to znova alebo skontroluj /api/tutor.` })
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `⚠ Sieťová chyba: ${e.message}` })
  } finally {
    loading.value = false
    saveHistory()
    scroll()
  }
}

function resetChat() {
  messages.value = []
  saveHistory()
}

const STORAGE_KEY = (s) => `fei.tutor.${s}.v1`
function loadHistory() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY(subject.value))
    messages.value = raw ? JSON.parse(raw) : []
  } catch { messages.value = [] }
}
function saveHistory() {
  try { sessionStorage.setItem(STORAGE_KEY(subject.value), JSON.stringify(messages.value.slice(-30))) } catch {}
}
onMounted(() => loadHistory())

function formatDate(iso) {
  const d = new Date(iso)
  const months = ['Jan','Feb','Mar','Apr','Máj','Jún','Júl','Aug','Sep','Okt','Nov','Dec']
  return `${d.getDate()}. ${months[d.getMonth()]} ${d.getFullYear()}`
}
</script>

<style scoped>
.page-hero { padding: 50px 0 26px; }
.lead { color: var(--text-dim); font-size: 1.1rem; max-width: 760px; margin: 18px 0 28px; }

/* Subject switcher */
.subj-switch { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px; }
.sw {
  display: flex; gap: 14px; align-items: center;
  padding: 14px 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  cursor: pointer; transition: all .15s;
  min-width: 220px; text-align: left;
}
.sw:hover { border-color: var(--line-strong); transform: translateY(-1px); }
.sw.active {
  border-color: var(--hazard);
  background: rgba(255, 122, 61, 0.06);
  box-shadow: 0 0 0 1px var(--hazard);
}
.sw-icon { font-size: 1.8rem; }
.sw-icon-svg { font-size: 1.8rem; color: var(--hazard); }
.sw.active .sw-icon-svg { color: var(--hazard); }
.sw-body { display: flex; flex-direction: column; gap: 2px; }
.sw-body strong { font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.1em; color: var(--hazard); }
.sw-body span { font-size: 0.96rem; color: var(--text); font-weight: 600; }

/* Grid layout */
.tutor-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 28px;
  padding: 30px 0 80px;
  align-items: start;
}
@media (max-width: 980px) {
  .tutor-grid {
    display: flex;
    flex-direction: column;
    padding: 24px 0 60px;
  }
  .tutor-grid > .console { order: -1; }
  .tutor-grid > .sidebar { order: 1; }
}

/* Subject swap entrance */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.sidebar { animation: fadeUp .4s ease both; }
.console { animation: fadeUp .4s .1s ease both; }

/* Sidebar cards */
.sidebar { display: flex; flex-direction: column; gap: 14px; }
.sidebar .card { padding: 20px 22px; }
.meta h3 { font-size: 1.4rem; }
.muted-en { color: var(--text-muted); font-family: var(--font-serif); font-style: italic; font-size: 0.92rem; margin-top: 2px; }
.kvs { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; font-size: 0.88rem; }
.kvs > div { display: grid; grid-template-columns: 90px 1fr; gap: 10px; padding: 6px 0; border-bottom: 1px dashed var(--line); }
.kvs > div:last-child { border-bottom: none; }
.kvs dt { color: var(--text-muted); font-family: var(--font-mono); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; padding-top: 2px; }
.kvs dd { color: var(--text); }

.grading { background: linear-gradient(135deg, rgba(255, 122, 61, 0.06), transparent); border-color: rgba(255, 122, 61, 0.25); }
.g-split { font-family: var(--font-mono); color: var(--hazard); font-size: 0.95rem; margin: 6px 0 10px; }
.g-min, .g-pass, .g-rule { font-size: 0.85rem; color: var(--text-dim); padding: 5px 0; display: flex; gap: 8px; align-items: flex-start; }
.dot-w, .dot-c { width: 7px; height: 7px; border-radius: 50%; flex: 0 0 7px; margin-top: 6px; }
.dot-w { background: var(--gold); box-shadow: 0 0 6px var(--gold); }
.dot-c { background: var(--cyan); box-shadow: 0 0 6px var(--cyan); }
.g-rule { color: var(--rust); font-style: italic; }

.spec-mark { font-family: var(--font-mono); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--text-muted); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.spec-mark::before { content: ''; width: 18px; height: 1px; background: var(--line-strong); }
.danger-h { color: var(--rust); }
.danger-h::before { background: var(--rust); }

.date-row { display: grid; grid-template-columns: 90px 1fr; gap: 12px; padding: 10px 0; border-bottom: 1px dashed var(--line); }
.date-row:last-child { border-bottom: none; }
.d-date { color: var(--hazard); font-size: 0.8rem; font-weight: 700; padding-top: 2px; }
.d-weight {
  display: inline-block; margin-top: 4px;
  padding: 2px 8px; border-radius: 999px;
  background: var(--accent-dim); color: var(--hazard);
  font-family: var(--font-mono); font-size: 0.65rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.date-row strong { display: block; font-size: 0.92rem; }
.date-row .muted { font-size: 0.82rem; color: var(--text-muted); margin-top: 2px; }

.plain { list-style: none; padding: 0; }
.plain li { padding: 8px 0; border-bottom: 1px dashed var(--line); font-size: 0.9rem; color: var(--text-dim); }
.plain li:last-child { border-bottom: none; }
.plain strong { color: var(--text); }
.block { display: block; margin-top: 2px; }

.topics-list { padding: 0; list-style: none; }
.topics-list li {
  display: grid; grid-template-columns: 36px 1fr; gap: 12px;
  padding: 12px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background .15s, border-color .15s, color .15s;
  margin-bottom: 4px;
}
.topics-list li:hover { background: rgba(127, 219, 255, 0.05); }
.topics-list li.active { background: rgba(255, 122, 61, 0.08); border: 1px solid rgba(255, 122, 61, 0.3); }
.t-num {
  font-size: 0.72rem; font-weight: 700; color: var(--hazard);
  padding-top: 2px;
}
.topics-list strong { display: block; font-size: 0.92rem; margin-bottom: 2px; }
.topics-list p { font-size: 0.82rem; color: var(--text-muted); line-height: 1.45; }

.danger { background: linear-gradient(135deg, rgba(212, 75, 46, 0.06), transparent); border-color: rgba(212, 75, 46, 0.22); }
.danger-list li { color: var(--text-dim); font-size: 0.88rem; padding-left: 18px; position: relative; }
.danger-list li::before { content: '⚠'; position: absolute; left: 0; color: var(--rust); font-size: 0.85rem; }

.pdfs li { padding-left: 0; }
.pdfs a { color: var(--cyan); font-size: 0.88rem; }
.pdfs a:hover { color: var(--cyan-2); }

/* === Console === */
.console-frame {
  background: linear-gradient(180deg, var(--surface) 0%, var(--surface-2) 100%);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  display: flex; flex-direction: column;
  min-height: 640px;
  position: sticky; top: 90px;
}
@media (max-width: 980px) {
  .console-frame { position: static; min-height: 520px; }
}
.cf-top {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 20px;
  font-family: var(--font-mono); font-size: 0.72rem;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px dashed var(--line-strong);
}
.cf-title { color: var(--text-dim); font-weight: 600; flex: 1; }
.cf-topic { color: var(--hazard); }
.cf-reset {
  font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.1em;
  color: var(--text-muted); padding: 8px 12px; border-radius: 4px;
  border: 1px solid var(--line-strong);
  min-height: 36px;
  transition: color .15s, border-color .15s, background .15s;
}
.cf-reset:hover { color: var(--rust); border-color: var(--rust); }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--rust); box-shadow: 0 0 8px var(--rust); }
.dot.rec { animation: blink-rec 1.4s ease-in-out infinite; }
@keyframes blink-rec { 50% { opacity: 0.35; } }

.messages {
  flex: 1; padding: 22px;
  overflow-y: auto;
  background:
    repeating-linear-gradient(0deg, transparent 0, transparent 31px, rgba(127, 219, 255, 0.025) 31px, rgba(127, 219, 255, 0.025) 32px);
  background-position: 0 22px;
  max-height: 70vh;
}
.empty { text-align: center; padding: 56px 20px; color: var(--text-muted); }
.big-emoji { font-size: 3rem; margin-bottom: 14px; line-height: 1; }
.big-icon { font-size: 3.2rem; color: var(--hazard); margin-bottom: 14px; line-height: 1; }
.m-title { font-size: 1.05rem; color: var(--text); margin-bottom: 14px; }
.m-sub { font-size: 0.85rem; color: var(--text-muted); display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.ex {
  padding: 8px 12px; border-radius: 4px;
  background: rgba(127, 219, 255, 0.06);
  border: 1px dashed rgba(127, 219, 255, 0.3);
  color: var(--cyan); font-size: 0.78rem; font-family: var(--font-mono);
  cursor: pointer; transition: background .15s, border-style .15s, color .15s;
  max-width: 100%;
  overflow-wrap: anywhere;
}
.ex:hover { background: rgba(127, 219, 255, 0.15); border-style: solid; }

.msg { margin-bottom: 22px; }
.m-head {
  display: flex; gap: 10px; align-items: center;
  font-family: var(--font-mono); font-size: 0.68rem;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-muted); margin-bottom: 8px;
}
.m-role { font-weight: 700; padding: 3px 8px; border-radius: 4px; }
.msg.user .m-role { color: var(--hazard); background: var(--accent-dim); }
.msg.assistant .m-role { color: var(--cyan); background: var(--primary-dim); }
.m-meta { color: var(--text-muted); }
.user-text {
  white-space: pre-wrap; word-wrap: break-word; font-family: var(--font-body);
  color: var(--text); background: rgba(255, 122, 61, 0.05);
  border-left: 2px solid var(--hazard);
  padding: 12px 14px; border-radius: 4px; font-size: 0.95rem;
}
.loading {
  display: flex; gap: 14px; align-items: center;
  padding: 14px; color: var(--text-dim); font-size: 0.9rem;
}
.bars { display: flex; gap: 4px; }
.bars span {
  width: 4px; height: 18px; background: var(--cyan); border-radius: 2px;
  animation: bar 1s ease-in-out infinite;
}
.bars span:nth-child(2) { animation-delay: 0.15s; }
.bars span:nth-child(3) { animation-delay: 0.3s; }
@keyframes bar { 0%, 100% { transform: scaleY(0.3); } 50% { transform: scaleY(1); } }
.l-text em { color: var(--text-muted); font-style: normal; font-family: var(--font-mono); font-size: 0.78rem; }

.composer {
  border-top: 1px dashed var(--line-strong);
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.15);
}
.composer textarea {
  width: 100%;
  background: var(--bg-deep);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  color: var(--text);
  padding: 12px 14px;
  font-family: var(--font-body); font-size: 0.95rem;
  resize: vertical; min-height: 64px; max-height: 200px;
}
.composer textarea:focus { outline: none; border-color: var(--cyan); box-shadow: 0 0 0 2px rgba(127, 219, 255, 0.15); }
.composer textarea:disabled { opacity: 0.5; }
.composer-row { display: flex; justify-content: space-between; align-items: center; gap: 14px; margin-top: 10px; flex-wrap: wrap; }
.hint { font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.06em; }

@media (max-width: 760px) {
  .composer textarea { font-size: 16px; }
}

@media (max-width: 560px) {
  .subj-switch { flex-direction: column; }
  .sw { min-width: 0; width: 100%; }
  .cf-top { font-size: 0.62rem; padding: 12px 14px; }
  .cf-topic { display: block; }
  .messages { padding: 16px; max-height: 60vh; }
  .composer { padding: 12px 14px; }
  .composer textarea { font-size: 16px; }
  .composer-row { flex-direction: column; align-items: stretch; }
  .composer-row .btn { width: 100%; justify-content: center; }
}
</style>
