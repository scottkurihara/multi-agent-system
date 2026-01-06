'use client';

import { useState, useEffect, useRef } from 'react';
import {
  ApprovalCard,
  EditableValue,
  DocumentViewer,
  OptionsSelector,
  ResearchSummary,
  TodoManager,
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
  const [showTodoManager, setShowTodoManager] = useState(false);
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
    setEvents([
      {
        type: 'user_message',
        message: userTask,
      },
    ]);
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
      case 'started':
        return '🚀';
      case 'thinking':
        return '🤔';
      case 'plan_created':
        return '📋';
      case 'routing':
        return '🔄';
      case 'agent_working':
        return '⚙️';
      case 'agent_completed':
        return '✅';
      case 'tool_call':
        return '🎨';
      case 'finalizing':
        return '🎯';
      case 'done':
        return '🎉';
      default:
        return '•';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'started':
        return '#3b82f6';
      case 'thinking':
        return '#8b5cf6';
      case 'plan_created':
        return '#10b981';
      case 'routing':
        return '#f59e0b';
      case 'agent_working':
        return '#06b6d4';
      case 'agent_completed':
        return '#059669';
      case 'tool_call':
        return '#8b5cf6';
      case 'finalizing':
        return '#ec4899';
      case 'done':
        return '#10b981';
      default:
        return '#6b7280';
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
        return <ResearchSummary title={event.args.title} findings={event.args.findings} />;
      default:
        return null;
    }
  };

  return (
    <main style={styles.main}>
      {showTodoManager ? (
        <TodoManager onClose={() => setShowTodoManager(false)} />
      ) : (
        <div style={styles.chatContainer}>
          {/* Header */}
          <div style={styles.header}>
            <div style={styles.headerDecor}></div>
            <div style={styles.headerContent}>
              <div>
                <h1 style={styles.title}>Multi-Agent System</h1>
                <p style={styles.subtitle}>[ AI agents working together ]</p>
              </div>
              <button
                onClick={() => setShowTodoManager(true)}
                style={styles.todoButton}
                title="Open Task Manager"
              >
                📋
              </button>
            </div>
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
              const isSystemMessage = [
                'started',
                'thinking',
                'routing',
                'agent_working',
                'finalizing',
              ].includes(event.type);
              const isResult = event.type === 'done';
              const isUserMessage = event.type === 'user_message';

              if (isUserMessage) {
                return (
                  <div key={idx} style={styles.userMessage}>
                    <div style={styles.userBubble}>{event.message}</div>
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
            <div style={styles.inputHint}>Press Enter to send, Shift+Enter for new line</div>
          </div>
        </div>
      )}
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  main: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: 'linear-gradient(165deg, #0a0e1a 0%, #1a1f2e 100%)',
    fontFamily: '"Manrope", system-ui, sans-serif',
    overflow: 'hidden',
    position: 'relative',
  },
  chatContainer: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '1400px',
    margin: '0 auto',
    width: '100%',
    background: 'transparent',
    position: 'relative',
    zIndex: 1,
  },
  header: {
    padding: '2rem 3rem',
    borderBottom: '2px solid rgba(0, 245, 212, 0.2)',
    background:
      'linear-gradient(135deg, rgba(0, 245, 212, 0.05) 0%, rgba(254, 228, 64, 0.05) 100%)',
    backdropFilter: 'blur(10px)',
    position: 'relative',
    overflow: 'hidden',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    position: 'relative',
    zIndex: 2,
  },
  todoButton: {
    width: '56px',
    height: '56px',
    fontSize: '1.75rem',
    background: 'rgba(0, 245, 212, 0.1)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: '800',
    margin: 0,
    fontFamily: '"Syne", sans-serif',
    letterSpacing: '-0.02em',
    background: 'linear-gradient(135deg, #00f5d4 0%, #fee440 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    textTransform: 'uppercase',
  },
  subtitle: {
    fontSize: '0.875rem',
    margin: '0.5rem 0 0 0',
    color: '#8892a6',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.05em',
  },
  headerDecor: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: '200px',
    height: '100%',
    background: 'linear-gradient(135deg, rgba(254, 228, 64, 0.1) 0%, transparent 50%)',
    clipPath: 'polygon(0 0, 100% 0, 100% 100%, 50% 100%)',
    pointerEvents: 'none',
  },
  messagesArea: {
    flex: 1,
    overflowY: 'auto',
    padding: '3rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
    background: 'transparent',
    position: 'relative',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#8892a6',
  },
  emptyIcon: {
    fontSize: '5rem',
    marginBottom: '1.5rem',
    filter: 'grayscale(1) opacity(0.3)',
  },
  emptyText: {
    fontSize: '1.5rem',
    fontWeight: '700',
    margin: '0 0 0.5rem 0',
    fontFamily: '"Syne", sans-serif',
    color: '#e8ecf4',
    letterSpacing: '-0.01em',
  },
  emptyHint: {
    fontSize: '0.875rem',
    margin: 0,
    fontFamily: '"JetBrains Mono", monospace',
    color: '#8892a6',
    letterSpacing: '0.02em',
  },
  systemMessage: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.75rem',
    padding: '0.75rem 1.5rem',
    fontSize: '0.8rem',
    color: '#8892a6',
    alignSelf: 'center',
    background: 'rgba(0, 245, 212, 0.05)',
    border: '1px solid rgba(0, 245, 212, 0.2)',
    maxWidth: '80%',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.02em',
  },
  systemIcon: {
    fontSize: '1.2rem',
    filter: 'grayscale(0.5)',
  },
  systemText: {
    fontStyle: 'normal',
  },
  userMessage: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'flex-start',
    alignSelf: 'flex-end',
    maxWidth: '75%',
    position: 'relative',
  },
  userBubble: {
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    color: '#0a0e1a',
    padding: '1.25rem 1.5rem',
    fontSize: '1rem',
    lineHeight: '1.6',
    boxShadow: '0 8px 24px rgba(0, 245, 212, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
    fontWeight: '500',
    clipPath: 'polygon(0 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%)',
    position: 'relative',
  },
  userAvatar: {
    width: '48px',
    height: '48px',
    background: 'rgba(254, 228, 64, 0.15)',
    border: '2px solid #fee440',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.5rem',
    flexShrink: 0,
    clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
  },
  agentMessage: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'flex-start',
    alignSelf: 'flex-start',
    maxWidth: '75%',
    position: 'relative',
  },
  agentAvatar: {
    width: '48px',
    height: '48px',
    background: 'linear-gradient(135deg, rgba(0, 245, 212, 0.2) 0%, rgba(0, 245, 212, 0.05) 100%)',
    border: '2px solid #00f5d4',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.5rem',
    flexShrink: 0,
    clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
  },
  agentBubble: {
    background: 'rgba(26, 31, 46, 0.8)',
    padding: '1.25rem 1.5rem',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(0, 245, 212, 0.1)',
    border: '1px solid rgba(0, 245, 212, 0.2)',
    backdropFilter: 'blur(10px)',
    clipPath: 'polygon(12px 0, 100% 0, 100% 100%, 0 100%, 0 12px)',
  },
  agentName: {
    fontSize: '0.7rem',
    fontWeight: '700',
    color: '#00f5d4',
    marginBottom: '0.5rem',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    fontFamily: '"JetBrains Mono", monospace',
  },
  agentText: {
    fontSize: '1rem',
    color: '#e8ecf4',
    lineHeight: '1.6',
  },
  toolCallMessage: {
    alignSelf: 'flex-start',
    maxWidth: '90%',
    marginLeft: '4rem',
  },
  finalMessage: {
    display: 'flex',
    gap: '1.5rem',
    padding: '2rem',
    background:
      'linear-gradient(135deg, rgba(254, 228, 64, 0.15) 0%, rgba(0, 245, 212, 0.15) 100%)',
    border: '2px solid #fee440',
    alignItems: 'flex-start',
    clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 0 100%)',
    position: 'relative',
  },
  finalIcon: {
    fontSize: '2.5rem',
    filter: 'drop-shadow(0 0 8px rgba(254, 228, 64, 0.5))',
  },
  finalContent: {
    flex: 1,
  },
  finalTitle: {
    fontSize: '1.25rem',
    fontWeight: '700',
    color: '#fee440',
    marginBottom: '0.75rem',
    fontFamily: '"Syne", sans-serif',
    letterSpacing: '-0.01em',
    textTransform: 'uppercase',
  },
  finalText: {
    fontSize: '1rem',
    color: '#e8ecf4',
    lineHeight: '1.7',
  },
  errorMessage: {
    padding: '1.5rem',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '2px solid #ef4444',
    color: '#fca5a5',
    alignSelf: 'center',
    maxWidth: '80%',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.875rem',
  },
  inputArea: {
    padding: '1.5rem 3rem 2rem 3rem',
    borderTop: '2px solid rgba(0, 245, 212, 0.2)',
    background: 'rgba(26, 31, 46, 0.6)',
    backdropFilter: 'blur(10px)',
  },
  inputForm: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    padding: '1rem 1.5rem',
    fontSize: '1rem',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    background: 'rgba(26, 31, 46, 0.8)',
    color: '#e8ecf4',
    fontFamily: 'inherit',
    resize: 'none',
    outline: 'none',
    maxHeight: '120px',
    transition: 'all 0.3s',
    clipPath: 'polygon(12px 0, 100% 0, 100% 100%, 0 100%, 0 12px)',
  },
  sendButton: {
    width: '56px',
    height: '56px',
    fontSize: '1.75rem',
    background: 'linear-gradient(135deg, #00f5d4 0%, #fee440 100%)',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    flexShrink: 0,
    clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
    boxShadow: '0 4px 12px rgba(0, 245, 212, 0.4)',
  },
  sendButtonDisabled: {
    opacity: 0.3,
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  inputHint: {
    fontSize: '0.7rem',
    color: '#8892a6',
    textAlign: 'center',
    marginTop: '0.75rem',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  },
};
