import { useState, useEffect } from 'react'
import type { Book, BookFormData } from '../../types'
import api from '../../utils/api'

const GENRES = [
  'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery',
  'Thriller', 'Romance', 'Horror', 'Biography', 'History',
  'Self-Help', 'Science', 'Technology', 'Children', 'Young Adult', 'Other',
]

const emptyForm: BookFormData = {
  title: '', author: '', description: '', genre: '',
  coverImage: '', isbn: '', publisher: '',
  publishedDate: '', pages: '', language: 'English',
}

function BookForm({ initial, onSave, onCancel, saving }: {
  initial: BookFormData
  onSave: (data: BookFormData) => void
  onCancel: () => void
  saving: boolean
}) {
  const [form, setForm] = useState(initial)

  const set = (field: keyof BookFormData) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }))

  return (
    <form
      onSubmit={e => { e.preventDefault(); onSave(form) }}
      style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="form-group">
          <label className="form-label">Title *</label>
          <input className="form-input" value={form.title} onChange={set('title')} required />
        </div>
        <div className="form-group">
          <label className="form-label">Author *</label>
          <input className="form-input" value={form.author} onChange={set('author')} required />
        </div>
        <div className="form-group">
          <label className="form-label">Genre *</label>
          <select className="form-select" value={form.genre} onChange={set('genre')} required>
            <option value="">Select genre...</option>
            {GENRES.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Language</label>
          <input className="form-input" value={form.language} onChange={set('language')} />
        </div>
        <div className="form-group">
          <label className="form-label">ISBN</label>
          <input className="form-input" value={form.isbn} onChange={set('isbn')} />
        </div>
        <div className="form-group">
          <label className="form-label">Publisher</label>
          <input className="form-input" value={form.publisher} onChange={set('publisher')} />
        </div>
        <div className="form-group">
          <label className="form-label">Published Date</label>
          <input type="date" className="form-input" value={form.publishedDate} onChange={set('publishedDate')} />
        </div>
        <div className="form-group">
          <label className="form-label">Pages</label>
          <input type="number" className="form-input" value={form.pages} onChange={set('pages')} min={1} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Cover Image URL</label>
        <input
          className="form-input" value={form.coverImage}
          onChange={set('coverImage')} placeholder="https://..."
        />
      </div>

      <div className="form-group">
        <label className="form-label">Description *</label>
        <textarea
          className="form-textarea" value={form.description}
          onChange={set('description')} required style={{ minHeight: 120 }}
        />
      </div>

      <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-ghost" onClick={onCancel}>Cancel</button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving...' : 'Save Book'}
        </button>
      </div>
    </form>
  )
}

export default function AdminBooks() {
  const [books, setBooks] = useState<Book[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState<'create' | 'edit' | null>(null)
  const [editing, setEditing] = useState<Book | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ page: String(page), limit: '15' })
      if (search) params.set('search', search)
      const { data } = await api.get(`/admin/books?${params}`)
      setBooks(data.books)
      setTotal(data.total)
      setTotalPages(data.totalPages)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, search])

  const openEdit = (book: Book) => {
    setEditing(book)
    setModal('edit')
  }

  const handleSave = async (form: BookFormData) => {
    setSaving(true)
    setError('')
    try {
      const payload = { ...form, pages: form.pages ? Number(form.pages) : undefined }
      if (modal === 'create') {
        const { data } = await api.post('/admin/books', payload)
        setBooks(prev => [data, ...prev])
        setTotal(t => t + 1)
      } else if (editing) {
        const { data } = await api.put(`/admin/books/${editing._id}`, payload)
        setBooks(prev => prev.map(b => b._id === editing._id ? data : b))
      }
      setModal(null)
      setSuccess(modal === 'create' ? 'Book created!' : 'Book updated!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to save.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return
    try {
      await api.delete(`/admin/books/${id}`)
      setBooks(prev => prev.filter(b => b._id !== id))
      setTotal(t => t - 1)
      setSuccess('Book deleted.')
      setTimeout(() => setSuccess(''), 3000)
    } catch {
      setError('Failed to delete.')
    }
  }

  const getInitialValues = (book: Book): BookFormData => ({
    title: book.title,
    author: book.author,
    description: book.description,
    genre: book.genre,
    coverImage: book.coverImage || '',
    isbn: book.isbn || '',
    publisher: book.publisher || '',
    publishedDate: book.publishedDate ? book.publishedDate.slice(0, 10) : '',
    pages: book.pages ? String(book.pages) : '',
    language: book.language,
  })

  return (
    <div style={{ minHeight: '100vh', background: 'var(--cream)' }}>
      <div style={{ background: 'var(--teal)', color: '#fff', padding: '32px 0' }}>
        <div className="container">
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 900 }}>
            Manage Books
          </h1>
          <p style={{ opacity: 0.8, marginTop: 4 }}>{total} books in catalog</p>
        </div>
      </div>

      <div className="container" style={{ padding: '32px 24px' }}>

        {/* Toolbar */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
          <input
            className="form-input" style={{ flex: 1, minWidth: 200 }}
            placeholder="Search books..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
          />
          <button
            className="btn btn-primary"
            onClick={() => { setEditing(null); setModal('create') }}
          >
            + Add Book
          </button>
        </div>

        {(error || success) && (
          <div style={{
            padding: '10px 14px', borderRadius: 'var(--radius-sm)', marginBottom: 16,
            background: error ? '#fef2f2' : '#f0fdf4',
            border: `1px solid ${error ? '#fca5a5' : '#86efac'}`,
            color: error ? 'var(--red)' : 'var(--green)',
          }}>
            {error || success}
          </div>
        )}

        {/* Table */}
        <div className="card" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)', background: 'var(--paper)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Title</th>
                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Author</th>
                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Genre</th>
                <th style={{ padding: '12px 8px', textAlign: 'center' }}>Rating</th>
                <th style={{ padding: '12px 8px', textAlign: 'center' }}>Reads</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <td key={j} style={{ padding: '12px 16px' }}>
                        <div className="skeleton" style={{ height: 14, borderRadius: 4 }} />
                      </td>
                    ))}
                  </tr>
                ))
              ) : books.map(book => (
                <tr key={book._id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 500 }}>{book.title}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--ink-muted)' }}>{book.author}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span className="badge badge-genre">{book.genre}</span>
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                    ⭐ {book.rating.toFixed(1)}
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                    {book.readCount.toLocaleString()}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => openEdit(book)}>
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(book._id, book.title)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 20 }}>
            <button
              className="btn btn-ghost btn-sm"
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
            >
              ← Prev
            </button>
            <span style={{ padding: '6px 12px', fontSize: '0.875rem' }}>
              Page {page} of {totalPages}
            </span>
            <button
              className="btn btn-ghost btn-sm"
              disabled={page === totalPages}
              onClick={() => setPage(p => p + 1)}
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      {modal && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
          display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
          zIndex: 200, padding: '40px 16px', overflowY: 'auto',
        }}>
          <div className="card" style={{ width: '100%', maxWidth: 700, padding: 28 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem' }}>
                {modal === 'create' ? 'Add New Book' : `Edit: ${editing?.title}`}
              </h2>
              <button
                onClick={() => setModal(null)}
                style={{
                  background: 'none', border: 'none',
                  fontSize: '1.2rem', color: 'var(--ink-muted)', cursor: 'pointer',
                }}
              >
                ✕
              </button>
            </div>
            {error && (
              <div style={{ color: 'var(--red)', fontSize: '0.875rem', marginBottom: 12 }}>
                {error}
              </div>
            )}
            <BookForm
              initial={editing ? getInitialValues(editing) : emptyForm}
              onSave={handleSave}
              onCancel={() => setModal(null)}
              saving={saving}
            />
          </div>
        </div>
      )}
    </div>
  )
}