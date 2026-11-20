import { useEffect, useRef, useState } from 'react'
import type { Chat, ModelCatalog } from '../types'
import Composer from '../components/Composer'
import Inspector from '../components/Inspector'
import TurnView from '../components/TurnView'

const SUGGESTIONS = [
  'Explain how transformers work, step by step',
  'Write a Python function to merge overlapping intervals',
  'Summarise the pros and cons of solar vs wind power',
  'Draft a polite email asking for a deadline extension',
]

type Props = { chat: Chat | null; busy: boolean; onSend: (text: string) => void; catalog: ModelCatalog | null }

export default function ChatPage({ chat, busy, onSend, catalog }: Props) {
  const [detailId, setDetailId] = useState<string | null>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => setDetailId(null), [chat?.id])
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [chat?.id, chat?.turns.length, busy])

  const detail = chat?.turns.find((t) => t.id === detailId)?.answer

  return (
    <section className="chat-page">
      <div className="thread">
        <div className="thread-inner">
          {!chat ? (
            <div className="welcome">
              <h1>Ask anything.<br />We pick the model.</h1>
              <p>GreenLens weighs capability, speed and estimated carbon, then shows which model answered and why.</p>
              <div className="suggest">
                {SUGGESTIONS.map((s) => <button key={s} onClick={() => onSend(s)} disabled={busy}>{s}</button>)}
              </div>
            </div>
          ) : (
            chat.turns.map((t) => <TurnView key={t.id} turn={t} onDetails={() => setDetailId(t.id)} />)
          )}
          <div ref={endRef} />
        </div>
      </div>

      <div className="composer-dock">
        <Composer busy={busy} onSend={onSend} />
        <p className="dock-note">Recent conversation turns are included within the selected model’s context limit. Carbon and energy figures are estimates.</p>
      </div>

      {detail && <Inspector answer={detail} catalog={catalog} onClose={() => setDetailId(null)} />}
    </section>
  )
}