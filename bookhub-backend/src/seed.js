const mongoose = require('mongoose');
const dotenv = require('dotenv');
dotenv.config();

const User = require('./models/User');
const Book = require('./models/Book');

const books = [
  {
    title: 'The Great Gatsby',
    author: 'F. Scott Fitzgerald',
    description: 'A story of the mysteriously wealthy Jay Gatsby and his love for Daisy Buchanan, set against the backdrop of the roaring twenties.',
    genre: 'Fiction',
    publishedDate: new Date('1925-04-10'),
    pages: 180,
    language: 'English',
    rating: 4.2,
    ratingCount: 1203,
    readCount: 850,
    coverImage: 'https://covers.openlibrary.org/b/id/8432209-L.jpg',
    isbn: '9780743273565',
  },
  {
    title: 'To Kill a Mockingbird',
    author: 'Harper Lee',
    description: 'The story of young Scout Finch and her father Atticus, a lawyer who defends a Black man falsely accused of rape in the American South.',
    genre: 'Fiction',
    publishedDate: new Date('1960-07-11'),
    pages: 281,
    language: 'English',
    rating: 4.5,
    ratingCount: 2450,
    readCount: 1200,
    coverImage: 'https://covers.openlibrary.org/b/id/8228691-L.jpg',
    isbn: '9780061935466',
  },
  {
    title: '1984',
    author: 'George Orwell',
    description: 'A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism.',
    genre: 'Science Fiction',
    publishedDate: new Date('1949-06-08'),
    pages: 328,
    language: 'English',
    rating: 4.6,
    ratingCount: 3100,
    readCount: 2100,
    coverImage: 'https://covers.openlibrary.org/b/id/7222246-L.jpg',
    isbn: '9780451524935',
  },
  {
    title: 'The Hitchhiker\'s Guide to the Galaxy',
    author: 'Douglas Adams',
    description: 'A comedy science fiction franchise following the misadventures of the last surviving man and his alien friend.',
    genre: 'Science Fiction',
    publishedDate: new Date('1979-10-12'),
    pages: 193,
    language: 'English',
    rating: 4.7,
    ratingCount: 1870,
    readCount: 950,
    coverImage: 'https://covers.openlibrary.org/b/id/8475781-L.jpg',
    isbn: '9780345391803',
  },
  {
    title: 'Atomic Habits',
    author: 'James Clear',
    description: 'An easy and proven way to build good habits and break bad ones.',
    genre: 'Self-Help',
    publishedDate: new Date('2018-10-16'),
    pages: 320,
    language: 'English',
    rating: 4.7,
    ratingCount: 3500,
    readCount: 2800,
    coverImage: 'https://covers.openlibrary.org/b/id/10519704-L.jpg',
    isbn: '9780735211292',
  },
  {
    title: 'Dune',
    author: 'Frank Herbert',
    description: 'Set in the distant future, it follows young Paul Atreides as his family assumes control of the desert planet Arrakis.',
    genre: 'Science Fiction',
    publishedDate: new Date('1965-08-01'),
    pages: 688,
    language: 'English',
    rating: 4.8,
    ratingCount: 4200,
    readCount: 1700,
    coverImage: 'https://covers.openlibrary.org/b/id/8097600-L.jpg',
    isbn: '9780441013593',
  },
  {
    title: 'Sapiens',
    author: 'Yuval Noah Harari',
    description: 'A brief history of humankind from the Stone Age to the twenty-first century.',
    genre: 'History',
    publishedDate: new Date('2011-01-01'),
    pages: 443,
    language: 'English',
    rating: 4.4,
    ratingCount: 2900,
    readCount: 1350,
    coverImage: 'https://covers.openlibrary.org/b/id/9255566-L.jpg',
    isbn: '9780062316097',
  },
  {
    title: 'The Alchemist',
    author: 'Paulo Coelho',
    description: 'A philosophical novel about a young Andalusian shepherd in his journey to the pyramids of Egypt.',
    genre: 'Fiction',
    publishedDate: new Date('1988-01-01'),
    pages: 208,
    language: 'English',
    rating: 4.3,
    ratingCount: 3800,
    readCount: 2200,
    coverImage: 'https://covers.openlibrary.org/b/id/9971193-L.jpg',
    isbn: '9780062315007',
  },
];

async function seed() {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ Connected to MongoDB');

    // Clear existing data
    await User.deleteMany({});
    await Book.deleteMany({});
    console.log('🗑️  Cleared existing data');

    // Create admin user
    const admin = await User.create({
      name: 'Admin User',
      email: 'admin@bookhub.com',
      password: 'admin123',
      role: 'admin',
    });

    // Create regular user
    await User.create({
      name: 'Jane Reader',
      email: 'user@bookhub.com',
      password: 'user1234',
      role: 'user',
    });

    // Create books
    const createdBooks = await Book.insertMany(
      books.map((b) => ({ ...b, createdBy: admin._id }))
    );

    console.log(`✅ Created ${createdBooks.length} books`);
    console.log('\n📋 Demo credentials:');
    console.log('   Admin → admin@bookhub.com / admin123');
    console.log('   User  → user@bookhub.com  / user1234');
    console.log('\n🎉 Seed complete!');
    process.exit(0);
  } catch (err) {
    console.error('❌ Seed error:', err.message);
    process.exit(1);
  }
}

seed();