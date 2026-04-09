import { ref, onMounted } from 'vue'
import { skillApi, healthApi } from '@/api/client'
import type { SkillManifest } from '@/types/skill'

export function useSkillStatus() {
  const skills = ref<SkillManifest[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const healthStatus = ref<Record<string, string>>({})

  async function loadSkills() {
    isLoading.value = true
    error.value = null
    
    try {
      skills.value = await skillApi.listSkills()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load skills'
    } finally {
      isLoading.value = false
    }
  }

  async function checkHealth() {
    try {
      const result = await healthApi.check()
      healthStatus.value = result.services || {}
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Health check failed'
      return null
    }
  }

  onMounted(() => {
    loadSkills()
  })

  return {
    skills,
    isLoading,
    error,
    healthStatus,
    loadSkills,
    checkHealth
  }
}
