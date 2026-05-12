<template>
  <div class="freshman">
    <section class="page-hero">
      <div class="container">
        <span class="eyebrow">MODULE 02 / FRESHMAN SURVIVAL KIT</span>
        <h1>Your <em>first 30 days</em> at FEI, sorted.</h1>
        <p class="lead">Campus orientation, the must-do checklist, Slovak survival phrases, and emergency numbers — everything an Erasmus or first-year needs to stop guessing.</p>
        <div class="tabs">
          <button v-for="t in tabs" :key="t.id"
                  :class="{ tab: true, active: tab === t.id }"
                  @click="tab = t.id">
            <Icon :name="t.lucide" class="ico-sm" />
            {{ t.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="container content">
      <!-- TAB: Campus map -->
      <div v-if="tab === 'map'" class="map-tab">
        <div class="map-wrap">
          <div class="map-stage">
            <img class="map-image"
                 src="/assets/fei-map.jpg"
                 srcset="/assets/fei-map-900.jpg 900w, /assets/fei-map.jpg 1500w"
                 sizes="(max-width: 900px) 100vw, 720px"
                 alt="3D mapa areálu FEI STU, Ilkovičova 3, Bratislava"
                 loading="lazy"
                 decoding="async" />
            <div class="map-tint"></div>
            <div class="map-grid"></div>
            <span class="map-label mono">FEI STU · ILKOVIČOVA 3 · 3D PLAN</span>
            <div class="pin-layer">
              <button v-for="(p, i) in campusPoints" :key="p.id"
                      class="pin"
                      :class="{ active: selectedPoint?.id === p.id }"
                      :style="`left: ${p.x}%; top: ${p.y}%; animation: stagger-up .5s ${100 + i * 50}ms both;`"
                      @click="selectedPoint = p"
                      :aria-label="p.name_sk">
                <Icon v-if="emojiToLucide(p.icon)" :name="emojiToLucide(p.icon)" class="pin-icon-svg" />
                <span v-else class="pin-icon">{{ p.icon }}</span>
                <span class="pin-tip">{{ p.name_sk }}</span>
              </button>
            </div>
          </div>
          <div class="legend">
            <strong>{{ campusPoints.length }} key spots</strong>
            <span class="muted">Tap a pin to learn more</span>
          </div>
        </div>
        <aside class="point-detail" v-if="selectedPoint">
          <div class="pd-icon">
            <Icon v-if="emojiToLucide(selectedPoint.icon)" :name="emojiToLucide(selectedPoint.icon)" class="ico-xxl ico-cyan" />
            <span v-else>{{ selectedPoint.icon }}</span>
          </div>
          <h3>{{ selectedPoint.name_sk }}</h3>
          <p class="en">{{ selectedPoint.name_en }}</p>
          <p class="pd-desc">{{ selectedPoint.description }}</p>
          <div class="tips" v-if="selectedPoint.tips?.length">
            <h4><Icon name="lucide:lightbulb" class="ico-sm ico-signal" /> Tips</h4>
            <ul>
              <li v-for="t in selectedPoint.tips" :key="t">{{ t }}</li>
            </ul>
          </div>
        </aside>
        <aside class="point-detail empty" v-else>
          <p><Icon name="lucide:mouse-pointer-click" class="ico-md ico-cyan" /> Tap any pin on the map.</p>
        </aside>
      </div>

      <!-- TAB: Survival 101 -->
      <div v-if="tab === 'survival'" class="survival-tab">
        <div class="warning-banner">
          <span class="warning-icon"><Icon name="lucide:triangle-alert" class="ico-lg ico-warn" /></span>
          <div>
            <strong>Real talk from upperclassmen.</strong>
            <p>Below: the two subjects that filter out the most first-years, and the bureaucratic chaos nobody warns you about.</p>
          </div>
        </div>

        <h2 class="sec-title">The <em>two killers</em> of semester one.</h2>
        <div class="killer-grid">
          <article v-for="k in killerSubjects" :key="k.id" class="killer-card bracket">
            <header class="killer-head">
              <span class="killer-icon">
                <Icon v-if="emojiToLucide(k.icon)" :name="emojiToLucide(k.icon)" class="ico-xxl ico-hazard" />
                <span v-else>{{ k.icon }}</span>
              </span>
              <div>
                <h3>{{ k.name_sk }}</h3>
                <p class="muted-en">{{ k.name_en }}</p>
              </div>
              <span class="killer-rate">{{ k.pass_rate }}</span>
            </header>
            <p class="killer-warn">{{ k.warning }}</p>
            <div class="killer-cols">
              <div>
                <h4 class="spec-mark">Core topics</h4>
                <ul class="topic-list">
                  <li v-for="t in k.topics" :key="t">{{ t }}</li>
                </ul>
              </div>
              <div>
                <h4 class="spec-mark">Survival tactics</h4>
                <ul class="tip-list">
                  <li v-for="t in k.survival_tips" :key="t">{{ t }}</li>
                </ul>
              </div>
            </div>
            <div v-if="k.resources?.length" class="killer-res">
              <h4 class="spec-mark">Resources</h4>
              <div class="res-row">
                <a v-for="r in k.resources" :key="r.label" :href="r.url" target="_blank" rel="noopener" class="res-link">
                  → {{ r.label }} ↗
                </a>
              </div>
            </div>
          </article>
        </div>

        <h2 class="sec-title chaos-title">Then the <em>bureaucratic</em> chaos.</h2>
        <p class="dim chaos-sub">Six things they don't tell you about — TransCard, dorms, room codes, AIS, ISIC, menza.</p>
        <div class="chaos-grid">
          <article v-for="c in chaosItems" :key="c.id" class="chaos-card">
            <header class="chaos-head">
              <span class="chaos-icon">
                <Icon v-if="emojiToLucide(c.icon)" :name="emojiToLucide(c.icon)" class="ico-lg ico-cyan" />
                <span v-else>{{ c.icon }}</span>
              </span>
              <h3>{{ c.title_sk }}</h3>
            </header>
            <p class="chaos-sum">{{ c.summary }}</p>
            <ol class="chaos-steps">
              <li v-for="(s, i) in c.steps" :key="i">{{ s }}</li>
            </ol>
            <div v-if="c.links?.length" class="chaos-links">
              <a v-for="l in c.links" :key="l.label" :href="l.url" target="_blank" rel="noopener">
                {{ l.label }} ↗
              </a>
            </div>
          </article>
        </div>
      </div>

      <!-- TAB: To-do -->
      <div v-if="tab === 'todo'" class="todo-tab">
        <div class="todo-head">
          <h2>Your first-week checklist</h2>
          <span class="muted">{{ done }}/{{ todos.length }} done · {{ Math.round(done/todos.length*100) }}%</span>
        </div>
        <div class="progress-bar"><div :style="`width:${(done/todos.length)*100}%`"></div></div>
        <ul class="todos">
          <li v-for="(t, i) in todos" :key="t.id"
              class="todo" :class="[t.priority, { done: checked[t.id] }]"
              @click="toggle(t.id)">
            <span class="check"><Icon v-if="checked[t.id]" name="lucide:check" class="check-icon" /></span>
            <span class="todo-icon">
              <Icon v-if="emojiToLucide(t.icon)" :name="emojiToLucide(t.icon)" class="ico-lg ico-cyan" />
              <span v-else>{{ t.icon }}</span>
            </span>
            <div class="todo-body">
              <strong>{{ t.title_sk }}</strong>
              <span class="todo-en">{{ t.title_en }}</span>
              <p>{{ t.description }}</p>
            </div>
            <span class="prio-badge" :class="t.priority">{{ t.priority }}</span>
          </li>
        </ul>
      </div>

      <!-- TAB: Slovak phrases -->
      <div v-if="tab === 'phrases'" class="phrases-tab">
        <h2>30 Slovak survival phrases</h2>
        <div class="phrase-controls">
          <input v-model="phraseSearch" placeholder="Search phrases…" class="search" />
          <select v-model="phraseCat" class="search" style="flex:0 0 200px;">
            <option value="">All categories</option>
            <option v-for="c in phraseCategories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="grid grid-2 phrase-grid">
          <div v-for="p in filteredPhrases" :key="p.sk" class="phrase-card">
            <div class="phrase-top">
              <span class="sk">{{ p.sk }}</span>
              <button class="speak" @click="speak(p.sk)" title="Listen"><Icon name="lucide:volume-2" class="ico-sm" /></button>
            </div>
            <div class="pron mono">/ {{ p.pronunciation }} /</div>
            <div class="tr"><span class="flag">🇬🇧</span> {{ p.en }}</div>
            <div v-if="p.uk" class="tr"><span class="flag">🇺🇦</span> {{ p.uk }}</div>
            <div class="tr"><span class="flag">🇷🇺</span> {{ p.ru }}</div>
            <span class="cat-badge">{{ p.category }}</span>
          </div>
        </div>
      </div>

      <!-- TAB: Contacts -->
      <div v-if="tab === 'contacts'" class="contacts-tab">
        <h2>Emergency contacts</h2>
        <div class="grid grid-2">
          <div v-for="c in contacts" :key="c.name" class="card contact-card">
            <h3>{{ c.name }}</h3>
            <p class="muted">{{ c.purpose }}</p>
            <div class="contact-rows">
              <div><strong><Icon name="lucide:phone" class="ico-sm ico-hazard" /></strong> <a :href="`tel:${c.phone}`">{{ c.phone }}</a></div>
              <div><strong><Icon name="lucide:mail" class="ico-sm ico-cyan" /></strong> <a :href="`mailto:${c.email}`">{{ c.email }}</a></div>
              <div><strong><Icon name="lucide:clock" class="ico-sm ico-muted" /></strong> {{ c.hours }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
useHead({
  title: 'Freshman Survival Kit — FEI Companion',
  meta: [{ name: 'description', content: 'Campus map, first-week checklist, Slovak phrases, and emergency contacts for new FEI STU Bratislava students.' }]
})

const { data: freshmanData } = await useFetch('/data/freshman.json')
const { data: phrasesData } = await useFetch('/data/slovak_phrases.json')
const { data: survivalData } = await useFetch('/data/survival101.json')
const killerSubjects = computed(() => survivalData.value?.killer_subjects || [])
const chaosItems = computed(() => survivalData.value?.first_week_chaos || [])

const campusPoints = computed(() => freshmanData.value?.campus_points || [])
const todos = computed(() => freshmanData.value?.first_week_todo || [])
const contacts = computed(() => freshmanData.value?.emergency_contacts || [])
const phrases = computed(() => phrasesData.value?.phrases || [])

const tabs = [
  { id: 'map',      lucide: 'lucide:map',             label: 'Campus map' },
  { id: 'survival', lucide: 'lucide:triangle-alert',  label: 'Survival 101' },
  { id: 'todo',     lucide: 'lucide:list-checks',     label: 'First week' },
  { id: 'phrases',  lucide: 'lucide:languages',       label: 'Slovak 101' },
  { id: 'contacts', lucide: 'lucide:phone',           label: 'Contacts' }
]
const tab = ref('map')
const selectedPoint = ref(null)

// Auto-select first point
watch(campusPoints, (pts) => { if (pts.length && !selectedPoint.value) selectedPoint.value = pts[0] }, { immediate: true })

// To-do checklist with localStorage persistence
const checked = ref({})
onMounted(() => {
  try { checked.value = JSON.parse(localStorage.getItem('fei_todos') || '{}') } catch {}
})
function toggle(id) {
  checked.value = { ...checked.value, [id]: !checked.value[id] }
  try { localStorage.setItem('fei_todos', JSON.stringify(checked.value)) } catch {}
}
const done = computed(() => todos.value.filter(t => checked.value[t.id]).length)

// Phrases
const phraseSearch = ref('')
const phraseCat = ref('')
const phraseCategories = computed(() => [...new Set(phrases.value.map(p => p.category))])
const filteredPhrases = computed(() => {
  const q = phraseSearch.value.toLowerCase().trim()
  return phrases.value.filter(p =>
    (!phraseCat.value || p.category === phraseCat.value) &&
    (!q || p.sk.toLowerCase().includes(q) || p.en.toLowerCase().includes(q) || (p.ru || '').toLowerCase().includes(q))
  )
})
function speak(text) {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'sk-SK'
  u.rate = 0.9
  window.speechSynthesis.cancel()
  window.speechSynthesis.speak(u)
}
</script>

<style scoped>
.page-hero { padding: 60px 0 30px; }
.lead { color: var(--text-dim); font-size: 1.1rem; max-width: 720px; margin: 18px 0 24px; }

.tabs { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 24px; }
.tab {
  position: relative;
  padding: 10px 18px; border-radius: var(--radius);
  background: rgba(255,255,255,0.03); border: 1px solid var(--border);
  color: var(--text-dim); font-weight: 500; font-size: 0.92rem;
  transition: all .15s;
}
.tab:hover { color: var(--text); background: rgba(255,255,255,0.06); }
.tab:focus-visible { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-dim); }
.tab.active { background: var(--primary-dim); border-color: var(--primary); color: var(--text); }
.tab.active::after {
  content: ''; position: absolute; left: 12px; right: 12px; bottom: -1px;
  height: 2px; background: linear-gradient(90deg, var(--hazard), var(--cyan));
  border-radius: 1px;
  animation: tab-slide .25s ease;
  transform-origin: left;
}
@keyframes tab-slide {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.content { padding: 40px 0 80px; }

/* Map */
.map-tab { display: grid; grid-template-columns: 1.4fr 1fr; gap: 30px; align-items: start; }
.map-wrap { position: sticky; top: 70px; }
.map-stage {
  position: relative;
  width: 100%;
  aspect-ratio: 1500 / 1815;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-strong);
  background: linear-gradient(160deg, #0c1a2e 0%, #08121f 100%);
  box-shadow: 0 30px 60px -30px rgba(0, 0, 0, 0.6);
}
.map-image {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  filter: saturate(1.05) brightness(0.92);
}
.map-tint {
  position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(10, 23, 38, 0.20) 0%, rgba(10, 23, 38, 0.0) 35%, rgba(10, 23, 38, 0.0) 70%, rgba(6, 14, 26, 0.55) 100%);
  pointer-events: none;
}
.map-grid {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(127, 219, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(127, 219, 255, 0.05) 1px, transparent 1px);
  background-size: 48px 48px;
  mix-blend-mode: lighten;
  mask-image: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.55) 30%, rgba(0,0,0,0.55) 70%, rgba(0,0,0,0) 100%);
}
.map-label {
  position: absolute; bottom: 10px; left: 12px;
  font-size: 0.62rem; letter-spacing: 0.16em;
  color: rgba(255, 122, 61, 0.85);
  font-weight: 700; text-transform: uppercase;
  background: rgba(6, 14, 26, 0.65);
  padding: 4px 8px;
  border: 1px solid rgba(255, 122, 61, 0.3);
  border-radius: 4px;
  pointer-events: none;
}
.pin-layer { position: absolute; inset: 0; pointer-events: none; }
.pin {
  pointer-events: auto;
  position: absolute;
  transform: translate(-50%, -50%);
  width: 38px; height: 38px;
  border-radius: 50%;
  background: rgba(12, 26, 46, 0.85);
  border: 1.5px solid rgba(127, 219, 255, 0.45);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.05rem; line-height: 1;
  cursor: pointer;
  transition: transform .18s ease, background .18s ease, border-color .18s ease, box-shadow .18s ease;
  backdrop-filter: blur(4px);
  z-index: 2;
}
.pin:hover { transform: translate(-50%, -50%) scale(1.18); border-color: var(--cyan); box-shadow: 0 0 0 4px rgba(127, 219, 255, 0.15); z-index: 5; }
.pin.active {
  background: var(--hazard); border-color: var(--hazard);
  box-shadow: 0 0 0 6px rgba(255, 122, 61, 0.22), 0 0 20px rgba(255, 122, 61, 0.5);
  z-index: 4;
}
.pin-icon { display: inline-block; line-height: 1; transform: translateY(0.5px); }
.pin-icon-svg { font-size: 1.05rem; color: var(--cyan); }
.pin.active .pin-icon-svg { color: #0a1726; }
.pin-tip {
  position: absolute; bottom: calc(100% + 6px); left: 50%;
  transform: translateX(-50%);
  max-width: 140px; word-wrap: break-word; white-space: normal; text-align: center;
  background: var(--surface-3); color: var(--text);
  padding: 4px 8px; border-radius: 4px;
  font-family: var(--font-mono); font-size: 0.66rem;
  text-transform: uppercase; letter-spacing: 0.06em;
  opacity: 0; pointer-events: none;
  transition: opacity .15s;
  border: 1px solid var(--line-strong);
}
.pin:hover .pin-tip, .pin.active .pin-tip { opacity: 1; }
@media (max-width: 600px) { .pin { width: 32px; height: 32px; font-size: 0.95rem; } }
.legend { display: flex; justify-content: space-between; padding: 12px 4px; font-size: 0.88rem; }
.legend .muted { color: var(--text-muted); }

.point-detail {
  padding: 28px;
  background: linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  position: sticky; top: 70px;
}
.point-detail.empty { text-align: center; color: var(--text-muted); padding: 60px 28px; }
.pd-icon { font-size: 2.4rem; margin-bottom: 10px; }
.point-detail h3 { font-size: 1.3rem; }
.en { color: var(--text-muted); font-style: italic; margin-top: -2px; font-size: 0.88rem; }
.pd-desc { color: var(--text-dim); margin: 16px 0; line-height: 1.5; }
.tips h4 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 10px; }
.tips ul { list-style: none; padding-left: 0; }
.tips li { padding: 6px 0; color: var(--text-dim); font-size: 0.92rem; padding-left: 18px; position: relative; }
.tips li::before { content: '→'; position: absolute; left: 0; color: var(--accent); }

/* To-do */
.todo-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
.muted { color: var(--text-muted); font-size: 0.92rem; }
.progress-bar { height: 6px; background: var(--surface-3); border-radius: 3px; overflow: hidden; margin-bottom: 24px; }
.progress-bar > div { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); transition: width .3s ease; }
.todos { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.todo {
  display: grid; grid-template-columns: 38px 38px 1fr auto; gap: 14px; align-items: center;
  padding: 16px 18px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); cursor: pointer;
  transition: all .15s;
}
.todo:hover { border-color: var(--border-strong); transform: translateX(4px); }
.todo.done { opacity: 0.55; }
.todo.done strong { text-decoration: line-through; }
.todo .check {
  width: 26px; height: 26px; border-radius: 7px;
  border: 2px solid var(--border-strong);
  display: flex; align-items: center; justify-content: center;
  color: var(--accent); font-weight: 800;
}
.todo.done .check { background: var(--accent); border-color: var(--accent); color: var(--bg); }
.check-icon { font-size: 0.95rem; color: var(--accent); }
.todo.done .check .check-icon { color: var(--bg); }
.todo-icon { font-size: 1.6rem; }
.todo-body strong { display: block; margin-bottom: 2px; }
.todo-en { color: var(--text-muted); font-size: 0.85rem; margin-left: 6px; font-style: italic; }
.todo-body p { color: var(--text-dim); font-size: 0.88rem; margin-top: 4px; }
.prio-badge {
  font-size: 0.7rem; padding: 4px 10px; border-radius: 999px;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
}
.prio-badge.critical { background: var(--hot-dim); color: var(--hot); }
.prio-badge.high { background: rgba(255,184,74,0.18); color: var(--gold); }
.prio-badge.medium { background: var(--primary-dim); color: var(--primary); }
.prio-badge.low { background: rgba(120,160,220,0.1); color: var(--text-muted); }

/* Phrases */
.phrase-controls { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.search {
  flex: 1; min-width: 240px;
  background: var(--surface); border: 1px solid var(--border-strong);
  color: var(--text); padding: 11px 16px; border-radius: var(--radius);
  font-size: 0.95rem; font-family: inherit;
}
.search:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-dim); }
.phrase-grid { gap: 14px; }
.phrase-card {
  padding: 22px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius);
  position: relative;
}
.phrase-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.sk { font-size: 1.2rem; font-weight: 600; }
.speak { width: 44px; height: 44px; border-radius: 50%; background: var(--primary-dim); color: var(--primary); font-size: 1rem; display: inline-flex; align-items: center; justify-content: center; }
.speak:hover { background: var(--primary); color: white; }
.pron { color: var(--accent); font-size: 0.82rem; margin: 4px 0 12px; }
.tr { font-size: 0.92rem; color: var(--text-dim); padding: 6px 0; }
.flag { margin-right: 6px; }
.cat-badge { position: static; display: inline-block; margin-top: 10px; font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }

/* Contacts */
.contacts-tab > h2,
.phrases-tab > h2,
.todo-tab .todo-head h2 { margin-bottom: 24px; }
.survival-tab .sec-title { margin-bottom: 32px; }
.contacts-tab > h2 { margin-bottom: 28px; }
.contact-card h3 { margin-bottom: 6px; }
.contact-rows { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; font-size: 0.92rem; color: var(--text-dim); }
.contact-rows a { color: var(--primary); }

/* === Survival 101 === */
.survival-tab { display: flex; flex-direction: column; gap: 36px; }
.warning-banner {
  display: flex; gap: 18px; align-items: flex-start;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(212, 75, 46, 0.12), rgba(255, 122, 61, 0.08));
  border: 1px solid rgba(212, 75, 46, 0.4);
  border-left: 4px solid var(--hot);
  border-radius: var(--radius);
}
.warning-icon { font-size: 1.8rem; line-height: 1; padding-top: 2px; }
.warning-banner strong { color: var(--text); display: block; margin-bottom: 4px; }
.warning-banner p { color: var(--text-dim); font-size: 0.94rem; }

.sec-title { margin-bottom: 6px; font-size: clamp(1.4rem, 2.6vw, 2rem); }
.chaos-sub { margin-bottom: 24px; }

.killer-grid { display: grid; grid-template-columns: 1fr; gap: 24px; }
.killer-card {
  padding: 32px;
  background:
    repeating-linear-gradient(135deg, transparent 0, transparent 18px, rgba(255, 122, 61, 0.02) 18px, rgba(255, 122, 61, 0.02) 19px),
    linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  transition: transform .25s, border-color .25s, box-shadow .25s;
}
.killer-card:hover {
  border-color: var(--hazard);
  transform: translateY(-3px);
  box-shadow: 0 0 0 1px var(--hazard), 0 24px 60px -20px rgba(255, 122, 61, 0.22);
}
.killer-head { display: grid; grid-template-columns: auto 1fr auto; gap: 16px; align-items: center; margin-bottom: 18px; }
.killer-icon { font-size: 2.4rem; line-height: 1; }
.killer-head h3 { font-size: 1.5rem; }
.muted-en { color: var(--text-muted); font-family: var(--font-serif); font-style: italic; font-size: 0.92rem; }
.killer-rate {
  font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.1em;
  background: var(--hot-dim); color: var(--rust);
  padding: 6px 10px; border-radius: 4px;
  border: 1px solid rgba(212, 75, 46, 0.35);
  white-space: nowrap;
}
.killer-warn {
  color: var(--text); padding: 16px 18px; margin-bottom: 22px;
  background: rgba(212, 75, 46, 0.08);
  border-left: 2px solid var(--hot);
  border-radius: 4px;
  font-size: 0.96rem;
}
.killer-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 22px; }
.topic-list, .tip-list { list-style: none; padding: 0; }
.topic-list li, .tip-list li {
  padding: 7px 0 7px 22px; position: relative;
  color: var(--text-dim); font-size: 0.94rem;
  border-bottom: 1px dashed var(--line);
}
.topic-list li::before { content: '▸'; position: absolute; left: 0; color: var(--hazard); font-family: var(--font-mono); }
.tip-list li::before { content: '→'; position: absolute; left: 0; color: var(--cyan); font-family: var(--font-mono); }
.topic-list li:last-child, .tip-list li:last-child { border: none; }
.killer-res { padding-top: 18px; border-top: 1px dashed var(--line-strong); }
.res-row { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; }
.res-link {
  color: var(--cyan); font-size: 0.88rem; font-weight: 500;
  padding: 5px 0;
  border-bottom: 1px solid transparent;
  transition: border-color .15s;
}
.res-link:hover { border-bottom-color: var(--cyan); }

.chaos-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; }
.chaos-card {
  padding: 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  transition: border-color .15s, transform .15s;
}
.chaos-card:hover { border-color: var(--cyan); transform: translateY(-2px); }
.chaos-head { display: flex; gap: 12px; align-items: center; margin-bottom: 10px; }
.chaos-icon { font-size: 1.6rem; }
.chaos-head h3 { font-size: 1.1rem; }
.chaos-sum { color: var(--text-dim); font-size: 0.92rem; margin-bottom: 14px; }
.chaos-steps { list-style: none; padding: 0; counter-reset: step; }
.chaos-steps li {
  counter-increment: step;
  position: relative;
  padding: 8px 0 8px 30px;
  font-size: 0.9rem;
  color: var(--text-dim);
  border-bottom: 1px dashed var(--line);
}
.chaos-steps li::before {
  content: counter(step, decimal-leading-zero);
  position: absolute; left: 0;
  font-family: var(--font-mono); font-size: 0.74rem;
  color: var(--hazard); font-weight: 700;
  padding-top: 2px;
}
.chaos-steps li:last-child { border: none; }
.chaos-links { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 14px; padding-top: 14px; border-top: 1px dashed var(--line-strong); }
.chaos-links a { color: var(--cyan); font-size: 0.85rem; font-weight: 500; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.05em; }

@media (max-width: 760px) {
  .killer-cols { grid-template-columns: 1fr; gap: 22px; }
  .killer-head { grid-template-columns: auto 1fr; }
  .killer-rate { grid-column: 1 / -1; justify-self: start; }
}

@media (max-width: 900px) {
  .map-tab { grid-template-columns: 1fr; }
  .point-detail, .map-wrap { position: static; }
}
@media (max-width: 600px) {
  .tabs { gap: 6px; overflow-x: auto; flex-wrap: nowrap; padding-bottom: 6px; -webkit-overflow-scrolling: touch; }
  .tabs::-webkit-scrollbar { display: none; }
  .tab { flex: 0 0 auto; padding: 10px 14px; font-size: 0.85rem; white-space: nowrap; min-height: 44px; }
  .todo { grid-template-columns: 36px 32px 1fr; gap: 10px; padding: 14px; }
  .prio-badge { grid-column: 1 / -1; justify-self: start; margin-top: 4px; }
  .killer-card { padding: 22px 18px; }
  .killer-head { gap: 12px; }
  .killer-head h3 { font-size: 1.25rem; }
  .phrase-controls { flex-direction: column; gap: 8px; }
  .phrase-controls .search { flex: 1 1 auto; min-width: 0; width: 100%; }
  .phrase-controls select { width: 100% !important; flex: 1 1 auto !important; }
  .sk { font-size: 1.05rem; }
  .contact-rows { font-size: 0.88rem; }
}
</style>
