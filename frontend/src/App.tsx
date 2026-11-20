
import { useCallback, useEffect, useState } from 'react'
import './App.css'
import {
  fetchModelCatalog,
  getCurrentUser,
  logout,
  sendPrompt,
} from './api'
import type { AuthUser } from './api'
import Sidebar from './components/Sidebar'
import { useChats } from './hooks/useChats'
import ChatPage from './pages/ChatPage'
import HowPage from './pages/Howpage'
import InsightsPage from './pages/Insightspage'
import LoginPage from './pages/LoginPage'
import type { ModelCatalog, Page } from './types'

function AppCredit() {
  return (
    <footer className="app-credit">
      <a
        href="https://github.com/aleenagibi/"
        target="_blank"
        rel="noopener noreferrer"
        className="app-credit-link"
        aria-label="GitHub - Aleena Gibi"
      >
        <svg
          viewBox="0 0 24 24"
          width="17"
          height="17"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.56.1.76-.24.76-.54v-2.08c-3.1.67-3.76-1.32-3.76-1.32-.51-1.3-1.24-1.65-1.24-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.72 1.16 1.72 1.16 1 1.72 2.62 1.22 3.26.93.1-.72.39-1.22.71-1.5-2.48-.28-5.09-1.24-5.09-5.52 0-1.22.44-2.22 1.16-3-.12-.28-.5-1.42.11-2.96 0 0 .95-.3 3.11 1.15a10.8 10.8 0 0 1 5.66 0c2.16-1.45 3.1-1.15 3.1-1.15.62 1.54.23 2.68.12 2.96.72.78 1.15 1.78 1.15 3 0 4.29-2.61 5.23-5.1 5.51.4.35.76 1.02.76 2.06v3.15c0 .3.2.65.77.54A11.1 11.1 0 0 0 12 .9Z" />
        </svg>
        <span>GitHub · Aleena Gibi</span>
      </a>
    </footer>
  )
}

export default function App() {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [authError, setAuthError] = useState('')

  const store = useChats(Boolean(user))

  const [page, setPage] = useState<Page>('chat')
  const [menu, setMenu] = useState(false)
  const [busy, setBusy] = useState(false)
  const [catalog, setCatalog] = useState<ModelCatalog | null>(null)

  // Restore the authenticated user without importing browser-wide legacy chats.
  useEffect(() => {
    let active = true

    getCurrentUser()
      .then((current) => {
        if (active) setUser(current)
      })
      .catch(() => {
        if (active) setUser(null)
      })
      .finally(() => {
        if (active) setAuthLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const onSignedIn = useCallback(async () => {
    try {
      const current = await getCurrentUser()
      setUser(current)
      setAuthError('')
    } catch (error) {
      setAuthError(
        error instanceof Error
          ? error.message
          : 'Could not establish your session.'
      )
    }
  }, [])

  useEffect(() => {
    if (!user) return

    let active = true

    fetchModelCatalog()
      .then((data) => {
        if (active) setCatalog(data)
      })
      .catch((error) => {
        console.warn('Could not load the live model catalogue:', error)
      })

    return () => {
      active = false
    }
  }, [user])

  const send = async (prompt: string) => {
    if (busy || !user) return

    setPage('chat')
    setBusy(true)

    let chatId = store.activeId

    try {
      if (!chatId) chatId = await store.create()

      const { turnId } = store.startTurn(prompt, chatId)

      try {
        const answer = await sendPrompt(prompt, chatId)
        store.finishTurn(chatId, turnId, { answer })
      } catch (error) {
        store.finishTurn(chatId, turnId, {
          error:
            error instanceof Error
              ? error.message
              : 'Could not reach the GreenLens server.',
        })
      }
    } catch (error) {
      setAuthError(
        error instanceof Error
          ? error.message
          : 'Could not create a conversation.'
      )
    } finally {
      setBusy(false)
    }
  }

  const go = (p: Page) => {
    setPage(p)
    setMenu(false)
  }

  const title =
    page === 'chat'
      ? store.active?.title ?? 'New chat'
      : page === 'insights'
        ? 'Insights'
        : 'How it works'

  const signOut = async () => {
    try {
      await logout()
      setUser(null)
      setCatalog(null)
      setPage('chat')
      setMenu(false)
    } catch (error) {
      setAuthError(
        error instanceof Error ? error.message : 'Could not sign out.'
      )
    }
  }

  if (authLoading) {
    return (
      <main className="gl-loading-screen">
        <div className="gl-loading-content">
          <div className="gl-loading-logo">
            <img src="/logo.png" alt="GreenLens" />
          </div>

          <h2>
            Green<span>Lens</span>
          </h2>

          <p>SUSTAINABLE AI, INTELLIGENTLY ROUTED</p>

          <div className="gl-loading-indicator">
            <span />
          </div>

          <small>Preparing your workspace...</small>
        </div>
      </main>
    )
  }

  if (!user) {
    return (
      <>
        <LoginPage onSignedIn={onSignedIn} />
        {authError && (
          <p className="auth-global-error">{authError}</p>
        )}
      </>
    )
  }

  return (
    <div className="frame">
      <div className="shell">
        {menu && (
          <div
            className="side-scrim"
            onClick={() => setMenu(false)}
          />
        )}

        <Sidebar
          chats={store.chats}
          activeId={store.activeId}
          page={page}
          open={menu}
          user={user}
          onLogout={signOut}
          onNew={() => {
            store.setActiveId(null)
            go('chat')
          }}
          onSelect={(id) => {
            void store.load(id).catch((error) =>
              setAuthError(
                error instanceof Error
                  ? error.message
                  : 'Could not load conversation.'
              )
            )
            go('chat')
          }}
          onDelete={(id) => {
            void store.remove(id).catch((error) =>
              setAuthError(
                error instanceof Error
                  ? error.message
                  : 'Could not delete conversation.'
              )
            )
          }}
          onPage={go}
        />

        <div className="main">
          <header className="topbar">
            <button
              className="menu-btn"
              onClick={() => setMenu(true)}
              aria-label="Open menu"
            >
              ☰
            </button>
            <span className="crumb">{title}</span>
          </header>

          {authError && (
            <div className="app-alert" role="alert">
              {authError}
              <button onClick={() => setAuthError('')}>
                Dismiss
              </button>
            </div>
          )}

          {page === 'chat' && (
            <ChatPage
              chat={store.active}
              busy={busy}
              onSend={send}
              catalog={catalog}
            />
          )}

          {page === 'insights' && (
            <InsightsPage catalog={catalog} />
          )}

          {page === 'how' && <HowPage />}

          <AppCredit />
        </div>
      </div>
    </div>
  )
}
