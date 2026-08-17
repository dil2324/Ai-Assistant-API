import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

type MessageRole = 'user' | 'assistant' | 'system'

type Message = {
  role: MessageRole
  content: string
}

type AuthMode = 'login' | 'register'

const SYSTEM_MESSAGE: Message = {
  role: 'system',
  content: 'Ты говоришь с AI-ассистентом. Пиши коротко и понятно.'
}

function App() {
  const [messages, setMessages] = useState<Message[]>([SYSTEM_MESSAGE])
  const [input, setInput] = useState('')
  const [status, setStatus] = useState<'idle' | 'sending' | 'error'>('idle')
  const [error, setError] = useState('')
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState('')
  const [currentUser, setCurrentUser] = useState('')

  const handleAuth = async () => {
    try {
      const response = await fetch(`/api/${authMode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json().catch(() => null)
      if (!response.ok) {
        throw new Error(data?.detail || 'Ошибка входа')
      }

      setToken(data.access_token)
      setCurrentUser(username)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || !token) return

    const userMessage: Message = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setStatus('sending')
    setError('')

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: text })
      })

      if (!response.ok) {
        const data = await response.json().catch(() => null)
        throw new Error(data?.detail || 'Ошибка запроса к серверу')
      }

      const data = await response.json()
      const answer = data.answer || 'Ответ отсутствует'
      setMessages((prev) => [...prev, { role: 'assistant', content: answer }])
      setStatus('idle')
    } catch (err) {
      setStatus('error')
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  const clearChat = async () => {
    if (!token) return

    try {
      const response = await fetch('/api/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({})
      })

      if (!response.ok) {
        throw new Error('Не удалось очистить историю')
      }

      setMessages([SYSTEM_MESSAGE])
      setError('')
      setStatus('idle')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <div className="app-shell">
      <div className="chat-box">
        <header className="chat-header">
          <div>
            <h1>AI Ассистент</h1>
            <p>Авторизуйтесь, чтобы сохранить доступ к своему чату.</p>
          </div>
          <button type="button" className="clear-button" onClick={clearChat}>
            Очистить
          </button>
        </header>

        {!token ? (
          <div className="auth-panel">
            <div className="auth-switch">
              <button type="button" className={authMode === 'login' ? 'active' : ''} onClick={() => setAuthMode('login')}>
                Вход
              </button>
              <button type="button" className={authMode === 'register' ? 'active' : ''} onClick={() => setAuthMode('register')}>
                Регистрация
              </button>
            </div>
            <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Имя пользователя" />
            <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Пароль" type="password" />
            <button type="button" className="send-button" onClick={handleAuth}>
              {authMode === 'login' ? 'Войти' : 'Зарегистрироваться'}
            </button>
            {error && <div className="error-text">Ошибка: {error}</div>}
          </div>
        ) : (
          <>
            <div className="user-bar">Пользователь: {currentUser}</div>
            <div className="messages">
              {messages
                .filter((message) => message.role !== 'system')
                .map((message, index) => (
                  <div key={index} className={`message ${message.role}`}>
                    <div className="message-content">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}
            </div>

            <div className="editor-panel">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Напиши вопрос ассистенту..."
                rows={4}
              />
              <div className="actions-row">
                <button
                  type="button"
                  className="send-button"
                  onClick={sendMessage}
                  disabled={status === 'sending'}
                >
                  {status === 'sending' ? 'Отправка...' : 'Отправить'}
                </button>
              </div>
              {error && <div className="error-text">Ошибка: {error}</div>}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App
