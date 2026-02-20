import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div style={{
      minHeight: 'calc(100vh - 64px)', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      textAlign: 'center', padding: 24,
    }}>
      <div>
        <div style={{ fontSize: '5rem', marginBottom: 16 }}>📭</div>
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '3rem', fontWeight: 900, marginBottom: 12,
        }}>
          404
        </h1>
        <p style={{ color: 'var(--ink-muted)', marginBottom: 28, fontSize: '1.1rem' }}>
          Oops — we couldn't find that page.
        </p>
        <Link to="/" className="btn btn-primary btn-lg">
          Back to Book Hub
        </Link>
      </div>
    </div>
  )
}