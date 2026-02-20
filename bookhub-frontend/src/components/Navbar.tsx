import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { isAuthenticated, isAdmin, user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
    setMenuOpen(false)
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <nav style={{
      background: '#fff',
      borderBottom: '1px solid var(--border)',
      position: 'sticky', top: 0, zIndex: 100,
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div className="container" style={{
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', height: 64,
      }}>

        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '1.6rem' }}>📚</span>
          <span style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700, fontSize: '1.4rem', color: 'var(--ink)',
          }}>
            Book<span style={{ color: 'var(--amber)' }}>Hub</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <div className="hide-mobile" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Link to="/" className="btn btn-ghost btn-sm" style={{
            background: isActive('/') ? 'var(--paper)' : undefined,
          }}>
            Discover
          </Link>

          {isAdmin && (
            <>
              <Link to="/admin" className="btn btn-ghost btn-sm">Dashboard</Link>
              <Link to="/admin/books" className="btn btn-ghost btn-sm">Manage Books</Link>
              <Link to="/admin/insights" className="btn btn-ghost btn-sm">Insights</Link>
            </>
          )}

          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 8 }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--ink-muted)' }}>
                👋 {user?.name}
                {isAdmin && (
                  <span className="badge badge-admin" style={{ marginLeft: 6 }}>Admin</span>
                )}
              </span>
              <button onClick={handleLogout} className="btn btn-ghost btn-sm">
                Sign Out
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 8, marginLeft: 8 }}>
              <Link to="/login" className="btn btn-ghost btn-sm">Sign In</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Join Free</Link>
            </div>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="hide-desktop"
          onClick={() => setMenuOpen(!menuOpen)}
          style={{ background: 'none', border: 'none', fontSize: '1.4rem', padding: 4 }}
          aria-label="Toggle menu"
        >
          {menuOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="hide-desktop" style={{
          background: '#fff', borderTop: '1px solid var(--border)',
          padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 8,
        }}>
          <Link to="/" className="btn btn-ghost" onClick={() => setMenuOpen(false)}>Discover</Link>
          {isAdmin && (
            <>
              <Link to="/admin" className="btn btn-ghost" onClick={() => setMenuOpen(false)}>Dashboard</Link>
              <Link to="/admin/books" className="btn btn-ghost" onClick={() => setMenuOpen(false)}>Manage Books</Link>
              <Link to="/admin/insights" className="btn btn-ghost" onClick={() => setMenuOpen(false)}>Insights</Link>
            </>
          )}
          {isAuthenticated ? (
            <button onClick={handleLogout} className="btn btn-ghost">Sign Out</button>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost" onClick={() => setMenuOpen(false)}>Sign In</Link>
              <Link to="/register" className="btn btn-primary" onClick={() => setMenuOpen(false)}>Join Free</Link>
            </>
          )}
        </div>
      )}
    </nav>
  )
}