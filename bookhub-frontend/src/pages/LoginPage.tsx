import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed.')
    }
  }

  return (
    <div style={{
      minHeight: 'calc(100vh - 64px)', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'var(--cream)', padding: 24,
    }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div className="card" style={{ padding: '40px 36px' }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <span style={{ fontSize: '2.5rem' }}>📚</span>
            <h1 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.8rem', fontWeight: 700, marginTop: 8,
            }}>
              Welcome Back
            </h1>
            <p style={{ color: 'var(--ink-muted)', fontSize: '0.9rem', marginTop: 4 }}>
              Sign in to your Book Hub account
            </p>
          </div>

          {error && (
            <div style={{
              background: '#fef2f2', border: '1px solid #fca5a5',
              borderRadius: 'var(--radius-sm)', padding: '10px 14px',
              color: 'var(--red)', fontSize: '0.875rem', marginBottom: 20,
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email" className="form-input"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password" className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit" className="btn btn-primary btn-lg"
              disabled={isLoading} style={{ marginTop: 8 }}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p style={{
            textAlign: 'center', marginTop: 20,
            fontSize: '0.875rem', color: 'var(--ink-muted)',
          }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--amber)', fontWeight: 500 }}>
              Register here
            </Link>
          </p>

          {/* Demo hint */}
          <div style={{
            marginTop: 20, padding: '12px 14px',
            background: 'var(--paper)', borderRadius: 'var(--radius-sm)',
            fontSize: '0.78rem', color: 'var(--ink-muted)',
          }}>
            <strong style={{ color: 'var(--ink-light)' }}>Demo accounts:</strong><br />
            Admin: admin@bookhub.com / admin123<br />
            User: user@bookhub.com / user1234
          </div>
        </div>
      </div>
    </div>
  )
}