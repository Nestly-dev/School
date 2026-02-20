import { Link } from 'react-router-dom'
import type { Book } from '../types'

interface Props { book: Book }

const StarRating = ({ rating }: { rating: number }) => {
  const full = Math.floor(rating)
  const half = rating % 1 >= 0.5
  return (
    <span className="stars" style={{ fontSize: '0.85rem' }}>
      {Array.from({ length: 5 }, (_, i) => {
        if (i < full) return '★'
        if (i === full && half) return '½'
        return '☆'
      }).join('')}
      <span style={{ color: 'var(--ink-muted)', marginLeft: 4 }}>
        {rating.toFixed(1)}
      </span>
    </span>
  )
}

export default function BookCard({ book }: Props) {
  const placeholderBg = ['#e8c090', '#90b8c8', '#c890a8', '#90c898', '#c8a890']
  const colorIdx = book.title.charCodeAt(0) % placeholderBg.length

  return (
    <Link to={`/books/${book._id}`} style={{ display: 'block' }}>
      <article
        className="card"
        style={{
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          height: '100%', display: 'flex', flexDirection: 'column',
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
        {/* Cover Image */}
        <div style={{
          height: 220, overflow: 'hidden', position: 'relative',
          background: placeholderBg[colorIdx],
        }}>
          {book.coverImage ? (
            <img
              src={book.coverImage}
              alt={book.title}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              onError={e => {
                (e.target as HTMLImageElement).style.display = 'none'
              }}
            />
          ) : (
            <div style={{
              height: '100%', display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: '3rem',
            }}>
              📖
            </div>
          )}
          <span className="badge badge-genre" style={{
            position: 'absolute', top: 10, right: 10,
            backdropFilter: 'blur(4px)',
          }}>
            {book.genre}
          </span>
        </div>

        {/* Content */}
        <div style={{
          padding: '16px', flex: 1,
          display: 'flex', flexDirection: 'column', gap: 6,
        }}>
          <h3 style={{
            fontFamily: 'var(--font-display)', fontWeight: 700,
            fontSize: '1.05rem', lineHeight: 1.3,
            display: '-webkit-box', WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical', overflow: 'hidden',
          }}>
            {book.title}
          </h3>

          <p style={{ fontSize: '0.85rem', color: 'var(--ink-muted)' }}>
            by {book.author}
          </p>

          <p style={{
            fontSize: '0.82rem', color: 'var(--ink-light)', flex: 1,
            display: '-webkit-box', WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical', overflow: 'hidden', marginTop: 4,
          }}>
            {book.description}
          </p>

          <div style={{
            display: 'flex', justifyContent: 'space-between',
            alignItems: 'center', marginTop: 8,
          }}>
            <StarRating rating={book.rating} />
            <span style={{ fontSize: '0.78rem', color: 'var(--ink-muted)' }}>
              👁 {book.readCount.toLocaleString()} reads
            </span>
          </div>
        </div>
      </article>
    </Link>
  )
}