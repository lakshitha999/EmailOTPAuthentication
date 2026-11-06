/**
 * AlertMessage.jsx
 * Reusable alert banner used by both LoginPage and OTPPage.
 * Props:
 *   type   – 'success' | 'error' | 'info'
 *   message – string
 */
import React from 'react'

const ICONS = {
  success: '✅',
  error:   '❌',
  info:    'ℹ️',
}

function AlertMessage({ type = 'info', message }) {
  if (!message) return null

  return (
    <div className={`alert alert-${type}`} role="alert">
      <span className="alert-icon">{ICONS[type]}</span>
      <span>{message}</span>
    </div>
  )
}

export default AlertMessage
