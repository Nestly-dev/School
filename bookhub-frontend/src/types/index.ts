
export interface Book {
  _id: string;
  title: string;
  author: string;
  description: string;
  genre: Genre;
  coverImage: string;
  isbn?: string;
  publisher?: string;
  publishedDate?: string;
  pages?: number;
  language: string;
  rating: number;
  ratingCount: number;
  readCount: number;
  tags?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
}

export type Genre =
  | 'Fiction'
  | 'Non-Fiction'
  | 'Science Fiction'
  | 'Fantasy'
  | 'Mystery'
  | 'Thriller'
  | 'Romance'
  | 'Horror'
  | 'Biography'
  | 'History'
  | 'Self-Help'
  | 'Science'
  | 'Technology'
  | 'Children'
  | 'Young Adult'
  | 'Other';


export interface PaginatedBooks {
  books: Book[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Insights {
  totalBooks: number;
  totalReads: number;
  topBooks: Book[];
  bottomBooks: Book[];
  recentBooks: Book[];
  readCountPerBook: {
    _id: string;
    title: string;
    author: string;
    readCount: number;
  }[];
  genreBreakdown: {
    _id: string;
    count: number;
    totalReads: number;
  }[];
}

// ─── Filter State

export type SortField =
  | 'createdAt'
  | 'rating'
  | 'readCount'
  | 'publishedDate'
  | 'title';

export type SortOrder = 'asc' | 'desc';

export interface FilterState {
  search: string;
  genre: string;
  author: string;
  minRating: string;
  sortBy: SortField;
  sortOrder: SortOrder;
  publishedFrom: string;
  publishedTo: string;
  page: number;
  limit: number;
}


export interface BookFormData {
  title: string;
  author: string;
  description: string;
  genre: Genre | '';
  coverImage: string;
  isbn: string;
  publisher: string;
  publishedDate: string;
  pages: string;
  language: string;
}