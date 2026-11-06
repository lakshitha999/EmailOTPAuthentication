/**
 * OTPPage.jsx
 * Step 2 – 6-box OTP entry with:
 *   • 5-minute countdown  (auto-disables form when expired)
 *   • Resend OTP with 30-second cooldown
 *   • Remaining attempts indicator
 *   • Navigation to /success on verified OTP
 */
import React, { useState, useCallback } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import OTPInput from '../components/OTPInput.jsx'
import CountdownTimer from '../components/CountdownTimer.jsx'
import AlertMessage from '../components/AlertMessage.jsx'
import { verifyOTP, resendOTP } from '../services/api.js'
import '../styles/auth.css'
import '../styles/otp.css'

const MAX_ATTEMPTS    = 5
const RESEND_COOLDOWN = 30   // seconds
const OTP_TTL         = 300  // 5 minutes

function OTPPage() {
  const navigate  = useNavigate()
  const { state } = useLocation()
  const email     = state?.email

  // Guard: must arrive via /login flow
  if (!email) {
    navigate('/', { replace: true })
    return null
  }

  const [otp,          setOtp]          = useState(Array(6).fill(''))
  const [loading,      setLoading]      = useState(false)
  const [hasError,     setHasError]     = useState(false)
  const [alert,        setAlert]        = useState({ type: '', message: '' })
  const [attemptsLeft, setAttemptsLeft] = useState(MAX_ATTEMPTS)
  const [otpExpired,   setOtpExpired]   = useState(false)

  // Resend state
  const [resendCooldown, setResendCooldown] = useState(0)   // seconds remaining
  const [timerResetKey,  setTimerResetKey]  = useState(0)   // changes → CountdownTimer restarts

  // Derived
  const otpStr      = otp.join('')
  const otpComplete = otpStr.length === 6
  const resendReady = resendCooldown === 0 && !otpExpired

  const showAlert  = (type, message) => setAlert({ type, message })
  const clearAlert = ()               => setAlert({ type: '', message: '' })

  /* ── Countdown expired ── */
  const handleOtpExpired = useCallback(() => {
    setOtpExpired(true)
    showAlert('error', 'Your OTP has expired. Please request a new one.')
  }, [])

  /* ── Verify ── */
  const handleVerify = async (e) => {
    e.preventDefault()
    if (!otpComplete) {
      showAlert('error', 'Please enter all 6 digits.')
      return
    }
    if (otpExpired) {
      showAlert('error', 'OTP expired. Request a new one.')
      return
    }

    clearAlert()
    setLoading(true)
    setHasError(false)

    try {
      const { data } = await verifyOTP(email, otpStr)
      showAlert('success', data.message || 'OTP verified! Logging you in…')
      setTimeout(() => navigate('/success', { state: { email } }), 800)
    } catch (err) {
      setHasError(true)
      setOtp(Array(6).fill(''))

      const remaining = err.response?.data?.attempts_left ?? (attemptsLeft - 1)
      setAttemptsLeft(remaining)

      const msg =
        err.response?.data?.error ||
        err.response?.data?.message ||
        'Invalid OTP. Please try again.'

      if (remaining <= 0) {
        showAlert('error', 'Too many failed attempts. Please request a new OTP.')
        setOtpExpired(true)
      } else {
        showAlert('error', `${msg} ${remaining} attempt${remaining !== 1 ? 's' : ''} left.`)
      }

      // Clear shake after animation
      setTimeout(() => setHasError(false), 500)
    } finally {
      setLoading(false)
    }
  }

  /* ── Resend ── */
  const handleResend = async () => {
    if (!resendReady) return
    clearAlert()
    setOtp(Array(6).fill(''))
    setAttemptsLeft(MAX_ATTEMPTS)
    setOtpExpired(false)

    try {
      const { data } = await resendOTP(email)
      showAlert('success', data.message || 'New OTP sent to your email.')

      // Restart the 5-min countdown
      setTimerResetKey((k) => k + 1)

      // Start resend cooldown
      setResendCooldown(RESEND_COOLDOWN)
      const tick = setInterval(() => {
        setResendCooldown((c) => {
          if (c <= 1) { clearInterval(tick); return 0 }
          return c - 1
        })
      }, 1000)
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.message ||
        'Could not resend OTP. Please try again.'
      showAlert('error', msg)
    }
  }

  const attemptsLow = attemptsLeft <= 2

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Brand icon */}
        <div className="auth-icon" aria-hidden="true">🔐</div>

        <h1 className="auth-title">Verify Your Email</h1>
        <p className="auth-subtitle">
          We sent a 6-digit code to&nbsp;<span>{email}</span>
        </p>

        {/* Alert banner */}
        <AlertMessage type={alert.type} message={alert.message} />

        <form className="auth-form" onSubmit={handleVerify} noValidate>
          {/* OTP boxes */}
          <div className="form-group">
            <label className="form-label" style={{ textAlign: 'center' }}>
              Enter 6-Digit OTP
            </label>
            <OTPInput
              otp={otp}
              setOtp={setOtp}
              disabled={loading || otpExpired || attemptsLeft <= 0}
              hasError={hasError}
            />
          </div>

          {/* Countdown + Resend row */}
          <div className="otp-resend-row">
            <div className="otp-countdown">
              ⏱ Expires in&nbsp;
              <CountdownTimer
                initialSeconds={OTP_TTL}
                onExpire={handleOtpExpired}
                resetKey={timerResetKey}
              />
            </div>

            {resendCooldown > 0 ? (
              <span style={{ color: 'var(--color-text-muted)' }}>
                Resend in {resendCooldown}s
              </span>
            ) : (
              <button
                type="button"
                className="btn-ghost"
                onClick={handleResend}
                disabled={!resendReady}
              >
                Resend OTP
              </button>
            )}
          </div>

          {/* Attempts indicator */}
          {attemptsLeft < MAX_ATTEMPTS && attemptsLeft > 0 && (
            <p className={`otp-attempts${attemptsLow ? ' low' : ''}`}>
              {attemptsLow ? '⚠️ ' : ''}
              {attemptsLeft} verification attempt{attemptsLeft !== 1 ? 's' : ''} remaining
            </p>
          )}

          {/* Submit */}
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !otpComplete || otpExpired || attemptsLeft <= 0}
          >
            {loading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                Verifying…
              </>
            ) : (
              <>🔓 Verify OTP</>
            )}
          </button>
        </form>

        {/* Back link */}
        <p className="auth-footer-note">
          Wrong email?&nbsp;
          <Link to="/" className="btn-ghost" style={{ display: 'inline' }}>
            Go back
          </Link>
        </p>
      </div>
    </div>
  )
}

export default OTPPage
