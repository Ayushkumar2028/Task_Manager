import { Pencil, Trash2, Calendar, AlertTriangle, User } from 'lucide-react';

const STATUS_META = {
  pending:     { label: 'Pending',     cls: 'status-pending'   },
  in_progress: { label: 'In Progress', cls: 'status-progress'  },
  completed:   { label: 'Completed',   cls: 'status-done'      },
  cancelled:   { label: 'Cancelled',   cls: 'status-cancelled' },
};

const PRIORITY_META = {
  low:    { label: 'Low',    cls: 'priority-low'    },
  medium: { label: 'Medium', cls: 'priority-medium' },
  high:   { label: 'High',   cls: 'priority-high'   },
  urgent: { label: 'Urgent', cls: 'priority-urgent' },
};

export default function TaskCard({ task, isAdmin, onEdit, onDelete, viewMode }) {
  const status   = STATUS_META[task.status]   || { label: task.status,   cls: '' };
  const priority = PRIORITY_META[task.priority] || { label: task.priority, cls: '' };

  return (
    <div className={`task-card ${viewMode === 'list' ? 'task-card-list' : ''} ${task.is_overdue ? 'task-overdue' : ''}`}>
      {/* Priority strip */}
      <div className={`priority-strip ${priority.cls}`} />

      <div className="task-body">
        <div className="task-top">
          <div className="task-badges">
            <span className={`badge ${status.cls}`}>{status.label}</span>
            <span className={`badge ${priority.cls}`}>{priority.label}</span>
            {task.is_overdue && (
              <span className="badge badge-overdue">
                <AlertTriangle size={11} /> Overdue
              </span>
            )}
          </div>
          <div className="task-actions">
            <button className="icon-btn icon-btn-edit" onClick={() => onEdit(task)} title="Edit">
              <Pencil size={14} />
            </button>
            <button className="icon-btn icon-btn-del" onClick={() => onDelete(task.id)} title="Delete">
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        <h3 className="task-title">{task.title}</h3>

        {task.description && viewMode !== 'list' && (
          <p className="task-desc">{task.description}</p>
        )}

        <div className="task-meta">
          {task.due_date && (
            <span className={`meta-item ${task.is_overdue ? 'meta-overdue' : ''}`}>
              <Calendar size={12} />
              {new Date(task.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          )}
          {isAdmin && (
            <span className="meta-item">
              <User size={12} />
              {task.owner_username}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
