import { useEffect, useRef, useState } from 'react'
import {
  Target,
  Leaf,
  ChartNoAxesCombined,
  GitCompareArrows,
} from 'lucide-react'

const STEPS = [
  { n: '01', title: 'Understand', text: 'Understand the task, its complexity and capability requirements.' },
  { n: '02', title: 'Evaluate', text: 'Compare candidate models using benchmark and performance signals.' },
  { n: '03', title: 'Estimate', text: 'Estimate energy consumption and carbon impact using available model data.' },
  { n: '04', title: 'Route', text: 'Recommend the best-fit model and run a suitable free alternative when available.' },
]

const FEATURES = [
  {
    icon: Target,
    title: 'Intelligent model selection',
    text: 'Evaluate models against the requirements of each task instead of a one-size-fits-all approach.',
  },
  {
    icon: Leaf,
    title: 'Environmental awareness',
    text: 'Bring estimated energy and carbon impact into the model selection process.',
  },
  {
    icon: ChartNoAxesCombined,
    title: 'Model comparison',
    text: 'See how candidate models compare across suitability and available performance signals.',
  },
  {
    icon: GitCompareArrows,
    title: 'Practical alternatives',
    text: 'Identify suitable free models when the ideal recommendation is not available as a free option.',
  },
]

const COMPARE = [
  ['One default model for every prompt', 'Model chosen per task, based on requirements'],
  ['Environmental cost is invisible', 'Energy and carbon estimates shown next to the answer'],
  ['Unclear which model actually answered', 'Ideal model and selected model shown separately'],
  ['No fallback when the best model is paid', 'A suitable free alternative is run when available'],
]

const TRUTHS = [
  { title: 'Ideal model vs selected model', text: 'The ideal model is the best-fit recommendation. The selected model is the one that actually generated the response.' },
  { title: 'Estimates, not measurements', text: 'Carbon and energy figures are estimates based on available model metadata, not directly measured emissions.' },
  { title: 'Independent routing', text: 'Each message is evaluated independently. Previous messages are not included in model routing.' },
]

const FAQ = [
  { q: 'Does GreenLens always use the ideal model?', a: 'No. The ideal model is a recommendation. When it is not available as a free option, a suitable free alternative is run, and the result shows which one actually responded.' },
  { q: 'Are the carbon figures exact?', a: 'No. They are estimates derived from available model metadata. They are useful for comparing options, not as audited emissions.' },
  { q: 'Does routing use my earlier messages?', a: 'No. Every message is routed on its own, so earlier messages do not influence which model is recommended.' },
]

const DEMO = [
  { label: 'Task', value: 'Summarise a short document' },
  { label: 'Needs', value: 'Low complexity, basic reasoning' },
  { label: 'Impact', value: 'Smaller model, lower estimated energy' },
  { label: 'Result', value: 'Ideal and selected model shown' },
]

function useReveal(root: React.RefObject<HTMLElement | null>) {
  useEffect(() => {
    const host = root.current
    if (!host) return
    const items = host.querySelectorAll<HTMLElement>('[data-ghx-reveal]')
    if (!('IntersectionObserver' in window)) {
      items.forEach((el) => el.classList.add('ghx-in'))
      return
    }
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('ghx-in')
            io.unobserve(e.target)
          }
        }),
      { root: host, threshold: 0.12 },
    )
    items.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [root])
}

export default function HowPage() {
  const ref = useRef<HTMLElement | null>(null)
  const [active, setActive] = useState(0)
  useReveal(ref)

  useEffect(() => {
    const t = setInterval(() => setActive((a) => (a + 1) % STEPS.length), 2200)
    return () => clearInterval(t)
  }, [])

  return (
    <section className="page-scroll ghx-page" ref={ref}>
      {/* HERO */}
      <header className="ghx-hero">
        <div className="ghx-hero-copy">
          <span className="ghx-eyebrow"><i className="ghx-pulse" /> INTRODUCING GREENLENS</span>
          <h1>Smarter AI.<br /><em>Lower impact.</em></h1>
          <p>
            Every AI task has different requirements. GreenLens identifies suitable models
            while bringing environmental impact into the decision.
          </p>
          <div className="ghx-hero-actions">
            <a href="#ghx-process" className="ghx-btn">Explore how it works <span>↗</span></a>
            <a href="#ghx-faq" className="ghx-btn-ghost">Read the FAQ</a>
          </div>
          <div className="ghx-tags">
            <span>Task-aware</span><span>Estimated impact</span><span>Free alternatives</span>
          </div>
        </div>  
        <div className="gl-auth-brand"><img src="/logo.png" alt="GreenLens" /></div>
      </header>

      {/* WHY */}
      <section className="ghx-why" data-ghx-reveal>
        <div>
          <span className="ghx-label">WHY GREENLENS</span>
          <h2>Choosing an AI model should mean more than choosing an answer.</h2>
        </div>
        <p>
          Different models have different capabilities, performance characteristics and
          resource requirements. GreenLens brings these together so model selection is
          informed and environmentally aware.
        </p>
      </section>

      {/* FEATURES */}
      <section className="ghx-features">
        {FEATURES.map((f, i) => (
          <article className="ghx-feature" key={f.title} data-ghx-reveal style={{ ['--i' as string]: i }}>
            <div className="ghx-feature-top">
              <span className="ghx-feature-icon">
  <f.icon size={22} strokeWidth={1.7} />
</span>
              <span className="ghx-feature-num">0{i + 1}</span>
            </div>
            <h3>{f.title}</h3>
            <p>{f.text}</p>
          </article>
        ))}
      </section>

      {/* PROCESS + DEMO */}
      <section className="ghx-process" id="ghx-process" data-ghx-reveal>
        <div className="ghx-process-head">
          <div>
            <span className="ghx-label">THE PROCESS</span>
            <h2>From prompt to model selection.</h2>
          </div>
          <p>Four stages. One task-aware, sustainability-conscious routing workflow.</p>
        </div>

        <ol className="ghx-steps">
          {STEPS.map((s, i) => (
            <li
              key={s.n}
              className={`ghx-step${i === active ? ' is-active' : ''}${i < active ? ' is-done' : ''}`}
              onMouseEnter={() => setActive(i)}
            >
              <span className="ghx-step-n">{s.n}</span>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </li>
          ))}
        </ol>

        <div className="ghx-demo">
          <div className="ghx-demo-head">
            <span>ILLUSTRATIVE EXAMPLE</span>
            <span>Step {STEPS[active].n} · {STEPS[active].title}</span>
          </div>
          <div className="ghx-demo-grid">
            {DEMO.map((d, i) => (
              <div key={d.label} className={`ghx-demo-cell${i <= active ? ' is-on' : ''}`}>
                <small>{d.label}</small>
                <strong>{d.value}</strong>
              </div>
            ))}
          </div>
          <div className="ghx-demo-bar"><i style={{ width: `${((active + 1) / STEPS.length) * 100}%` }} /></div>
        </div>
      </section>

      {/* COMPARE */}
      <section className="ghx-compare" data-ghx-reveal>
        <div className="ghx-compare-head">
          <span className="ghx-label">THE DIFFERENCE</span>
          <h2>A fixed default vs task-aware routing.</h2>
        </div>
        <div className="ghx-compare-table" role="table">
          <div className="ghx-compare-row ghx-compare-title" role="row">
            <span role="columnheader">Typical approach</span>
            <span role="columnheader">With GreenLens</span>
          </div>
          {COMPARE.map(([a, b]) => (
            <div className="ghx-compare-row" role="row" key={a}>
              <span role="cell" className="ghx-before">{a}</span>
              <span role="cell" className="ghx-after"><i>✓</i>{b}</span>
            </div>
          ))}
        </div>
      </section>

      {/* TRANSPARENCY */}
      <section className="ghx-truth" data-ghx-reveal>
        <div className="ghx-truth-head">
          <span className="ghx-label">TRANSPARENCY FIRST</span>
          <h2>Understand what the numbers actually mean.</h2>
          <p>
            GreenLens makes environmental estimates visible while separating
            recommendations from actual inference results.
          </p>
        </div>
        <div className="ghx-truth-list">
          {TRUTHS.map((t, i) => (
            <div className="ghx-truth-item" key={t.title}>
              <span>0{i + 1}</span>
              <div>
                <h3>{t.title}</h3>
                <p>{t.text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="ghx-faq" id="ghx-faq" data-ghx-reveal>
        <span className="ghx-label">FAQ</span>
        <h2>Common questions.</h2>
        <div className="ghx-faq-list">
          {FAQ.map((f) => (
            <details key={f.q} className="ghx-faq-item">
              <summary>{f.q}<i>+</i></summary>
              <p>{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="ghx-cta" data-ghx-reveal>
        <span className="ghx-label">THE FUTURE OF CONSCIOUS AI</span>
        <h2>Make your next AI decision a smarter one.</h2>
        <p>Explore model recommendations, compare alternatives and understand their estimated environmental impact.</p>
      </section>
    </section>
  )
}