const STEPS: [string, string][] = [
  ['Understand', 'Classify the task and estimate its complexity.'],
  ['Score', 'Rate each candidate model with benchmark signals.'],
  ['Estimate', 'Apply energy and carbon estimates, with a fallback when data is missing.'],
  ['Route', 'Name an ideal model and run a free alternative when one is suitable.'],
]

export default function HowPage() {
  return (
    <section className="page-scroll">
      <div className="tiles four">
        {STEPS.map(([title, text], i) => (
          <div className="tile step" key={title} style={{ ['--d' as string]: `${i * 70}ms` }}>
            <span className="tile-label">Step {i + 1}</span>
            <span className="tile-dots" aria-hidden="true">•••</span>
            <strong>{title}</strong>
            <div className="neon">{text}</div>
          </div>
        ))}
      </div>
      <div className="card">
        <h3>Reading the numbers</h3>
        <ul className="plain">
          <li>The ideal model is the best fit for the task. The selected model is the one that actually answered.</li>
          <li>Carbon and energy are estimates from model metadata. They are not measured emissions.</li>
          <li>Each message is routed on its own. The model does not see earlier messages in the chat.</li>
        </ul>
      </div>
    </section>
  )
}