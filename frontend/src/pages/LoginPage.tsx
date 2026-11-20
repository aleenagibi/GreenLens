
import { useState } from 'react'
import type { FormEvent } from 'react'
import { signIn, signUp } from '../api'

type Props = {
  onSignedIn: () => void
}

export default function LoginPage({ onSignedIn }: Props) {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const switchMode = (next: 'signin' | 'signup') => {
    if (loading || mode === next) return

    setMode(next)
    setError('')
    setPassword('')
    setConfirmPassword('')
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')

    if (mode === 'signup' && password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)

    try {
      if (mode === 'signup') {
        await signUp(name.trim(), email.trim(), password)
      } else {
        await signIn(email.trim(), password)
      }

      await onSignedIn()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Authentication failed. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="gl-auth-screen">
      <section
        className={`gl-auth-layout ${mode === 'signup' ? 'signup-active' : ''}`}
      >

        {/* Sign-in form */}
        <div className="gl-auth-form-panel gl-signin-panel">

          <div className="gl-auth-brand">
            <img src="/logo.png" alt="GreenLens logo" />
              <span>
    <span className="brand-green">Green</span>
    <span className="brand-lens">Lens</span>
  </span>
            
          </div>

          <p className="gl-auth-eyebrow">
            SUSTAINABLE AI, INTELLIGENTLY ROUTED
          </p>

          <h1>Welcome back</h1>

          <p className="gl-auth-description">
            Sign in to access your AI conversations, model decisions and
            sustainability insights across devices.
          </p>

          <form className="gl-auth-form" onSubmit={submit}>
            <label>
              Email address
              <input
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                maxLength={320}
                required
                disabled={mode !== 'signin' || loading}
              />
            </label>

            <label>
              Password
              <input
                type="password"
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={1}
                maxLength={128}
                required
                disabled={mode !== 'signin' || loading}
              />
            </label>

            {mode === 'signin' && error && (
              <p className="gl-auth-error" role="alert">
                {error}
              </p>
            )}

            <button
              className="gl-auth-submit"
              type="submit"
              disabled={loading || mode !== 'signin'}
            >
              {loading ? 'Please wait…' : 'Sign in'}
            </button>
          </form>

          <p className="gl-auth-mobile-switch">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={() => switchMode('signup')}
            >
              Sign up
            </button>
          </p>

          <p className="gl-auth-footnote">
            Your password is securely hashed. Your conversations are private
            to your account.
          </p>
        </div>

        {/* Sign-up form */}
        <div className="gl-auth-form-panel gl-signup-panel">

          <div className="gl-auth-brand">
            <img src="/logo.png" alt="GreenLens logo" />
                        <span>
    <span className="brand-green">Green</span>
    <span className="brand-lens">Lens</span>
  </span>
          </div>

          <p className="gl-auth-eyebrow">
            SUSTAINABLE AI, INTELLIGENTLY ROUTED
          </p>

          <h1>Create your account</h1>

          <p className="gl-auth-description">
            Join GreenLens to save your AI conversations and sustainability
            insights across devices.
          </p>

          <form className="gl-auth-form" onSubmit={submit}>
            <label>
              Full name
              <input
                type="text"
                autoComplete="name"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={255}
                required
                disabled={mode !== 'signup' || loading}
              />
            </label>

            <label>
              Email address
              <input
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                maxLength={320}
                required
                disabled={mode !== 'signup' || loading}
              />
            </label>

            <label>
              Password
              <input
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                maxLength={128}
                required
                disabled={mode !== 'signup' || loading}
              />
            </label>

            <label>
              Confirm password
              <input
                type="password"
                autoComplete="new-password"
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                minLength={8}
                maxLength={128}
                required
                disabled={mode !== 'signup' || loading}
              />
            </label>

            {mode === 'signup' && error && (
              <p className="gl-auth-error" role="alert">
                {error}
              </p>
            )}

            <button
              className="gl-auth-submit"
              type="submit"
              disabled={loading || mode !== 'signup'}
            >
              {loading ? 'Please wait…' : 'Create account'}
            </button>
          </form>

          <p className="gl-auth-mobile-switch">
            Already have an account?{' '}
            <button
              type="button"
              onClick={() => switchMode('signin')}
            >
              Sign in
            </button>
          </p>

          <p className="gl-auth-footnote">
            Your password is securely hashed. Your conversations are private
            to your account.
          </p>
        </div>

        {/* Sliding promotional panel */}
        <div className="gl-auth-overlay">
          <div className="gl-auth-overlay-inner">

            {/* Promotional panel for sign in */}
            <div className="gl-auth-promo">
              {/* <div className="gl-promo-icon">✳</div> */}
              <div className="gl-auth-brand"><img alt="GreenLens logo" src="/logo.png"/></div>

              <h2>Make AI greener.</h2>

              <p>
                Smarter model choices. Carbon-aware routing.
                A more sustainable way to use AI.
              </p>

              <button
                type="button"
                onClick={() => switchMode('signup')}
                disabled={loading}
              >
                Sign up
              </button>
            </div>

            {/* Promotional panel for sign up */}
            <div className="gl-auth-promo">
              <div className="gl-auth-brand"><img alt="GreenLens logo" src="/logo.png"/></div>

              <h2>Welcome back.</h2>

              <p>
                Your AI workspace is ready.
                Continue making smarter, more sustainable AI decisions.
              </p>

              <button
                type="button"
                onClick={() => switchMode('signin')}
                disabled={loading}
              >
                Sign in
              </button>
            </div>

          </div>
        </div>

      </section>
      <footer className="app-credit">
  <a
    href="YOUR_GITHUB_PROFILE_URL"
    target="_blank"
    rel="noopener noreferrer"
    className="app-credit-link"
  >
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor">
      <path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.56.1.76-.24.76-.54v-2.08c-3.1.67-3.76-1.32-3.76-1.32-.51-1.3-1.24-1.65-1.24-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.72 1.16 1.72 1.16 1 1.72 2.62 1.22 3.26.93.1-.72.39-1.22.71-1.5-2.48-.28-5.09-1.24-5.09-5.52 0-1.22.44-2.22 1.16-3-.12-.28-.5-1.42.11-2.96 0 0 .95-.3 3.11 1.15a10.8 10.8 0 0 1 5.66 0c2.16-1.45 3.1-1.15 3.1-1.15.62 1.54.23 2.68.12 2.96.72.78 1.15 1.78 1.15 3 0 4.29-2.61 5.23-5.1 5.51.4.35.76 1.02.76 2.06v3.15c0 .3.2.65.77.54A11.1 11.1 0 0 0 12 .9Z" />
    </svg>
    <span>GitHub · Aleena Gibi</span>
  </a>
</footer>
    </main>
  )
}
