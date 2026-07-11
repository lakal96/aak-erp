import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

const useAuthStore = create((set) => ({
  isAuthenticated: false,
  user: null,

  login: async ({ api_key, api_secret, user }) => {
    await SecureStore.setItemAsync('api_key', api_key);
    await SecureStore.setItemAsync('api_secret', api_secret);
    set({ isAuthenticated: true, user });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('api_key');
    await SecureStore.deleteItemAsync('api_secret');
    set({ isAuthenticated: false, user: null });
  },

  // Restore session on app start
  restoreSession: async () => {
    const api_key = await SecureStore.getItemAsync('api_key');
    const api_secret = await SecureStore.getItemAsync('api_secret');
    if (api_key && api_secret) {
      try {
        const { getCurrentUser } = require('../services/api');
        const user = await getCurrentUser();
        set({ isAuthenticated: true, user });
      } catch {
        // Token invalid — clear and force re-login
        await SecureStore.deleteItemAsync('api_key');
        await SecureStore.deleteItemAsync('api_secret');
      }
    }
  },
}));

export default useAuthStore;
