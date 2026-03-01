import api from '../lib/axios';
// import { Product, Cart, Order, AdminStats, Review } from '../types';

export const productApi = {
  list: (params: any) => api.get('/products', { params }),
  get: (id: string) => api.get(`/products/${id}`),
  getSimilar: (id: string) => api.get(`/products/${id}/similar`),
  getCategories: () => api.get('/products/categories'),
};

export const cartApi = {
  get: () => api.get('/cart'),
  update: (productId: string, quantity: number) => api.post('/cart/items', { product_id: productId, quantity }),
  remove: (productId: string) => api.delete(`/cart/items/${productId}`),
  clear: () => api.delete('/cart'),
};

export const orderApi = {
  checkout: (data: any) => api.post('/orders/checkout', data),
  list: () => api.get('/orders'),
  get: (id: string) => api.get(`/orders/${id}`),
  cancel: (id: string) => api.post(`/orders/${id}/cancel`),
};

export const reviewApi = {
  list: (productId: string) => api.get(`/reviews/${productId}`),
  create: (data: any) => api.post('/reviews', data),
  delete: (id: string) => api.delete(`/reviews/${id}`),
};

export const userApi = {
  updateMe: (data: { name?: string }) => api.put('/auth/me', data),
};

export const wishlistApi = {
  get: () => api.get('/wishlist'),
  add: (productId: string) => api.post('/wishlist/items', { product_id: productId }),
  remove: (productId: string) => api.delete(`/wishlist/items/${productId}`),
};

export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  createProduct: (data: any) => api.post('/products', data),
  updateProduct: (id: string, data: any) => api.put(`/products/${id}`, data),
  deleteProduct: (id: string) => api.delete(`/products/${id}`),
  uploadImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/products/upload-image', formData);
  },
};
