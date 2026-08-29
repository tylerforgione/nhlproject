import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it } from 'vitest'

import { appApiMocks } from './test/appApiMocks'
import App from './App'

it('announces loading without collapsing the scores area', () => {
  appApiMocks.getCurrentContext.mockReturnValue(new Promise(() => undefined))

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(screen.getByRole('status')).toHaveTextContent("Loading today's games")
  expect(screen.getByTestId('scores-state')).toHaveClass('scores-state')
})
