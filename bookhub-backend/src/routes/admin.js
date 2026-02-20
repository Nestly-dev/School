const express = require('express');
const { body, validationResult } = require('express-validator');
const Book = require('../models/Book');
const { protect, adminOnly } = require('../middleware/auth');

const router = express.Router();

// All admin routes require authentication + admin role
router.use(protect, adminOnly);

const bookValidation = [
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('author').trim().notEmpty().withMessage('Author is required'),
  body('description').trim().notEmpty().withMessage('Description is required'),
  body('genre').notEmpty().withMessage('Genre is required'),
];

// @route POST /api/admin/books - Create a book
router.post('/books', bookValidation, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ message: errors.array()[0].msg });

  try {
    const book = await Book.create({ ...req.body, createdBy: req.user._id });
    res.status(201).json(book);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route PUT /api/admin/books/:id - Update a book
router.put('/books/:id', bookValidation, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ message: errors.array()[0].msg });

  try {
    const book = await Book.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!book) return res.status(404).json({ message: 'Book not found.' });
    res.json(book);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route DELETE /api/admin/books/:id - Delete a book
router.delete('/books/:id', async (req, res) => {
  try {
    const book = await Book.findByIdAndDelete(req.params.id);
    if (!book) return res.status(404).json({ message: 'Book not found.' });
    res.json({ message: 'Book deleted successfully.' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route GET /api/admin/books - Get all books (admin view)
router.get('/books', async (req, res) => {
  try {
    const { page = 1, limit = 20, search } = req.query;
    const filter = search ? { $text: { $search: search } } : {};
    const skip = (parseInt(page) - 1) * parseInt(limit);

    const [books, total] = await Promise.all([
      Book.find(filter).sort({ createdAt: -1 }).skip(skip).limit(parseInt(limit)).lean(),
      Book.countDocuments(filter),
    ]);

    res.json({
      books, total,
      page: parseInt(page),
      totalPages: Math.ceil(total / parseInt(limit)),
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// @route GET /api/admin/insights - Analytics dashboard
router.get('/insights', async (req, res) => {
  try {
    const [
      totalBooks, totalReads, topBooks, bottomBooks,
      recentBooks, readCountPerBook, genreBreakdown,
    ] = await Promise.all([
      Book.countDocuments(),
      Book.aggregate([{ $group: { _id: null, total: { $sum: '$readCount' } } }]),
      Book.find().sort({ readCount: -1 }).limit(5).select('title author readCount rating coverImage').lean(),
      Book.find().sort({ readCount: 1 }).limit(5).select('title author readCount rating coverImage').lean(),
      Book.find().sort({ createdAt: -1 }).limit(10).select('title author genre createdAt coverImage').lean(),
      Book.find().select('title author readCount').sort({ readCount: -1 }).lean(),
      Book.aggregate([
        { $group: { _id: '$genre', count: { $sum: 1 }, totalReads: { $sum: '$readCount' } } },
        { $sort: { count: -1 } },
      ]),
    ]);

    res.json({
      totalBooks,
      totalReads: totalReads[0]?.total || 0,
      topBooks,
      bottomBooks,
      recentBooks,
      readCountPerBook,
      genreBreakdown,
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;