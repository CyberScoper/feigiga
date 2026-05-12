interface AiMessage { role: 'user' | 'assistant'; content: string }

export const useAi = () => {
  const send = async (opts: {
    mode?: 'chat' | 'quiz' | 'match'
    messages: AiMessage[]
    context?: Record<string, any>
  }) => {
    const { data, error } = await useFetch<{ reply: string; model?: string; error?: string }>('/api/ai', {
      method: 'POST',
      body: {
        mode: opts.mode || 'chat',
        messages: opts.messages,
        context: opts.context || {}
      }
    })
    if (error.value) throw new Error(error.value.message)
    if (data.value?.error) throw new Error(data.value.error)
    return data.value?.reply || ''
  }
  return { send }
}
