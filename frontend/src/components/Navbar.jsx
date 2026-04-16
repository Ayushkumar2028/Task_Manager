import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LogOut, User, CheckSquare, Shield } from 'lucide-react';

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success('Logged out successfully.');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/dashboard" className="brand-link">
          <div className="brand-icon"><CheckSquare size={20} /></div>
          <span className="brand-name">TaskManager</span>
        </Link>
      </div>

      <div className="navbar-right">
        <div className="user-chip">
          <div className="user-avatar">
            {(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}
          </div>
          <div className="user-info">
            <span className="user-name">{user?.first_name || user?.username}</span>
            <span className={`role-badge ${isAdmin ? 'role-admin' : 'role-user'}`}>
              {isAdmin ? <><Shield size={10} /> Admin</> : <><User size={10} /> User</>}
            </span>
          </div>
        </div>

        <button className="btn btn-ghost btn-sm" onClick={handleLogout} title="Logout">
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
}
