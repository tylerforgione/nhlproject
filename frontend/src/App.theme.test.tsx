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
      matches: true,
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

  expect(document.documentElement).toHaveAttribute('data-theme', 'dark')
  const themeSwitch = screen.getByRole('switch', { name: 'Dark mode' })
  expect(themeSwitch).toBeChecked()
  await user.click(themeSwitch)
  expect(document.documentElement).toHaveAttribute('data-theme', 'light')
  expect(localStorage.getItem('hockey-stat-pack-theme')).toBe('light')
  expect(themeSwitch).not.toBeChecked()

  firstRender.unmount()
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  expect(document.documentElement).toHaveAttribute('data-theme', 'light')
  expect(screen.getByRole('switch', { name: 'Dark mode' })).not.toBeChecked()
})
