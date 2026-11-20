import { useMemo } from 'react'
import type { Chat } from '../types'
import { fmtCarbon, routeCarbon } from '../utils'

export default function Footprint({ chats }: { chats: Chat[] }) {
  const { used, saved, n } = useMemo(() => {
    const today = new Date().toDateString()
    const rows = chats.flatMap((c) => c.turns).filter((t) => t.answer && new Date(t.ts).toDateString() === today)
    return {
      n: rows.length,
      used: rows.reduce((s, t) => s + t.answer!.carbonG, 0),
      saved: rows.reduce((s, t) => s + routeCarbon(t.answer!).saved, 0),
    }
  }, [chats])
  const share = used + saved > 0 ? saved / (used + saved) : 0

  return (
    <div className="meter" key={n} aria-label="Today's footprint">
      <div className="meter-gauge">
        <svg viewBox="0 0 100 56" aria-hidden="true">
          <path d="M10 50 A40 40 0 0 1 90 50" pathLength={100} className="g-track" />
          <path d="M10 50 A40 40 0 0 1 90 50" pathLength={100} className="g-val" style={{ strokeDasharray: `${share * 100} 100` }} />
        </svg>
        <strong>{Math.round(share * 100)}%</strong>
      </div>
      <div className="meter-rows">
        <span>Used today<b>{fmtCarbon(used)}</b></span>
        <span>Avoided<b className="good">{fmtCarbon(saved)}</b></span>
      </div>
      <small>Estimates, {n} {n === 1 ? 'response' : 'responses'} today</small>
    </div>
  )
}