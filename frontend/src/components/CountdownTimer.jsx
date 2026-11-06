/**
 * CountdownTimer.jsx
 * Counts down from initialSeconds.
 * Props:
 *   initialSeconds – number  (default 300 = 5 min)
 *   onExpire       – callback fired when it hits 0
 *   resetKey       – any value; changing it restarts the timer
 */
import React, { useEffect, useState } from 'react'

function CountdownTimer({ initialSeconds = 300, onExpire, resetKey }) {
  const [seconds, setSeconds] = useState(initialSeconds)

  // Restart whenever resetKey changes
  useEffect(() => {
    setSeconds(initialSeconds)
  }, [resetKey, initialSeconds])

  useEffect(() => {
    if (seconds <= 0) {
      onExpire?.()
      return
    }
    const id = setInterval(() => setSeconds((s) => s - 1), 1000)
    return () => clearInterval(id)
  }, [seconds, onExpire])

  const mins = String(Math.floor(seconds / 60)).padStart(2, '0')
  const secs = String(seconds % 60).padStart(2, '0')

  return (
    <span className="otp-countdown-badge" aria-live="polite">
      {mins}:{secs}
    </span>
  )
}

export default CountdownTimer
