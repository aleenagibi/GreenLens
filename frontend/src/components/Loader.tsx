import { useEffect, useState } from 'react'

const STAGES = [
  'Understanding your task',
  'Scoring candidate models',
  'Estimating carbon impact',
  'Selecting a route',
  'Generating the answer',
]

export default function Loader() {
  const [i, setI] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setI((v) => Math.min(v + 1, STAGES.length - 1)), 1600)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="msg-ai loader" role="status" aria-live="polite">
      <div className="loader-head">
        <span className="orb" />
        <span key={i} className="stage">{STAGES[i]}…</span>
      </div>
      <div className="stage-dots" aria-hidden="true">
        {STAGES.map((s, n) => <i key={s} className={n <= i ? 'on' : ''} />)}
      </div>
      <div className="skeleton" aria-hidden="true"><i /><i /><i /></div>
    </div>
  )
}