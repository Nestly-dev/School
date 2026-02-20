import { useState, useEffect, useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setSearch } from '../store/filterSlice'
import FilterPanel from '../components/FilterPanel'
import BookCard from '../components/BookCard'
import Pagination from '../components/Pagination'
import api from '../utils/api'
import type { PaginatedBooks } from '../types'

function SearchBar() {
  const dispatch = useAppDispatch()
  const search = useAppSelector(s => s.filters.search)

  return (
    <div style={{ position: 'relative', maxWidth: 560 }}>
      <span style={{
        position: 'absolute', left: 14, top: '50%',
        transform: 'translateY(-50%)',
        color: 'var(--ink-muted)', fontSize: '1.1rem', pointerEvents: 'none',
      }}>
        🔍
      </span>
      <input
        className="form-input"
        style={{ paddingLeft: 42, height: 48, fontSize: '1rem', boxShadow: 'var(--shadow-sm)' }}
        placeholder="Search books by title, author, or description..."
        value={search}
        onChange={e => dispatch(setSearch(e.target.value))}
      />
    </div>
  )
}

export default function HomePage() {
  const filters = useAppSelector(s => s.filters)
  const [data, setData] = useState<PaginatedBooks | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchBooks = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      if (filters.search) params.set('search', filters.search)
      if (filters.genre) params.set('genre', filters.genre)
      if (filters.author) params.set('author', filters.author)
      if (filters.minRating) params.set('minRating', filters.minRating)
      if (filters.publishedFrom) params.set('publishedFrom', filters.publishedFrom)
      if (filters.publishedTo) params.set('publishedTo', filters.publishedTo)
      params.set('sortBy', filters.sortBy)
      params.set('sortOrder', filters.sortOrder)
      params.set('page', String(filters.page))
      params.set('limit', String(filters.limit))

      const { data } = await api.get<PaginatedBooks>(`/books?${params}`)
      setData(data)
    } catch {
      setError('Failed to load books. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    const debounce = setTimeout(fetchBooks, filters.search ? 350 : 0)
    return () => clearTimeout(debounce)
  }, [fetchBooks, filters.search])

  return (
    <div style={{ minHeight: '100vh', background: 'var(--cream)' }}>

      {/* Hero */}
      <header style={{
        background: 'linear-gradient(135deg, var(--ink) 0%, #3a2a14 100%)',
        color: '#fff', padding: '56px 0 48px',
      }}>
        <div className="container">
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2rem, 5vw, 3.2rem)',
            fontWeight: 900, lineHeight: 1.1, marginBottom: 12,
          }}>
            Discover Your<br />
            <span style={{ color: 'var(--amber-light)' }}>Next Great Read</span>
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.7)', marginBottom: 28, maxWidth: 480 }}>
            Explore thousands of books across every genre. Filter, search, and find your perfect story.
          </p>
          <SearchBar />
        </div>
      </header>

      {/* Main content */}
      <div className="container" style={{ padding: '32px 24px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'clamp(220px, 22%, 280px) 1fr',
          gap: 28,
        }}>

          {/* Sidebar */}
          <div className="hide-mobile">
            <FilterPanel />
          </div>

          {/* Book grid */}
          <main>
            <div style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginBottom: 20,
            }}>
              <p style={{ color: 'var(--ink-muted)', fontSize: '0.9rem' }}>
                {loading ? 'Loading...' : data
                  ? `${data.pagination.total.toLocaleString()} books found`
                  : ''}
              </p>
            </div>

            {error && (
              <div style={{
                background: '#fef2f2', border: '1px solid #fca5a5',
                borderRadius: 'var(--radius)', padding: 16,
                color: 'var(--red)', marginBottom: 20,
              }}>
                ⚠️ {error}
              </div>
            )}

            {/* Skeleton loading */}
            {loading ? (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: 20,
              }}>
                {Array.from({ length: 12 }).map((_, i) => (
                  <div key={i} className="card" style={{ height: 340 }}>
                    <div className="skeleton" style={{ height: 220 }} />
                    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <div className="skeleton" style={{ height: 16, width: '80%' }} />
                      <div className="skeleton" style={{ height: 12, width: '50%' }} />
                      <div className="skeleton" style={{ height: 12, width: '60%', marginTop: 8 }} />
                    </div>
                  </div>
                ))}
              </div>

            ) : data && data.books.length > 0 ? (
              <>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                  gap: 20,
                }} className="fade-in">
                  {data.books.map(book => (
                    <BookCard key={book._id} book={book} />
                  ))}
                </div>
                <Pagination
                  totalPages={data.pagination.totalPages}
                  total={data.pagination.total}
                />
              </>

            ) : (
              <div style={{
                textAlign: 'center', padding: '60px 20px',
                color: 'var(--ink-muted)',
              }}>
                <div style={{ fontSize: '3rem', marginBottom: 16 }}>📭</div>
                <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 8 }}>
                  No books found
                </h3>
                <p>Try adjusting your filters or search terms.</p>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}