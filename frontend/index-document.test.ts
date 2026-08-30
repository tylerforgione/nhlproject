import { readFileSync } from 'node:fs'

import { expect, it } from 'vitest'
import { renderStaticRouteDocument } from './static-route-documents'

it('ships meaningful metadata in the initial Home document', () => {
  const html = readFileSync('index.html', 'utf8')

  expect(html).toContain("<title>Today's NHL Games | Hockey Stat Pack</title>")
  expect(html).toContain(
    'content="See today\'s NHL schedule, local start times, and game status."',
  )
  expect(html).toContain('<link rel="canonical" href="/" />')
})

it('renders initial metadata for the indexable Games route', () => {
  const homeHtml = readFileSync('index.html', 'utf8')
  const gamesHtml = renderStaticRouteDocument(homeHtml, {
    path: 'games',
    title: 'NHL Games | Hockey Stat Pack',
    canonicalPath: '/games',
  })

  expect(gamesHtml).toContain('<title>NHL Games | Hockey Stat Pack</title>')
  expect(gamesHtml).toContain('<link rel="canonical" href="/games" />')
})
