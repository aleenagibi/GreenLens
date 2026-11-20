
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { Chat, Turn } from '../types'
import {
  createConversation,
  deleteConversation,
  fetchConversation,
  fetchConversations,
} from '../api'
import { uid } from '../utils'

export function useChats(enabled: boolean) {
  const [chats, setChats] = useState<Chat[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Invalidates requests started under a previous authentication session.
  const sessionRef = useRef(0)

  useEffect(() => {
    sessionRef.current += 1
    const session = sessionRef.current

    if (!enabled) {
      setChats([])
      setActiveId(null)
      setLoading(false)
      return
    }

    let active = true
    setChats([])
    setActiveId(null)
    setLoading(true)

    fetchConversations()
      .then((items) => {
        if (!active || sessionRef.current !== session) return
        setChats(items)
      })
      .catch((error) => {
        if (active && sessionRef.current === session) {
          console.error('Could not load conversations:', error)
        }
      })
      .finally(() => {
        if (active && sessionRef.current === session) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [enabled])

  const active = useMemo(
    () => chats.find((chat) => chat.id === activeId) ?? null,
    [chats, activeId]
  )

  const refresh = useCallback(async () => {
    if (!enabled) return

    const session = sessionRef.current
    setLoading(true)

    try {
      const items = await fetchConversations()

      if (sessionRef.current !== session) return

      setChats(items)
      setActiveId((current) =>
        current && items.some((item) => item.id === current)
          ? current
          : null
      )
    } finally {
      if (sessionRef.current === session) {
        setLoading(false)
      }
    }
  }, [enabled])

  const load = useCallback(async (id: string) => {
    const session = sessionRef.current
    setActiveId(id)

    try {
      const full = await fetchConversation(id)

      if (sessionRef.current !== session) return

      setChats((current) => [
        full,
        ...current.filter((chat) => chat.id !== id),
      ])
    } catch (error) {
      if (sessionRef.current === session) {
        setActiveId(null)
        throw error
      }
    }
  }, [])

  const create = useCallback(async () => {
    const session = sessionRef.current
    const chat = await createConversation()

    if (sessionRef.current !== session) {
      throw new Error('Your session changed. Please try again.')
    }

    setChats((current) => [chat, ...current])
    setActiveId(chat.id)
    return chat.id
  }, [])

  const startTurn = useCallback((prompt: string, chatId: string) => {
    const now = new Date().toISOString()
    const turn: Turn = {
      id: uid(),
      prompt,
      ts: now,
      pending: true,
    }

    setChats((current) => {
      const existing = current.find((chat) => chat.id === chatId)
      if (!existing) return current

      const updated = {
        ...existing,
        title:
          existing.title === 'New chat'
            ? prompt.slice(0, 48)
            : existing.title,
        updatedAt: now,
        turns: [...existing.turns, turn],
      }

      return [
        updated,
        ...current.filter((chat) => chat.id !== chatId),
      ]
    })

    setActiveId(chatId)
    return { turnId: turn.id }
  }, [])

  const finishTurn = useCallback((
    chatId: string,
    turnId: string,
    patch: Partial<Turn>
  ) => {
    setChats((current) =>
      current.map((chat) =>
        chat.id !== chatId
          ? chat
          : {
              ...chat,
              turns: chat.turns.map((turn) =>
                turn.id === turnId
                  ? { ...turn, ...patch, pending: false }
                  : turn
              ),
            }
      )
    )
  }, [])

  const remove = useCallback(async (id: string) => {
    const session = sessionRef.current

    await deleteConversation(id)

    if (sessionRef.current !== session) return

    setChats((current) => current.filter((chat) => chat.id !== id))
    setActiveId((current) => current === id ? null : current)
  }, [])

  return {
    chats,
    active,
    activeId,
    setActiveId,
    startTurn,
    finishTurn,
    remove,
    load,
    create,
    refresh,
    loading,
  }
}
