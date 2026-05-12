<template>
  <div class="course-page">
    <section class="page-hero">
      <div class="container">
        <span class="eyebrow">MODULE 01 / COURSE EXPLORER</span>
        <h1>All <em>9 bachelor</em> programs at FEI STU.</h1>
        <p class="lead">From applied informatics to nuclear engineering — pick the path that fits your future. Filter by interest, or let Gemini run you through a 6-question quiz.</p>
        <div class="controls">
          <input v-model="search" placeholder="Search programs, subjects, careers…" class="search" />
          <button class="btn btn-primary" @click="openQuiz">
            <Icon name="lucide:sparkles" /> AI Quiz — find my program
          </button>
        </div>
      </div>
    </section>

    <section class="container">
      <div class="grid grid-3 programs stagger">
        <article
          v-for="p in filtered" :key="p.id"
          class="program-card"
          :style="`--card-color: ${p.color}`"
          @click="open = p"
        >
          <div class="pc-top">
            <Icon v-if="emojiToLucide(p.icon)" :name="emojiToLucide(p.icon)" class="pc-icon ico-lg" />
            <span v-else class="pc-icon">{{ p.icon }}</span>
            <span class="pc-meta">Bc.</span>
          </div>
          <h3>{{ p.name_sk }}</h3>
          <p class="en">{{ p.name_en }}</p>
          <p class="desc">{{ truncate(p.description_sk, 140) }}</p>
          <div class="chips">
            <span v-for="s in p.subjects.slice(0, 4)" :key="s" class="chip">{{ s }}</span>
          </div>
          <div class="pc-footer">
            <span class="open-link">Open →</span>
          </div>
        </article>
      </div>
      <p v-if="!filtered.length" class="empty">No programs match "{{ search }}".</p>
    </section>

    <!-- Program detail modal -->
    <div v-if="open" class="modal-bg" @click.self="open = null">
      <div class="modal">
        <button class="close" @click="open = null">✕</button>
        <div class="modal-head" :style="`--card-color: ${open.color}`">
          <Icon v-if="emojiToLucide(open.icon)" :name="emojiToLucide(open.icon)" class="pc-icon ico-xl" />
          <span v-else class="pc-icon">{{ open.icon }}</span>
          <div>
            <h2>{{ open.name_sk }}</h2>
            <p class="en">{{ open.name_en }}</p>
          </div>
        </div>
        <p class="long">{{ open.description_sk }}</p>
        <p class="long en-desc">{{ open.description_en }}</p>
        <div class="detail-grid">
          <div>
            <h4>Key subjects</h4>
            <div class="chips">
              <span v-for="s in open.subjects" :key="s" class="chip">{{ s }}</span>
            </div>
          </div>
          <div>
            <h4>Career paths</h4>
            <ul class="careers">
              <li v-for="c in open.careers" :key="c">→ {{ c }}</li>
            </ul>
          </div>
        </div>
        <div class="modal-cta">
          <a :href="open.url" target="_blank" rel="noopener" class="btn btn-primary">Official FEI page ↗</a>
          <NuxtLink to="/freshman" class="btn btn-ghost">Need freshman tips →</NuxtLink>
        </div>
      </div>
    </div>

    <!-- AI Quiz modal -->
    <div v-if="quizOpen" class="modal-bg" @click.self="closeQuiz">
      <div class="modal modal-quiz">
        <button class="close" @click="closeQuiz">✕</button>
        <h2><Icon name="lucide:sparkles" /> AI Program Quiz</h2>
        <p class="muted">Answer 6 quick questions — Gemini picks your program.</p>

        <div v-if="!quizDone" class="quiz">
          <div class="progress"><div :style="`width:${(quizStep/quizQuestions.length)*100}%`"></div></div>
          <h3 class="qtitle">{{ quizQuestions[quizStep].q }}</h3>
          <div class="qopts">
            <button v-for="(opt, i) in quizQuestions[quizStep].opts" :key="i" class="qopt" @click="answer(opt)">
              <span class="opt-tag">{{ opt.label }}</span>
            </button>
          </div>
        </div>

        <div v-else class="quiz-result">
          <div v-if="quizLoading" class="loading">
            <div class="spinner"></div>
            <p>FEI Buddy is thinking…</p>
          </div>
          <div v-else>
            <h3><Icon name="lucide:target" class="ico-sm" /> Recommendation</h3>
            <div class="ai-output" v-html="quizReplyHtml"></div>
            <div class="quiz-actions">
              <button class="btn btn-ghost" @click="restartQuiz">Try again</button>
              <button class="btn btn-primary" @click="closeQuiz">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'Course Explorer — FEI Companion',
  meta: [{ name: 'description', content: 'Explore all 9 bachelor programs at FEI STU Bratislava: applied informatics, robotics, electronics, automotive mechatronics, and more. AI-powered quiz to find your perfect program.' }]
})

const { data: programsData } = await useFetch('/data/programs.json')
const programs = computed(() => programsData.value?.programs || [])

const search = ref('')
const open = ref(null)
const filtered = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return programs.value
  return programs.value.filter(p =>
    p.name_sk.toLowerCase().includes(q) ||
    p.name_en.toLowerCase().includes(q) ||
    p.description_sk.toLowerCase().includes(q) ||
    p.subjects.some(s => s.toLowerCase().includes(q)) ||
    p.careers.some(c => c.toLowerCase().includes(q))
  )
})
const truncate = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s)

// === AI Quiz ===
const quizQuestions = [
  { q: 'What excites you most?', opts: [
    { label: '💻 Writing software / algorithms', tag: 'software' },
    { label: '🤖 Building robots / control systems', tag: 'robotics' },
    { label: '⚡ Power, energy, electrical grids', tag: 'energy' },
    { label: '📡 Networks, signals, telecom', tag: 'telecom' },
    { label: '🔬 Physics, quantum, particles', tag: 'physics' }
  ]},
  { q: 'Math difficulty you enjoy?', opts: [
    { label: 'High — proofs, abstractions', tag: 'math-high' },
    { label: 'Practical — applied calc, stats', tag: 'math-applied' },
    { label: 'Whatever gets the job done', tag: 'math-pragmatic' }
  ]},
  { q: 'Hardware or software?', opts: [
    { label: 'Pure software', tag: 'sw' },
    { label: 'Embedded / firmware', tag: 'embed' },
    { label: 'Hardware design / circuits', tag: 'hw' },
    { label: 'Mixed — both', tag: 'mixed' }
  ]},
  { q: 'Dream job after Bc?', opts: [
    { label: 'AI/ML engineer', tag: 'ai' },
    { label: 'Cybersecurity', tag: 'sec' },
    { label: 'Engineer at Tesla/automotive', tag: 'auto' },
    { label: 'Energy company / nuclear plant', tag: 'energy-job' },
    { label: 'Telecom / 5G / satellites', tag: 'telecom-job' },
    { label: 'R&D / academia', tag: 'rd' }
  ]},
  { q: 'How much do you like teamwork?', opts: [
    { label: 'Love it — pair, hack, present', tag: 'team' },
    { label: 'Prefer focus + small group', tag: 'focus' },
    { label: 'Don\'t know yet', tag: 'unknown' }
  ]},
  { q: 'Slovak language level?', opts: [
    { label: 'Native', tag: 'sk-native' },
    { label: 'Conversational', tag: 'sk-mid' },
    { label: 'Beginner — need English-friendly', tag: 'sk-en' }
  ]}
]
const quizOpen = ref(false)
const quizStep = ref(0)
const quizAnswers = ref([])
const quizDone = ref(false)
const quizLoading = ref(false)
const quizReply = ref('')

function openQuiz() {
  quizOpen.value = true
  quizStep.value = 0
  quizAnswers.value = []
  quizDone.value = false
  quizReply.value = ''
}
function closeQuiz() { quizOpen.value = false }
function restartQuiz() { openQuiz() }
async function answer(opt) {
  quizAnswers.value.push({ q: quizQuestions[quizStep.value].q, answer: opt.label, tag: opt.tag })
  if (quizStep.value < quizQuestions.length - 1) {
    quizStep.value++
  } else {
    quizDone.value = true
    await runAi()
  }
}

const quizReplyHtml = computed(() => {
  // Simple markdown-ish: **bold**, line breaks
  return quizReply.value
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
})

async function runAi() {
  quizLoading.value = true
  try {
    const ai = useAi()
    const userText = `My quiz answers:\n${quizAnswers.value.map(a => `- ${a.q} → ${a.answer}`).join('\n')}\n\nWhich of these 9 FEI STU bachelor programs fits best, and why? Recommend ONE primary + ONE backup. Be specific, mention 2-3 subjects from the program and one career outcome.`
    const reply = await ai.send({
      mode: 'quiz',
      messages: [{ role: 'user', content: userText }],
      context: { programs: programs.value.map(p => ({ id: p.id, name: p.name_sk, name_en: p.name_en, desc: p.description_en, subjects: p.subjects, careers: p.careers })) }
    })
    quizReply.value = reply || 'Sorry, no recommendation generated. Try again?'
  } catch (e) {
    quizReply.value = `⚠️ AI request failed: ${e.message}. (Tip: AI is optional — browse programs above directly.)`
  } finally {
    quizLoading.value = false
  }
}
</script>

<style scoped>
.page-hero { padding: 60px 0 30px; }
.lead { color: var(--text-dim); font-size: 1.1rem; max-width: 720px; margin: 18px 0 24px; }
.controls { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }
.search {
  flex: 1; min-width: 280px;
  background: var(--surface); border: 1px solid var(--border-strong);
  color: var(--text); padding: 13px 18px; border-radius: var(--radius);
  font-size: 0.95rem; font-family: inherit;
}
.search:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-dim); }

.programs { margin: 30px 0 80px; }
.program-card {
  cursor: pointer;
  padding: 26px;
  background: linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex; flex-direction: column; gap: 12px;
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
  position: relative; overflow: hidden;
}
.program-card::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 0% 0%, var(--card-color, var(--primary)), transparent 60%);
  opacity: 0.07; transition: opacity .25s;
}
.program-card:hover { transform: translateY(-3px); border-color: var(--card-color, var(--primary)); }
.program-card:hover::before { opacity: 0.15; }
.pc-top { display: flex; justify-content: space-between; align-items: center; }
.pc-icon { font-size: 2rem; }
.pc-meta { font-size: 0.7rem; color: var(--text-muted); border: 1px solid var(--border); padding: 3px 8px; border-radius: 999px; font-weight: 600; letter-spacing: 0.05em; }
.program-card h3 { font-size: 1.18rem; }
.en { color: var(--text-muted); font-size: 0.85rem; font-style: italic; margin-top: -6px; }
.desc { color: var(--text-dim); font-size: 0.92rem; flex: 1; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  font-size: 0.75rem; padding: 4px 9px; border-radius: 999px;
  background: rgba(120,160,220,0.08); color: var(--text-dim);
  border: 1px solid var(--border);
}
.pc-footer { margin-top: auto; padding-top: 8px; }
.open-link { color: var(--card-color, var(--primary)); font-weight: 600; font-size: 0.9rem; }

.empty { text-align: center; color: var(--text-muted); padding: 60px 0; }

/* Modal */
.modal-bg {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(2, 6, 14, 0.75);
  backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
  animation: modal-backdrop-in .25s ease both;
}
.modal {
  background: linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 36px;
  max-width: 720px; width: 100%; max-height: 90vh; overflow-y: auto;
  position: relative;
  animation: modal-panel-in .4s cubic-bezier(.2,.8,.2,1) both;
}
.close { position: absolute; top: 16px; right: 16px; width: 36px; height: 36px; border-radius: 50%; background: rgba(255,255,255,0.06); color: var(--text); font-size: 1.1rem; }
.close:hover { background: rgba(255,255,255,0.12); }
.modal-head { display: flex; gap: 18px; align-items: center; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
.modal-head .pc-icon { font-size: 2.6rem; }
.modal-head h2 { font-size: 1.6rem; }
.long { color: var(--text-dim); margin-bottom: 16px; line-height: 1.6; }
.en-desc { font-style: italic; color: var(--text-muted); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 24px 0; }
.detail-grid h4 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 12px; }
.careers { list-style: none; }
.careers li { color: var(--text-dim); padding: 4px 0; }
.modal-cta { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 20px; }

/* Quiz */
.modal-quiz { max-width: 600px; }
.muted { color: var(--text-muted); margin-bottom: 24px; }
.progress { height: 6px; background: var(--surface-3); border-radius: 3px; overflow: hidden; margin-bottom: 30px; }
.progress > div { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); transition: width .25s ease; }
.qtitle { font-size: 1.3rem; margin-bottom: 22px; }
.qopts { display: flex; flex-direction: column; gap: 10px; }
.qopt {
  text-align: left; padding: 14px 18px;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--text); font-size: 0.95rem;
  transition: background .15s, border-color .15s, transform .15s;
}
.qopt:hover { background: var(--primary-dim); border-color: var(--primary); transform: translateX(4px); }
.quiz-result h3 { margin-bottom: 16px; font-size: 1.5rem; }
.ai-output { background: rgba(0,0,0,0.25); padding: 20px; border-radius: var(--radius); border-left: 3px solid var(--accent); line-height: 1.65; }
.loading { text-align: center; padding: 40px 0; color: var(--text-dim); }
.spinner {
  width: 44px; height: 44px; margin: 0 auto 18px;
  border: 3px solid rgba(79,140,255,0.2); border-top-color: var(--primary);
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.quiz-actions { display: flex; gap: 10px; margin-top: 24px; }

@media (max-width: 600px) {
  .detail-grid { grid-template-columns: 1fr; }
  .modal { padding: 24px 18px; }
  .controls { flex-direction: column; align-items: stretch; }
  .controls .btn { width: 100%; justify-content: center; }
  .search { min-width: 0; width: 100%; }
  .program-card { padding: 22px 18px; }
  .program-card h3 { font-size: 1.1rem; }
  .modal-head { gap: 14px; padding-bottom: 16px; margin-bottom: 18px; }
  .modal-head h2 { font-size: 1.35rem; }
  .modal-head .pc-icon { font-size: 2rem; }
  .modal-cta { flex-direction: column; }
  .modal-cta .btn { width: 100%; justify-content: center; }
  .qtitle { font-size: 1.1rem; }
  .qopt { padding: 12px 14px; min-height: 48px; }
}
</style>
