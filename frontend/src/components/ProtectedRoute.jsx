import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/** Redirect to /login if not authenticated. */
export function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="full-spinner"><div className="spinner" /></div>;
  return user ? children : <Navigate to="/login" replace />;
}

/** Redirect to /dashboard if already authenticated. */
export function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="full-spinner"><div className="spinner" /></div>;
  return !user ? children : <Navigate to="/dashboard" replace />;
}
