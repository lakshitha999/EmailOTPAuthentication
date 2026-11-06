/**
 * LoginPage.jsx
 * Step 1 – email collection & "Send OTP" action.
 * On success navigates to /verify, passing email via location state.
 */
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AlertMessage from '../components/AlertMessage.jsx'
import { sendOTP } from '../services/api.js'
import '../styles/auth.css'

// Simple RFC-5322-ish email regex
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function LoginPage() {
  const navigate = useNavigate()

  const [email,   setEmail]   = useState('')
  const [loading, setLoading] = useState(false)
  const [alert,   setAlert]   = useState({ type: '', message: '' })
  const [touched, setTouched] = useState(false)

  const emailError = touched && !EMAIL_RE.test(email)

  const showAlert = (type, message) => setAlert({ type, message })
  const clearAlert = () => setAlert({ type: '', message: '' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setTouched(true)
    clearAlert()

    if (!EMAIL_RE.test(email)) {
      showAlert('error', 'Please enter a valid email address.')
      return
    }

    setLoading(true)
    try {
      const { data } = await sendOTP(email)
      showAlert('success', data.message || 'OTP sent! Check your inbox.')

      // Brief pause so the user can read the success message
      setTimeout(() => navigate('/verify', { state: { email } }), 1200)
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.message ||
        'Failed to send OTP. Please try again.'
      showAlert('error', msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Brand icon */}
        <div className="auth-icon" aria-hidden="true">📧</div>

        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">
          Enter your email to receive a&nbsp;
          <span>one-time passcode</span>.
        </p>

        {/* Alert banner */}
        <AlertMessage type={alert.type} message={alert.message} />

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearAlert() }}
              onBlur={() => setTouched(true)}
              className={`form-input${emailError ? ' input-error' : ''}`}
              placeholder="you@example.com"
              autoComplete="email"
              autoFocus
              disabled={loading}
              aria-describedby={emailError ? 'email-error' : undefined}
              aria-invalid={emailError}
            />
            {emailError && (
              <span id="email-error" style={{ color: 'var(--color-error)', fontSize: '0.82rem' }}>
                Please enter a valid email address.
              </span>
            )}
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                Sending OTP…
              </>
            ) : (
              <>✉️ Send OTP</>
            )}
          </button>
        </form>

        <p className="auth-footer-note">
          🔒 Your email is used only for authentication. We never share it.
        </p>
      </div>
    </div>
  )
}

export default LoginPage
