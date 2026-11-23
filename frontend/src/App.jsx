import { useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { apiGet } from './api.js'

function Home() {
  const [status, setStatus] = useState('checking…')

  useEffect(() => {
    apiGet('/health')
      .then((data) => setStatus(data.status))
      .catch((err) => setStatus(`unreachable (${err.message})`))
  }, [])

  return (
    <main>
      <h1>LLM Roadmap</h1>
      <p>Scaffold is running. Backend status: <strong data-testid="api-status">{status}</strong></p>
    </main>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  )
}
