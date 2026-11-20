import { useMemo, useState } from 'react'
import type { Chat, Page } from '../types'
import type { AuthUser } from '../api'
import { Gauge } from "lucide-react";

type Props = {
  chats: Chat[]
  activeId: string | null
  page: Page
  open: boolean
  user: AuthUser
  onLogout: () => void
  onNew: () => void
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  onPage: (p: Page) => void
}

export default function Sidebar({ chats, activeId, page, open, user, onLogout, onNew, onSelect, onDelete, onPage }: Props) {
  const [q, setQ] = useState('')

  const list = useMemo(() => {
    const s = q.trim().toLowerCase()
    if (!s) return chats
    return chats.filter(
      (c) =>
        c.title.toLowerCase().includes(s) ||
        c.turns.some((t) => t.prompt.toLowerCase().includes(s) || t.answer?.content.toLowerCase().includes(s)),
    )
  }, [q, chats])

  return (
    <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Chats">
      <div className="brand">
        <div className="brand-mark"><img src="/logo.png" alt="GreenLens" /></div>
        <div className="brand-name">GreenLens</div>
      </div>

      <button className="new-chat" onClick={onNew}>
        <span>+</span> New chat
      </button>

      <label className="search">
        <span aria-hidden="true">⌕</span>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search chats" aria-label="Search chats" />
        {q && <button onClick={() => setQ('')} aria-label="Clear search">×</button>}
      </label>

      <div className="chat-list">
        {list.length === 0 && <p className="side-empty">{q ? 'No chats match your search.' : 'Your chats will appear here.'}</p>}
        {list.map((c) => (
          <div key={c.id} className={`chat-item ${page === 'chat' && c.id === activeId ? 'active' : ''}`}>
            <button className="chat-open" onClick={() => onSelect(c.id)} title={c.title}>{c.title}</button>
            <button className="chat-del" onClick={() => onDelete(c.id)} aria-label={`Delete chat: ${c.title}`}>×</button>
          </div>
        ))}
      </div>

      <nav className="side-nav">
        <button className={page === 'insights' ? 'active' : ''} onClick={() => onPage('insights')}><Gauge size={18} strokeWidth={2} /> Insights</button>
        <button className={page === 'how' ? 'active' : ''} onClick={() => onPage('how')}>  <span className="nav-help-icon">?</span> How it works</button>
      </nav>

      <div className="account-panel">
        {user.picture_url
          ? <img className="account-avatar" src={user.picture_url} alt="" referrerPolicy="no-referrer" />
          : <span className="account-avatar account-initial">{(user.name || user.email).slice(0, 1).toUpperCase()}</span>}
        <div className="account-identity">
          <strong>{user.name || 'GreenLens user'}</strong>
          <span>{user.email}</span>
        </div>
        <button className="account-logout" onClick={onLogout} title="Sign out" aria-label="Sign out">↗</button>
      </div>
    </aside>
  )
}