import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gamesResponseFixture,
} from './test/appApiMocks'
import App from './App'

it('shows a deliberate empty state for an official date with no games', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContextFixture())
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(gamesResponseFixture())

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText('No NHL games are scheduled for this official date.'),
  ).toBeInTheDocument()
  expect(screen.getByText('January 15, 2026')).toBeInTheDocument()
  expect(
    screen.queryByRole('region', { name: "Today's NHL games" }),
  ).not.toBeInTheDocument()
})
