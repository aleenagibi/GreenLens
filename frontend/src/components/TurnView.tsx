import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import type { Turn } from '../types'
import { fmtCarbon, fmtLatency, modelName } from '../utils'
import Loader from './Loader'

function TurnView({ turn, onDetails }: { turn: Turn; onDetails: () => void }) {
  const a = turn.answer
  return (
    <div className="turn">
      <div className="msg-user"><p>{turn.prompt}</p></div>

      {turn.pending && <Loader />}
      {turn.error && (
        <div className="msg-ai msg-error" role="alert">
          <strong>The request failed.</strong>
          <p>{turn.error}</p>
        </div>
      )}

      {a && (
        <div className="msg-ai">
          <div className="ai-head">
            <span className="ai-dot">❊</span>
            <div className="ai-who">
              <strong>{modelName(a.model)}</strong>
              {a.idealModel !== a.selectedModel && <small>Ideal route: {a.idealModel}</small>}
            </div>
            {a.selectedIsFree && <span className="pill lime">Free</span>}
          </div>

          <div className="md">
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
              {a.content}
            </ReactMarkdown>
          </div>

          <div className="ai-meta">
            <span className="chip">{fmtCarbon(a.carbonG)} CO₂e</span>
            <span className="chip">{fmtLatency(a.latencyMs)}</span>
            <span className="chip">Fit {a.fitScore.toFixed(1)}/10</span>
            {a.context && (
              <span
                className="chip"
                title={`Estimated input: ${a.context.input_tokens_estimated.toLocaleString()} tokens. ` +
                  `${a.context.history_messages_included} history messages included.`}
              >
                Context {(a.context.input_tokens_actual ?? a.context.input_tokens_estimated).toLocaleString()} / {a.context.context_window_tokens.toLocaleString()}
                {a.context.context_trimmed ? ' · trimmed' : ''}
              </span>
            )}
            <button className="details-btn" onClick={onDetails}>Routing details ›</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default memo(TurnView)