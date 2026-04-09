import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatMessage, IntentInfo, UsageInfo } from '@/types/skill'
import { chatApi } from '@/api/client'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const currentSessionId = ref<string | null>(null)
  const currentIntent = ref<IntentInfo | null>(null)
  const skillStatuses = ref<Record<string, 'pending' | 'success' | 'failed'>>({})
  const currentUsage = ref<UsageInfo | null>(null)
  const error = ref<string | null>(null)

  const hasMessages = computed(() => messages.value.length > 0)

  async function sendMessage(content: string) {
    if (!content.trim() || isStreaming.value) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: Date.now()
    }
    messages.value.push(userMessage)

    const assistantMessage: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      skillStatus: {}
    }
    messages.value.push(assistantMessage)

    isStreaming.value = true
    error.value = null
    skillStatuses.value = {}
    currentIntent.value = null

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: content.trim(),
          session_id: currentSessionId.value
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let eventType = ''
      let dataBuffer = ''

      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                eventType = line.slice(7).trim()
              } else if (line.startsWith('data: ')) {
                dataBuffer = line.slice(6).trim()

                try {
                  const data = JSON.parse(dataBuffer)

                  switch (eventType) {
                    case 'session_start':
                      currentSessionId.value = data.session_id
                      break
                    case 'intent_parsed':
                      currentIntent.value = data
                      break
                    case 'skill_start':
                      skillStatuses.value[data.skill] = 'pending'
                      break
                    case 'skill_end':
                      skillStatuses.value[data.skill] = data.success ? 'success' : 'failed'
                      break
                    case 'content':
                      const lastIdx = messages.value.length - 1
                      if (lastIdx >= 0 && messages.value[lastIdx].role === 'assistant') {
                        messages.value[lastIdx] = {
                          ...messages.value[lastIdx],
                          content: messages.value[lastIdx].content + data.content
                        }
                      }
                      break
                    case 'done':
                      currentUsage.value = data.usage
                      isStreaming.value = false
                      return
                  }

                  if (eventType !== 'content') {
                    assistantMessage.skillStatus = { ...skillStatuses.value }
                  }
                } catch (e) {
                  console.error('Failed to parse SSE data:', e)
                }
              }
            }
          }
        } finally {
          isStreaming.value = false
        }
      }

      processStream()

    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Request failed'
      isStreaming.value = false
    }
  }

  function clearMessages() {
    messages.value = []
    currentSessionId.value = null
    currentIntent.value = null
    skillStatuses.value = {}
    error.value = null
  }

  return {
    messages,
    isStreaming,
    currentSessionId,
    currentIntent,
    skillStatuses,
    currentUsage,
    error,
    hasMessages,
    sendMessage,
    clearMessages
  }
})
