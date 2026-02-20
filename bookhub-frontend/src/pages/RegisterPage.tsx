import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const { register, isLoading } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')

  const update = (field: string) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) return setError('Passwords do not match.')
    if (form.password.length < 6) return setError('Password must be at least 6 characters.')
    try {
      await register(form.name, form.email, form.password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed.')
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
              Join Book Hub
            </h1>
            <p style={{ color: 'var(--ink-muted)', fontSize: '0.9rem', marginTop: 4 }}>
              Create your free account
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
              <label className="form-label">Full Name</label>
              <input
                type="text" className="form-input" placeholder="Your name"
                value={form.name} onChange={update('name')} required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email" className="form-input" placeholder="you@example.com"
                value={form.email} onChange={update('email')} required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password" className="form-input" placeholder="Min. 6 characters"
                value={form.password} onChange={update('password')} required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <input
                type="password" className="form-input" placeholder="Repeat password"
                value={form.confirm} onChange={update('confirm')} required
              />
            </div>

            <button
              type="submit" className="btn btn-primary btn-lg"
              disabled={isLoading} style={{ marginTop: 8 }}
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p style={{
            textAlign: 'center', marginTop: 20,
            fontSize: '0.875rem', color: 'var(--ink-muted)',
          }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--amber)', fontWeight: 500 }}>
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}