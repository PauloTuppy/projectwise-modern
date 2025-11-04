import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  
  login: async (email: string, _password: string) => {
    // TODO: Implement actual login logic with password
    const mockUser: User = {
      id: '1',
      email,
      name: 'Test User',
      role: 'admin'
    };
    const mockToken = 'mock-jwt-token';
    
    localStorage.setItem('token', mockToken);
    set({ user: mockUser, token: mockToken, isAuthenticated: true });
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  setUser: (user: User) => {
    set({ user });
  }
}));
