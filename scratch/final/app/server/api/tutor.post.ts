// POST /api/tutor — Gemini-powered tutor for B-MAT1 / B-FYZ1
// Body: { subject: 'math1'|'fyz1', topic?: string, problem: string, history?: [...] }
// Returns: { reply: string, model: 'gemini-2.5-flash' }

import { defineEventHandler, readBody, getRequestIP, createError } from 'h3'

type Subject = 'math1' | 'fyz1'

interface TutorBody {
  subject: Subject
  topic?: string
  problem: string
  history?: { role: 'user' | 'assistant'; content: string }[]
}

const RATE_WINDOW_MS = 60_000
const RATE_LIMIT = 15
const ipHits: Map<string, number[]> = new Map()
function rateOk(ip: string) {
  const now = Date.now()
  const arr = (ipHits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS)
  if (arr.length >= RATE_LIMIT) {
    ipHits.set(ip, arr)
    return false
  }
  arr.push(now)
  ipHits.set(ip, arr)
  return true
}

function buildSystemPrompt(subject: Subject, topic?: string): string {
  if (subject === 'math1') {
    return [
      'Si tútor predmetu B-MAT1 Matematika 1 na FEI STU v Bratislave. Pracuješ podľa skripta Marko (M1MarkoPrednasky.pdf) a prednášok paralelky B (Polakovič / Rudolf / Čipková).',
      'Tvoja úloha: vysvetľovať a riešiť úlohy z týchto 7 tém: 1) Komplexné čísla, 2) Matice a SLR, 3) Determinanty a Cramer, 4) Reálne funkcie, 5) Postupnosti a limity, 6) Diferenciálny počet, 7) Postupnosti a nekonečné rady (Taylor).',
      'JAZYK ODPOVEDE: detekuj jazyk otázky a odpovedaj v ňom (SK/EN/RU). Predvolene slovenčina.',
      'FORMÁT: každú matematickú formulu uzavri do KaTeX delimitérov $...$ (inline) alebo $$...$$ (display). NIKDY nepouži \\(...\\) ani \\[...\\]. Používaj LaTeX príkazy: \\frac, \\sqrt, \\sum, \\int, \\lim, \\to, \\infty, \\sin, \\cos, \\ln, \\binom, \\cdot.',
      'ŠTRUKTÚRA ODPOVEDE pre úlohy:',
      '1) **Téma:** krátko, do akej z 7 tém úloha patrí.',
      '2) **Riešenie krok po kroku:** očíslované kroky s formulami $...$. Vždy 4-8 krokov, nie viac.',
      '3) **Výsledok:** zarámovaný do **odpovede** na konci ($$\\boxed{...}$$).',
      '4) **Skriptum:** odkaz "↗ Marko, kap. X" alebo "↗ Priklady2.pdf, str. ~X" (uveď reálnu kapitolu zo skript Marka pre danú tému, ak je to relevantné).',
      'Ak je otázka konceptuálna (nie úloha), vysvetli intuíciu + 1 príklad + jednu typickú chybu, ktorú robia študenti.',
      'NIKDY nepiš obecné disclaimery typu "ako AI nemôžem...". Si tútor. Konkrétne, krátke, presné. Maximálne 350 slov.'
    ]
      .concat(topic ? [`AKTUÁLNA TÉMA, KTORÁ ZAUJÍMA ŠTUDENTA: "${topic}". Začni odpoveď z tejto témy, ak má súvis.`] : [])
      .join('\n\n')
  }

  // fyz1
  return [
    'Si tútor predmetu B-FYZ1 Fyzika 1 na FEI STU v Bratislave (prednáša RNDr. Juraj Chlpík, garant prof. Cirák). Pracuješ podľa sylabu Fyzika 1 (LS 2026) a archívu kf.elf.stuba.sk/~chlpik/.',
    'Témy: 1) Kinematika hmotného bodu, 2) Dynamika hmotného bodu, 3) Práca/energia/výkon, 4) Tuhé teleso, 5) Kmitanie a vlnenie, 6) Hydrostatika a hydrodynamika, 7) Termodynamika (úvod).',
    'Pamätaj na kontrolky: K1 (20.03.2026, témy 1-2), K2 (08.05.2026, témy 4-6). Skúška 54 b, semester 46 b (laby 16 + kontrolky 30). Bez 25 b zo semestra → FX.',
    'JAZYK: detekuj jazyk otázky (SK/EN/RU). Predvolene slovenčina.',
    'FORMÁT: $...$ pre inline, $$...$$ pre display. Vždy uveď jednotky SI ($\\mathrm{m}, \\mathrm{s}^{-2}, \\mathrm{kg}\\cdot\\mathrm{m}^2$). NIKDY nepouži \\(...\\) ani \\[...\\].',
    'ŠTRUKTÚRA pre úlohy:',
    '1) **Známe / hľadané:** vypíš dané veličiny so symbolmi a jednotkami.',
    '2) **Fyzikálny model:** ktorý zákon používame (Newton, zachovanie energie, ...).',
    '3) **Riešenie:** 3-6 krokov, formuly v KaTeX.',
    '4) **Výsledok:** $$\\boxed{...}$$ + slovné overenie rozumnosti čísla.',
    '5) **Pozor na:** typická chyba študentov pri tejto téme.',
    'Pri laboratóriách: vysvetli, ako spočítať chybu merania (Gaussova kombinácia, relatívna chyba).',
    'Stručné, konkrétne. Max 350 slov.'
  ]
    .concat(topic ? [`AKTUÁLNA TÉMA: "${topic}".`] : [])
    .join('\n\n')
}

export default defineEventHandler(async (event) => {
  const ip = getRequestIP(event, { xForwardedFor: true }) || 'unknown'
  if (!rateOk(ip)) {
    throw createError({ statusCode: 429, statusMessage: 'Spomaľ. Skús to o minútu.' })
  }

  const config = useRuntimeConfig()
  const apiKey = config.geminiApiKey
  if (!apiKey) {
    throw createError({ statusCode: 500, statusMessage: 'GEMINI_API_KEY not configured' })
  }

  let body: TutorBody
  try { body = await readBody<TutorBody>(event) } catch {
    throw createError({ statusCode: 400, statusMessage: 'Invalid JSON' })
  }

  const subject: Subject = body?.subject === 'fyz1' ? 'fyz1' : 'math1'
  const problem = (body?.problem || '').trim()
  if (problem.length === 0) {
    throw createError({ statusCode: 400, statusMessage: 'problem is required' })
  }
  if (problem.length > 4000) {
    throw createError({ statusCode: 400, statusMessage: 'problem too long (max 4000 chars)' })
  }

  const history = Array.isArray(body?.history) ? body.history.slice(-6) : []
  const systemText = buildSystemPrompt(subject, body?.topic)

  const contents = [
    ...history
      .filter((m) => m && typeof m.content === 'string' && m.content.trim())
      .map((m) => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }]
      })),
    { role: 'user', parts: [{ text: problem }] }
  ]

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${encodeURIComponent(apiKey)}`

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        contents,
        systemInstruction: { parts: [{ text: systemText }] },
        generationConfig: { temperature: 0.4, maxOutputTokens: 1400 }
      })
    })
    if (!res.ok) {
      const errText = await res.text().catch(() => '')
      console.error('[tutor] Gemini error', res.status, errText.slice(0, 400))
      return { error: `Gemini API ${res.status}`, detail: errText.slice(0, 300) }
    }
    const data: any = await res.json()
    const reply: string =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ??
      data?.candidates?.[0]?.content?.parts?.map((p: any) => p?.text).filter(Boolean).join('\n') ??
      ''
    if (!reply) return { error: 'Empty response from Gemini', raw: data?.promptFeedback || null }
    return { reply: reply.trim(), model: 'gemini-2.5-flash' }
  } catch (err: any) {
    console.error('[tutor] fetch failed', err)
    return { error: err?.message || 'Network error' }
  }
})
