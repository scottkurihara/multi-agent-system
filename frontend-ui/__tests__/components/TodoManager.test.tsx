/**
 * Tests for TodoManager component - Task Management UI
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoManager from '../../app/components/TodoManager';

// Mock fetch globally
global.fetch = jest.fn();

describe('TodoManager Component', () => {
  const mockOnClose = jest.fn();

  const mockTodos = [
    {
      id: 1,
      title: 'Test Task 1',
      description: 'Description 1',
      status: 'pending' as const,
      priority: 'high' as const,
      completed: false,
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      title: 'Test Task 2',
      description: 'Description 2',
      status: 'completed' as const,
      priority: 'low' as const,
      completed: true,
      created_at: '2024-01-02T00:00:00Z',
    },
    {
      id: 3,
      title: 'Test Task 3',
      description: 'Description 3',
      status: 'in_progress' as const,
      priority: 'medium' as const,
      completed: false,
      created_at: '2024-01-03T00:00:00Z',
    },
  ];

  beforeEach(() => {
    mockOnClose.mockClear();
    (global.fetch as jest.Mock).mockClear();

    // Default mock for loading todos
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ todos: mockTodos }),
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('renders todo manager with header', async () => {
      render(<TodoManager onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText('Task Archive')).toBeInTheDocument();
        expect(screen.getByText('Task Management System')).toBeInTheDocument();
      });
    });

    it('displays statistics correctly', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument(); // Total
        expect(screen.getByText('2')).toBeInTheDocument(); // Active
        expect(screen.getByText('1')).toBeInTheDocument(); // Completed
      });
    });

    it('renders close button when onClose prop provided', async () => {
      render(<TodoManager onClose={mockOnClose} />);

      await waitFor(() => {
        const closeButton = screen.getByTitle('');
        expect(closeButton).toBeInTheDocument();
      });
    });

    it('does not render close button when onClose not provided', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        const closeButtons = screen.queryAllByText('✕');
        expect(closeButtons.length).toBe(0);
      });
    });
  });

  describe('Loading Todos', () => {
    it('loads todos on mount', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/todos');
      });

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
        expect(screen.getByText('Test Task 2')).toBeInTheDocument();
        expect(screen.getByText('Test Task 3')).toBeInTheDocument();
      });
    });

    it('displays empty state when no todos', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ todos: [] }),
      });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('No tasks yet')).toBeInTheDocument();
        expect(screen.getByText('Add your first task to get started')).toBeInTheDocument();
      });
    });

    it('handles loading error gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument();
      });
    });

    it('displays error when API returns non-ok response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Server error' }),
      });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load todos/i)).toBeInTheDocument();
      });
    });
  });

  describe('Adding Tasks', () => {
    it('adds new task when form submitted', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 4, title: 'New Task', completed: false }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            todos: [
              ...mockTodos,
              { id: 4, title: 'New Task', completed: false, created_at: new Date().toISOString() },
            ],
          }),
        });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText('Enter a new task...');
      const addButton = screen.getByText('Add Task');

      fireEvent.change(input, { target: { value: 'New Task' } });
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/todos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: 'New Task',
            status: 'pending',
            completed: false,
          }),
        });
      });
    });

    it('clears input after adding task', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, title: 'New Task' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: [] }),
        });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Enter a new task...')).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText('Enter a new task...') as HTMLInputElement;
      fireEvent.change(input, { target: { value: 'New Task' } });

      const addButton = screen.getByText('Add Task');
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('does not add task when input is empty', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Enter a new task...')).toBeInTheDocument();
      });

      const addButton = screen.getByText('Add Task');
      fireEvent.click(addButton);

      // Should not make POST request
      expect(global.fetch).toHaveBeenCalledTimes(1); // Only initial GET
    });

    it('adds task on Enter key press', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ id: 1, title: 'New Task' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: [] }),
        });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Enter a new task...')).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText('Enter a new task...');
      fireEvent.change(input, { target: { value: 'New Task' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/todos', expect.any(Object));
      });
    });

    it('handles error when adding task fails', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: [] }),
        })
        .mockRejectedValueOnce(new Error('Failed to create'));

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Enter a new task...')).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText('Enter a new task...');
      fireEvent.change(input, { target: { value: 'New Task' } });

      const addButton = screen.getByText('Add Task');
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to create/i)).toBeInTheDocument();
      });
    });
  });

  describe('Toggling Tasks', () => {
    it('toggles task completion status', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos }),
        });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const checkboxes = screen.getAllByRole('generic');
      const firstCheckbox = checkboxes.find((el) => el.className.includes('taskCheckbox'));

      if (firstCheckbox) {
        fireEvent.click(firstCheckbox);
      }

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/todos/1', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            completed: true,
            status: 'completed',
          }),
        });
      });
    });

    it('handles error when toggling fails', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos }),
        })
        .mockRejectedValueOnce(new Error('Update failed'));

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const checkboxes = screen.getAllByRole('generic');
      const firstCheckbox = checkboxes.find((el) => el.className.includes('taskCheckbox'));

      if (firstCheckbox) {
        fireEvent.click(firstCheckbox);
      }

      await waitFor(() => {
        expect(screen.getByText(/Update failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Deleting Tasks', () => {
    it('deletes task when delete button clicked', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos.slice(1) }),
        });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/todos/1', {
          method: 'DELETE',
        });
      });
    });

    it('handles error when deleting fails', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ todos: mockTodos }),
        })
        .mockRejectedValueOnce(new Error('Delete failed'));

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/Delete failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Filtering', () => {
    it('shows all tasks by default', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
        expect(screen.getByText('Test Task 2')).toBeInTheDocument();
        expect(screen.getByText('Test Task 3')).toBeInTheDocument();
      });
    });

    it('filters to show only active tasks', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const activeFilter = screen.getByText('Active Tasks');
      fireEvent.click(activeFilter);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
        expect(screen.getByText('Test Task 3')).toBeInTheDocument();
        expect(screen.queryByText('Test Task 2')).not.toBeInTheDocument();
      });
    });

    it('filters to show only completed tasks', async () => {
      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      });

      const completedFilter = screen.getByText('Completed Tasks');
      fireEvent.click(completedFilter);

      await waitFor(() => {
        expect(screen.getByText('Test Task 2')).toBeInTheDocument();
        expect(screen.queryByText('Test Task 1')).not.toBeInTheDocument();
        expect(screen.queryByText('Test Task 3')).not.toBeInTheDocument();
      });
    });

    it('shows empty state when filter has no results', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          todos: [
            {
              id: 1,
              title: 'Task 1',
              completed: false,
              created_at: new Date().toISOString(),
            },
          ],
        }),
      });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText('Task 1')).toBeInTheDocument();
      });

      const completedFilter = screen.getByText('Completed Tasks');
      fireEvent.click(completedFilter);

      await waitFor(() => {
        expect(screen.getByText('No tasks yet')).toBeInTheDocument();
      });
    });
  });

  describe('Date Formatting', () => {
    it('formats dates correctly', async () => {
      const now = new Date();
      const oneMinuteAgo = new Date(now.getTime() - 60000);
      const oneHourAgo = new Date(now.getTime() - 3600000);
      const oneDayAgo = new Date(now.getTime() - 86400000);

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          todos: [
            {
              id: 1,
              title: 'Recent',
              completed: false,
              created_at: oneMinuteAgo.toISOString(),
            },
            {
              id: 2,
              title: 'Hour ago',
              completed: false,
              created_at: oneHourAgo.toISOString(),
            },
            {
              id: 3,
              title: 'Day ago',
              completed: false,
              created_at: oneDayAgo.toISOString(),
            },
          ],
        }),
      });

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText(/1m ago/i)).toBeInTheDocument();
        expect(screen.getByText(/1h ago/i)).toBeInTheDocument();
        expect(screen.getByText(/1d ago/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument();
      });
    });

    it('allows dismissing error message', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Test error'));

      render(<TodoManager />);

      await waitFor(() => {
        expect(screen.getByText(/Test error/i)).toBeInTheDocument();
      });

      const closeButton = screen.getByText('✕');
      fireEvent.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByText(/Test error/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Close Functionality', () => {
    it('calls onClose when close button clicked', async () => {
      render(<TodoManager onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText('Task Archive')).toBeInTheDocument();
      });

      const closeButton = screen.getByText('✕');
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });
});
