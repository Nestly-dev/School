import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setPage } from '../store/filterSlice'

interface Props {
  totalPages: number
  total: number
}

export default function Pagination({ totalPages, total }: Props) {
  const dispatch = useAppDispatch()
  const { page, limit } = useAppSelector(s => s.filters)

  if (totalPages <= 1) return null

  const pages: (number | '...')[] = []
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) pages.push(i)
  } else {
    pages.push(1)
    if (page > 3) pages.push('...')
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) {
      pages.push(i)
    }
    if (page < totalPages - 2) pages.push('...')
    pages.push(totalPages)
  }

  const from = (page - 1) * limit + 1
  const to = Math.min(page * limit, total)

  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', gap: 12, marginTop: 32,
    }}>
      <p style={{ fontSize: '0.85rem', color: 'var(--ink-muted)' }}>
        Showing {from}–{to} of {total} books
      </p>

      <div style={{
        display: 'flex', gap: 6,
        flexWrap: 'wrap', justifyContent: 'center',
      }}>
        <button
          className="btn btn-ghost btn-sm"
          disabled={page === 1}
          onClick={() => dispatch(setPage(page - 1))}
        >
          ← Prev
        </button>

        {pages.map((p, i) =>
          p === '...' ? (
            <span key={`dot-${i}`} style={{
              padding: '6px 4px', color: 'var(--ink-muted)',
            }}>
              …
            </span>
          ) : (
            <button
              key={p}
              onClick={() => dispatch(setPage(p as number))}
              style={{
                minWidth: 36, height: 36,
                background: p === page ? 'var(--amber)' : 'transparent',
                color: p === page ? '#fff' : 'var(--ink)',
                border: p === page ? 'none' : '1.5px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
                fontWeight: p === page ? 600 : 400,
                cursor: 'pointer', fontSize: '0.85rem',
                transition: 'all 0.15s',
              }}
            >
              {p}
            </button>
          )
        )}

        <button
          className="btn btn-ghost btn-sm"
          disabled={page === totalPages}
          onClick={() => dispatch(setPage(page + 1))}
        >
          Next →
        </button>
      </div>
    </div>
  )
}