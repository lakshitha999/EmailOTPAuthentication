/**
 * OTPInput.jsx
 * Six individual single-character boxes.
 * Props:
 *   otp         – string[6] stored in parent state
 *   setOtp      – state setter
 *   disabled    – bool
 *   hasError    – bool  (triggers red shake animation)
 */
import React, { useRef } from 'react'

const OTP_LENGTH = 6

function OTPInput({ otp, setOtp, disabled = false, hasError = false }) {
  const inputs = useRef([])

  const focusNext = (index) => {
    if (index < OTP_LENGTH - 1) inputs.current[index + 1]?.focus()
  }

  const focusPrev = (index) => {
    if (index > 0) inputs.current[index - 1]?.focus()
  }

  const handleChange = (e, index) => {
    const val = e.target.value.replace(/\D/g, '').slice(-1) // digits only, 1 char
    const newOtp = [...otp]
    newOtp[index] = val
    setOtp(newOtp)
    if (val) focusNext(index)
  }

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace') {
      if (otp[index]) {
        // Clear current box
        const newOtp = [...otp]
        newOtp[index] = ''
        setOtp(newOtp)
      } else {
        focusPrev(index)
      }
    } else if (e.key === 'ArrowLeft') {
      focusPrev(index)
    } else if (e.key === 'ArrowRight') {
      focusNext(index)
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH)
    if (!pasted) return
    const newOtp = [...otp]
    for (let i = 0; i < pasted.length; i++) newOtp[i] = pasted[i]
    setOtp(newOtp)
    // Focus the box after the last pasted digit
    const lastIndex = Math.min(pasted.length, OTP_LENGTH - 1)
    inputs.current[lastIndex]?.focus()
  }

  return (
    <div className="otp-boxes" onPaste={handlePaste}>
      {Array.from({ length: OTP_LENGTH }).map((_, i) => (
        <input
          key={i}
          ref={(el) => (inputs.current[i] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={otp[i] || ''}
          disabled={disabled}
          aria-label={`OTP digit ${i + 1}`}
          className={[
            'otp-box',
            otp[i] ? 'filled' : '',
            hasError   ? 'otp-error' : '',
          ].filter(Boolean).join(' ')}
          onChange={(e) => handleChange(e, i)}
          onKeyDown={(e) => handleKeyDown(e, i)}
          onFocus={(e) => e.target.select()}
          autoComplete="one-time-code"
        />
      ))}
    </div>
  )
}

export default OTPInput
