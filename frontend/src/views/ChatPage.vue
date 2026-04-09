<template>
  <div class="chat-page">
    <header class="chat-header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-icon" :class="{ 'logo-excited': messageCount > 5 }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-title">TinyBill</span>
            <span class="logo-subtitle">智能旅游助手</span>
          </div>
        </div>

        <Transition name="slide">
          <div v-if="contextIcon" class="context-badge">
            <span class="context-icon">{{ contextIcon }}</span>
            <span class="context-text">{{ contextText }}</span>
          </div>
        </Transition>
      </div>

      <div class="header-right">
        <div v-if="messageCount > 0" class="message-counter">
          <span class="counter-num">{{ messageCount }}</span>
          <span class="counter-label">条对话</span>
        </div>

        <div class="shortcuts-hint">
          <kbd>⌘</kbd> + <kbd>K</kbd>
        </div>
        <button class="icon-btn" @click="clearMessages" :disabled="isStreaming" title="清空对话">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
          </svg>
        </button>
      </div>
    </header>

    <main class="chat-main">
      <div class="messages-container" ref="messagesContainer">
        <Transition name="onboard" appear>
          <div v-if="showOnboarding" class="onboarding">
            <div class="onboard-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            <h3>你好，我是 TinyBill！</h3>
            <p>我可以帮你规划旅游行程、查询天气。<br/>试试这样问我：</p>
          </div>
        </Transition>

        <div v-if="!hasMessages && !isStreaming && !showOnboarding" class="welcome-state">
          <div class="idle-robot">
            <div class="robot-body">
              <div class="robot-head">
                <div class="robot-eyes">
                  <span class="eye"></span>
                  <span class="eye"></span>
                </div>
                <div class="robot-mouth"></div>
              </div>
              <div class="robot-antenna">
                <div class="antenna-light"></div>
              </div>
            </div>
            <div class="robot-shadow"></div>
          </div>
          <p class="idle-text">有什么可以帮助你的吗？</p>
        </div>

        <div v-else class="message-list">
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            class="message-item"
          >
            <div v-if="shouldShowTimeDivider(message, index)" class="time-divider">
              <span>{{ formatDateDivider(message.timestamp) }}</span>
            </div>
            <ChatMessage
              :message="message"
              :is-typing="isStreaming && index === messages.length - 1"
            />
          </div>
        </div>

        <div v-if="isStreaming && messages.length > 0" class="typing-indicator">
          <div class="typing-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="typing-label">{{ typingLabel }}</div>
        </div>
      </div>
    </main>

    <footer class="chat-footer">
      <div v-if="showProgress" class="progress-bar">
        <div class="progress-steps">
          <div
            v-for="(step, index) in progressSteps"
            :key="index"
            :class="['progress-step', { active: step.active, completed: step.completed }]"
          >
            <div class="step-dot">
              <svg v-if="step.completed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
            </div>
            <span class="step-label">{{ step.label }}</span>
          </div>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper" :class="{ focused: inputFocused, breathing: isStreaming }">
          <textarea
            v-model="inputText"
            :disabled="isStreaming"
            placeholder="输入你的问题..."
            @keydown.enter.exact.prevent="handleSend"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
            @input="autoResize"
            ref="textareaRef"
            rows="1"
          ></textarea>
          <button
            class="send-btn"
            @click="handleSend"
            :disabled="!inputText.trim() || isStreaming"
            :class="{ active: inputText.trim() && !isStreaming, sending: isSending }"
            @mousedown="onSendMouseDown"
          >
            <svg v-if="!isSending" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="send-icon">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="paper-plane">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </footer>

    <Transition name="command">
      <div v-if="showCommandPalette" class="command-palette" @click.self="showCommandPalette = false">
        <div class="command-modal">
          <div class="command-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              v-model="commandSearch"
              placeholder="搜索命令..."
              class="command-input"
              @keydown.esc="showCommandPalette = false"
            />
          </div>
          <div class="command-list">
            <button
              v-for="cmd in filteredCommands"
              :key="cmd.name"
              class="command-item"
              @click="executeCommand(cmd)"
            >
              <span class="command-icon">{{ cmd.icon }}</span>
              <div class="command-info">
                <span class="command-name">{{ cmd.name }}</span>
                <span class="command-desc">{{ cmd.description }}</span>
              </div>
              <kbd v-if="cmd.shortcut" class="command-shortcut">{{ cmd.shortcut }}</kbd>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="easter-egg">
      <div v-if="easterEgg" class="easter-egg-overlay" @click="easterEgg = null">
        <div class="easter-egg-content">
          <div class="egg-face">{{ easterEgg.emoji }}</div>
          <p>{{ easterEgg.message }}</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/ChatMessage.vue'

interface Command {
  name: string
  description: string
  icon: string
  shortcut?: string
  action: () => void
}

interface ProgressStep {
  label: string
  active: boolean
  completed: boolean
}

interface EasterEgg {
  emoji: string
  message: string
  trigger: string
}

const chatStore = useChatStore()

const inputText = ref('')
const inputFocused = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const showCommandPalette = ref(false)
const commandSearch = ref('')
const isSending = ref(false)
const showOnboarding = ref(false)
const easterEgg = ref<EasterEgg | null>(null)
const progressSteps = ref<ProgressStep[]>([])

const messages = computed(() => chatStore.messages)
const isStreaming = computed(() => chatStore.isStreaming)
const hasMessages = computed(() => chatStore.hasMessages)

const messageCount = computed(() => messages.value.length)

const contextIcon = computed(() => {
  const lastUserMessage = messages.value.filter(m => m.role === 'user').pop()
  if (!lastUserMessage) return null
  const text = lastUserMessage.content
  if (text.includes('天气') || text.includes('雨') || text.includes('晴')) return '🌤️'
  if (text.includes('桂林') || text.includes('南宁') || text.includes('旅游')) return '🗺️'
  if (text.includes('伞')) return '☂️'
  if (text.includes('吃') || text.includes('美食') || text.includes('餐厅')) return '🍜'
  return null
})

const contextText = computed(() => {
  if (contextIcon.value === '🌤️') return '查询天气'
  if (contextIcon.value === '🗺️') return '规划行程'
  if (contextIcon.value === '☂️') return '准备雨具'
  if (contextIcon.value === '🍜') return '美食推荐'
  return ''
})

const typingLabel = computed(() => {
  if (currentIntent.value === 'travel_plan') return '规划中...'
  if (currentIntent.value === 'weather_query') return '查询中...'
  return '思考中...'
})

const currentIntent = computed(() => {
  // 简化逻辑，从消息推断
  return null
})

const showProgress = computed(() => progressSteps.value.length > 0)

const progressPercent = computed(() => {
  const completed = progressSteps.value.filter(s => s.completed).length
  return (completed / progressSteps.value.length) * 100
})

const suggestions = [
  { icon: '🌤️', text: '南宁明天天气怎么样？' },
  { icon: '🗺️', text: '帮我制定一个三天的南宁旅游计划' },
  { icon: '☂️', text: '去桂林玩3天需要带伞吗' },
  { icon: '🍜', text: '南宁有什么好吃的推荐？' },
]

const commands: Command[] = [
  {
    name: '清空对话',
    description: '清除所有聊天记录',
    icon: '🗑️',
    shortcut: 'Ctrl+Shift+D',
    action: () => clearMessages()
  },
  {
    name: '导出对话',
    description: '将对话导出为 Markdown',
    icon: '📤',
    action: () => exportConversation()
  },
]

const easterEggs: EasterEgg[] = [
  { emoji: '🤖', message: '哎呀，被你发现了！', trigger: '小笨笨' },
  { emoji: '😮', message: '诶，这个我也会！', trigger: '你好' },
  { emoji: '🤔', message: '让我想想...', trigger: '为什么' },
  { emoji: '👋', message: '再见啦！下次见！', trigger: '再见' },
]

const filteredCommands = computed(() => {
  if (!commandSearch.value) return commands
  const search = commandSearch.value.toLowerCase()
  return commands.filter(cmd =>
    cmd.name.toLowerCase().includes(search) ||
    cmd.description.toLowerCase().includes(search)
  )
})

function handleSend() {
  if (!inputText.value.trim() || isStreaming.value) return

  const text = inputText.value.trim()
  checkEasterEgg(text)

  chatStore.sendMessage(text)
  inputText.value = ''
  isSending.value = true

  setTimeout(() => {
    isSending.value = false
  }, 600)

  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

function onSendMouseDown() {
  if (inputText.value.trim() && !isStreaming.value) {
    isSending.value = true
  }
}

function clearMessages() {
  chatStore.clearMessages()
  showCommandPalette.value = false
  showOnboarding.value = false
  messageCount.value
}

function checkEasterEgg(text: string) {
  for (const egg of easterEggs) {
    if (text.includes(egg.trigger)) {
      easterEgg.value = egg
      setTimeout(() => {
        easterEgg.value = null
      }, 3000)
      break
    }
  }
}

function exportConversation() {
  const content = messages.value.map(m => {
    const role = m.role === 'user' ? '**用户**' : '**TinyBill**'
    return `${role}:\n${m.content}\n`
  }).join('\n---\n\n')

  const blob = new Blob([`# 对话记录\n\n${content}`], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `conversation-${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
  showCommandPalette.value = false
}

function quickAsk(question: string) {
  inputText.value = question
  handleSend()
}

function autoResize(e: Event) {
  const textarea = e.target as HTMLTextAreaElement
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
}

function shouldShowTimeDivider(message: any, index: number): boolean {
  if (index === 0) return true
  const prevMessage = messages.value[index - 1]
  const timeDiff = message.timestamp - prevMessage.timestamp
  return timeDiff > 5 * 60 * 1000
}

function formatDateDivider(timestamp: number): string {
  const date = new Date(timestamp)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
  }
}

function executeCommand(cmd: Command) {
  cmd.action()
  showCommandPalette.value = false
  commandSearch.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showCommandPalette.value = !showCommandPalette.value
  }
  if (e.ctrlKey && e.shiftKey && e.key === 'D') {
    e.preventDefault()
    clearMessages()
  }
}

function updateProgress(steps: string[]) {
  progressSteps.value = steps.map((label, i) => ({
    label,
    active: i === 0,
    completed: false
  }))

  let current = 0
  const interval = setInterval(() => {
    if (current < progressSteps.value.length) {
      progressSteps.value[current].completed = true
      progressSteps.value[current].active = false
      if (current + 1 < progressSteps.value.length) {
        progressSteps.value[current + 1].active = true
      }
      current++
    } else {
      clearInterval(interval)
      setTimeout(() => {
        progressSteps.value = []
      }, 1000)
    }
  }, 800)
}

watch(messages, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}, { deep: true })

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)

  const hasVisited = localStorage.getItem('tinybill_visited')
  if (!hasVisited) {
    showOnboarding.value = true
    setTimeout(() => {
      showOnboarding.value = false
      localStorage.setItem('tinybill_visited', 'true')
    }, 4000)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.chat-page {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 900px;
  margin: 0 auto;
  background: transparent;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s;
}

.logo-icon svg {
  width: 24px;
  height: 24px;
}

.logo-icon.logo-excited {
  animation: logoExcited 0.5s ease;
}

@keyframes logoExcited {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-10deg) scale(1.1); }
  75% { transform: rotate(10deg) scale(1.1); }
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: -0.5px;
}

.logo-subtitle {
  font-size: 12px;
  color: #6b7280;
}

.context-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 20px;
  animation: badgePop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes badgePop {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.context-icon {
  font-size: 16px;
}

.context-text {
  font-size: 12px;
  color: #92400e;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.message-counter {
  display: flex;
  align-items: baseline;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 20px;
}

.counter-num {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
}

.counter-label {
  font-size: 11px;
  color: #9ca3af;
}

.shortcuts-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #9ca3af;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 8px;
}

.shortcuts-hint kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 5px;
  font-size: 10px;
  font-family: inherit;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.08);
  color: #1a1a2e;
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.icon-btn svg {
  width: 20px;
  height: 20px;
}

.chat-main {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.onboarding {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  z-index: 10;
  text-align: center;
  padding: 24px;
}

.onboard-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  animation: onboardBounce 1s ease infinite;
}

@keyframes onboardBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.onboard-avatar svg {
  width: 40px;
  height: 40px;
  color: #d97706;
}

.onboarding h3 {
  font-size: 24px;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.onboarding p {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
}

.onboard-enter-active {
  animation: onboardIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.onboard-leave-active {
  animation: onboardOut 0.5s ease forwards;
}

@keyframes onboardIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes onboardOut {
  to { opacity: 0; transform: scale(1.1); }
}

.welcome-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.idle-robot {
  position: relative;
  margin-bottom: 24px;
}

.robot-body {
  position: relative;
  width: 100px;
  height: 100px;
}

.robot-head {
  width: 80px;
  height: 60px;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 20px;
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: robotIdle 3s ease-in-out infinite;
}

@keyframes robotIdle {
  0%, 100% { transform: translateX(-50%) rotate(0); }
  25% { transform: translateX(-50%) rotate(-3deg); }
  75% { transform: translateX(-50%) rotate(3deg); }
}

.robot-eyes {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.eye {
  width: 12px;
  height: 12px;
  background: #1a1a2e;
  border-radius: 50%;
  animation: blink 4s ease-in-out infinite;
}

@keyframes blink {
  0%, 90%, 100% { transform: scaleY(1); }
  95% { transform: scaleY(0.1); }
}

.robot-mouth {
  width: 20px;
  height: 8px;
  background: #d1d5db;
  border-radius: 4px;
}

.robot-antenna {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 30px;
  background: #d1d5db;
  border-radius: 2px;
}

.antenna-light {
  width: 12px;
  height: 12px;
  background: #10b981;
  border-radius: 50%;
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  50% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
}

.robot-shadow {
  width: 60px;
  height: 10px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  margin-top: -5px;
  animation: shadowPulse 3s ease-in-out infinite;
}

@keyframes shadowPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(0.8); opacity: 0.3; }
}

.idle-text {
  font-size: 14px;
  color: #9ca3af;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  flex-direction: column;
}

.time-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 16px 0;
}

.time-divider span {
  padding: 4px 12px;
  font-size: 11px;
  color: #9ca3af;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
}

.typing-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: typingPulse 1.5s ease-in-out infinite;
}

@keyframes typingPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.typing-avatar svg {
  width: 18px;
  height: 18px;
}

.typing-label {
  font-size: 13px;
  color: #9ca3af;
  animation: typingText 1.5s ease-in-out infinite;
}

@keyframes typingText {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.chat-footer {
  padding: 16px 24px 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.progress-bar {
  margin-bottom: 12px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.progress-step.active .step-dot {
  background: #fef3c7;
  animation: stepPulse 1s ease-in-out infinite;
}

@keyframes stepPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.progress-step.completed .step-dot {
  background: #10b981;
  color: white;
}

.step-dot svg {
  width: 14px;
  height: 14px;
}

.step-label {
  font-size: 11px;
  color: #9ca3af;
  transition: color 0.3s;
}

.progress-step.active .step-label {
  color: #d97706;
  font-weight: 500;
}

.progress-step.completed .step-label {
  color: #10b981;
}

.progress-track {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  transition: all 0.3s;
}

.input-wrapper.focused {
  border-color: #1a1a2e;
  box-shadow: 0 0 0 4px rgba(26, 26, 46, 0.1);
}

.input-wrapper.breathing {
  animation: breathingGlow 2s ease-in-out infinite;
}

@keyframes breathingGlow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.2); }
  50% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
}

.input-wrapper textarea {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #1a1a2e;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  line-height: 1.5;
  max-height: 120px;
}

.input-wrapper textarea::placeholder {
  color: #9ca3af;
}

.send-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: #f3f4f6;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn svg {
  width: 20px;
  height: 20px;
  transition: transform 0.2s;
}

.send-btn.active {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(26, 26, 46, 0.3);
}

.send-btn.active:hover {
  transform: scale(1.05);
}

.send-btn.sending .send-icon {
  animation: sendPlane 0.5s ease-out forwards;
}

@keyframes sendPlane {
  0% { transform: translateX(0) translateY(0) rotate(0); opacity: 1; }
  100% { transform: translateX(30px) translateY(-30px) rotate(15deg); opacity: 0; }
}

.send-btn.sending .paper-plane {
  animation: flyAway 0.5s ease-out forwards;
}

@keyframes flyAway {
  0% { transform: translateX(-30px) translateY(30px) rotate(-15deg); opacity: 0; }
  100% { transform: translateX(0) translateY(0) rotate(0); opacity: 1; }
}

.send-btn:disabled {
  cursor: not-allowed;
}

.command-palette {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.command-modal {
  width: 90%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.command-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #9ca3af;
  flex-shrink: 0;
}

.command-input {
  flex: 1;
  padding: 0;
  font-size: 16px;
  border: none;
  outline: none;
  background: none;
  color: #1a1a2e;
}

.command-input::placeholder {
  color: #9ca3af;
}

.command-list {
  max-height: 280px;
  overflow-y: auto;
  padding: 8px;
}

.command-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  background: none;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.command-item:hover {
  background: #f3f4f6;
}

.command-icon {
  font-size: 20px;
}

.command-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.command-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.command-desc {
  font-size: 12px;
  color: #9ca3af;
}

.command-shortcut {
  padding: 4px 8px;
  font-size: 10px;
  font-family: inherit;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #6b7280;
}

.command-enter-active,
.command-leave-active {
  transition: all 0.2s ease;
}

.command-enter-from,
.command-leave-to {
  opacity: 0;
}

.easter-egg-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  z-index: 2000;
  cursor: pointer;
  backdrop-filter: blur(8px);
}

.easter-egg-content {
  text-align: center;
  animation: eggPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes eggPop {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.egg-face {
  font-size: 80px;
  margin-bottom: 16px;
  animation: eggBounce 1s ease infinite;
}

@keyframes eggBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.easter-egg-content p {
  font-size: 20px;
  color: white;
  font-weight: 500;
}

.easter-egg-enter-active {
  animation: eggFadeIn 0.3s ease;
}

.easter-egg-leave-active {
  animation: eggFadeIn 0.3s ease reverse;
}

@keyframes eggFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
  .chat-page {
    max-width: 100%;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .shortcuts-hint,
  .message-counter {
    display: none;
  }

  .context-badge {
    padding: 4px 8px;
    font-size: 11px;
  }

  .messages-container {
    padding: 16px;
  }

  .chat-footer {
    padding: 12px 16px 20px;
  }
}
</style>
