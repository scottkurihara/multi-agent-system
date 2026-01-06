'use client';

import { useState, useEffect, useRef } from 'react';

interface Todo {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  completed: boolean;
  created_at: string;
}

interface Message {
  id: number;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
}

interface TaskChatViewProps {
  task: Todo;
  onBack: () => void;
  onTaskUpdate: () => void;
}

export default function TaskChatView({ task, onBack, onTaskUpdate }: TaskChatViewProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages();
  }, [task.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = () => {
    const stored = localStorage.getItem(`task_messages_${task.id}`);
    if (stored) {
      setMessages(JSON.parse(stored));
    }
  };

  const saveMessages = (msgs: Message[]) => {
    localStorage.setItem(`task_messages_${task.id}`, JSON.stringify(msgs));
  };

  const sendMessage = async () => {
    if (isTyping || !inputText.trim()) return;

    const text = inputText.trim();
    const newMessage: Message = {
      id: Date.now(),
      sender: 'user',
      text: text,
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    saveMessages(updatedMessages);
    setInputText('');

    // Simulate agent response
    simulateAgentResponse(text, updatedMessages);
  };

  const simulateAgentResponse = async (userMessage: string, currentMessages: Message[]) => {
    setIsTyping(true);

    // Simulate delay
    await new Promise((resolve) => setTimeout(resolve, 1500 + Math.random() * 1000));

    const response = generateAgentResponse(userMessage);
    const agentMessage: Message = {
      id: Date.now(),
      sender: 'agent',
      text: response,
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...currentMessages, agentMessage];
    setMessages(updatedMessages);
    saveMessages(updatedMessages);
    setIsTyping(false);
  };

  const generateAgentResponse = (userMessage: string): string => {
    const lower = userMessage.toLowerCase();

    if (lower.includes('help') || lower.includes('how') || lower.includes('what')) {
      return `I'm here to help you with "${task.title}". I can assist with breaking down the task into smaller steps, providing guidance, or answering questions. What specific aspect would you like to work on?`;
    }

    if (lower.includes('start') || lower.includes('begin')) {
      return `Great! Let's get started on "${task.title}". First, let's identify the key requirements and create an action plan. What's the most important outcome you want to achieve?`;
    }

    if (lower.includes('done') || lower.includes('complete') || lower.includes('finish')) {
      return `Excellent work on making progress! Before marking "${task.title}" as complete, let's verify everything is done:\n\n✓ Have you tested the implementation?\n✓ Is documentation updated?\n✓ Are all requirements met?\n\nLet me know if you need help with any of these steps.`;
    }

    if (
      lower.includes('stuck') ||
      lower.includes('problem') ||
      lower.includes('issue') ||
      lower.includes('error')
    ) {
      return `I understand you're facing a challenge with "${task.title}". Let's troubleshoot this together. Can you describe the specific issue you're encountering? The more details you provide, the better I can assist you.`;
    }

    if (lower.includes('thank')) {
      return `You're welcome! I'm always here to help you with "${task.title}". Feel free to ask me anything else!`;
    }

    if (lower.includes('break') || lower.includes('step')) {
      return `Let me break down "${task.title}" into manageable steps:\n\n1. Research and gather requirements\n2. Plan the implementation approach\n3. Execute the core functionality\n4. Test and validate results\n5. Document and finalize\n\nWhich step would you like to focus on first?`;
    }

    return `I'm here to assist you with "${task.title}". I can help you:\n\n• Break down the task into smaller steps\n• Provide implementation guidance\n• Answer specific questions\n• Review your progress\n\nWhat would you like to work on?`;
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

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div style={styles.container}>
      {/* Back Button */}
      <button onClick={onBack} style={styles.backBtn}>
        ← Back to Tasks
      </button>

      {/* Task Header */}
      <div style={styles.chatHeader}>
        <div style={styles.chatTaskTitle}>{task.title}</div>
        <div style={styles.chatTaskMeta}>
          <span
            style={{
              ...styles.statusBadge,
              ...(task.completed ? styles.statusBadgeCompleted : styles.statusBadgeActive),
            }}
          >
            {task.completed ? '✓ Completed' : '⏱ Active'}
          </span>
          <span>Created {formatDate(task.created_at)}</span>
          <span>ID: {task.id}</span>
        </div>
      </div>

      {/* Chat Container */}
      <div style={styles.chatContainer}>
        <div style={styles.chatMessages}>
          {messages.length === 0 ? (
            <div style={styles.emptyChat}>
              <div style={styles.emptyChatIcon}>💬</div>
              <div style={styles.emptyChatText}>Start a conversation</div>
              <div style={styles.emptyChatSubtext}>Ask the agent anything about this task</div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    ...styles.message,
                    ...(msg.sender === 'user' ? styles.messageUser : {}),
                  }}
                >
                  <div
                    style={{
                      ...styles.messageAvatar,
                      ...(msg.sender === 'agent'
                        ? styles.messageAvatarAgent
                        : styles.messageAvatarUser),
                    }}
                  >
                    {msg.sender === 'agent' ? '🤖' : '👤'}
                  </div>
                  <div style={styles.messageContent}>
                    <div style={styles.messageSender}>
                      {msg.sender === 'agent' ? 'Task Agent' : 'You'}
                    </div>
                    <div
                      style={{
                        ...styles.messageText,
                        ...(msg.sender === 'agent' ? styles.messageTextAgent : {}),
                      }}
                    >
                      {msg.text.split('\n').map((line, i) => (
                        <span key={i}>
                          {line}
                          {i < msg.text.split('\n').length - 1 && <br />}
                        </span>
                      ))}
                    </div>
                    <div style={styles.messageTime}>{formatTime(msg.timestamp)}</div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div style={styles.message}>
                  <div style={{ ...styles.messageAvatar, ...styles.messageAvatarAgent }}>🤖</div>
                  <div style={styles.messageContent}>
                    <div style={styles.messageSender}>Task Agent</div>
                    <div style={styles.typingIndicator}>
                      <div style={styles.typingDot}></div>
                      <div style={{ ...styles.typingDot, animationDelay: '0.2s' }}></div>
                      <div style={{ ...styles.typingDot, animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Container */}
        <div style={styles.chatInputContainer}>
          <div style={styles.chatInputGroup}>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Type your message..."
              style={styles.chatInput}
              disabled={isTyping}
              rows={1}
            />
            <button
              onClick={sendMessage}
              style={styles.sendBtn}
              disabled={isTyping || !inputText.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </div>
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
  backBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
    background: 'transparent',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    borderRadius: '8px',
    padding: '0.75rem 1.25rem',
    color: '#8892a6',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.85rem',
    cursor: 'pointer',
    transition: 'all 0.3s',
    marginBottom: '2rem',
  },
  chatHeader: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    padding: '2rem',
    marginBottom: '2rem',
    position: 'relative',
    clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%)',
  },
  chatTaskTitle: {
    fontFamily: '"Syne", sans-serif',
    fontSize: '1.75rem',
    fontWeight: '700',
    marginBottom: '1rem',
    lineHeight: '1.3',
    color: '#e8ecf4',
  },
  chatTaskMeta: {
    display: 'flex',
    gap: '1.5rem',
    fontSize: '0.8rem',
    color: '#8892a6',
    fontFamily: '"JetBrains Mono", monospace',
  },
  statusBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    fontSize: '0.7rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    fontWeight: '600',
  },
  statusBadgeActive: {
    background: 'rgba(0, 245, 212, 0.1)',
    color: '#00f5d4',
    border: '2px solid rgba(0, 245, 212, 0.3)',
  },
  statusBadgeCompleted: {
    background: 'rgba(0, 212, 255, 0.1)',
    color: '#00d4ff',
    border: '2px solid rgba(0, 212, 255, 0.3)',
  },
  chatContainer: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    borderRadius: '12px',
    height: '500px',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  chatMessages: {
    flex: 1,
    padding: '2rem',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  message: {
    display: 'flex',
    gap: '1rem',
  },
  messageUser: {
    flexDirection: 'row-reverse',
  },
  messageAvatar: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1rem',
    flexShrink: 0,
  },
  messageAvatarAgent: {
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    color: '#0a0e1a',
  },
  messageAvatarUser: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
  },
  messageContent: {
    flex: 1,
    maxWidth: '70%',
  },
  messageSender: {
    fontSize: '0.75rem',
    color: '#8892a6',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: '0.5rem',
    fontFamily: '"JetBrains Mono", monospace',
  },
  messageText: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    borderRadius: '12px',
    padding: '1rem 1.25rem',
    lineHeight: '1.6',
    fontSize: '0.95rem',
    fontFamily: '"Manrope", sans-serif',
  },
  messageTextAgent: {
    background: 'rgba(10, 14, 26, 0.6)',
    borderColor: 'rgba(0, 245, 212, 0.3)',
  },
  messageTime: {
    fontSize: '0.7rem',
    color: '#8892a6',
    marginTop: '0.5rem',
    fontFamily: '"JetBrains Mono", monospace',
  },
  typingIndicator: {
    display: 'flex',
    gap: '0.5rem',
    padding: '1rem 1.25rem',
    background: 'rgba(10, 14, 26, 0.6)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    borderRadius: '12px',
    width: 'fit-content',
  },
  typingDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: '#00f5d4',
    animation: 'typingDot 1.4s infinite',
  },
  emptyChat: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#8892a6',
    textAlign: 'center',
    padding: '2rem',
  },
  emptyChatIcon: {
    fontSize: '3rem',
    marginBottom: '1rem',
    opacity: 0.3,
  },
  emptyChatText: {
    fontSize: '1.1rem',
    marginBottom: '0.5rem',
    fontFamily: '"Syne", sans-serif',
  },
  emptyChatSubtext: {
    fontSize: '0.85rem',
  },
  chatInputContainer: {
    padding: '1.5rem',
    borderTop: '2px solid rgba(0, 245, 212, 0.2)',
    background: 'rgba(10, 14, 26, 0.6)',
  },
  chatInputGroup: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'flex-end',
  },
  chatInput: {
    flex: 1,
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    borderRadius: '8px',
    padding: '1rem 1.5rem',
    color: '#e8ecf4',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.95rem',
    resize: 'none',
    minHeight: '50px',
    maxHeight: '150px',
    transition: 'all 0.3s',
  },
  sendBtn: {
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    color: '#0a0e1a',
    border: 'none',
    borderRadius: '8px',
    padding: '1rem 1.5rem',
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.9rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    whiteSpace: 'nowrap',
    textTransform: 'uppercase',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
    boxShadow: '0 4px 12px rgba(0, 245, 212, 0.3)',
  },
};
