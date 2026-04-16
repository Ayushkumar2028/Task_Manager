import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { tasksAPI } from '../api/services';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import TaskCard from '../components/TaskCard';
import TaskModal from '../components/TaskModal';
import StatsBar from '../components/StatsBar';
import UsersList from '../components/UsersList';
import {
  Plus, Search, Filter, ListTodo, Loader2, RefreshCw, LayoutGrid, Users
} from 'lucide-react';

const STATUS_OPTIONS = ['', 'pending', 'in_progress', 'completed', 'cancelled'];
const PRIORITY_OPTIONS = ['', 'low', 'medium', 'high', 'urgent'];

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'
  const [activeTab, setActiveTab] = useState('tasks'); // 'tasks' | 'users'

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      const res = await tasksAPI.list(params);
      setTasks(res.data.data.tasks);
    } catch {
      toast.error('Failed to load tasks.');
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, priorityFilter]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await tasksAPI.getStats();
      setStats(res.data.data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    fetchTasks();
    fetchStats();
  }, [fetchTasks, fetchStats]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => fetchTasks(), 400);
    return () => clearTimeout(timer);
  }, [search]); // eslint-disable-line

  const handleCreate = () => { setEditingTask(null); setModalOpen(true); };
  const handleEdit = (task) => { setEditingTask(task); setModalOpen(true); };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this task?')) return;
    try {
      await tasksAPI.delete(id);
      toast.success('Task deleted.');
      setTasks((prev) => prev.filter((t) => t.id !== id));
      fetchStats();
    } catch {
      toast.error('Failed to delete task.');
    }
  };

  const handleSaved = (saved, isNew) => {
    if (isNew) {
      setTasks((prev) => [saved, ...prev]);
    } else {
      setTasks((prev) => prev.map((t) => (t.id === saved.id ? saved : t)));
    }
    fetchStats();
    setModalOpen(false);
  };

  return (
    <div className="dashboard-layout">
      <Navbar />

      <main className="dashboard-main">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">
              {isAdmin ? 'Admin Dashboard' : 'My Tasks'}
            </h1>
            <p className="dashboard-subtitle">
              Welcome back, <strong>{user?.first_name || user?.username}</strong>
              {isAdmin && <span className="badge badge-admin">Admin</span>}
            </p>
          </div>
          {activeTab === 'tasks' && (
            <button className="btn btn-primary" onClick={handleCreate}>
              <Plus size={18} /> New Task
            </button>
          )}
        </div>

        {isAdmin && (
          <div className="tabs-bar">
            <button 
              className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
              onClick={() => setActiveTab('tasks')}
            >
              <ListTodo size={16} /> Tasks
            </button>
            <button 
              className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              <Users size={16} /> Manage Users
            </button>
          </div>
        )}

        {/* Content */}
        {activeTab === 'tasks' ? (
          <>
            {stats && <StatsBar stats={stats} />}

            <div className="filters-bar">
              <div className="search-wrapper">
                <Search size={16} className="search-icon" />
                <input
                  type="text" placeholder="Search tasks…"
                  value={search} onChange={(e) => setSearch(e.target.value)}
                  className="search-input"
                />
              </div>

              <div className="filter-group">
                <Filter size={15} />
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="filter-select">
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s ? s.replace('_', ' ') : 'All Status'}</option>
                  ))}
                </select>

                <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)} className="filter-select">
                  {PRIORITY_OPTIONS.map((p) => (
                    <option key={p} value={p}>{p ? p : 'All Priority'}</option>
                  ))}
                </select>
              </div>

              <div className="view-toggle">
                <button
                  className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                  onClick={() => setViewMode('grid')} title="Grid view"
                >
                  <LayoutGrid size={16} />
                </button>
                <button
                  className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                  onClick={() => setViewMode('list')} title="List view"
                >
                  <ListTodo size={16} />
                </button>
                <button className="view-btn" onClick={fetchTasks} title="Refresh">
                  <RefreshCw size={16} />
                </button>
              </div>
            </div>

            {loading ? (
              <div className="loading-state">
                <Loader2 size={36} className="spin" />
                <p>Loading tasks…</p>
              </div>
            ) : tasks.length === 0 ? (
              <div className="empty-state">
                <ListTodo size={56} />
                <h3>No tasks found</h3>
                <p>
                  {search || statusFilter || priorityFilter
                    ? 'Try adjusting your filters.'
                    : 'Create your first task to get started!'}
                </p>
                <button className="btn btn-primary" onClick={handleCreate}>
                  <Plus size={16} /> Create Task
                </button>
              </div>
            ) : (
              <div className={`tasks-container ${viewMode === 'list' ? 'tasks-list' : 'tasks-grid'}`}>
                {tasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    isAdmin={isAdmin}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    viewMode={viewMode}
                  />
                ))}
              </div>
            )}
          </>
        ) : (
          <UsersList />
        )}
      </main>

      {modalOpen && (
        <TaskModal
          task={editingTask}
          onClose={() => setModalOpen(false)}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
}
