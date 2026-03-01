import { create } from 'zustand';
import { User } from '../types';
import api from '../lib/axios';
import { userApi } from '../services/api';

interface AuthState {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  fetchMe: () => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: { name?: string }) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  setUser: (user) => set({ user }),
  fetchMe: async () => {
    set({ loading: true });
    try {
      const { data } = await api.get('/auth/me');
      set({ user: data, loading: false });
    } catch (error: any) {
      // Only set user to null if it's a 401 error
      if (error.response?.status === 401) {
        set({ user: null, loading: false });
      } else {
        // For other errors, keep the current user state but stop loading
        set({ loading: false });
      }
    }
  },
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (err) {
      // Silent fail for logout
    } finally {
      set({ user: null });
    }
  },
  updateProfile: async (data) => {
    const response = await userApi.updateMe(data);
    set({ user: response.data });
  },
}));