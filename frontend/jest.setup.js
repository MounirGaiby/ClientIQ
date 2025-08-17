import '@testing-library/jest-dom'

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => null),
    setItem: jest.fn(() => null),
    removeItem: jest.fn(() => null),
  },
  writable: true,
});

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: false,
    json: () => Promise.resolve({}),
  })
);
