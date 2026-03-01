import { create } from 'zustand';
import { CartItem } from '../types';
import api from '../lib/axios';

interface CartState {
  items: CartItem[];
  loading: boolean;
  fetchCart: () => Promise<void>;
  addItem: (productId: string, quantity: number) => Promise<void>;
  removeItem: (productId: string) => Promise<void>;
  clearCart: () => Promise<void>;
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  loading: false,
  fetchCart: async () => {
    set({ loading: true });
    try {
      const { data } = await api.get('/cart');
      set({ items: data.items, loading: false });
    } catch {
      set({ loading: false });
    }
  },
  addItem: async (productId, quantity) => {
    try {
      await api.post('/cart/items', { product_id: productId, quantity });
      await get().fetchCart();
    } catch (err) {
      console.error('Failed to add item', err);
    }
  },
  removeItem: async (productId) => {
    try {
      await api.delete(`/cart/items/${productId}`);
      await get().fetchCart();
    } catch (err) {
      console.error('Failed to remove item', err);
    }
  },
  clearCart: async () => {
    try {
      await api.delete('/cart');
      set({ items: [] });
    } catch (err) {
      console.error('Failed to clear cart', err);
    }
  },
}));
