/**
 * api.js
 * Thin Axios wrapper – all backend calls go through here.
 * Base URL is proxied by Vite to http://localhost:5000
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

/**
 * POST /api/send-otp
 * Body: { email }
 * Returns: { message, expires_in }
 */
export const sendOTP = (email) =>
  api.post('/send-otp', { email })

/**
 * POST /api/verify-otp
 * Body: { email, otp }
 * Returns: { message, token? }
 */
export const verifyOTP = (email, otp) =>
  api.post('/verify-otp', { email, otp })

/**
 * POST /api/resend-otp
 * Body: { email }
 * Returns: { message, expires_in }
 */
export const resendOTP = (email) =>
  api.post('/resend-otp', { email })

export default api
