import { useState, useRef, useEffect } from 'react'
import './App.css'

const CHAT_ICON = (
  <svg viewBox="0 0 24 24">
    <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12Z" />
  </svg>
)

const USER_ICON = (
  <svg viewBox="0 0 24 24">
    <circle cx="12" cy="8" r="4" />
    <path d="M4 21a8 8 0 0 1 16 0" />
  </svg>
)

const INFO_ICON = (
  <svg viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
)

const SUGGESTIONS = [
  'What orders do I have?',
  'Check status of order 3',
  'I need to report an issue',
]

// Preset mock conversation histories for demonstrative review
const DEFAULT_PRESET_CHATS = [
  {
    id: 'chat-refund-2',
    title: 'Refund for order 2',
    messages: [
      { role: 'bot', text: "Hi! I'm your customer support assistant. How can I help you today?" },
      { role: 'me', text: 'I would like to request a refund for order 2.' },
      { role: 'bot', text: 'I can certainly help you with that. Could you please share your registered email address so I can pull up your account?' },
      { role: 'me', text: 'My email is asha@example.com' },
      { role: 'bot', text: "Thank you, Asha Rao. I've found order #2 (Phone Case - ₹599.00). It is currently marked as shipped. I have logged a refund request ticket for you (#104). Our billing team will process the reimbursement within 3-5 business days." }
    ]
  },
  {
    id: 'chat-addr-change',
    title: 'Change delivery address',
    messages: [
      { role: 'bot', text: "Hi! I'm your customer support assistant. How can I help you today?" },
      { role: 'me', text: 'Can I change my delivery address for an upcoming delivery?' },
      { role: 'bot', text: 'Yes, if the order is still processing, we can update the shipping address. Please provide your email address and the order ID.' },
      { role: 'me', text: 'Email is carlos@example.com and order is #3' },
      { role: 'bot', text: 'Order #3 (Mechanical keyboard) is currently processing. Please share your new shipping address, and I will submit an update ticket to the warehouse immediately.' }
    ]
  },
  {
    id: 'chat-invoice-1',
    title: 'Invoice not received',
    messages: [
      { role: 'bot', text: "Hi! I'm your customer support assistant. How can I help you today?" },
      { role: 'me', text: 'I never received an invoice copy for order 1.' },
      { role: 'bot', text: 'Apologies for the inconvenience! May I have your registered email to locate the tax invoice?' },
      { role: 'me', text: 'asha@example.com' },
      { role: 'bot', text: 'Found it! Order #1 (Wireless Headphones - ₹2,499.00) was delivered on Jan 10. A duplicate copy of your PDF tax invoice has been re-sent to asha@example.com.' }
    ]
  }
]

export default function App() {
  const [currentTab, setCurrentTab] = useState('chat') // 'chat' | 'about'
  const [savedChats, setSavedChats] = useState(() => {
    try {
      const stored = localStorage.getItem('recent_chats_v1')
      return stored ? JSON.parse(stored) : DEFAULT_PRESET_CHATS
    } catch {
      return DEFAULT_PRESET_CHATS
    }
  })

  const [activeChatId, setActiveChatId] = useState(() => 'live-' + Math.random().toString(36).slice(2))
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: "Hi! I'm your customer support assistant. How can I help you today?",
    },
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // User custom Groq API key support
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('groq_api_key') || '')
  const [keyInput, setKeyInput] = useState(() => localStorage.getItem('groq_api_key') || '')
  const [showKey, setShowKey] = useState(false)
  const [keySavedNotice, setKeySavedNotice] = useState(false)

  const logRef = useRef(null)

  // Persist recent chats to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('recent_chats_v1', JSON.stringify(savedChats))
    } catch {}
  }, [savedChats])

  // Sync theme
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
  }, [theme])

  // Scroll to bottom on new message
  useEffect(() => {
    if (currentTab === 'chat' && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [messages, loading, currentTab])

  function toggleTheme() {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))
  }

  function startNewChat() {
    const newId = 'live-' + Math.random().toString(36).slice(2)
    setActiveChatId(newId)
    setMessages([
      {
        role: 'bot',
        text: "Hi! I'm your customer support assistant. How can I help you today?",
      },
    ])
    setCurrentTab('chat')
    setMobileMenuOpen(false)
  }

  function loadChatHistory(chatItem) {
    setActiveChatId(chatItem.id)
    setMessages(chatItem.messages || [])
    setCurrentTab('chat')
    setMobileMenuOpen(false)
  }

  function saveApiKey(e) {
    e?.preventDefault()
    const trimmed = keyInput.trim()
    setApiKey(trimmed)
    if (trimmed) {
      localStorage.setItem('groq_api_key', trimmed)
    } else {
      localStorage.removeItem('groq_api_key')
    }
    setKeySavedNotice(true)
    setTimeout(() => setKeySavedNotice(false), 2200)
  }

  function clearApiKey() {
    setApiKey('')
    setKeyInput('')
    localStorage.removeItem('groq_api_key')
    setKeySavedNotice(true)
    setTimeout(() => setKeySavedNotice(false), 2200)
  }

  async function handleSend(textToSend) {
    const text = (textToSend !== undefined ? textToSend : input).trim()
    if (!text || loading) return

    setCurrentTab('chat')
    setMobileMenuOpen(false)
    const newMessages = [...messages, { role: 'me', text }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeChatId,
          message: text,
          api_key: apiKey || undefined,
        }),
      })

      let data
      try {
        data = await res.json()
      } catch {
        data = { error: `Server error (${res.status})` }
      }

      let updatedMessages
      if (data.error) {
        updatedMessages = [...newMessages, { role: 'bot', text: data.error, isError: true }]
      } else {
        updatedMessages = [...newMessages, { role: 'bot', text: data.reply || 'No response.' }]
      }
      setMessages(updatedMessages)

      // Update or create entry in savedChats for quick access in "Recent chats"
      setSavedChats(prev => {
        const titleSnippet = text.length > 28 ? text.slice(0, 28) + '…' : text
        const existingIndex = prev.findIndex(c => c.id === activeChatId)
        if (existingIndex >= 0) {
          const updated = [...prev]
          updated[existingIndex] = {
            ...updated[existingIndex],
            messages: updatedMessages,
          }
          return updated
        } else {
          return [
            {
              id: activeChatId,
              title: titleSnippet,
              messages: updatedMessages,
            },
            ...prev,
          ]
        }
      })
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'bot', text: 'Network error. Please make sure the backend server is running.', isError: true },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* ── Sidebar ────────────────────────────────────────── */}
      <aside className={`side ${mobileMenuOpen ? 'open' : ''}`} aria-label="Sidebar">
        <div className="brand">
          <div className="logo">{CHAT_ICON}</div>
          <div>
            <b>Support Desk</b>
            <small>Powered by Groq AI</small>
          </div>
        </div>

        <button className="new" onClick={startNewChat}>
          <svg viewBox="0 0 24 24">
            <path d="M12 5v14M5 12h14" />
          </svg>
          New chat
        </button>

        {/* ── Dashboard Navigation ─────────────────────────── */}
        <div className="nav-section">
          <h3>Dashboard</h3>
          <nav className="nav" aria-label="Sections">
            <button
              aria-current={currentTab === 'chat' && !savedChats.some(c => c.id === activeChatId) ? 'page' : undefined}
              onClick={() => {
                setCurrentTab('chat')
                setMobileMenuOpen(false)
              }}
            >
              {CHAT_ICON}
              Chat
            </button>
            <button
              aria-current={currentTab === 'about' ? 'page' : undefined}
              onClick={() => {
                setCurrentTab('about')
                setMobileMenuOpen(false)
              }}
            >
              {INFO_ICON}
              About
            </button>
            <button onClick={() => handleSend('What orders do I have?')}>
              <svg viewBox="0 0 24 24">
                <path d="M21 8 12 3 3 8l9 5 9-5ZM3 8v8l9 5 9-5V8M12 13v8" />
              </svg>
              My orders
            </button>
            <button onClick={() => handleSend('I need to report an issue')}>
              <svg viewBox="0 0 24 24">
                <path d="M12 9v4m0 4h.01M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
              </svg>
              Report an issue
            </button>
          </nav>
        </div>

        {/* ── Recent Chats History ──────────────────────────── */}
        <div className="hist">
          <h3>Recent chats</h3>
          {savedChats.map(chatItem => (
            <button
              key={chatItem.id}
              onClick={() => loadChatHistory(chatItem)}
              className={currentTab === 'chat' && activeChatId === chatItem.id ? 'active-history' : ''}
              title={chatItem.title}
            >
              <svg viewBox="0 0 24 24">
                <path d="M4 6h16M4 12h16M4 18h10" />
              </svg>
              <span>{chatItem.title}</span>
            </button>
          ))}
        </div>

        {/* ── User Groq API Key Box ───────────────────────────── */}
        <div className={`key ${apiKey ? 'ok' : ''}`}>
          <label>
            Groq API Key
            <em>
              <span className="dot" />
              {apiKey ? 'Configured' : 'Using Default'}
            </em>
          </label>

          <form onSubmit={saveApiKey}>
            <div className="field">
              <input
                type={showKey ? 'text' : 'password'}
                placeholder="gsk_..."
                value={keyInput}
                onChange={e => setKeyInput(e.target.value)}
                autoComplete="off"
              />
              <button
                type="button"
                className="ico"
                title={showKey ? 'Hide key' : 'Show key'}
                onClick={() => setShowKey(!showKey)}
              >
                {showKey ? (
                  <svg viewBox="0 0 24 24">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                )}
              </button>
            </div>

            <div className="row" style={{ marginTop: '8px' }}>
              <button type="submit" className="btn p">
                Save
              </button>
              {apiKey && (
                <button type="button" className="btn" onClick={clearApiKey}>
                  Clear
                </button>
              )}
            </div>
          </form>

          <p>
            {keySavedNotice
              ? '✓ Preference updated!'
              : 'Add your custom key or leave blank to use the backend server key.'}
          </p>
        </div>
      </aside>

      {/* Scrim overlay for mobile menu */}
      {mobileMenuOpen && <div className="scrim" onClick={() => setMobileMenuOpen(false)} />}

      {/* ── Main Window Area ───────────────────────────────── */}
      <main className="main">
        <header className="head">
          <button
            className="menu"
            aria-label="Open menu"
            onClick={() => setMobileMenuOpen(true)}
          >
            <svg viewBox="0 0 24 24">
              <path d="M4 7h16M4 12h16M4 17h10" />
            </svg>
          </button>

          <div>
            <h1>{currentTab === 'about' ? 'About Project' : 'Customer Support Agent'}</h1>
            <small>Powered by Groq AI</small>
          </div>

          <div className="pill">
            <i />
            <span>Online</span>
          </div>

          <button
            className="theme"
            aria-label="Switch light or dark theme"
            onClick={toggleTheme}
          >
            {theme === 'dark' ? (
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="5" />
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24">
                <path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10Z" />
              </svg>
            )}
          </button>
        </header>

        {/* ── TAB 1: Chat Stream ── */}
        {currentTab === 'chat' && (
          <>
            <div className="log" ref={logRef} aria-live="polite">
              {messages.map((m, i) => (
                <div key={i} className={`msg ${m.role === 'me' ? 'me' : ''}`}>
                  <div className={`av ${m.role === 'me' ? 'u' : ''}`}>
                    {m.role === 'me' ? USER_ICON : CHAT_ICON}
                  </div>
                  <div className={`bub ${m.isError ? 'err' : ''}`}>{m.text}</div>
                </div>
              ))}

              {loading && (
                <div className="msg">
                  <div className="av">{CHAT_ICON}</div>
                  <div className="bub">
                    <div className="typing">
                      <i />
                      <i />
                      <i />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="dock">
              <div className="chips">
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    className="chip"
                    onClick={() => handleSend(s)}
                    disabled={loading}
                  >
                    {s}
                  </button>
                ))}
              </div>

              <form
                className="bar"
                onSubmit={e => {
                  e.preventDefault()
                  handleSend()
                }}
              >
                <div className="field">
                  <input
                    id="msg"
                    placeholder="Ask a question or type a message…"
                    autoComplete="off"
                    aria-label="Message"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    disabled={loading}
                    autoFocus
                  />
                </div>
                <button
                  className="send"
                  type="submit"
                  aria-label="Send message"
                  disabled={loading || !input.trim()}
                >
                  <svg viewBox="0 0 24 24">
                    <path d="m22 2-7 20-4-9-9-4 20-7ZM22 2 11 13" />
                  </svg>
                </button>
              </form>
            </div>
          </>
        )}

        {/* ── TAB 2: Simple & Clean Tabular About View ── */}
        {currentTab === 'about' && (
          <div className="about-view">
            <div className="about-header">
              <h2>About This Project</h2>
              <p>A fast, autonomous customer support agent that connects natural language to real database operations.</p>
            </div>

            <div className="about-table-card">
              <table className="about-table">
                <thead>
                  <tr>
                    <th style={{ width: '28%' }}>Aspect</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="aspect">🛠️ Tech Stack</td>
                    <td>
                      <b>Frontend:</b> React 18, Vite, Soft Neumorphic CSS<br />
                      <b>Backend:</b> Python (Flask), SQLite Database<br />
                      <b>AI Engine:</b> Groq Fast LPU (OpenAI GPT-OSS)
                    </td>
                  </tr>

                  <tr>
                    <td className="aspect">🤖 Why It's Agentic</td>
                    <td>
                      Unlike a standard chatbot that just guesses answers, this agent uses <b>autonomous function calling</b>. It analyzes your question, queries the SQLite database, and returns real order and ticket data.
                    </td>
                  </tr>

                  <tr>
                    <td className="aspect">⚡ Capabilities</td>
                    <td>
                      • Look up past and current orders<br />
                      • Check live shipping & delivery statuses<br />
                      • Automatically open new support tickets<br />
                      • Protect customer privacy via email verification
                    </td>
                  </tr>

                  <tr>
                    <td className="aspect">💡 How to Use</td>
                    <td>
                      1. Open <b>Chat</b> and ask a question (e.g. <i>"What orders do I have?"</i>).<br />
                      2. Provide your email when asked (try sample email: <code>asha@example.com</code>).<br />
                      3. Get instant real-time answers.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
