import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it, vi } from 'vitest'

import App from './App'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

it('announces loading without collapsing the scores area', () => {
  vi.mocked(getCurrentContext).mockReturnValue(new Promise(() => undefined))

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(screen.getByRole('status')).toHaveTextContent("Loading today's games")
  expect(screen.getByTestId('scores-state')).toHaveClass('scores-state')
})
