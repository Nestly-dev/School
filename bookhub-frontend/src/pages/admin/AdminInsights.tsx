import { useState, useEffect } from 'react'
import type { Insights, Book } from '../../types'
import api from '../../utils/api'

const StatCard = ({ label, value, icon, color }: {
  label: string; value: string | number; icon: string; color: string
}) => (
  <div className="card" style={{ padding: 24, borderTop: `4px solid ${color}` }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <p style={{ fontSize: '0.8rem', color: 'var(--ink-muted)', marginBottom: 6 }}>{label}</p>
        <p style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 900, color }}>
          {value}
        </p>
      </div>
      <span style={{ fontSize: '2rem' }}>{icon}</span>
    </div>
  </div>
)

const BookRow = ({ book, rank }: { book: Book; rank: number }) => (
  <div style={{
    display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0',
    borderBottom: '1px solid var(--border)',
  }}>
    <span style={{
      width: 28, height: 28, borderRadius: '50%',
      background: rank <= 3 ? 'var(--amber)' : 'var(--paper)',
      color: rank <= 3 ? '#fff' : 'var(--ink-muted)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: '0.75rem', fontWeight: 700, flexShrink: 0,
    }}>
      {rank}
    </span>
    <div style={{ flex: 1, minWidth: 0 }}>
      <p style={{
        fontWeight: 600, fontSize: '0.875rem',
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
      }}>
        {book.title}
      </p>
      <p style={{ fontSize: '0.75rem', color: 'var(--ink-muted)' }}>{book.author}</p>
    </div>
    <span style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--teal)', flexShrink: 0 }}>
      {book.readCount.toLocaleString()} reads
    </span>
  </div>
)

export default function AdminInsights() {
  const [data, setData] = useState<Insights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get<Insights>('/admin/insights')
      .then(({ data }) => setData(data))
      .catch(() => setError('Failed to load insights.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 40, textAlign: 'center', color: 'var(--ink-muted)' }}>
      Loading insights...
    </div>
  )

  if (error) return (
    <div style={{ padding: 40, textAlign: 'center', color: 'var(--red)' }}>{error}</div>
  )

  const d = data!

  return (
    <div style={{ minHeight: '100vh', background: 'var(--cream)' }}>
      <div style={{ background: 'var(--teal)', color: '#fff', padding: '32px 0' }}>
        <div className="container">
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 900 }}>
            Book Insights
          </h1>
          <p style={{ opacity: 0.8, marginTop: 4 }}>Analytics and performance overview</p>
        </div>
      </div>

      <div className="container" style={{ padding: '32px 24px' }}>

        {/* Summary Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 20, marginBottom: 32,
        }}>
          <StatCard label="Total Books" value={d.totalBooks} icon="📚" color="var(--amber)" />
          <StatCard label="Total Reads" value={d.totalReads.toLocaleString()} icon="👁" color="var(--teal)" />
          <StatCard
            label="Avg Reads / Book"
            value={d.totalBooks ? Math.round(d.totalReads / d.totalBooks).toLocaleString() : 0}
            icon="📈"
            color="var(--ink)"
          />
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 24, marginBottom: 24,
        }}>

          {/* Top 5 Most Read */}
          <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginBottom: 16 }}>
              🏆 Top 5 Most Read
            </h2>
            {d.topBooks.map((book, i) => (
              <BookRow key={book._id} book={book} rank={i + 1} />
            ))}
          </div>

          {/* Bottom 5 Least Read */}
          <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginBottom: 16 }}>
              📉 Bottom 5 Least Read
            </h2>
            {d.bottomBooks.map((book, i) => (
              <BookRow key={book._id} book={book} rank={i + 1} />
            ))}
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 24,
        }}>

          {/* Recently Added */}
          <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginBottom: 16 }}>
              🆕 Recently Added
            </h2>
            {d.recentBooks.map((book, i) => (
              <div key={book._id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '8px 0',
                borderBottom: i < d.recentBooks.length - 1 ? '1px solid var(--border)' : 'none',
              }}>
                <div>
                  <p style={{ fontWeight: 600, fontSize: '0.875rem' }}>{book.title}</p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--ink-muted)' }}>
                    <span className="badge badge-genre" style={{ marginRight: 4 }}>{book.genre}</span>
                    {new Date(book.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Genre Breakdown */}
          <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginBottom: 16 }}>
              📂 Genre Breakdown
            </h2>
            {d.genreBreakdown.map(g => {
              const maxCount = Math.max(...d.genreBreakdown.map(x => x.count))
              const pct = (g.count / maxCount) * 100
              return (
                <div key={g._id} style={{ marginBottom: 12 }}>
                  <div style={{
                    display: 'flex', justifyContent: 'space-between',
                    marginBottom: 4, fontSize: '0.85rem',
                  }}>
                    <span>{g._id}</span>
                    <span style={{ color: 'var(--ink-muted)' }}>
                      {g.count} books · {g.totalReads.toLocaleString()} reads
                    </span>
                  </div>
                  <div style={{
                    height: 6, background: 'var(--paper)',
                    borderRadius: 3, overflow: 'hidden',
                  }}>
                    <div style={{
                      height: '100%', width: `${pct}%`,
                      background: 'linear-gradient(90deg, var(--amber), var(--teal))',
                      borderRadius: 3, transition: 'width 0.6s ease',
                    }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Read Count Per Book Table */}
        <div className="card" style={{ padding: 24, marginTop: 24 }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginBottom: 16 }}>
            📊 Read Count Per Book
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ background: 'var(--paper)', borderBottom: '2px solid var(--border)' }}>
                  <th style={{ padding: '10px 12px', textAlign: 'left' }}>Title</th>
                  <th style={{ padding: '10px 12px', textAlign: 'left' }}>Author</th>
                  <th style={{ padding: '10px 12px', textAlign: 'right' }}>Reads</th>
                </tr>
              </thead>
              <tbody>
                {d.readCountPerBook.map((b, i) => (
                  <tr key={b._id} style={{
                    borderBottom: '1px solid var(--border)',
                    background: i % 2 === 0 ? '#fff' : 'var(--cream)',
                  }}>
                    <td style={{ padding: '10px 12px', fontWeight: 500 }}>{b.title}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--ink-muted)' }}>{b.author}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: 600, color: 'var(--teal)' }}>
                      {b.readCount.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  )
}