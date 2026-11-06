/**
 * SuccessPage.jsx
 * Shown after successful OTP verification.
 * Receives { email } via location state.
 */
import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import '../styles/success.css'

function SuccessPage() {
  const navigate  = useNavigate()
  const { state } = useLocation()
  const email     = state?.email ?? 'your email'

  return (
    <div className="success-page">
      <div className="success-card">
        {/* Animated checkmark */}
        <div className="success-checkmark" aria-hidden="true">✅</div>

        <h1 className="success-title">You're Verified!</h1>
        <p className="success-message">
          Successfully authenticated with
        </p>
        <span className="success-email">{email}</span>

        <div className="success-divider" />

        <p className="success-message" style={{ fontSize: '0.9rem', marginBottom: '24px' }}>
          🎉 Your identity has been confirmed. You can now access the application securely.
        </p>

        <button
          className="btn-success"
          onClick={() => navigate('/')}
          aria-label="Return to login"
        >
          🏠 Back to Home
        </button>
      </div>
    </div>
  )
}

export default SuccessPage
