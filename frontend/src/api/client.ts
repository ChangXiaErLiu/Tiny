import axios from 'axios'
import type { SkillManifest, ChatResponse } from '@/types/skill'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const chatApi = {
  sendMessage: async (message: string, sessionId?: string) => {
    const response = await client.post<ChatResponse>('/chat/chat', {
      message,
      session_id: sessionId
    })
    return response.data
  },

  sendMessageStream: (message: string, sessionId?: string) => {
    return new EventSource(`${client.defaults.baseURL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, session_id: sessionId })
    })
  }
}

export const skillApi = {
  listSkills: async () => {
    const response = await client.get<{ skills: SkillManifest[] }>('/skills')
    return response.data.skills
  },

  getSkill: async (name: string) => {
    const response = await client.get<SkillManifest>(`/skills/${name}`)
    return response.data
  },

  invokeSkill: async (name: string, parameters: Record<string, any>) => {
    const response = await client.post(`/skills/${name}/invoke`, { parameters })
    return response.data
  }
}

export const healthApi = {
  check: async () => {
    const response = await client.get('/health')
    return response.data
  }
}

export default client
