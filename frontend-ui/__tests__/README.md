# Frontend Tests - Generative UI Components

Comprehensive test suite for the generative UI components used in the multi-agent system.

## Test Coverage

### Generative UI Component Tests

**ApprovalCard.test.tsx** - Approval card with action buttons
- Renders title and description
- Displays all option buttons
- Calls onResponse callback when clicked
- Shows confirmation message after selection
- Disables buttons after selection
- Handles empty options array

**ResearchSummary.test.tsx** - Research findings display
- Renders title
- Displays all findings as list items
- Maintains correct order
- Handles empty findings array
- Works with single finding

**EditableValue.test.tsx** - Inline value editing
- Renders label and initial value
- Enables editing mode
- Calls onSave with new value
- Cancels editing and reverts changes
- Supports different field types (text, number, date)

**OptionsSelector.test.tsx** - Multiple choice selector
- Renders question text
- Displays numbered options
- Calls onSelect callback
- Shows selected option
- Disables options after selection
- Handles single option

**DocumentViewer.test.tsx** - Document display with metadata
- Renders document title
- Displays content
- Shows metadata when provided
- Works without metadata
- Handles multiline content
- Renders multiple metadata fields

## Running Tests

### Run All Frontend Tests
```bash
cd frontend-ui
npm test
```

### Run Tests in Watch Mode
```bash
npm test -- --watch
```

### Run Tests with Coverage
```bash
npm test -- --coverage
```

### Run Specific Test File
```bash
npm test ApprovalCard.test
```

### Run Tests in CI Mode
```bash
npm test -- --ci --coverage --maxWorkers=2
```

## Test Configuration

**jest.config.js** - Jest configuration
- Uses next/jest for Next.js integration
- jsdom environment for React component testing
- Module path mapping for imports
- Coverage collection settings

**jest.setup.js** - Test setup
- Imports @testing-library/jest-dom for custom matchers

## Test Dependencies

Required packages (installed via npm):
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers for DOM
- `@testing-library/user-event` - User interaction simulation
- `jest` - Testing framework
- `jest-environment-jsdom` - Browser-like environment

Install dependencies:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom
```

## Writing New Tests

### Test Structure
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MyComponent from '../../app/components/MyComponent';

describe('MyComponent - Generative UI', () => {
  const mockCallback = jest.fn();

  beforeEach(() => {
    mockCallback.mockClear();
  });

  it('renders correctly', () => {
    render(<MyComponent onAction={mockCallback} />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', () => {
    render(<MyComponent onAction={mockCallback} />);
    fireEvent.click(screen.getByText('Button'));
    expect(mockCallback).toHaveBeenCalledWith('expected-value');
  });
});
```

### Best Practices
1. **Test user behavior, not implementation** - Focus on what users see and do
2. **Use accessible queries** - Prefer getByRole, getByLabelText, getByText
3. **Test edge cases** - Empty data, single items, many items
4. **Mock callbacks** - Verify components call props correctly
5. **Clear test names** - Describe what the test verifies

## Integration with CI/CD

Add to your CI pipeline:
```yaml
# Example GitHub Actions
- name: Run frontend tests
  run: |
    cd frontend-ui
    npm ci
    npm test -- --ci --coverage
```

## Coverage Goals

- **Components**: 80%+ coverage for all generative UI components
- **User Interactions**: All clickable elements tested
- **Edge Cases**: Empty states, single items, many items
- **Callbacks**: All callback props verified

## Debugging Tests

### Run with debugging
```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

### View test output
```bash
npm test -- --verbose
```

### Check specific matcher failures
```bash
npm test -- --no-coverage
```

## Troubleshooting

### "Cannot find module" errors
- Check that jest.config.js has correct moduleNameMapper
- Verify file paths match the actual component locations

### "Window is not defined" errors
- Ensure testEnvironment is set to 'jest-environment-jsdom'
- Install jest-environment-jsdom if missing

### Async test warnings
- Use async/await for async operations
- Wait for elements with findBy queries instead of getBy

## Test Statistics

Current test count:
- **Component Tests**: 5 files, 30+ individual tests
- **Total Coverage**: High coverage of generative UI components
