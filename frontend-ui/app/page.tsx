'use client';

import { useState } from 'react';

interface StreamEvent {
  type: string;
  message: string;
  agent?: string;
  plan?: any[];
  summary?: any;
  result?: any;
}

export default function Home() {
  const [task, setTask] = useState('');
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;

    setLoading(true);
    setError(null);
    setEvents([]);
    setFinalResult(null);

    try {
      const response = await fetch('/api/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task }),
      });

      if (!response.ok) {
        throw new Error('Failed to start streaming');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6);
            try {
              const event = JSON.parse(data);
              setEvents((prev) => [...prev, event]);

              if (event.type === 'done') {
                setFinalResult(event.result);
                setLoading(false);
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'started': return '🚀';
      case 'thinking': return '🤔';
      case 'plan_created': return '📋';
      case 'routing': return '🔄';
      case 'agent_working': return '⚙️';
      case 'agent_completed': return '✅';
      case 'finalizing': return '🎯';
      case 'done': return '🎉';
      default: return '•';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'started': return '#3b82f6';
      case 'thinking': return '#8b5cf6';
      case 'plan_created': return '#10b981';
      case 'routing': return '#f59e0b';
      case 'agent_working': return '#06b6d4';
      case 'agent_completed': return '#059669';
      case 'finalizing': return '#ec4899';
      case 'done': return '#10b981';
      default: return '#6b7280';
    }
  };

  return (
    <main style={styles.main}>
      <div style={styles.container}>
        <h1 style={styles.title}>Multi-Agent System</h1>
        <p style={styles.subtitle}>Watch the agents work together in real-time</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Enter your question or task here..."
            style={styles.textarea}
            rows={4}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !task.trim()}
            style={{
              ...styles.button,
              ...(loading || !task.trim() ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? 'Processing...' : 'Submit Task'}
          </button>
        </form>

        {error && (
          <div style={styles.error}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {events.length > 0 && (
          <div style={styles.eventsContainer}>
            <h2 style={styles.eventsTitle}>Real-Time Activity</h2>
            <div style={styles.eventsList}>
              {events.map((event, idx) => (
                <div
                  key={idx}
                  style={{
                    ...styles.eventItem,
                    borderLeft: `4px solid ${getEventColor(event.type)}`,
                  }}
                >
                  <div style={styles.eventHeader}>
                    <span style={styles.eventIcon}>{getEventIcon(event.type)}</span>
                    <span style={styles.eventMessage}>{event.message}</span>
                  </div>
                  {event.agent && (
                    <div style={styles.eventDetail}>
                      <strong>Agent:</strong> {event.agent}
                    </div>
                  )}
                  {event.plan && (
                    <div style={styles.eventDetail}>
                      <strong>Tasks:</strong> {event.plan.length} items
                    </div>
                  )}
                  {event.summary && (
                    <div style={styles.eventDetail}>
                      <strong>Summary:</strong> {event.summary.short_summary}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {finalResult && (
          <div style={styles.responseContainer}>
            <h2 style={styles.responseTitle}>Final Response</h2>
            <div style={styles.responseContent}>
              <p>{finalResult.output}</p>
            </div>

            {finalResult.supervisor_state?.plan && (
              <div style={styles.planContainer}>
                <h3 style={styles.planTitle}>Execution Plan</h3>
                <div style={styles.plan}>
                  {finalResult.supervisor_state.plan.map((todo: any, idx: number) => (
                    <div key={idx} style={styles.todoItem}>
                      <span style={styles.todoStatus}>{todo.status}</span>
                      <span style={styles.todoAgent}>{todo.owner_agent}</span>
                      <span style={styles.todoDescription}>{todo.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  main: {
    minHeight: '100vh',
    padding: '2rem',
    background: 'linear-gradient(to bottom, #f9fafb, #e5e7eb)',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  container: {
    maxWidth: '900px',
    margin: '0 auto',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    marginBottom: '0.5rem',
    color: '#111827',
  },
  subtitle: {
    fontSize: '1.125rem',
    color: '#6b7280',
    marginBottom: '2rem',
  },
  form: {
    marginBottom: '2rem',
  },
  textarea: {
    width: '100%',
    padding: '1rem',
    fontSize: '1rem',
    border: '2px solid #d1d5db',
    borderRadius: '8px',
    marginBottom: '1rem',
    fontFamily: 'inherit',
    resize: 'vertical',
    outline: 'none',
  },
  button: {
    width: '100%',
    padding: '0.875rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '600',
    color: 'white',
    background: '#3b82f6',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  buttonDisabled: {
    background: '#9ca3af',
    cursor: 'not-allowed',
  },
  error: {
    padding: '1rem',
    background: '#fee2e2',
    border: '1px solid #ef4444',
    borderRadius: '8px',
    color: '#991b1b',
    marginBottom: '1rem',
  },
  eventsContainer: {
    background: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    marginBottom: '1.5rem',
  },
  eventsTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#111827',
  },
  eventsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  eventItem: {
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '6px',
    transition: 'all 0.3s ease',
  },
  eventHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  eventIcon: {
    fontSize: '1.25rem',
  },
  eventMessage: {
    color: '#374151',
    fontWeight: '500',
    flex: 1,
  },
  eventDetail: {
    marginTop: '0.5rem',
    paddingLeft: '2rem',
    fontSize: '0.875rem',
    color: '#6b7280',
  },
  responseContainer: {
    background: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  responseTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#111827',
  },
  responseContent: {
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '8px',
    marginBottom: '1.5rem',
    lineHeight: '1.6',
  },
  planContainer: {
    marginTop: '1.5rem',
  },
  planTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    marginBottom: '0.75rem',
    color: '#374151',
  },
  plan: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  todoItem: {
    display: 'flex',
    gap: '0.75rem',
    padding: '0.75rem',
    background: '#f3f4f6',
    borderRadius: '6px',
    fontSize: '0.875rem',
  },
  todoStatus: {
    fontWeight: '600',
    color: '#059669',
    minWidth: '80px',
  },
  todoAgent: {
    color: '#3b82f6',
    fontWeight: '500',
    minWidth: '120px',
  },
  todoDescription: {
    color: '#4b5563',
    flex: 1,
  },
};
