import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { FilterState, SortField, SortOrder } from '../types';


const initialState: FilterState = {
  search: '',
  genre: '',
  author: '',
  minRating: '',
  sortBy: 'createdAt',
  sortOrder: 'desc',
  publishedFrom: '',
  publishedTo: '',
  page: 1,
  limit: 12,
};

const filterSlice = createSlice({
  name: 'filters',
  initialState,
  reducers: {
    setSearch(state, action: PayloadAction<string>) {
      state.search = action.payload;
      state.page = 1;
    },
    setGenre(state, action: PayloadAction<string>) {
      state.genre = action.payload;
      state.page = 1;
    },
    setAuthor(state, action: PayloadAction<string>) {
      state.author = action.payload;
      state.page = 1;
    },
    setMinRating(state, action: PayloadAction<string>) {
      state.minRating = action.payload;
      state.page = 1;
    },
    setSortBy(state, action: PayloadAction<SortField>) {
      state.sortBy = action.payload;
      state.page = 1;
    },
    setSortOrder(state, action: PayloadAction<SortOrder>) {
      state.sortOrder = action.payload;
    },
    setPublishedFrom(state, action: PayloadAction<string>) {
      state.publishedFrom = action.payload;
      state.page = 1;
    },
    setPublishedTo(state, action: PayloadAction<string>) {
      state.publishedTo = action.payload;
      state.page = 1;
    },
    setPage(state, action: PayloadAction<number>) {
      state.page = action.payload;
    },
    setLimit(state, action: PayloadAction<number>) {
      state.limit = action.payload;
      state.page = 1;
    },
    resetFilters() {
      return initialState;
    },
  },
});

export const {
  setSearch, setGenre, setAuthor, setMinRating,
  setSortBy, setSortOrder, setPublishedFrom, setPublishedTo,
  setPage, setLimit, resetFilters,
} = filterSlice.actions;

export default filterSlice.reducer;
