import { render, screen } from '@testing-library/react'
import Home from '@/app/page'

describe('Home', () => {
  it('renders the home page', () => {
    render(<Home />)
    
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toBeInTheDocument()
  })

  it('contains the main content', () => {
    render(<Home />)
    
    // Look for specific text content - use getByRole for the main heading
    expect(screen.getByRole('heading', { name: /Welcome to ClientIQ/i })).toBeInTheDocument()
  })
})
