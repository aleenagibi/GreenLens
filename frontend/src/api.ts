import type {
  Answer, BackendRoutingDetails, Candidate, Chat, InsightsData, ModelCatalog, Turn,
} from './types'
import { modelName } from './utils'

const CHAT_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/chat'
const API_BASE_URL = CHAT_URL.replace(/\/chat\/?$/, '')
type Err = { detail?: string | { message?: string } }
let csrfTokenValue = ''
type RawChatResponse = BackendRoutingDetails & {
  provider: string
  content: string
  recommendation: { task_type: string; score: number; reason: string }
  benchmark: BackendRoutingDetails['benchmark']
  sustainability: BackendRoutingDetails['sustainability']
  routing: BackendRoutingDetails['routing']
  pipeline: BackendRoutingDetails['pipeline']
  inference?: BackendRoutingDetails['inference']
  context?: BackendRoutingDetails['context']
  conversation_id?: string | null
}
export type AuthUser = {
  id: string
  email: string
  name: string | null
  picture_url: string | null
  email_verified: boolean
}
type ConversationSummary = {
  id: string
  title: string
  created_at: string
  updated_at: string
}
type StoredMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  metadata?: (Partial<RawChatResponse> & { legacy_answer?: Answer }) | null
  created_at: string
}

function errorMessage(data: unknown, fallback: string): string {
  const detail = (data as Err | null)?.detail
  return typeof detail === 'string' ? detail : detail?.message || fallback
}

function csrfToken(): string {
  return csrfTokenValue
}

async function request<T>(path: string, init: RequestInit = {}, csrf = false): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  if (csrf) {
    const token = csrfToken()
    if (token) headers.set('X-CSRF-Token', token)
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init, headers, credentials: 'include',
  })
  if (response.status === 204) return undefined as T
  const data = await response.json().catch(() => null)
  if (!response.ok || data == null) throw new Error(errorMessage(data, `Request failed (${response.status}).`))
  return data as T
}

function mapAnswer(data: RawChatResponse): Answer {
  const routing = data.routing
  const comparison: Candidate[] = (routing.comparison ?? []).filter(
    (candidate, index) => index < 12 || candidate.selected || candidate.ideal,
  )
  return {
    content: data.content,
    model: data.benchmark.model,
    taskType: data.recommendation.task_type,
    latencyMs: data.benchmark.latency_ms,
    carbonG: data.sustainability.carbon_g,
    energyWh: data.sustainability.energy_wh,
    waterL: data.sustainability.water_l ?? null,
    sustainabilitySource: data.sustainability.source ?? "unknown",
    fitScore: routing.fit_score,
    idealModel: modelName(routing.ideal_model, routing.ideal_display_name),
    selectedModel: modelName(routing.selected_model, routing.selected_display_name),
    idealIsFree: routing.ideal_is_free,
    selectedIsFree: routing.selected_is_free,
    reason: routing.reason,
    comparison,
    context: data.context,
    routingDetails: {
      provider: data.provider,
      usage: data.usage,
      benchmark: data.benchmark,
      sustainability: data.sustainability,
      routing: { ...routing, comparison },
      pipeline: data.pipeline,
      inference: data.inference,
      context: data.context,
    },
  }
}

export async function getCurrentUser(): Promise<AuthUser> {
  const data = await request<{ user: AuthUser; csrf_token: string }>('/auth/me')
  csrfTokenValue = data.csrf_token
  return data.user
}

export async function signUp(
  name: string,
  email: string,
  password: string
): Promise<AuthUser> {
  const data = await request<{ user: AuthUser; csrf_token: string }>(
    '/auth/signup',
    {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    }
  )

  csrfTokenValue = data.csrf_token
  return data.user
}

export async function signIn(
  email: string,
  password: string
): Promise<AuthUser> {
  const data = await request<{ user: AuthUser; csrf_token: string }>(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }
  )

  csrfTokenValue = data.csrf_token
  return data.user
}

export async function logout(): Promise<void> {
  await request('/auth/logout', { method: 'POST' }, true)
  csrfTokenValue = ''
}

export async function fetchInsights(): Promise<InsightsData> {
  return request<InsightsData>('/stats')
}

export async function fetchModelCatalog(): Promise<ModelCatalog> {
  return request<ModelCatalog>('/catalog')
}

export async function fetchConversations(): Promise<Chat[]> {
  const data = await request<{ conversations: ConversationSummary[] }>('/conversations')
  return data.conversations.map((item) => ({
    id: item.id, title: item.title, createdAt: item.created_at, updatedAt: item.updated_at, turns: [],
  }))
}

export async function fetchConversation(id: string): Promise<Chat> {
  const data = await request<{ conversation: ConversationSummary & { messages: StoredMessage[] } }>(
    `/conversations/${encodeURIComponent(id)}`,
  )
  const conversation = data.conversation
  const turns: Turn[] = []
  let pendingUser: StoredMessage | null = null
  for (const message of conversation.messages) {
    if (message.role === 'user') {
      pendingUser = message
      continue
    }
    if (message.role === 'assistant' && pendingUser) {
      const metadata = message.metadata
      let answer: Answer | undefined
      try {
        if (metadata?.legacy_answer) {
          answer = metadata.legacy_answer
        } else if (metadata?.routing && metadata?.benchmark && metadata?.sustainability) {
          answer = mapAnswer({ ...metadata, content: message.content } as RawChatResponse)
        }
      } catch {
        answer = undefined
      }
      turns.push({
        id: pendingUser.id,
        prompt: pendingUser.content,
        ts: pendingUser.created_at,
        answer,
      })
      pendingUser = null
    }
  }
  if (pendingUser) {
    turns.push({
      id: pendingUser.id, prompt: pendingUser.content, ts: pendingUser.created_at,
      error: 'This request did not finish. You can send it again.',
    })
  }
  return {
    id: conversation.id, title: conversation.title,
    createdAt: conversation.created_at, updatedAt: conversation.updated_at, turns,
  }
}

export async function createConversation(title = 'New chat'): Promise<Chat> {
  const data = await request<{ conversation: ConversationSummary }>('/conversations', {
    method: 'POST', body: JSON.stringify({ title }),
  }, true)
  const item = data.conversation
  return { id: item.id, title: item.title, createdAt: item.created_at, updatedAt: item.updated_at, turns: [] }
}

export async function deleteConversation(id: string): Promise<void> {
  await request(`/conversations/${encodeURIComponent(id)}`, { method: 'DELETE' }, true)
}

// export async function importLegacyChats(userId: string): Promise<void> {
//   const marker = `greenlens_imported_${userId}`
//   if (localStorage.getItem(marker)) return

//   const currentRaw = localStorage.getItem('greenlens_chats_v2')
//   let chats: unknown
//   if (currentRaw) {
//     try { chats = JSON.parse(currentRaw) } catch { return }
//   } else {
//     // Support the older flat-history format used by earlier GreenLens builds.
//     const oldRaw = localStorage.getItem('greenlens_history_v1')
//     if (!oldRaw) {
//       localStorage.setItem(marker, '1')
//       return
//     }
//     let oldItems: unknown
//     try { oldItems = JSON.parse(oldRaw) } catch { return }
//     if (!Array.isArray(oldItems)) return
//     chats = oldItems.flatMap((item, index) => {
//       const prompt = String(item.prompt ?? '').trim()
//       if (!prompt) return []
//       const createdAt = typeof item.createdAt === 'string' ? item.createdAt : new Date().toISOString()
//       const comparison: Candidate[] = Array.isArray(item.comparison) ? item.comparison : []
//       const answer: Answer = {
//         content: String(item.content ?? ''),
//         model: String(item.model ?? 'Unknown model'),
//         taskType: String(item.taskType ?? 'unknown'),
//         latencyMs: Number(item.latencyMs ?? 0),
//         carbonG: Number(item.carbonG ?? 0),
//         energyWh: Number(item.energyWh ?? 0),
//         fitScore: Number(item.fitScore ?? 0),
//         idealModel: String(item.idealModel ?? 'Unknown'),
//         selectedModel: String(item.selectedModel ?? item.model ?? 'Unknown'),
//         idealIsFree: false,
//         selectedIsFree: Boolean(comparison.find((candidate) => candidate.selected)?.is_free),
//         reason: '',
//         comparison: comparison.slice(0, 12),
//       }
//       return [{
//         id: `legacy-v1-${index}-${Date.parse(createdAt) || index}`,
//         title: prompt.slice(0, 48),
//         createdAt,
//         updatedAt: createdAt,
//         turns: [{ id: `legacy-turn-${index}`, prompt, ts: createdAt, answer }],
//       }]
//     })
//   }

//   if (!Array.isArray(chats) || chats.length === 0) {
//     localStorage.setItem(marker, '1')
//     return
//   }
//   const normalized = chats.slice(0, 30).map((chat) => ({
//     ...chat,
//     turns: Array.isArray(chat.turns) ? chat.turns.slice(-200) : [],
//   }))
//   await request('/conversations/import', {
//     method: 'POST',
//     body: JSON.stringify({ conversations: normalized }),
//   }, true)
//   localStorage.setItem(marker, '1')
// }

export async function sendPrompt(prompt: string, conversationId: string): Promise<Answer> {
  const data = await request<RawChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ prompt, conversation_id: conversationId }),
  }, true)
  return mapAnswer(data)
}
