<template>
  <div class="skill-status">
    <template v-for="(status, skill) in statuses" :key="skill">
      <div :class="['skill-badge', `skill-${status}`]">
        <div class="skill-icon">
          <svg v-if="status === 'pending'" class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
          </svg>
          <svg v-else-if="status === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M15 9l-6 6M9 9l6 6"/>
          </svg>
        </div>
        <span>{{ getSkillLabel(skill) }}</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  statuses: Record<string, 'pending' | 'success' | 'failed'>
  tagSize?: 'small' | 'default'
}>(), {
  tagSize: 'small'
})

function getSkillLabel(skill: string): string {
  const labels: Record<string, string> = {
    weather_query: '天气',
    travel_planner: '旅游',
    deepseek_llm: 'AI'
  }
  return labels[skill] || skill
}
</script>

<style scoped>
.skill-status {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.skill-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s;
}

.skill-icon {
  width: 12px;
  height: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skill-icon svg {
  width: 12px;
  height: 12px;
}

.skill-pending {
  background: #fef3c7;
  color: #d97706;
}

.skill-success {
  background: #d1fae5;
  color: #059669;
}

.skill-failed {
  background: #fee2e2;
  color: #dc2626;
}

.spin {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
