import { render, screen } from '@testing-library/react'
import { AuthProvider } from '@/contexts/AuthContext'
import Home from '@/app/page'

// Mock localStorage for tests
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => null),
    setItem: jest.fn(() => null),
    removeItem: jest.fn(() => null),
  },
  writable: true,
});

describe('Home', () => {
  it('renders the home page', () => {
    render(
      <AuthProvider>
        <Home />
      </AuthProvider>
    )
    
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toBeInTheDocument()
  })

  it('contains the main content', () => {
    render(
      <AuthProvider>
        <Home />
      </AuthProvider>
    )
    
    // Look for specific text content - use getByRole for the main heading
    expect(screen.getByRole('heading', { name: /powerful multi-tenant customer intelligence/i })).toBeInTheDocument()
  })
})
