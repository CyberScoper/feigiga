// POST /api/ai — прокси к Gemini 2.5 Flash для FEI Buddy
// Принимает { mode, messages, context } и возвращает { reply, model }.

import { defineEventHandler, readBody, getRequestIP, createError } from 'h3'

type Role = 'user' | 'assistant'
type Mode = 'chat' | 'quiz' | 'match'

interface ChatMessage {
  role: Role
  content: string
}

interface AiRequestBody {
  mode?: Mode
  messages?: ChatMessage[]
  context?: Record<string, unknown>
}

// Простой in-memory rate limiter: 20 req / минуту / IP
const RATE_WINDOW_MS = 60_000
const RATE_LIMIT = 20
const ipHits: Map<string, number[]> = new Map()

function rateLimitOk(ip: string): boolean {
  const now = Date.now()
  const arr = ipHits.get(ip) || []
  const fresh = arr.filter((t) => now - t < RATE_WINDOW_MS)
  if (fresh.length >= RATE_LIMIT) {
    ipHits.set(ip, fresh)
    return false
  }
  fresh.push(now)
  ipHits.set(ip, fresh)
  return true
}

function buildSystemPrompt(mode: Mode, context?: Record<string, unknown>): string {
  const base = [
    'You are "FEI Buddy", a friendly and knowledgeable AI assistant for students of the Faculty of Electrical Engineering and Information Technology (FEI) at Slovak University of Technology (STU) in Bratislava.',
    'Languages: detect the user\'s language automatically and reply IN THE SAME LANGUAGE. You MUST fully support Slovak (default), English and Russian. Never mix languages in one reply unless the user does.',
    'Keep replies under 250 words. Be concrete, warm, and use light formatting (short paragraphs, bullets when helpful). Avoid disclaimers and filler.',
    'If you are unsure about an exact fact (course code, room number, deadline), say so briefly and suggest checking AIS (is.stuba.sk) or fei.stuba.sk.'
  ]

  if (mode === 'quiz') {
    base.push(
      'MODE = QUIZ. The user has just completed a short orientation quiz. Analyze their answers in the context object and recommend ONE primary FEI STU bachelor study program that fits them best, plus 1-2 backup options. Explain in 2-3 sentences why. End with one actionable next step.'
    )
  } else if (mode === 'match') {
    base.push(
      'MODE = MATCH. The user is preparing for FEI JobFair. Using the student profile and the list of companies in the context object, pick the TOP 3 companies that best match their interests/skills. For each, give: company name, 1-line why it fits, and 1 suggested talking point or question to ask at the booth.'
    )
  } else {
    base.push(
      'MODE = CHAT. Answer the student\'s question about FEI STU life: programs, subjects, professors, Erasmus, dorms, AIS, JobFair, survival tips. Be helpful and conversational.'
    )
  }

  if (context && Object.keys(context).length > 0) {
    let ctxStr = ''
    try {
      ctxStr = JSON.stringify(context, null, 2)
    } catch {
      ctxStr = String(context)
    }
    if (ctxStr.length > 6000) ctxStr = ctxStr.slice(0, 6000) + '\n... [truncated]'
    base.push(`\nCONTEXT (page-specific data, JSON):\n${ctxStr}`)
  }

  return base.join('\n\n')
}

export default defineEventHandler(async (event) => {
  const ip = getRequestIP(event, { xForwardedFor: true }) || 'unknown'

  if (!rateLimitOk(ip)) {
    throw createError({ statusCode: 429, statusMessage: 'Too many requests. Skús to za chvíľu.' })
  }

  const config = useRuntimeConfig()
  const apiKey = config.geminiApiKey
  if (!apiKey) {
    throw createError({ statusCode: 500, statusMessage: 'GEMINI_API_KEY not configured' })
  }

  let body: AiRequestBody
  try {
    body = await readBody<AiRequestBody>(event)
  } catch {
    throw createError({ statusCode: 400, statusMessage: 'Invalid JSON body' })
  }

  const mode: Mode = body?.mode === 'quiz' || body?.mode === 'match' ? body.mode : 'chat'
  const messages = Array.isArray(body?.messages) ? body!.messages! : []
  if (messages.length === 0) {
    throw createError({ statusCode: 400, statusMessage: 'messages[] is required' })
  }

  // Конвертируем в формат Gemini: role "user" | "model", parts:[{text}]
  const contents = messages
    .filter((m) => m && typeof m.content === 'string' && m.content.trim().length > 0)
    .map((m) => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }]
    }))

  if (contents.length === 0) {
    throw createError({ statusCode: 400, statusMessage: 'No valid messages' })
  }

  const systemText = buildSystemPrompt(mode, body?.context)

  const payload = {
    contents,
    systemInstruction: { parts: [{ text: systemText }] },
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 800
    }
  }

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${encodeURIComponent(apiKey)}`

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const errText = await res.text().catch(() => '')
      console.error('[ai] Gemini error', res.status, errText.slice(0, 500))
      return {
        error: `Gemini API failed (${res.status})`,
        detail: errText.slice(0, 300)
      }
    }

    const data: any = await res.json()
    const reply: string =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ??
      data?.candidates?.[0]?.content?.parts?.map((p: any) => p?.text).filter(Boolean).join('\n') ??
      ''

    if (!reply) {
      return { error: 'Empty response from Gemini', raw: data?.promptFeedback || null }
    }

    return { reply: reply.trim(), model: 'gemini-2.5-flash' }
  } catch (err: any) {
    console.error('[ai] fetch threw', err)
    return { error: err?.message || 'Network error talking to Gemini' }
  }
})
