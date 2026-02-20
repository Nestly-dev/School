import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const AdminCard = ({ title, icon, desc, to, color }: {
  title: string; icon: string; desc: string; to: string; color: string
}) => (
  <Link to={to} style={{ display: 'block' }}>
    <div
      className="card"
      style={{
        padding: 28, cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        borderTop: `4px solid ${color}`,
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.transform = 'translateY(-4px)'
        ;(e.currentTarget as HTMLElement).style.boxShadow = 'var(--shadow-md)'
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.transform = ''
        ;(e.currentTarget as HTMLElement).style.boxShadow = ''
      }}
    >
      <div style={{ fontSize: '2.2rem', marginBottom: 12 }}>{icon}</div>
      <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 6 }}>
        {title}
      </h3>
      <p style={{ color: 'var(--ink-muted)', fontSize: '0.875rem' }}>{desc}</p>
    </div>
  </Link>
)

export default function AdminDashboard() {
  const { user } = useAuth()

  return (
    <div style={{ minHeight: '100vh', background: 'var(--cream)' }}>
      {/* Header */}
      <div style={{ background: 'var(--teal)', color: '#fff', padding: '40px 0' }}>
        <div className="container">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span className="badge badge-admin" style={{
              background: 'rgba(255,255,255,0.2)', color: '#fff',
            }}>
              Admin
            </span>
          </div>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '2.2rem', fontWeight: 900,
          }}>
            Admin Dashboard
          </h1>
          <p style={{ opacity: 0.8, marginTop: 6 }}>Welcome back, {user?.name}</p>
        </div>
      </div>

      <div className="container" style={{ padding: '40px 24px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: 24,
        }}>
          <AdminCard
            title="Manage Books"
            icon="📚"
            desc="Create, edit, and delete books from the catalog."
            to="/admin/books"
            color="var(--amber)"
          />
          <AdminCard
            title="Book Insights"
            icon="📊"
            desc="View read counts, top performers, and analytics."
            to="/admin/insights"
            color="var(--teal)"
          />
          <AdminCard
            title="Browse Catalog"
            icon="🔍"
            desc="Explore the public book discovery interface."
            to="/"
            color="var(--ink-muted)"
          />
        </div>

        <div style={{
          marginTop: 32, padding: 24,
          background: '#fff', borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
        }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            marginBottom: 12, fontSize: '1.1rem',
          }}>
            Quick Guide
          </h2>
          <ul style={{
            color: 'var(--ink-light)', fontSize: '0.9rem',
            lineHeight: 2, listStyle: 'none',
          }}>
            <li>→ Use <strong>Manage Books</strong> to add new titles or edit existing ones.</li>
            <li>→ Use <strong>Book Insights</strong> to monitor read counts and discover top/bottom performers.</li>
            <li>→ Admin routes are protected — only users with the <code>admin</code> role can access this dashboard.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}