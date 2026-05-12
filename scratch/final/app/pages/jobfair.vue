<template>
  <div class="jobfair">
    <section class="page-hero">
      <div class="container">
        <span class="eyebrow">MODULE 03 / JOBFAIR MATCH</span>
        <h1>Land your <em>first engineering</em> job.</h1>
        <p class="lead lead-editorial">Twice a year, 16+ top employers — ESET, Nokia, JetBrains, Slovenské elektrárne — set up at the FEI hallway. Browse partners, or let Gemini rank the best 3 for your profile.</p>

        <div v-if="event" class="event-box">
          <div class="ev-row">
            <div>
              <strong class="ev-name">{{ event.name }}</strong>
              <p class="muted">{{ event.location }}</p>
            </div>
            <div class="ev-stats">
              <div><strong>{{ event.audience }}</strong><span>audience</span></div>
              <div><strong>{{ event.typical_partners_per_event }}+</strong><span>partners</span></div>
              <div><strong>2× / year</strong><span>frequency</span></div>
            </div>
          </div>
          <div class="ev-dates">
            <span class="badge"><Icon name="lucide:skip-forward" class="ico-xs" /> Next: {{ event.next_date }}</span>
            <span v-for="d in (event.last_dates || []).slice(0,2)" :key="d" class="badge accent"><Icon name="lucide:check" class="ico-xs" /> {{ d }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="container content">
      <div class="filter-bar">
        <button v-for="t in tagOptions" :key="t"
                class="tag" :class="{ active: activeTag === t }"
                @click="activeTag = activeTag === t ? '' : t">
          {{ t }}
        </button>
        <button class="btn btn-primary match-btn" @click="openMatch">
          <Icon name="lucide:sparkles" class="ico-sm" /> AI Match — find my employer
        </button>
      </div>

      <div class="grid grid-3 companies stagger">
        <article v-for="c in filteredCompanies" :key="c.id" class="company-card">
          <div class="cc-top">
            <h3>{{ c.name }}</h3>
            <span class="industry">{{ c.industry }}</span>
          </div>
          <p class="cc-tagline">{{ c.tagline }}</p>
          <div class="roles">
            <strong>Hiring for:</strong>
            <ul>
              <li v-for="r in c.roles" :key="r">→ {{ r }}</li>
            </ul>
          </div>
          <div class="cc-foot">
            <div class="tags">
              <span v-for="t in c.tags" :key="t" class="chip">{{ t }}</span>
            </div>
            <a v-if="c.url" :href="c.url" target="_blank" rel="noopener" class="cc-link">Careers ↗</a>
          </div>
          <div v-if="c.attended?.length" class="attended">
            <span class="muted">Last 6: </span>
            <span v-for="a in c.attended.slice(-3)" :key="a" class="attended-pill">{{ a }}</span>
          </div>
        </article>
      </div>
      <p v-if="!filteredCompanies.length" class="empty">No companies match "{{ activeTag }}".</p>
    </section>

    <!-- AI Match modal -->
    <div v-if="matchOpen" class="modal-bg" @click.self="matchOpen = false">
      <div class="modal">
        <button class="close" @click="matchOpen = false">✕</button>
        <h2><Icon name="lucide:sparkles" class="ico-md ico-hazard" /> AI Employer Match</h2>
        <p class="muted">Tell us about you — Gemini ranks the best fits from the {{ companies.length }} confirmed FEI JobFair partners.</p>

        <form v-if="!matchReply && !matchLoading" @submit.prevent="runMatch" class="match-form">
          <label>
            <span>Your study program / interests</span>
            <input v-model="form.program" placeholder="e.g. Applied Informatics, AI, embedded" required />
          </label>
          <label>
            <span>Skills</span>
            <input v-model="form.skills" placeholder="Python, C++, microcontrollers, networking…" required />
          </label>
          <label>
            <span>Ideal role</span>
            <input v-model="form.role" placeholder="e.g. ML engineer, embedded, security analyst" required />
          </label>
          <label>
            <span>Industry preference (optional)</span>
            <select v-model="form.industry">
              <option value="">Any</option>
              <option v-for="i in industries" :key="i" :value="i">{{ i }}</option>
            </select>
          </label>
          <button class="btn btn-primary" type="submit">Find my matches →</button>
        </form>

        <div v-if="matchLoading" class="loading">
          <div class="spinner"></div>
          <p>FEI Buddy is reviewing {{ companies.length }} employers…</p>
        </div>

        <div v-if="matchReply && !matchLoading" class="match-result">
          <div class="ai-output" v-html="matchReplyHtml"></div>
          <div class="match-actions">
            <button class="btn btn-ghost" @click="resetMatch">Try again</button>
            <button class="btn btn-primary" @click="matchOpen = false">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'JobFair Match — FEI Companion',
  meta: [{ name: 'description', content: 'Browse 16+ confirmed FEI JobFair partners — ESET, Nokia, Slovenské elektrárne, JetBrains, Continental, and more. AI matches you to the best employer.' }]
})

const { data: jobData } = await useFetch('/data/jobfair.json')
const event = computed(() => jobData.value?.event || null)
const companies = computed(() => jobData.value?.companies || [])
const tagOptions = computed(() => [...new Set(companies.value.flatMap(c => c.tags || []))])
const industries = computed(() => [...new Set(companies.value.map(c => c.industry))])
const activeTag = ref('')
const filteredCompanies = computed(() => {
  if (!activeTag.value) return companies.value
  return companies.value.filter(c => (c.tags || []).includes(activeTag.value))
})

// AI match
const matchOpen = ref(false)
const matchLoading = ref(false)
const matchReply = ref('')
const form = ref({ program: '', skills: '', role: '', industry: '' })
function openMatch() {
  matchOpen.value = true
  matchReply.value = ''
}
function resetMatch() { matchReply.value = '' }

async function runMatch() {
  matchLoading.value = true
  try {
    const ai = useAi()
    const userText = `My profile:
- Program/interest: ${form.value.program}
- Skills: ${form.value.skills}
- Ideal role: ${form.value.role}
- Industry preference: ${form.value.industry || 'any'}

From the FEI JobFair partner list (in context), rank the TOP 3 best-fit companies for me. For each: company name, why it fits (1 sentence), and which of their roles to apply for. Be concrete.`
    const reply = await ai.send({
      mode: 'match',
      messages: [{ role: 'user', content: userText }],
      context: { companies: companies.value.map(c => ({ name: c.name, industry: c.industry, tagline: c.tagline, roles: c.roles, tags: c.tags })) }
    })
    matchReply.value = reply || 'No matches generated.'
  } catch (e) {
    matchReply.value = `⚠️ AI unavailable: ${e.message}. Browse partners above directly.`
  } finally {
    matchLoading.value = false
  }
}
const matchReplyHtml = computed(() =>
  matchReply.value
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
)
</script>

<style scoped>
.page-hero { padding: 60px 0 30px; }
.lead { color: var(--text-dim); font-size: 1.1rem; max-width: 720px; margin: 18px 0 24px; }

.event-box {
  margin-top: 30px; padding: 28px;
  background: linear-gradient(135deg, rgba(255,81,81,0.08), rgba(79,140,255,0.08));
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
}
.ev-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 30px; flex-wrap: wrap; }
.ev-name { font-size: 1.3rem; }
.muted { color: var(--text-muted); font-size: 0.92rem; margin-top: 4px; }
.ev-stats { display: flex; gap: 30px; }
.ev-stats strong {
  display: block; font-size: 1.4rem; font-weight: 800;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.ev-stats span { font-size: 0.74rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.ev-dates { margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; }

.content { padding: 40px 0 80px; }
.filter-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 30px; align-items: center; }
.tag {
  padding: 7px 14px; border-radius: 999px;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  color: var(--text-dim); font-size: 0.85rem; font-weight: 500;
  transition: background .15s, border-color .15s, color .15s;
}
.tag:hover { color: var(--text); border-color: var(--primary); }
.tag.active { background: var(--primary-dim); color: var(--primary); border-color: var(--primary); animation: chipPop .25s ease both; }
@keyframes chipPop {
  0%   { transform: scale(0.9); }
  60%  { transform: scale(1.08); }
  100% { transform: scale(1); }
}
.match-btn { margin-left: auto; flex: 0 0 auto; }

.companies { margin-top: 10px; }
.company-card {
  padding: 24px;
  background: linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex; flex-direction: column; gap: 12px;
  transition: transform .2s, border-color .2s, box-shadow .2s;
}
.company-card:hover { border-color: var(--border-strong); transform: translateY(-2px); }
.cc-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.cc-top h3 { font-size: 1.15rem; }
.industry {
  font-size: 0.72rem; padding: 4px 10px; border-radius: 999px;
  background: var(--primary-dim); color: var(--primary);
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
  white-space: nowrap;
}
.cc-tagline { color: var(--text-dim); font-size: 0.92rem; }
.roles strong { display: block; font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 4px; letter-spacing: 0.06em; }
.roles ul { list-style: none; padding: 0; }
.roles li { color: var(--text-dim); padding: 2px 0; font-size: 0.92rem; }
.cc-foot { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: auto; padding-top: 8px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  font-size: 0.72rem; padding: 3px 8px; border-radius: 999px;
  background: rgba(120,160,220,0.08); color: var(--text-dim);
  border: 1px solid var(--border);
}
.cc-link { color: var(--accent); font-weight: 600; font-size: 0.88rem; }
.attended { font-size: 0.78rem; color: var(--text-muted); }
.attended-pill {
  display: inline-block; padding: 2px 7px; margin-right: 4px;
  background: rgba(0,224,216,0.08); color: var(--accent);
  border-radius: 999px; font-size: 0.7rem;
}

.empty { text-align: center; color: var(--text-muted); padding: 60px 0; }

/* Modal */
.modal-bg {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(2,6,14,0.75); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
  animation: modal-backdrop-in .25s ease both;
}
.modal {
  background: linear-gradient(160deg, var(--surface), var(--surface-2));
  border: 1px solid var(--border-strong); border-radius: var(--radius-lg);
  padding: 36px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;
  position: relative;
  animation: modal-panel-in .4s cubic-bezier(.2,.8,.2,1) both;
}
.close { position: absolute; top: 16px; right: 16px; width: 44px; height: 44px; border-radius: 50%; background: rgba(255,255,255,0.06); color: var(--text); font-size: 1.1rem; }
.match-form { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }
.match-form label { display: flex; flex-direction: column; gap: 6px; }
.match-form label span { font-size: 0.85rem; color: var(--text-dim); font-weight: 500; }
.match-form input, .match-form select {
  background: var(--surface); border: 1px solid var(--border-strong);
  color: var(--text); padding: 11px 14px; border-radius: var(--radius);
  font-family: inherit; font-size: 0.95rem;
}
.match-form input:focus, .match-form select:focus { outline: none; border-color: var(--primary); }
.match-form .btn { align-self: flex-start; margin-top: 10px; }

.loading { text-align: center; padding: 40px 0; color: var(--text-dim); }
.spinner {
  width: 44px; height: 44px; margin: 0 auto 18px;
  border: 3px solid rgba(79,140,255,0.2); border-top-color: var(--primary);
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.match-result { margin-top: 20px; }
.ai-output { background: rgba(0,0,0,0.25); padding: 20px; border-radius: var(--radius); border-left: 3px solid var(--accent); line-height: 1.65; }
.match-actions { display: flex; gap: 10px; margin-top: 20px; }

@media (max-width: 760px) {
  .ev-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .ev-stats > div { flex: none; }
  .ev-stats strong { font-size: 1rem; }
  .match-btn { margin-left: 0; width: 100%; justify-content: center; flex: 0 0 auto; }
  .ev-row { gap: 16px; }
  .event-box { padding: 20px 18px; }
  .filter-bar {
    gap: 8px;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 6px;
    -webkit-overflow-scrolling: touch;
  }
  .filter-bar::-webkit-scrollbar { display: none; }
  .tag { padding: 8px 12px; font-size: 0.82rem; min-height: 38px; flex: 0 0 auto; }
  .company-card { padding: 20px 18px; }
  .cc-top { flex-direction: column; align-items: flex-start; gap: 8px; }
  .industry { font-size: 0.68rem; }
  .modal { padding: 24px 18px; }
  .match-form input, .match-form select { font-size: 16px; }
}
</style>
