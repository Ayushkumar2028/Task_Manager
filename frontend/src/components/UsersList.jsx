import { useState, useEffect } from 'react';
import { authAPI } from '../api/services';
import toast from 'react-hot-toast';
import { Shield, User, Loader2, Trash2 } from 'lucide-react';

export default function UsersList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await authAPI.listUsers();
      setUsers(res.data.data);
    } catch {
      toast.error('Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handlePromote = async (id) => {
    if (!window.confirm("Promote this user to Admin?")) return;
    try {
      await authAPI.promoteUser(id);
      toast.success("User promoted to Admin!");
      fetchUsers();
    } catch {
      toast.error("Failed to promote user.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this user? This cannot be undone.")) return;
    try {
      await authAPI.deleteUser(id);
      toast.success("User deleted.");
      setUsers(users.filter(u => u.id !== id));
    } catch {
      toast.error("Failed to delete user.");
    }
  };

  if (loading) {
    return <div className="loading-state"><Loader2 size={36} className="spin" /><p>Loading users...</p></div>;
  }

  return (
    <div className="users-list-wrapper">
      <div className="users-grid">
        {users.map(u => (
          <div key={u.id} className="stat-card">
            <div className={`stat-icon ${u.role === 'Admin' ? 'stat-pending' : 'stat-total'}`}>
               {u.role === 'Admin' ? <Shield size={24}/> : <User size={24}/>}
            </div>
            
            <div className="stat-info" style={{ flex: 1 }}>
              <span className="stat-value">{u.username}</span>
              <span className="stat-label">{u.email}</span>
            </div>

            <div className="task-actions" style={{ opacity: 1 }}>
               {u.role !== 'Admin' && (
                 <button className="icon-btn icon-btn-edit" onClick={() => handlePromote(u.id)} title="Promote to Admin">
                    <Shield size={16} />
                 </button>
               )}
               <button className="icon-btn icon-btn-del" onClick={() => handleDelete(u.id)} title="Delete User">
                  <Trash2 size={16} />
               </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
