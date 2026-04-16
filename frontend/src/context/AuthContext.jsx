/**
 * AuthContext — global authentication state management.
 * Provides user info, login/logout functions, and loading state to the app.
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../api/services';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // true during initial token validation

  // On mount, validate stored token by fetching profile
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      authAPI.getProfile()
        .then((res) => setUser(res.data.data))
        .catch(() => {
          localStorage.clear();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (credentials) => {
    const res = await authAPI.login(credentials);
    const { access, refresh, user: userData } = res.data.data;
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(async () => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      if (refresh) await authAPI.logout(refresh);
    } catch (_) { /* ignore errors */ }
    localStorage.clear();
    setUser(null);
  }, []);

  const isAdmin = user?.role === 'Admin';

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAdmin, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
