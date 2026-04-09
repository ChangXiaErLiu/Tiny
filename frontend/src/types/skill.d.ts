export interface SkillManifest {
  name: string
  version: string
  description: string
  parameters: Record<string, any>
  timeout?: number
  retry?: number
}

export interface SkillResult {
  success: boolean
  data?: any
  error?: string
  execution_time_ms: number
  skill_name: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  skillStatus?: Record<string, 'pending' | 'success' | 'failed'>
}

export interface StreamEvent {
  event: string
  data: Record<string, any>
}

export interface IntentInfo {
  type: string
  confidence: number
  required_skills: string[]
}

export interface UsageInfo {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface ChatResponse {
  session_id: string
  content: string
  skill_results: Record<string, any>
  usage: UsageInfo
}
