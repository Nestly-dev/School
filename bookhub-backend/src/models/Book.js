const mongoose = require('mongoose');

const bookSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: [true, 'Title is required'],
      trim: true,
    },
    author: {
      type: String,
      required: [true, 'Author is required'],
      trim: true,
    },
    description: {
      type: String,
      required: [true, 'Description is required'],
    },
    genre: {
      type: String,
      required: [true, 'Genre is required'],
      enum: [
        'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy',
        'Mystery', 'Thriller', 'Romance', 'Horror', 'Biography',
        'History', 'Self-Help', 'Science', 'Technology',
        'Children', 'Young Adult', 'Other',
      ],
    },
    coverImage: {
      type: String,
      default: '',
    },
    isbn: { type: String, trim: true },
    publisher: { type: String, trim: true },
    publishedDate: { type: Date },
    pages: { type: Number, min: 1 },
    language: { type: String, default: 'English' },
    rating: { type: Number, default: 0, min: 0, max: 5 },
    ratingCount: { type: Number, default: 0 },
    readCount: { type: Number, default: 0 },
    tags: [String],
    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
  },
  { timestamps: true }
);

// Enables full-text search on these fields
bookSchema.index({ title: 'text', author: 'text', description: 'text' });

module.exports = mongoose.model('Book', bookSchema);