import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export default function Agent() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [discoveries, setDiscoveries] = useState([])
  const bottomRef = useRef(null)
  const recognitionRef = useRef(null)

  // Auto-scroll
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  // Start session on mount
  useEffect(() => { startSession() }, [])

  const startSession = async () => {
    setMessages([])
    setDiscoveries([])
    const r = await api.post('/agent/start', { template_id: null })
    setSessionId(r.data.id)
    // Kick off with first agent message
    sendToAgent(r.data.id, 'Hello, I am ready to start.')
  }

  const sendToAgent = async (sid, text) => {
    const id = sid || sessionId
    if (!id || !text.trim()) return
    setLoading(true)

    // Add user message to UI (skip the silent kickoff)
    if (text !== 'Hello, I am ready to start.') {
      setMessages(m => [...m, { role: 'user', content: text }])
    }

    try {
      const r = await api.post(`/agent/${id}/message`, { message: text })
      const { reply, discoveries: found, actions_taken } = r.data

      setMessages(m => [...m, { role: 'assistant', content: reply, actions: actions_taken, found }])

      if (found?.length) {
        setDiscoveries(d => [...d, ...found])
      }
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }])
    }
    setLoading(false)
  }

  const send = () => {
    if (!input.trim() || loading) return
    const text = input
    setInput('')
    sendToAgent(null, text)
  }

  const handleKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }

  // Voice input
  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Voice input not supported in this browser. Use Chrome.')
      return
    }
    if (listening) {
      recognitionRef.current?.stop()
      setListening(false)
      return
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const rec = new SR()
    rec.continuous = false
    rec.interimResults = false
    rec.lang = 'en-US'
    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      setInput(transcript)
      setListening(false)
    }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    recognitionRef.current = rec
    rec.start()
    setListening(true)
  }

  return (
    <div style={{ display: 'flex', gap: 20, height: 'calc(100vh - 64px)' }}>

      {/* ── Chat Panel ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div className="page-title" style={{ margin: 0 }}>🤖 Job Finder Agent</div>
          <button className="ghost" style={{ fontSize: '0.8rem' }} onClick={startSession}>↺ New Session</button>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, paddingRight: 4 }}>
          {messages.map((m, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: m.role === 'user' ? 'row-reverse' : 'row', gap: 10, alignItems: 'flex-start' }}>
              <div style={{
                width: 34, height: 34, borderRadius: '50%', flexShrink: 0,
                background: m.role === 'user' ? 'linear-gradient(135deg,#1b5e20,#43a047)' : 'linear-gradient(135deg,#1565c0,#7c83fd)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem'
              }}>
                {m.role === 'user' ? '👤' : '🤖'}
              </div>
              <div style={{ maxWidth: '75%' }}>
                <div style={{
                  padding: '12px 16px', borderRadius: m.role === 'user' ? '14px 4px 14px 14px' : '4px 14px 14px 14px',
                  background: m.role === 'user' ? '#0d3320' : '#0d1b2a',
                  border: `1px solid ${m.role === 'user' ? 'rgba(100,255,160,0.2)' : 'rgba(100,160,255,0.2)'}`,
                  fontSize: '0.875rem', lineHeight: 1.7, color: m.role === 'user' ? '#c8e6c9' : '#cfd8dc',
                  whiteSpace: 'pre-wrap'
                }}>
                  {m.content}
                </div>
                {/* Action log */}
                {m.actions?.length > 0 && (
                  <div style={{ marginTop: 8, background: 'rgba(0,0,0,0.4)', borderLeft: '3px solid #7c83fd', borderRadius: 6, padding: '8px 12px', fontSize: '0.75rem', color: '#7c83fd', fontFamily: 'monospace' }}>
                    {m.actions.map((a, j) => (
                      <div key={j} style={{ marginBottom: 2 }}>
                        🔧 <span style={{ color: '#90a4ae' }}>{a.tool}</span>
                        {a.result?.status === 'added' && <span style={{ color: '#81c784' }}> → ✓ added</span>}
                        {a.result?.status === 'already_exists' && <span style={{ color: '#ffd54f' }}> → already exists</span>}
                        {a.result?.status === 'built' && <span style={{ color: '#81c784' }}> → ✓ resume built</span>}
                        {a.result?.status === 'updated' && <span style={{ color: '#81c784' }}> → ✓ profile updated</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,#1565c0,#7c83fd)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🤖</div>
              <div style={{ padding: '12px 16px', background: '#0d1b2a', border: '1px solid rgba(100,160,255,0.2)', borderRadius: '4px 14px 14px 14px', color: '#7c83fd', fontSize: '0.85rem' }}>
                <span style={{ animation: 'pulse 1s infinite' }}>Thinking...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
          <button onClick={toggleVoice} style={{
            padding: '8px 14px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: '1.1rem',
            background: listening ? '#c62828' : '#2a2d3a', color: listening ? '#fff' : '#90a4ae',
            transition: 'all 0.2s'
          }} title={listening ? 'Stop listening' : 'Voice input'}>
            {listening ? '⏹' : '🎙️'}
          </button>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Type your answer or click 🎙️ to speak... (Enter to send)"
            rows={2}
            style={{ flex: 1, resize: 'none', padding: '10px 14px', fontSize: '0.875rem' }}
          />
          <button className="primary" onClick={send} disabled={loading || !input.trim()}
            style={{ padding: '8px 20px', alignSelf: 'flex-end' }}>
            Send
          </button>
        </div>
      </div>

      {/* ── Discovery Feed ── */}
      <div style={{ width: 260, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ fontWeight: 600, color: '#90caf9', fontSize: '0.9rem' }}>🔍 Discovered</div>

        {discoveries.length === 0
          ? <div className="card" style={{ color: '#546e7a', fontSize: '0.82rem' }}>
              Institutions and jobs found during the interview will appear here.
            </div>
          : discoveries.map((d, i) => (
            <div key={i} className="card" style={{ padding: '12px 14px' }}>
              {d.type === 'institution' && (
                <>
                  <div style={{ fontSize: '0.75rem', color: '#80deea', marginBottom: 4 }}>🏛️ Institution Added</div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{d.name}</div>
                </>
              )}
              {d.type === 'job' && (
                <>
                  <div style={{ fontSize: '0.75rem', color: '#ffd54f', marginBottom: 4 }}>💼 Job Queued</div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{d.title}</div>
                </>
              )}
              {d.type === 'resume' && (
                <>
                  <div style={{ fontSize: '0.75rem', color: '#81c784', marginBottom: 4 }}>📄 Resume Built</div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Resume #{d.resume_id}</div>
                  <a href={`/api/resumes/${d.resume_id}/pdf`} target="_blank" rel="noreferrer"
                    style={{ color: '#7c83fd', fontSize: '0.75rem' }}>Download PDF</a>
                </>
              )}
            </div>
          ))
        }
      </div>

    </div>
  )
}
