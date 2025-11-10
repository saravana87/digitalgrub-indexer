/**
 * API client for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Indexing API
export const indexingApi = {
  getStats: () => api.get('/indexing/stats'),
  getDashboard: () => api.get('/indexing/dashboard'),
  getCrawlers: () => api.get('/indexing/crawlers'),
};

// Content Generation API
export const contentApi = {
  // Get available filter options
  getFilters: () => api.get('/content/filters'),
  
  // Generate titles with filters
  generateTitles: (data: { 
    topic: string; 
    source_type: 'jobs' | 'news';
    count?: number;
    sector?: string;
    category?: string;
    source?: string;
  }) => api.post('/content/generate-titles', data),
  
  // Title management
  saveTitle: (data: {
    source_type: string;
    topic: string;
    title: string;
    filter_sector?: string;
    filter_category?: string;
    filter_source?: string;
    source_id?: number;
  }) => api.post('/content/titles/save', data),
  
  listTitles: (data: {
    source_type?: string;
    filter_sector?: string;
    filter_category?: string;
    filter_source?: string;
    topic?: string;
    is_used?: boolean;
    limit?: number;
    offset?: number;
  }) => api.post('/content/titles/list', data),
  
  // Social media content
  generateSocial: (data: {
    title_id?: number;
    title?: string;
    topic: string;
    source_type: string;
    tone?: string;
    filter_sector?: string;
    filter_category?: string;
    filter_source?: string;
  }) => api.post('/content/social/generate', data),
  
  listSocial: (data: {
    source_type?: string;
    filter_sector?: string;
    filter_category?: string;
    filter_source?: string;
    is_published?: boolean;
    limit?: number;
    offset?: number;
  }) => api.post('/content/social/list', data),
  
  // Blog content
  generateBlog: (data: {
    title_id?: number;
    title: string;
    topic: string;
    source_type: string;
    tone?: string;
    length?: string;
    filter_sector?: string;
    filter_category?: string;
    filter_source?: string;
  }) => api.post('/content/blogs/generate', data),
  
  listBlogs: (data: {
    source_type?: string;
    filter_sector?: string;
    filter_category?: string;
    filter_source?: string;
    is_published?: boolean;
    limit?: number;
    offset?: number;
  }) => api.post('/content/blogs/list', data),
};
