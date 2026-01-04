'use client';

import { useState, useEffect, useRef } from 'react';
import {
  ApprovalCard,
  EditableValue,
  DocumentViewer,
  OptionsSelector,
  ResearchSummary,
} from './components';

interface StreamEvent {
  type: string;
  message: string;
  agent?: string;
  plan?: any[];
  summary?: any;
  result?: any;
  tool?: string;
  args?: any;
  tool_call_id?: string;
}

export default function Home() {
  const [task, setTask] = useState('');
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [events]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;

    const userTask = task;
    setTask(''); // Clear input immediately
    setLoading(true);
    setError(null);
    setEvents([{
      type: 'user_message',
      message: userTask,
    }]);
    setFinalResult(null);

    try {
      const response = await fetch('/api/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task: userTask }),
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
      case 'tool_call': return '🎨';
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
      case 'tool_call': return '#8b5cf6';
      case 'finalizing': return '#ec4899';
      case 'done': return '#10b981';
      default: return '#6b7280';
    }
  };

  const handleToolResponse = async (toolCallId: string, response: any) => {
    // In a full implementation, this would send the response back to the backend
    // For now, we'll just log it
    console.log('Tool response:', { toolCallId, response });
    // TODO: Send response back to backend to continue agent execution
  };

  const renderToolCall = (event: StreamEvent) => {
    if (!event.tool || !event.args) return null;

    const commonProps = {
      onResponse: (response: any) => handleToolResponse(event.tool_call_id || '', response),
      onSelect: (response: any) => handleToolResponse(event.tool_call_id || '', response),
      onSave: (response: any) => handleToolResponse(event.tool_call_id || '', response),
    };

    switch (event.tool) {
      case 'show_approval_card':
        return (
          <ApprovalCard
            title={event.args.title}
            description={event.args.description}
            options={event.args.options}
            onResponse={commonProps.onResponse}
          />
        );
      case 'show_editable_value':
        return (
          <EditableValue
            label={event.args.label}
            value={event.args.value}
            field_type={event.args.field_type}
            onSave={commonProps.onSave}
          />
        );
      case 'show_document':
        return (
          <DocumentViewer
            title={event.args.title}
            content={event.args.content}
            metadata={event.args.metadata}
          />
        );
      case 'show_options':
        return (
          <OptionsSelector
            question={event.args.question}
            options={event.args.options}
            onSelect={commonProps.onSelect}
          />
        );
      case 'show_research_summary':
        return (
          <ResearchSummary
            title={event.args.title}
            findings={event.args.findings}
          />
        );
      default:
        return null;
    }
  };

  return (
    <main style={styles.main}>
      <div style={styles.chatContainer}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>Multi-Agent System</h1>
          <p style={styles.subtitle}>AI agents working together</p>
        </div>

        {/* Messages Area */}
        <div style={styles.messagesArea}>
          {events.length === 0 && !finalResult && (
            <div style={styles.emptyState}>
              <div style={styles.emptyIcon}>💬</div>
              <p style={styles.emptyText}>Start a conversation with the multi-agent system</p>
              <p style={styles.emptyHint}>Ask a question or describe a task below</p>
            </div>
          )}

          {events.map((event, idx) => {
            const isToolCall = event.type === 'tool_call';
            const isSystemMessage = ['started', 'thinking', 'routing', 'agent_working', 'finalizing'].includes(event.type);
            const isResult = event.type === 'done';
            const isUserMessage = event.type === 'user_message';

            if (isUserMessage) {
              return (
                <div key={idx} style={styles.userMessage}>
                  <div style={styles.userBubble}>
                    {event.message}
                  </div>
                  <div style={styles.userAvatar}>👤</div>
                </div>
              );
            }

            if (isToolCall) {
              return (
                <div key={idx} style={styles.toolCallMessage}>
                  {renderToolCall(event)}
                </div>
              );
            }

            if (isSystemMessage) {
              return (
                <div key={idx} style={styles.systemMessage}>
                  <span style={styles.systemIcon}>{getEventIcon(event.type)}</span>
                  <span style={styles.systemText}>{event.message}</span>
                </div>
              );
            }

            if (event.type === 'plan_created') {
              return (
                <div key={idx} style={styles.agentMessage}>
                  <div style={styles.agentAvatar}>📋</div>
                  <div style={styles.agentBubble}>
                    <div style={styles.agentName}>Supervisor</div>
                    <div style={styles.agentText}>
                      Created a plan with {event.plan?.length || 0} tasks
                    </div>
                  </div>
                </div>
              );
            }

            if (event.type === 'agent_completed' && event.summary) {
              return (
                <div key={idx} style={styles.agentMessage}>
                  <div style={styles.agentAvatar}>
                    {event.agent === 'research_agent' ? '🔍' : '⚙️'}
                  </div>
                  <div style={styles.agentBubble}>
                    <div style={styles.agentName}>
                      {event.agent === 'research_agent' ? 'Research Agent' : 'Transform Agent'}
                    </div>
                    <div style={styles.agentText}>{event.summary.short_summary}</div>
                  </div>
                </div>
              );
            }

            if (isResult && event.result) {
              return (
                <div key={idx} style={styles.finalMessage}>
                  <div style={styles.finalIcon}>🎉</div>
                  <div style={styles.finalContent}>
                    <div style={styles.finalTitle}>Task Completed</div>
                    <div style={styles.finalText}>{event.result.output}</div>
                  </div>
                </div>
              );
            }

            return null;
          })}

          {error && (
            <div style={styles.errorMessage}>
              <strong>Error:</strong> {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area at Bottom */}
        <div style={styles.inputArea}>
          <form onSubmit={handleSubmit} style={styles.inputForm}>
            <textarea
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Ask a question or describe your task..."
              style={styles.input}
              rows={1}
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={loading || !task.trim()}
              style={{
                ...styles.sendButton,
                ...(loading || !task.trim() ? styles.sendButtonDisabled : {}),
              }}
            >
              {loading ? '⏳' : '📤'}
            </button>
          </form>
          <div style={styles.inputHint}>
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  main: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: '#f5f5f5',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    overflow: 'hidden',
  },
  chatContainer: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '1200px',
    margin: '0 auto',
    width: '100%',
    background: 'white',
    boxShadow: '0 0 20px rgba(0, 0, 0, 0.1)',
  },
  header: {
    padding: '1.5rem 2rem',
    borderBottom: '1px solid #e5e7eb',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    margin: 0,
  },
  subtitle: {
    fontSize: '0.875rem',
    margin: '0.25rem 0 0 0',
    opacity: 0.9,
  },
  messagesArea: {
    flex: 1,
    overflowY: 'auto',
    padding: '2rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    background: '#fafafa',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#9ca3af',
  },
  emptyIcon: {
    fontSize: '4rem',
    marginBottom: '1rem',
  },
  emptyText: {
    fontSize: '1.25rem',
    fontWeight: '600',
    margin: '0 0 0.5rem 0',
  },
  emptyHint: {
    fontSize: '0.875rem',
    margin: 0,
  },
  systemMessage: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    color: '#6b7280',
    alignSelf: 'center',
    background: '#f3f4f6',
    borderRadius: '16px',
    maxWidth: '80%',
  },
  systemIcon: {
    fontSize: '1rem',
  },
  systemText: {
    fontStyle: 'italic',
  },
  userMessage: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'flex-start',
    alignSelf: 'flex-end',
    maxWidth: '80%',
  },
  userBubble: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '1rem',
    borderRadius: '16px',
    fontSize: '1rem',
    lineHeight: '1.5',
    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
  },
  userAvatar: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: '#e5e7eb',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.25rem',
    flexShrink: 0,
  },
  agentMessage: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'flex-start',
    alignSelf: 'flex-start',
    maxWidth: '80%',
  },
  agentAvatar: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.25rem',
    flexShrink: 0,
  },
  agentBubble: {
    background: 'white',
    padding: '1rem',
    borderRadius: '16px',
    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e5e7eb',
  },
  agentName: {
    fontSize: '0.75rem',
    fontWeight: '600',
    color: '#667eea',
    marginBottom: '0.25rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  agentText: {
    fontSize: '1rem',
    color: '#374151',
    lineHeight: '1.5',
  },
  toolCallMessage: {
    alignSelf: 'flex-start',
    maxWidth: '90%',
    marginLeft: '3.25rem',
  },
  finalMessage: {
    display: 'flex',
    gap: '1rem',
    padding: '1.5rem',
    background: 'linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)',
    borderRadius: '16px',
    alignItems: 'flex-start',
  },
  finalIcon: {
    fontSize: '2rem',
  },
  finalContent: {
    flex: 1,
  },
  finalTitle: {
    fontSize: '1.125rem',
    fontWeight: 'bold',
    color: '#065f46',
    marginBottom: '0.5rem',
  },
  finalText: {
    fontSize: '1rem',
    color: '#047857',
    lineHeight: '1.6',
  },
  errorMessage: {
    padding: '1rem',
    background: '#fee2e2',
    border: '1px solid #ef4444',
    borderRadius: '12px',
    color: '#991b1b',
    alignSelf: 'center',
    maxWidth: '80%',
  },
  inputArea: {
    padding: '1rem 2rem 1.5rem 2rem',
    borderTop: '1px solid #e5e7eb',
    background: 'white',
  },
  inputForm: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    padding: '0.875rem 1rem',
    fontSize: '1rem',
    border: '2px solid #e5e7eb',
    borderRadius: '24px',
    fontFamily: 'inherit',
    resize: 'none',
    outline: 'none',
    maxHeight: '120px',
    transition: 'border-color 0.2s',
  },
  sendButton: {
    width: '48px',
    height: '48px',
    fontSize: '1.5rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '50%',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'transform 0.2s, opacity 0.2s',
    flexShrink: 0,
  },
  sendButtonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  inputHint: {
    fontSize: '0.75rem',
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: '0.5rem',
  },
};
