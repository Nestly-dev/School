const express = require('express');
const { body, validationResult } = require('express-validator');
const Book = require('../models/Book');
const { protect } = require('../middleware/auth');

const router = express.Router();

// @route GET /api/books - Get all books with filtering, sorting, pagination
router.get('/', async (req, res) => {
  try {
    const {
      search, genre, author, language, minRating,
      sortBy = 'createdAt', sortOrder = 'desc',
      page = 1, limit = 12,
      publishedFrom, publishedTo,
    } = req.query;

    const filter = {};

    if (search) filter.$text = { $search: search };
    if (genre) filter.genre = genre;
    if (author) filter.author = { $regex: author, $options: 'i' };
    if (language) filter.language = language;
    if (minRating) filter.rating = { $gte: parseFloat(minRating) };

    if (publishedFrom || publishedTo) {
      filter.publishedDate = {};
      if (publishedFrom) filter.publishedDate.$gte = new Date(publishedFrom);
      if (publishedTo) filter.publishedDate.$lte = new Date(publishedTo);
    }

    const sortOptions = {};
    sortOptions[sortBy] = sortOrder === 'asc' ? 1 : -1;

    const pageNum = Math.max(1, parseInt(page));
    const limitNum = Math.min(50, Math.max(1, parseInt(limit)));
    const skip = (pageNum - 1) * limitNum;

    const [books, total] = await Promise.all([
      Book.find(filter).sort(sortOptions).skip(skip).limit(limitNum).lean(),
      Book.countDocuments(filter),
    ]);

    res.json({
      books,
      pagination: {
        total,
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(total / limitNum),
      },
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route GET /api/books/genres - Get all available genres
router.get('/genres', async (req, res) => {
  try {
    const genres = await Book.distinct('genre');
    res.json(genres);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route GET /api/books/:id - Get single book
router.get('/:id', async (req, res) => {
  try {
    const book = await Book.findById(req.params.id).lean();
    if (!book) return res.status(404).json({ message: 'Book not found.' });
    res.json(book);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route POST /api/books/:id/read - Mark book as read
router.post('/:id/read', protect, async (req, res) => {
  try {
    const book = await Book.findByIdAndUpdate(
      req.params.id,
      { $inc: { readCount: 1 } },
      { new: true }
    );
    if (!book) return res.status(404).json({ message: 'Book not found.' });

    await require('../models/User').findByIdAndUpdate(
      req.user._id,
      { $addToSet: { readBooks: book._id } }
    );

    res.json({ message: 'Marked as read', readCount: book.readCount });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route POST /api/books/:id/rate - Rate a book
router.post('/:id/rate', protect, [
  body('rating').isFloat({ min: 1, max: 5 }).withMessage('Rating must be between 1 and 5'),
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ message: errors.array()[0].msg });

  try {
    const { rating } = req.body;
    const book = await Book.findById(req.params.id);
    if (!book) return res.status(404).json({ message: 'Book not found.' });

    const newRatingCount = book.ratingCount + 1;
    const newRating = ((book.rating * book.ratingCount) + rating) / newRatingCount;

    book.rating = Math.round(newRating * 10) / 10;
    book.ratingCount = newRatingCount;
    await book.save();

    res.json({ rating: book.rating, ratingCount: book.ratingCount });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;