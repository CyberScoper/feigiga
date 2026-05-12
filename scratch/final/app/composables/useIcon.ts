// Emoji → Lucide icon mapper. Returns null if no mapping; caller can fall back to emoji.
const MAP: Record<string, string> = {
  // Tech / abstract
  '🧭': 'lucide:compass',
  '🎒': 'lucide:backpack',
  '💼': 'lucide:briefcase',
  '🚀': 'lucide:rocket',
  '🔬': 'lucide:flask-conical',
  '🤖': 'lucide:bot',
  '⚡': 'lucide:zap',
  '📚': 'lucide:book-open',
  '🔑': 'lucide:key',
  '🌐': 'lucide:globe',
  '🏠': 'lucide:house',
  '📧': 'lucide:mail',
  '📐': 'lucide:triangle-right',
  '🧲': 'lucide:magnet',
  '🗺️': 'lucide:map',
  '🗺': 'lucide:map',
  '⚠️': 'lucide:triangle-alert',
  '⚠': 'lucide:triangle-alert',
  '✅': 'lucide:circle-check',
  '✓': 'lucide:check',
  '🔊': 'lucide:volume-2',
  '🇸🇰': 'lucide:flag',
  '📞': 'lucide:phone',
  '💻': 'lucide:laptop',
  '🎓': 'lucide:graduation-cap',
  '🏛️': 'lucide:landmark',
  '🏛': 'lucide:landmark',
  '📋': 'lucide:clipboard-list',
  '🤝': 'lucide:handshake',
  '🏐': 'lucide:volleyball',
  '🏊': 'lucide:waves',
  '🧗': 'lucide:mountain',
  '🎉': 'lucide:party-popper',
  '🅿️': 'lucide:circle-parking',
  '🅿': 'lucide:circle-parking',
  '🚌': 'lucide:bus',
  '🚪': 'lucide:door-open',
  '🍽️': 'lucide:utensils',
  '🍽': 'lucide:utensils',
  '🥪': 'lucide:sandwich',
  '✨': 'lucide:sparkles',
  '⏭': 'lucide:skip-forward',
  '💡': 'lucide:lightbulb',
  '👈': 'lucide:hand-pointing',
  '👋': 'lucide:hand',
  '🎯': 'lucide:target',
  '🚇': 'lucide:train',
  '🎫': 'lucide:ticket',
  '🔐': 'lucide:lock-keyhole',
  '📡': 'lucide:radio-tower',
  '🔋': 'lucide:battery-charging',
  '☢️': 'lucide:radiation',
  '☢': 'lucide:radiation',
  '🛡️': 'lucide:shield',
  '🛡': 'lucide:shield',
  '🚗': 'lucide:car',
  '🏗️': 'lucide:construction',
  '🏗': 'lucide:construction',
  '🌡️': 'lucide:thermometer',
  '🌡': 'lucide:thermometer',
  '📊': 'lucide:bar-chart-3',
  '🧪': 'lucide:test-tube',
  '🧬': 'lucide:dna',
  '⚙️': 'lucide:settings',
  '⚙': 'lucide:settings',
  '🛰️': 'lucide:satellite',
  '🛰': 'lucide:satellite',
  // additional mappings from data files
  '🔌': 'lucide:plug-zap',
  '⚽': 'lucide:goal',
  '🏥': 'lucide:hospital',
  '👥': 'lucide:users',
  '💬': 'lucide:message-circle',
  '💳': 'lucide:credit-card',
  '📅': 'lucide:calendar-days',
  '⚛': 'lucide:atom',
  '⚛️': 'lucide:atom',
  '📄': 'lucide:file-text',
  '📍': 'lucide:map-pin',
  '🗓': 'lucide:calendar',
  '🗓️': 'lucide:calendar',
  '🔍': 'lucide:search',
  '🧮': 'lucide:calculator',
  '🌀': 'lucide:loader-circle',
  '🛠️': 'lucide:wrench',
  '🛠': 'lucide:wrench',
  '📈': 'lucide:trending-up',
  '✏️': 'lucide:pencil',
  '✏': 'lucide:pencil',
  '🧱': 'lucide:wall',
  '⏰': 'lucide:alarm-clock',
  '🕒': 'lucide:clock'
}

export const useIcon = () => {
  const toLucide = (emoji?: string | null) => {
    if (!emoji) return null
    const trimmed = String(emoji).trim()
    return MAP[trimmed] || MAP[trimmed.normalize('NFC')] || null
  }
  return { toLucide }
}

// Convenience: direct lookup without composable (for templates)
export const emojiToLucide = (e?: string | null) => {
  if (!e) return null
  const t = String(e).trim()
  return MAP[t] || MAP[t.normalize('NFC')] || null
}
