import { useEffect, useRef, useState } from 'react'

export default function Composer({ busy, onSend }: { busy: boolean; onSend: (text: string) => void }) {
  const [value, setValue] = useState('')
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 176)}px`
  }, [value])

  const submit = () => {
    const text = value.trim()
    if (!text || busy) return
    onSend(text)
    setValue('')
  }

  return (
    <div className="composer">
      <textarea
        ref={ref}
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
            e.preventDefault()
            submit()
          }
        }}
        placeholder="Message GreenLens…"
        aria-label="Message"
      />
      <button className="send" onClick={submit} disabled={!value.trim() || busy} aria-label="Send message">
        {busy ? <span className="spinner" /> : '↑'}
      </button>
    </div>
  )
}