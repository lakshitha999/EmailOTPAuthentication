import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage.jsx'
import OTPPage from './pages/OTPPage.jsx'
import SuccessPage from './pages/SuccessPage.jsx'

function App() {
  return (
    <Routes>
      <Route path="/"         element={<LoginPage />} />
      <Route path="/verify"   element={<OTPPage />} />
      <Route path="/success"  element={<SuccessPage />} />
      {/* Fallback */}
      <Route path="*"         element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
