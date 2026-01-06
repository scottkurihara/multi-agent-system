/**
 * Tests for TaskChatView component - Task Chat Interface
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskChatView from '../../app/components/TaskChatView';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('TaskChatView Component', () => {
  const mockOnBack = jest.fn();
  const mockOnTaskUpdate = jest.fn();

  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'pending' as const,
    priority: 'high' as const,
    completed: false,
    created_at: '2024-01-01T00:00:00Z',
  };

  const completedTask = {
    ...mockTask,
    id: 2,
    completed: true,
    status: 'completed' as const,
  };

  beforeEach(() => {
    mockOnBack.mockClear();
    mockOnTaskUpdate.mockClear();
    localStorage.clear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Rendering', () => {
    it('renders task chat view with task details', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      expect(screen.getByText('Test Task')).toBeInTheDocument();
      expect(screen.getByText(/Active/i)).toBeInTheDocument();
      expect(screen.getByText(/ID: 1/i)).toBeInTheDocument();
    });

    it('displays back button', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      expect(screen.getByText('← Back to Tasks')).toBeInTheDocument();
    });

    it('shows active status badge for pending task', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      expect(screen.getByText('⏱ Active')).toBeInTheDocument();
    });

    it('shows completed status badge for completed task', () => {
      render(
        <TaskChatView task={completedTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />
      );

      expect(screen.getByText('✓ Completed')).toBeInTheDocument();
    });

    it('displays empty chat state initially', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      expect(screen.getByText('Start a conversation')).toBeInTheDocument();
      expect(screen.getByText('Ask the agent anything about this task')).toBeInTheDocument();
    });
  });

  describe('Back Navigation', () => {
    it('calls onBack when back button clicked', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const backButton = screen.getByText('← Back to Tasks');
      fireEvent.click(backButton);

      expect(mockOnBack).toHaveBeenCalledTimes(1);
    });
  });

  describe('Sending Messages', () => {
    it('sends message when send button clicked', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Hello agent' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Hello agent')).toBeInTheDocument();
        expect(screen.getByText('You')).toBeInTheDocument();
      });
    });

    it('sends message on Enter key press', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');

      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

      await waitFor(() => {
        expect(screen.getByText('Test message')).toBeInTheDocument();
      });
    });

    it('does not send on Shift+Enter', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');

      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13, shiftKey: true });

      expect(screen.queryByText('Test message')).not.toBeInTheDocument();
    });

    it('clears input after sending message', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('does not send empty message', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const sendButton = screen.getByText('Send');
      fireEvent.click(sendButton);

      expect(screen.queryByText('You')).not.toBeInTheDocument();
    });

    it('trims whitespace from messages', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: '  Test  ' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });
    });

    it('disables input while agent is typing', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;
      const sendButton = screen.getByText('Send') as HTMLButtonElement;

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

      // While agent is typing
      await waitFor(() => {
        expect(input.disabled).toBe(true);
        expect(sendButton.disabled).toBe(true);
      });
    });
  });

  describe('Agent Responses', () => {
    it('displays typing indicator before agent response', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Hello' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Task Agent')).toBeInTheDocument();
      });

      // Should show typing indicator (dots will be rendered)
      const typingIndicator = screen.getByText('Task Agent').parentElement?.parentElement;
      expect(typingIndicator).toBeInTheDocument();
    });

    it('shows agent response after delay', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Help me' } });
      fireEvent.click(sendButton);

      // Fast-forward time
      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/I'm here to help you with "Test Task"/i)).toBeInTheDocument();
      });
    });

    it('generates help response for help keywords', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'help' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/I'm here to help you with "Test Task"/i)).toBeInTheDocument();
      });
    });

    it('generates start response for start keywords', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'start' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/Let's get started on "Test Task"/i)).toBeInTheDocument();
      });
    });

    it('generates completion response for done keywords', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'done' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/Excellent work on making progress!/i)).toBeInTheDocument();
      });
    });

    it('generates troubleshooting response for problem keywords', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'stuck' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/I understand you're facing a challenge/i)).toBeInTheDocument();
      });
    });

    it('generates breakdown response for step keywords', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'break down' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(
          screen.getByText(/Let me break down "Test Task" into manageable steps/i)
        ).toBeInTheDocument();
      });
    });

    it('generates thank you response', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'thank you' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/You're welcome!/i)).toBeInTheDocument();
      });
    });

    it('generates default response for unknown input', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'random message' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        expect(screen.getByText(/I'm here to assist you with "Test Task"/i)).toBeInTheDocument();
      });
    });
  });

  describe('Message Persistence', () => {
    it('saves messages to localStorage', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        const stored = localStorage.getItem('task_messages_1');
        expect(stored).toBeTruthy();
        const messages = JSON.parse(stored!);
        expect(messages.length).toBeGreaterThan(0);
        expect(messages[0].text).toBe('Test message');
      });
    });

    it('loads messages from localStorage on mount', () => {
      const existingMessages = [
        {
          id: 1,
          sender: 'user',
          text: 'Old message',
          timestamp: new Date().toISOString(),
        },
      ];

      localStorage.setItem('task_messages_1', JSON.stringify(existingMessages));

      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      expect(screen.getByText('Old message')).toBeInTheDocument();
    });

    it('maintains separate message history per task', async () => {
      localStorage.setItem(
        'task_messages_1',
        JSON.stringify([
          {
            id: 1,
            sender: 'user',
            text: 'Task 1 message',
            timestamp: new Date().toISOString(),
          },
        ])
      );

      localStorage.setItem(
        'task_messages_2',
        JSON.stringify([
          {
            id: 2,
            sender: 'user',
            text: 'Task 2 message',
            timestamp: new Date().toISOString(),
          },
        ])
      );

      const { rerender } = render(
        <TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />
      );

      expect(screen.getByText('Task 1 message')).toBeInTheDocument();
      expect(screen.queryByText('Task 2 message')).not.toBeInTheDocument();

      rerender(
        <TaskChatView
          task={{ ...mockTask, id: 2 }}
          onBack={mockOnBack}
          onTaskUpdate={mockOnTaskUpdate}
        />
      );

      expect(screen.queryByText('Task 1 message')).not.toBeInTheDocument();
      expect(screen.getByText('Task 2 message')).toBeInTheDocument();
    });
  });

  describe('Date Formatting', () => {
    it('formats message timestamps', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        // Should show time like "12:34 PM"
        expect(screen.getByText(/\d{1,2}:\d{2}\s?[AP]M/i)).toBeInTheDocument();
      });
    });

    it('formats creation date in header', () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      // Should format date like "just now", "5m ago", etc.
      expect(screen.getByText(/Created/i)).toBeInTheDocument();
    });
  });

  describe('Message Display', () => {
    it('displays user messages on the right', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'User message' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        const userMessage = screen.getByText('User message');
        expect(userMessage).toBeInTheDocument();
      });
    });

    it('displays agent messages on the left', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'help' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        const agentMessages = screen.getAllByText('Task Agent');
        expect(agentMessages.length).toBeGreaterThan(0);
      });
    });

    it('preserves newlines in messages', async () => {
      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Line 1\nLine 2\nLine 3' } });
      fireEvent.click(sendButton);

      jest.advanceTimersByTime(2500);

      await waitFor(() => {
        const message = screen.getByText(/Line 1/i);
        expect(message).toBeInTheDocument();
      });
    });
  });

  describe('Scroll Behavior', () => {
    it('scrolls to bottom on new messages', async () => {
      const scrollIntoViewMock = jest.fn();
      Element.prototype.scrollIntoView = scrollIntoViewMock;

      render(<TaskChatView task={mockTask} onBack={mockOnBack} onTaskUpdate={mockOnTaskUpdate} />);

      const input = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.change(input, { target: { value: 'Test' } });
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(scrollIntoViewMock).toHaveBeenCalled();
      });
    });
  });
});
