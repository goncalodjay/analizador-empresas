'use client';
import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { apiFetch, ApiError } from './api';
import type { UserOut, UserLogin, UserCreate } from './types';

interface AuthContextType {
  user: UserOut | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const userData = await apiFetch<UserOut>('/auth/me');
      setUser(userData);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (email: string, password: string) => {
    const payload: UserLogin = { email, password };
    await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    await fetchUser();
  };

  const register = async (email: string, password: string) => {
    const payload: UserCreate = { email, password };
    await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  };

  const logout = async () => {
    await apiFetch('/auth/logout', { method: 'POST' });
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
