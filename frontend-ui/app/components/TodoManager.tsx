'use client';

import { useState, useEffect } from 'react';
import TaskChatView from './TaskChatView';

interface Todo {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  completed: boolean;
  created_at: string;
}

interface TodoManagerProps {
  onClose?: () => void;
}

export default function TodoManager({ onClose }: TodoManagerProps) {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTaskText, setNewTaskText] = useState('');
  const [currentFilter, setCurrentFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load todos on mount
  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    try {
      const response = await fetch('/api/todos');
      if (!response.ok) throw new Error('Failed to load todos');
      const data = await response.json();
      setTodos(data.todos || []);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const addTask = async () => {
    const text = newTaskText.trim();
    if (!text) return;

    setLoading(true);
    try {
      const response = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: text,
          status: 'pending',
          completed: false,
        }),
      });

      if (!response.ok) throw new Error('Failed to create todo');

      await loadTodos();
      setNewTaskText('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleTask = async (id: number) => {
    const todo = todos.find((t) => t.id === id);
    if (!todo) return;

    try {
      const response = await fetch(`/api/todos/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          completed: !todo.completed,
          status: !todo.completed ? 'completed' : 'pending',
        }),
      });

      if (!response.ok) throw new Error('Failed to update todo');
      await loadTodos();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const deleteTask = async (id: number) => {
    try {
      const response = await fetch(`/api/todos/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete todo');
      await loadTodos();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const getFilteredTodos = () => {
    switch (currentFilter) {
      case 'active':
        return todos.filter((t) => !t.completed);
      case 'completed':
        return todos.filter((t) => t.completed);
      default:
        return todos;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
  };

  const stats = {
    total: todos.length,
    active: todos.filter((t) => !t.completed).length,
    completed: todos.filter((t) => t.completed).length,
  };

  const filteredTodos = getFilteredTodos();

  if (selectedTaskId !== null) {
    const selectedTodo = todos.find((t) => t.id === selectedTaskId);
    if (selectedTodo) {
      return (
        <TaskChatView
          task={selectedTodo}
          onBack={() => setSelectedTaskId(null)}
          onTaskUpdate={loadTodos}
        />
      );
    }
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerTop}>
          <div>
            <div style={styles.subtitle}>Task Management System</div>
            <h1 style={styles.title}>Task Archive</h1>
          </div>
          {onClose && (
            <button onClick={onClose} style={styles.closeBtn}>
              ✕
            </button>
          )}
        </div>

        <div style={styles.stats}>
          <div style={styles.stat}>
            <div style={styles.statValue}>{stats.total}</div>
            <div style={styles.statLabel}>Total</div>
          </div>
          <div style={styles.stat}>
            <div style={styles.statValue}>{stats.active}</div>
            <div style={styles.statLabel}>Active</div>
          </div>
          <div style={styles.stat}>
            <div style={styles.statValue}>{stats.completed}</div>
            <div style={styles.statLabel}>Completed</div>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div style={styles.inputSection}>
        <div style={styles.inputGroup}>
          <input
            type="text"
            value={newTaskText}
            onChange={(e) => setNewTaskText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTask()}
            placeholder="Enter a new task..."
            style={styles.input}
            disabled={loading}
          />
          <button onClick={addTask} style={styles.addBtn} disabled={loading}>
            {loading ? 'Adding...' : 'Add Task'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div style={styles.filters}>
        {(['all', 'active', 'completed'] as const).map((filter) => (
          <button
            key={filter}
            onClick={() => setCurrentFilter(filter)}
            style={{
              ...styles.filterBtn,
              ...(currentFilter === filter ? styles.filterBtnActive : {}),
            }}
          >
            {filter.charAt(0).toUpperCase() + filter.slice(1)} Tasks
          </button>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div style={styles.error}>
          {error}
          <button onClick={() => setError(null)} style={styles.errorClose}>
            ✕
          </button>
        </div>
      )}

      {/* Tasks Grid */}
      {filteredTodos.length === 0 ? (
        <div style={styles.emptyState}>
          <div style={styles.emptyIcon}>📋</div>
          <div style={styles.emptyText}>No tasks yet</div>
          <div style={styles.emptySubtext}>Add your first task to get started</div>
        </div>
      ) : (
        <div style={styles.tasksGrid}>
          {filteredTodos.map((todo) => (
            <div
              key={todo.id}
              style={{
                ...styles.taskItem,
                ...(todo.completed ? styles.taskItemCompleted : {}),
              }}
            >
              <div
                style={{
                  ...styles.taskCheckbox,
                  ...(todo.completed ? styles.taskCheckboxChecked : {}),
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleTask(todo.id);
                }}
              >
                {todo.completed && <span style={styles.checkmark}>✓</span>}
              </div>

              <div style={styles.taskContent} onClick={() => setSelectedTaskId(todo.id)}>
                <div
                  style={{
                    ...styles.taskText,
                    ...(todo.completed ? styles.taskTextCompleted : {}),
                  }}
                >
                  {todo.title}
                </div>
                <div style={styles.taskMeta}>
                  <span>⏱ {formatDate(todo.created_at)}</span>
                  <span>• ID: {todo.id}</span>
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteTask(todo.id);
                }}
                style={styles.deleteBtn}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem',
    color: '#e8ecf4',
  },
  header: {
    marginBottom: '3rem',
  },
  headerTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '2rem',
  },
  subtitle: {
    fontSize: '0.875rem',
    color: '#8892a6',
    textTransform: 'uppercase',
    letterSpacing: '0.15em',
    marginBottom: '0.5rem',
    fontFamily: '"JetBrains Mono", monospace',
  },
  title: {
    fontFamily: '"Syne", sans-serif',
    fontSize: 'clamp(2.5rem, 6vw, 4rem)',
    fontWeight: '800',
    lineHeight: '0.9',
    letterSpacing: '-0.02em',
    background: 'linear-gradient(135deg, #e8ecf4 0%, #00f5d4 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  closeBtn: {
    background: 'transparent',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    color: '#00f5d4',
    width: '40px',
    height: '40px',
    borderRadius: '8px',
    fontSize: '1.5rem',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  stats: {
    display: 'flex',
    gap: '2rem',
  },
  stat: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
  },
  statValue: {
    fontFamily: '"Syne", sans-serif',
    fontSize: '2rem',
    fontWeight: '700',
    color: '#00f5d4',
  },
  statLabel: {
    fontSize: '0.75rem',
    color: '#8892a6',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    fontFamily: '"JetBrains Mono", monospace',
  },
  inputSection: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    padding: '2rem',
    marginBottom: '2rem',
    backdropFilter: 'blur(10px)',
    clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%)',
  },
  inputGroup: {
    display: 'flex',
    gap: '1rem',
  },
  input: {
    flex: 1,
    background: 'rgba(10, 14, 26, 0.6)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    borderRadius: '8px',
    padding: '1rem 1.5rem',
    color: '#e8ecf4',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.95rem',
    transition: 'all 0.3s',
  },
  addBtn: {
    padding: '1rem 2rem',
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#0a0e1a',
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    border: '2px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.3s',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.02em',
    textTransform: 'uppercase',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
    boxShadow: '0 4px 12px rgba(0, 245, 212, 0.3)',
  },
  filters: {
    display: 'flex',
    gap: '0.75rem',
    marginBottom: '2rem',
  },
  filterBtn: {
    background: 'transparent',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    borderRadius: '20px',
    padding: '0.5rem 1.25rem',
    color: '#8892a6',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.8rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  filterBtnActive: {
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    borderColor: '#00f5d4',
    color: '#0a0e1a',
    boxShadow: '0 4px 12px rgba(0, 245, 212, 0.3)',
  },
  error: {
    background: 'rgba(254, 68, 68, 0.1)',
    border: '2px solid rgba(254, 68, 68, 0.3)',
    padding: '1rem 1.5rem',
    marginBottom: '2rem',
    color: '#fe4444',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.875rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
  },
  errorClose: {
    background: 'transparent',
    border: 'none',
    color: '#fe4444',
    cursor: 'pointer',
    fontSize: '1.25rem',
  },
  tasksGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  taskItem: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    padding: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
    transition: 'all 0.3s',
    position: 'relative',
    clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%)',
    cursor: 'pointer',
  },
  taskItemCompleted: {
    opacity: 0.5,
  },
  taskCheckbox: {
    width: '24px',
    height: '24px',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    borderRadius: '6px',
    cursor: 'pointer',
    position: 'relative',
    transition: 'all 0.3s',
    flexShrink: 0,
  },
  taskCheckboxChecked: {
    background: '#00f5d4',
    borderColor: '#00f5d4',
  },
  checkmark: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    color: '#0a0e1a',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  taskContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  taskText: {
    fontSize: '1rem',
    color: '#e8ecf4',
    lineHeight: '1.5',
    fontFamily: '"Manrope", sans-serif',
  },
  taskTextCompleted: {
    textDecoration: 'line-through',
    color: '#8892a6',
  },
  taskMeta: {
    display: 'flex',
    gap: '1rem',
    fontSize: '0.75rem',
    color: '#8892a6',
    fontFamily: '"JetBrains Mono", monospace',
  },
  deleteBtn: {
    background: 'rgba(254, 68, 68, 0.1)',
    border: '2px solid rgba(254, 68, 68, 0.3)',
    borderRadius: '6px',
    padding: '0.5rem 0.75rem',
    color: '#fe4444',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.75rem',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textTransform: 'uppercase',
  },
  emptyState: {
    textAlign: 'center',
    padding: '4rem 2rem',
    color: '#8892a6',
  },
  emptyIcon: {
    fontSize: '4rem',
    marginBottom: '1rem',
    opacity: 0.3,
  },
  emptyText: {
    fontFamily: '"Syne", sans-serif',
    fontSize: '1.5rem',
    marginBottom: '0.5rem',
  },
  emptySubtext: {
    fontSize: '0.9rem',
  },
};
