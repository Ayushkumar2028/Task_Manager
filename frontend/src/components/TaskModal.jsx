import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { tasksAPI, authAPI } from '../api/services';
import toast from 'react-hot-toast';
import { X, Save, Loader2, Plus, User } from 'lucide-react';

export default function TaskModal({ task, onClose, onSaved }) {
  const { isAdmin, user: currentUser } = useAuth();
  const isEdit = !!task;
  
  const EMPTY_FORM = {
    title: '', description: '', status: 'pending',
    priority: 'medium', due_date: '', user: currentUser?.id || ''
  };

  const [form, setForm] = useState(isEdit ? {
    title:       task.title,
    description: task.description || '',
    status:      task.status,
    priority:    task.priority,
    due_date:    task.due_date || '',
    user:        task.user || currentUser?.id || ''
  } : EMPTY_FORM);

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [usersList, setUsersList] = useState([]);

  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Fetch users if admin
  useEffect(() => {
    if (isAdmin) {
      authAPI.listUsers()
        .then(res => setUsersList(res.data.data))
        .catch(() => toast.error('Failed to load users list'));
    }
  }, [isAdmin]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    // Build payload — omit empty due_date
    const payload = { ...form };
    if (!payload.due_date) delete payload.due_date;
    // Don't send user ID if not admin
    if (!isAdmin) delete payload.user;

    try {
      let res;
      if (isEdit) {
        res = await tasksAPI.update(task.id, payload);
        toast.success('Task updated!');
      } else {
        res = await tasksAPI.create(payload);
        toast.success('Task created!');
      }
      onSaved(res.data.data, !isEdit);
    } catch (err) {
      const data = err.response?.data;
      if (data?.errors && Object.keys(data.errors).length > 0) {
        setErrors(data.errors);
      } else {
        toast.error(data?.message || 'Failed to save task.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">
            {isEdit ? 'Edit Task' : 'Create New Task'}
          </h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {/* Title */}
          <div className="form-group">
            <label htmlFor="m-title">Title <span className="required">*</span></label>
            <input
              id="m-title" name="title" type="text" required
              placeholder="What needs to be done?"
              value={form.title} onChange={handleChange}
              className={errors.title ? 'error' : ''}
            />
            {errors.title && <span className="field-error">{Array.isArray(errors.title) ? errors.title[0] : errors.title}</span>}
          </div>

          {/* Admin Assign User */}
          {isAdmin && (
            <div className="form-group">
              <label htmlFor="m-user">Assign To <span className="required">*</span></label>
              <div className="input-wrapper">
                <select 
                  id="m-user" name="user" 
                  value={form.user} onChange={handleChange}
                  required
                >
                  <option value="">Select a user...</option>
                  {usersList.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.username} ({u.role})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Description */}
          <div className="form-group">
            <label htmlFor="m-desc">Description</label>
            <textarea
              id="m-desc" name="description" rows={3}
              placeholder="Optional details about the task…"
              value={form.description} onChange={handleChange}
            />
          </div>

          {/* Status + Priority */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="m-status">Status</label>
              <select id="m-status" name="status" value={form.status} onChange={handleChange}>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="m-priority">Priority</label>
              <select id="m-priority" name="priority" value={form.priority} onChange={handleChange}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          {/* Due Date */}
          <div className="form-group">
            <label htmlFor="m-due">Due Date</label>
            <input
              id="m-due" name="due_date" type="date"
              value={form.due_date} onChange={handleChange}
              min={new Date().toISOString().split('T')[0]}
              className={errors.due_date ? 'error' : ''}
            />
            {errors.due_date && <span className="field-error">{Array.isArray(errors.due_date) ? errors.due_date[0] : errors.due_date}</span>}
          </div>

          {/* Footer */}
          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading
                ? <><Loader2 size={16} className="spin" /> Saving…</>
                : isEdit
                  ? <><Save size={16} /> Update Task</>
                  : <><Plus size={16} /> Create Task</>
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
