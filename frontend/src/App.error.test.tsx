import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { expect, it } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gamesResponseFixture,
} from './test/appApiMocks'
import App from './App'

it('lets a visitor retry a recoverable games error', async () => {
  const user = userEvent.setup()
  appApiMocks.getCurrentContext
    .mockRejectedValueOnce(new Error('Unavailable'))
    .mockResolvedValueOnce(currentContextFixture())
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture(),
  )

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  const alert = await screen.findByRole('alert')
  expect(alert).toHaveTextContent("We couldn't load today's games")
  await user.click(screen.getByRole('button', { name: 'Try again' }))
  expect(
    await screen.findByText('No NHL games are scheduled for this official date.'),
  ).toBeInTheDocument()
  expect(appApiMocks.getCurrentContext).toHaveBeenCalledTimes(2)
})
