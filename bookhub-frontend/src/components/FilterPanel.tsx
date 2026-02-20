import { useAppDispatch, useAppSelector } from '../store/hooks'
import {
  setGenre, setAuthor, setMinRating,
  setSortBy, setSortOrder, setPublishedFrom, setPublishedTo,
  resetFilters,
} from '../store/filterSlice'
import type { SortField } from '../types'

const GENRES = [
  'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery',
  'Thriller', 'Romance', 'Horror', 'Biography', 'History',
  'Self-Help', 'Science', 'Technology', 'Children', 'Young Adult', 'Other',
]

export default function FilterPanel() {
  const dispatch = useAppDispatch()
  const filters = useAppSelector(s => s.filters)

  const activeCount = [
    filters.genre, filters.author, filters.minRating,
    filters.publishedFrom, filters.publishedTo,
  ].filter(Boolean).length

  return (
    <aside style={{
      background: '#fff', border: '1px solid var(--border)',
      borderRadius: 'var(--radius)', padding: '20px',
      position: 'sticky', top: 80,
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 16,
      }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontWeight: 700 }}>
          Filters {activeCount > 0 && (
            <span style={{
              background: 'var(--amber)', color: '#fff',
              borderRadius: '50%', width: 20, height: 20,
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.7rem', marginLeft: 6,
            }}>
              {activeCount}
            </span>
          )}
        </h2>
        {activeCount > 0 && (
          <button
            onClick={() => dispatch(resetFilters())}
            style={{
              fontSize: '0.78rem', color: 'var(--red)',
              background: 'none', border: 'none', cursor: 'pointer',
            }}
          >
            Clear all
          </button>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* Genre */}
        <div className="form-group">
          <label className="form-label">Genre</label>
          <select
            className="form-select"
            value={filters.genre}
            onChange={e => dispatch(setGenre(e.target.value))}
          >
            <option value="">All genres</option>
            {GENRES.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>

        {/* Author */}
        <div className="form-group">
          <label className="form-label">Author</label>
          <input
            className="form-input"
            placeholder="Filter by author..."
            value={filters.author}
            onChange={e => dispatch(setAuthor(e.target.value))}
          />
        </div>

        {/* Min Rating */}
        <div className="form-group">
          <label className="form-label">Minimum Rating</label>
          <select
            className="form-select"
            value={filters.minRating}
            onChange={e => dispatch(setMinRating(e.target.value))}
          >
            <option value="">Any rating</option>
            <option value="4.5">★ 4.5+</option>
            <option value="4">★ 4.0+</option>
            <option value="3.5">★ 3.5+</option>
            <option value="3">★ 3.0+</option>
          </select>
        </div>

        {/* Sort By */}
        <div className="form-group">
          <label className="form-label">Sort By</label>
          <select
            className="form-select"
            value={filters.sortBy}
            onChange={e => dispatch(setSortBy(e.target.value as SortField))}
          >
            <option value="createdAt">Newest Added</option>
            <option value="rating">Highest Rated</option>
            <option value="readCount">Most Read</option>
            <option value="publishedDate">Publication Date</option>
            <option value="title">Title (A–Z)</option>
          </select>
        </div>

        {/* Sort Order */}
        <div className="form-group">
          <label className="form-label">Order</label>
          <select
            className="form-select"
            value={filters.sortOrder}
            onChange={e => dispatch(setSortOrder(e.target.value as 'asc' | 'desc'))}
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>

        {/* Published From */}
        <div className="form-group">
          <label className="form-label">Published From</label>
          <input
            type="date" className="form-input"
            value={filters.publishedFrom}
            onChange={e => dispatch(setPublishedFrom(e.target.value))}
          />
        </div>

        {/* Published To */}
        <div className="form-group">
          <label className="form-label">Published To</label>
          <input
            type="date" className="form-input"
            value={filters.publishedTo}
            onChange={e => dispatch(setPublishedTo(e.target.value))}
          />
        </div>

      </div>
    </aside>
  )
}