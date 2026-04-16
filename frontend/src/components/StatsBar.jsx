import { CheckCircle2, Clock, PlayCircle, XCircle, ListTodo } from 'lucide-react';

const STAT_ITEMS = [
  { key: 'total',       label: 'Total',       icon: ListTodo,     color: 'stat-total'     },
  { key: 'pending',     label: 'Pending',     icon: Clock,        color: 'stat-pending'   },
  { key: 'in_progress', label: 'In Progress', icon: PlayCircle,   color: 'stat-progress'  },
  { key: 'completed',   label: 'Completed',   icon: CheckCircle2, color: 'stat-done'      },
  { key: 'cancelled',   label: 'Cancelled',   icon: XCircle,      color: 'stat-cancelled' },
];

export default function StatsBar({ stats }) {
  const byStatus = stats?.by_status || {};

  const items = [
    { ...STAT_ITEMS[0], value: stats?.total ?? 0 },
    { ...STAT_ITEMS[1], value: byStatus.pending ?? 0 },
    { ...STAT_ITEMS[2], value: byStatus.in_progress ?? 0 },
    { ...STAT_ITEMS[3], value: byStatus.completed ?? 0 },
    { ...STAT_ITEMS[4], value: byStatus.cancelled ?? 0 },
  ];

  return (
    <div className="stats-bar">
      {items.map(({ key, label, icon: Icon, color, value }) => (
        <div key={key} className={`stat-card ${color}`}>
          <div className="stat-icon"><Icon size={20} /></div>
          <div className="stat-info">
            <span className="stat-value">{value}</span>
            <span className="stat-label">{label}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
