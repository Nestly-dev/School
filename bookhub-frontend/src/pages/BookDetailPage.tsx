import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import type { Book } from '../types'
import { useAuth } from '../context/AuthContext'
import api from '../utils/api'

export default function BookDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { isAuthenticated } = useAuth()
  const [book, setBook] = useState<Book | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [readMsg, setReadMsg] = useState('')
  const [rateMsg, setRateMsg] = useState('')

  useEffect(() => {
    api.get<Book>(`/books/${id}`)
      .then(({ data }) => setBook(data))
      .catch(() => setError('Book not found.'))
      .finally(() => setLoading(false))
  }, [id])

  const markRead = async () => {
    if (!isAuthenticated) return setReadMsg('Sign in to mark as read.')
    try {
      const { data } = await api.post(`/books/${id}/read`)
      setBook(prev => prev ? { ...prev, readCount: data.readCount } : prev)
      setReadMsg('Marked as read! ✅')
    } catch {
      setReadMsg('Error marking as read.')
    }
  }

  const rateBook = async (rating: number) => {
    if (!isAuthenticated) return setRateMsg('Sign in to rate.')
    try {
      const { data } = await api.post(`/books/${id}/rate`, { rating })
      setBook(prev => prev ? { ...prev, rating: data.rating, ratingCount: data.ratingCount } : prev)
      setRateMsg('Thanks for your rating! ⭐')
    } catch {
      setRateMsg('Error submitting rating.')
    }
  }

  if (loading) return (
    <div style={{ padding: 40, textAlign: 'center', color: 'var(--ink-muted)' }}>
      Loading book...
    </div>
  )

  if (error || !book) return (
    <div style={{ padding: 40, textAlign: 'center' }}>
      <p style={{ color: 'var(--red)' }}>{error}</p>
      <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>
        Back to Books
      </Link>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', background: 'var(--cream)' }}>
      <div className="container" style={{ padding: '40px 24px' }}>
        <Link to="/" style={{
          color: 'var(--amber)', fontSize: '0.9rem',
          marginBottom: 24, display: 'inline-block',
        }}>
          ← Back to Discover
        </Link>

        <div style={{
          display: 'grid', gridTemplateColumns: '280px 1fr', gap: 40,
          background: '#fff', borderRadius: 'var(--radius)',
          border: '1px solid var(--border)', padding: 32,
          boxShadow: 'var(--shadow-md)',
        }}>

          {/* Cover */}
          <div>
            <div style={{
              borderRadius: 'var(--radius)', overflow: 'hidden',
              aspectRatio: '2/3', background: 'var(--paper)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: 'var(--shadow-md)',
            }}>
              {book.coverImage ? (
                <img
                  src={book.coverImage} alt={book.title}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <span style={{ fontSize: '4rem' }}>📖</span>
              )}
            </div>

            {/* Actions */}
            <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button onClick={markRead} className="btn btn-primary" style={{ width: '100%' }}>
                📚 Mark as Read
              </button>
              {readMsg && (
                <p style={{ fontSize: '0.8rem', textAlign: 'center', color: 'var(--green)' }}>
                  {readMsg}
                </p>
              )}

              {/* Star Rating */}
              <div style={{ textAlign: 'center', marginTop: 8 }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--ink-muted)', marginBottom: 6 }}>
                  Rate this book:
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: 6 }}>
                  {[1, 2, 3, 4, 5].map(n => (
                    <button key={n} onClick={() => rateBook(n)} style={{
                      background: 'none', border: 'none',
                      fontSize: '1.4rem', color: 'var(--amber)', cursor: 'pointer', padding: 2,
                    }}>
                      ★
                    </button>
                  ))}
                </div>
                {rateMsg && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--green)', marginTop: 4 }}>
                    {rateMsg}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Details */}
          <div>
            <span className="badge badge-genre" style={{ marginBottom: 12 }}>
              {book.genre}
            </span>
            <h1 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(1.6rem, 3vw, 2.4rem)',
              fontWeight: 900, lineHeight: 1.2, marginBottom: 8,
            }}>
              {book.title}
            </h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--ink-muted)', marginBottom: 20 }}>
              by <strong style={{ color: 'var(--ink)' }}>{book.author}</strong>
            </p>

            {/* Stats */}
            <div style={{
              display: 'flex', gap: 24, flexWrap: 'wrap',
              padding: '16px 0',
              borderTop: '1px solid var(--border)',
              borderBottom: '1px solid var(--border)',
              marginBottom: 24,
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontFamily: 'var(--font-display)', fontWeight: 700,
                  fontSize: '1.5rem', color: 'var(--amber)',
                }}>
                  {book.rating.toFixed(1)}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--ink-muted)' }}>
                  Rating ({book.ratingCount})
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontFamily: 'var(--font-display)', fontWeight: 700,
                  fontSize: '1.5rem', color: 'var(--teal)',
                }}>
                  {book.readCount.toLocaleString()}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--ink-muted)' }}>Reads</div>
              </div>
              {book.pages && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{
                    fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.5rem',
                  }}>
                    {book.pages}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--ink-muted)' }}>Pages</div>
                </div>
              )}
            </div>

            <p style={{
              lineHeight: 1.8, color: 'var(--ink-light)',
              marginBottom: 24, fontSize: '0.95rem',
            }}>
              {book.description}
            </p>

            {/* Metadata */}
            <div style={{
              display: 'grid', gridTemplateColumns: '1fr 1fr',
              gap: '8px 16px', fontSize: '0.85rem',
            }}>
              {book.publisher && (
                <>
                  <span style={{ color: 'var(--ink-muted)' }}>Publisher</span>
                  <span>{book.publisher}</span>
                </>
              )}
              {book.publishedDate && (
                <>
                  <span style={{ color: 'var(--ink-muted)' }}>Published</span>
                  <span>{new Date(book.publishedDate).getFullYear()}</span>
                </>
              )}
              {book.isbn && (
                <>
                  <span style={{ color: 'var(--ink-muted)' }}>ISBN</span>
                  <span>{book.isbn}</span>
                </>
              )}
              <>
                <span style={{ color: 'var(--ink-muted)' }}>Language</span>
                <span>{book.language}</span>
              </>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}