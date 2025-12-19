# Dropdown Performance Tests

This directory contains performance tests for dropdown components to ensure they remain responsive and don't cause performance issues.

## Test Coverage

### NavDropdown Component (`Layout.test.tsx`)
- ✅ Throttling of scroll and resize events
- ✅ Event listener cleanup on unmount
- ✅ Memoized handlers to prevent unnecessary re-renders
- ✅ Efficient positioning without layout thrashing
- ✅ Handling rapid open/close cycles

### Performance Requirements (`DropdownPerformance.test.tsx`)
- ✅ Throttle utility usage verification
- ✅ requestAnimationFrame usage for smooth updates
- ✅ Event listener cleanup verification
- ✅ Handler memoization verification
- ✅ Rapid interaction handling

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Performance Benchmarks

The tests ensure that:
1. **Scroll events are throttled** to ~60fps (16ms intervals)
2. **Event listeners are properly cleaned up** to prevent memory leaks
3. **Handlers are memoized** using `useCallback` to prevent unnecessary re-renders
4. **Position updates use requestAnimationFrame** for smooth animations
5. **Rapid interactions** don't cause performance degradation

## Preventing Regressions

These tests should catch:
- Removal of throttling/debouncing
- Missing event listener cleanup
- Unmemoized handlers causing re-renders
- Excessive DOM reads (getBoundingClientRect)
- Performance regressions in dropdown interactions








