<template>
  <div :class="['message-wrapper', `message-${message.role}`, { 'is-typing': isTyping, 'is-new': isNew }]">
    <div class="message-avatar">
      <div v-if="message.role === 'user'" class="avatar user-avatar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
      <div v-else class="avatar bot-avatar" :class="{ 'bot-thinking': isTyping }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </div>
    </div>

    <div class="message-content">
      <div class="message-bubble" :class="{ 'bubble-animate': isNew }">
        <div class="message-text">
          <MarkdownRenderer v-if="message.content" :content="message.content" />
          <div v-else-if="isTyping" class="typing-container">
            <span class="typing-star">✦</span>
            <span class="typing-star">✦</span>
            <span class="typing-star">✦</span>
          </div>
          <span v-else class="empty-text">...</span>
        </div>

        <Transition name="fade">
          <div v-if="message.content" class="message-actions">
            <button class="action-btn" @click="copyContent" :title="copied ? '已复制!' : '复制'">
              <svg v-if="!copied" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
            </button>
          </div>
        </Transition>
      </div>

      <div class="message-meta" v-if="message.timestamp">
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
        <SkillStatus
          v-if="message.role === 'assistant' && message.skillStatus && Object.keys(message.skillStatus).length > 0"
          :statuses="message.skillStatus"
        />
      </div>
    </div>

    <Transition name="confetti">
      <div v-if="showCelebration" class="celebration">
        <span v-for="i in 12" :key="i" class="confetti-piece" :style="{ '--i': i }">🎉</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import SkillStatus from './SkillStatus.vue'
import type { ChatMessage } from '@/types/skill'

const props = withDefaults(defineProps<{
  message: ChatMessage
  isTyping?: boolean
}>(), {
  isTyping: false
})

const copied = ref(false)
const isNew = ref(false)
const showCelebration = ref(false)

onMounted(() => {
  isNew.value = true
  setTimeout(() => {
    isNew.value = false
  }, 500)

  if (props.message.content && props.message.content.includes('旅游计划')) {
    showCelebration.value = true
    setTimeout(() => {
      showCelebration.value = false
    }, 2000)
  }
})

watch(() => props.message.content, (newVal) => {
  if (newVal) {
    isNew.value = true
    setTimeout(() => {
      isNew.value = false
    }, 500)

    if (newVal.includes('旅游计划') || newVal.includes('行程')) {
      showCelebration.value = true
      setTimeout(() => {
        showCelebration.value = false
      }, 2000)
    }
  }
})

async function copyContent() {
  if (!props.message.content) return
  try {
    await navigator.clipboard.writeText(props.message.content)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}

function formatTime(timestamp: number): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.message-wrapper {
  position: relative;
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message-wrapper.is-new {
  animation: messageSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-assistant {
  margin-right: auto;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.avatar svg {
  width: 20px;
  height: 20px;
}

.user-avatar {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
}

.bot-avatar {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  color: #1a1a2e;
  border: 1px solid #e5e7eb;
}

.bot-avatar.bot-thinking {
  animation: botThink 2s ease-in-out infinite;
}

@keyframes botThink {
  0%, 100% { transform: rotate(-3deg) scale(1); }
  50% { transform: rotate(3deg) scale(1.05); }
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.message-user .message-content {
  align-items: flex-end;
}

.message-bubble {
  position: relative;
  padding: 14px 18px;
  border-radius: 18px;
  max-width: 100%;
  word-break: break-word;
  line-height: 1.6;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.message-bubble.bubble-animate {
  animation: bubblePop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes bubblePop {
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); opacity: 1; }
}

.message-bubble:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.message-bubble:hover .message-actions {
  opacity: 1;
}

.message-user .message-bubble {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #f1f5f9;
  border-bottom-right-radius: 6px;
}

.message-assistant .message-bubble {
  background: #ffffff;
  color: #374151;
  border-bottom-left-radius: 6px;
  border: 1px solid #e5e7eb;
}

.message-text {
  min-height: 20px;
}

.typing-container {
  display: inline-flex;
  gap: 6px;
  padding: 4px 0;
}

.typing-star {
  font-size: 12px;
  color: #fbbf24;
  animation: starPulse 1.5s ease-in-out infinite;
}

.typing-star:nth-child(1) { animation-delay: 0s; }
.typing-star:nth-child(2) { animation-delay: 0.2s; }
.typing-star:nth-child(3) { animation-delay: 0.4s; }

@keyframes starPulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.empty-text {
  opacity: 0.4;
}

.message-actions {
  position: absolute;
  top: -8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-user .message-actions {
  right: auto;
  left: 8px;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: white;
  border-radius: 8px;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #1a1a2e;
  transform: scale(1.1);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.message-time {
  font-size: 11px;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.message-user .message-time {
  color: rgba(255, 255, 255, 0.5);
}

.message-assistant .message-time {
  color: rgba(0, 0, 0, 0.35);
}

.celebration {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.confetti-piece {
  position: absolute;
  font-size: 20px;
  animation: confettiFall 2s ease-out forwards;
  animation-delay: calc(var(--i) * 0.1s);
}

@keyframes confettiFall {
  0% {
    opacity: 1;
    transform: translateY(0) rotate(0deg) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-100px) translateX(calc(var(--i) * 20px - 120px)) rotate(720deg) scale(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.confetti-enter-active {
  animation: confettiIn 0.3s ease-out;
}

.confetti-leave-active {
  animation: confettiIn 0.3s ease-out reverse;
}

@keyframes confettiIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 640px) {
  .message-wrapper {
    max-width: 92%;
    gap: 8px;
  }

  .avatar {
    width: 34px;
    height: 34px;
    border-radius: 10px;
  }

  .avatar svg {
    width: 16px;
    height: 16px;
  }

  .message-bubble {
    padding: 12px 14px;
    font-size: 14px;
  }

  .message-actions {
    opacity: 1;
  }
}
</style>
