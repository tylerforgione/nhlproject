import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'

import App from './App'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

beforeEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-theme')
  vi.stubGlobal(
    'matchMedia',
    vi.fn().mockReturnValue({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }),
  )
  vi.mocked(getCurrentContext).mockReturnValue(new Promise(() => undefined))
})

it('persists a manual theme override over the system preference', async () => {
  const user = userEvent.setup()
  const firstRender = render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  expect(document.documentElement).toHaveAttribute('data-theme', 'light')
  const themeSwitch = screen.getByRole('switch', { name: 'Dark mode' })
  expect(themeSwitch).not.toBeChecked()
  expect(screen.getByText('☾')).toBeInTheDocument()
  await user.click(themeSwitch)
  expect(document.documentElement).toHaveAttribute('data-theme', 'dark')
  expect(localStorage.getItem('hockey-stat-pack-theme')).toBe('dark')
  expect(themeSwitch).toBeChecked()
  expect(screen.getByText('☀')).toBeInTheDocument()
  expect(screen.queryByText('☾')).not.toBeInTheDocument()

  firstRender.unmount()
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  expect(document.documentElement).toHaveAttribute('data-theme', 'dark')
  expect(screen.getByRole('switch', { name: 'Dark mode' })).toBeChecked()
  expect(screen.getByText('☀')).toBeInTheDocument()
})
