<template>
  <div class="ai-chat-root">
    <!-- Плавающая кнопка -->
    <button
      v-show="!open"
      class="fab"
      aria-label="Open FEI Buddy chat"
      @click="toggle(true)"
    >
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">
        <path
          d="M12 3C6.48 3 2 6.92 2 11.5c0 2.06.9 3.94 2.4 5.4-.13 1.3-.62 2.66-1.4 3.6-.16.2-.05.5.2.5.05 0 .1 0 .15-.02 1.7-.3 3.2-.95 4.3-1.78 1.3.5 2.7.8 4.35.8 5.52 0 10-3.92 10-8.5S17.52 3 12 3z"
          fill="currentColor"
        />
      </svg>
      <span class="fab-pulse" aria-hidden="true"></span>
    </button>

    <!-- Панель чата -->
    <transition name="panel">
      <section v-if="open" class="panel" role="dialog" aria-label="FEI Buddy chat">
        <header class="panel-head">
          <div class="head-left">
            <span class="avatar">
              <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                <path
                  d="M12 3C6.48 3 2 6.92 2 11.5c0 2.06.9 3.94 2.4 5.4-.13 1.3-.62 2.66-1.4 3.6-.16.2-.05.5.2.5.05 0 .1 0 .15-.02 1.7-.3 3.2-.95 4.3-1.78 1.3.5 2.7.8 4.35.8 5.52 0 10-3.92 10-8.5S17.52 3 12 3z"
                  fill="#0a1929"
                />
              </svg>
            </span>
            <div>
              <div class="title">FEI Buddy</div>
              <div class="sub">
                <span class="badge accent">AI</span>
                <span class="status"><span class="dot"></span> Online</span>
              </div>
            </div>
          </div>
          <button class="close" aria-label="Close" @click="toggle(false)">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
            </svg>
          </button>
        </header>

        <div ref="scrollEl" class="messages">
          <div
            v-for="(m, i) in messages"
            :key="i"
            class="msg"
            :class="m.role === 'user' ? 'me' : 'bot'"
          >
            <div class="bubble" v-html="renderContent(m.content)"></div>
          </div>

          <div v-if="loading" class="msg bot">
            <div class="bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>

          <div v-if="errorMsg" class="msg bot">
            <div class="bubble err">{{ errorMsg }}</div>
          </div>
        </div>

        <form class="input" @submit.prevent="send">
          <textarea
            ref="taEl"
            v-model="draft"
            rows="1"
            placeholder="Spýtaj sa čokoľvek o FEI STU…"
            :disabled="loading"
            @keydown="onKeydown"
            @input="autosize"
          ></textarea>
          <button
            type="submit"
            class="send"
            :disabled="loading || !draft.trim()"
            aria-label="Send"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path d="M3 12l18-8-7 18-3-7-8-3z" fill="currentColor" />
            </svg>
          </button>
        </form>
      </section>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'

const props = defineProps({
  context: { type: Object, default: () => ({}) },
  mode: { type: String, default: 'chat' }
})

const GREETING = "Ahoj! 👋 I'm FEI Buddy. Spýtaj sa ma na FEI STU — odpoviem v slovenčine, English alebo по-русски."
const STORAGE_KEY = 'feiBuddy.chat.v1'

const open = ref(false)
const draft = ref('')
const loading = ref(false)
const errorMsg = ref('')
const messages = ref([])
const scrollEl = ref(null)
const taEl = ref(null)

function loadHistory() {
  if (typeof window === 'undefined') return
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length) {
        messages.value = parsed
        return
      }
    }
  } catch {}
  messages.value = [{ role: 'assistant', content: GREETING }]
}

function saveHistory() {
  if (typeof window === 'undefined') return
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
  } catch {}
}

onMounted(loadHistory)

watch(
  messages,
  () => {
    saveHistory()
    scrollToBottom()
  },
  { deep: true }
)

function scrollToBottom() {
  nextTick(() => {
    const el = scrollEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function toggle(v) {
  open.value = v
  if (v) {
    nextTick(() => {
      scrollToBottom()
      taEl.value?.focus()
    })
  }
}

function autosize() {
  const el = taEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

// Лёгкое форматирование: переносы строк + escape
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
function renderContent(s) {
  const esc = escapeHtml(s)
  // **bold** -> <strong>
  const bold = esc.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  return bold.replace(/\n/g, '<br>')
}

async function send() {
  const text = draft.value.trim()
  if (!text || loading.value) return
  errorMsg.value = ''
  messages.value.push({ role: 'user', content: text })
  draft.value = ''
  autosize()
  loading.value = true

  try {
    const payload = {
      mode: props.mode,
      messages: messages.value.map((m) => ({ role: m.role, content: m.content })),
      context: props.context || {}
    }
    const res = await $fetch('/api/ai', {
      method: 'POST',
      body: payload
    })
    if (res?.error) {
      errorMsg.value = res.error
    } else if (res?.reply) {
      messages.value.push({ role: 'assistant', content: res.reply })
    } else {
      errorMsg.value = 'Empty reply.'
    }
  } catch (e) {
    errorMsg.value = e?.statusMessage || e?.message || 'Network error'
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.ai-chat-root { position: fixed; right: 22px; bottom: max(22px, env(safe-area-inset-bottom, 22px)); z-index: 1000; }

/* --- FAB --- */
.fab {
  position: relative;
  width: 60px; height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f8cff 0%, #00e0d8 100%);
  color: #0a1929;
  box-shadow: 0 10px 30px rgba(79, 140, 255, 0.45), 0 0 30px rgba(0, 224, 216, 0.3);
  display: inline-flex; align-items: center; justify-content: center;
  transition: transform .18s ease, box-shadow .2s ease;
}
.fab:hover { transform: translateY(-2px) scale(1.04); box-shadow: 0 12px 36px rgba(79,140,255,.55), 0 0 40px rgba(0,224,216,.4); }
.fab:active { transform: translateY(0) scale(0.98); }
.fab-pulse {
  position: absolute; inset: -4px; border-radius: 50%;
  border: 2px solid rgba(0, 224, 216, 0.45);
  animation: pulseRing 2.2s ease-out infinite;
}
@keyframes pulseRing {
  0%   { transform: scale(0.85); opacity: 0.9; }
  100% { transform: scale(1.35); opacity: 0; }
}

/* --- Panel --- */
.panel {
  width: 380px;
  max-width: calc(100vw - 24px);
  height: min(80vh, 620px);
  display: flex; flex-direction: column;
  background: linear-gradient(160deg, rgba(12,26,46,0.92) 0%, rgba(18,38,66,0.92) 100%);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(18px) saturate(140%);
  -webkit-backdrop-filter: blur(18px) saturate(140%);
  box-shadow: 0 24px 60px rgba(0,0,0,0.5), 0 0 60px rgba(79,140,255,0.18);
  overflow: hidden;
}

.panel-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(79,140,255,0.08), transparent);
}
.head-left { display: flex; align-items: center; gap: 12px; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #4f8cff, #00e0d8);
  display: inline-flex; align-items: center; justify-content: center;
  box-shadow: 0 0 18px rgba(0,224,216,0.4);
}
.title { font-weight: 700; font-size: 0.98rem; color: var(--text); letter-spacing: -0.01em; }
.sub { display: flex; align-items: center; gap: 8px; margin-top: 2px; }
.sub .badge {
  display: inline-flex; align-items: center;
  padding: 2px 8px; font-size: 0.65rem; font-weight: 700;
  border-radius: 999px;
  background: var(--accent-dim); color: var(--accent);
  border: 1px solid rgba(0,224,216,0.3);
  letter-spacing: 0.04em;
}
.status { font-size: 0.72rem; color: var(--text-muted); display: inline-flex; align-items: center; gap: 5px; }
.status .dot { width: 7px; height: 7px; border-radius: 50%; background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
.close {
  width: 32px; height: 32px; border-radius: 10px;
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--text-dim);
  transition: background .15s ease, color .15s ease;
}
.close:hover { background: rgba(255,255,255,0.06); color: var(--text); }

/* --- Messages --- */
.messages {
  flex: 1; min-height: 0;
  overflow-y: auto;
  padding: 16px;
  display: flex; flex-direction: column; gap: 10px;
  scroll-behavior: smooth;
}
.messages::-webkit-scrollbar { width: 6px; }
.messages::-webkit-scrollbar-thumb { background: rgba(120,160,220,0.2); border-radius: 6px; }

.msg { display: flex; }
.msg.me { justify-content: flex-end; }
.msg.bot { justify-content: flex-start; }

.bubble {
  max-width: 82%;
  padding: 10px 14px;
  font-size: 0.92rem;
  line-height: 1.5;
  border-radius: 16px;
  word-wrap: break-word;
  white-space: normal;
  animation: bubbleIn .22s ease both;
}
.msg.me .bubble {
  background: linear-gradient(135deg, var(--primary-dim), rgba(0,224,216,0.12));
  border: 1px solid rgba(79,140,255,0.35);
  color: var(--text);
  border-bottom-right-radius: 6px;
}
.msg.bot .bubble {
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text);
  border-bottom-left-radius: 6px;
}
.bubble.err {
  background: var(--hot-dim);
  border-color: rgba(255,81,81,0.4);
  color: #ffd2d2;
}
.bubble :deep(strong) { color: var(--accent); font-weight: 700; }

@keyframes bubbleIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Typing indicator */
.typing { display: inline-flex; gap: 5px; padding: 14px 16px; }
.typing span {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--text-dim);
  animation: typingDot 1.2s infinite ease-in-out;
}
.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }
@keyframes typingDot {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* --- Input --- */
.input {
  display: flex; align-items: flex-end; gap: 8px;
  padding: 12px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  border-top: 1px solid var(--border);
  background: rgba(6,13,26,0.4);
}
.input textarea {
  flex: 1;
  resize: none;
  max-height: 140px;
  min-height: 40px;
  padding: 10px 12px;
  font: inherit;
  font-size: 0.92rem;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  border-radius: 12px;
  outline: none;
  transition: border-color .15s ease, box-shadow .15s ease;
}
.input textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-dim);
}
.input textarea:disabled { opacity: 0.6; }

.send {
  width: 40px; height: 40px; flex: 0 0 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #0a1929;
  display: inline-flex; align-items: center; justify-content: center;
  transition: transform .15s ease, box-shadow .15s ease, opacity .15s;
  box-shadow: 0 6px 20px rgba(79,140,255,0.35);
}
.send:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 8px 26px rgba(0,224,216,0.45); }
.send:disabled { opacity: 0.45; cursor: not-allowed; box-shadow: none; }

/* --- Transitions --- */
.panel-enter-active, .panel-leave-active {
  transition: opacity .22s ease, transform .25s cubic-bezier(.2,.8,.2,1);
  transform-origin: bottom right;
}
.panel-enter-from, .panel-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
}

/* --- Mobile --- */
@media (max-width: 600px) {
  .ai-chat-root { right: 14px; bottom: max(14px, env(safe-area-inset-bottom, 14px)); }
  .panel {
    width: calc(100vw - 16px);
    height: calc(100vh - 16px);
    max-width: none;
    border-radius: 18px;
    position: fixed;
    right: 8px;
    bottom: max(8px, env(safe-area-inset-bottom, 8px));
  }
  .fab { width: 56px; height: 56px; }
  .input textarea { font-size: 16px; }
}
</style>
