import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

const themeCss = readFileSync('src/theme.css', 'utf8')

function themeVariable(theme: 'light' | 'dark', variable: string) {
  const block = themeCss.match(
    new RegExp(`:root\\[data-theme='${theme}'\\] \\{([^}]*)\\}`),
  )?.[1]
  const value = block?.match(
    new RegExp(`--${variable}:\\s*(#[\\da-f]{6});`, 'i'),
  )?.[1]

  if (!value) throw new Error(`Missing --${variable} for the ${theme} theme`)
  return value
}

function luminance(hex: string) {
  const channels = [1, 3, 5]
    .map((index) => Number.parseInt(hex.slice(index, index + 2), 16) / 255)
    .map((channel) =>
      channel <= 0.04045
        ? channel / 12.92
        : ((channel + 0.055) / 1.055) ** 2.4,
    )

  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
}

function contrastRatio(first: string, second: string) {
  const firstLuminance = luminance(first)
  const secondLuminance = luminance(second)

  return (
    (Math.max(firstLuminance, secondLuminance) + 0.05) /
    (Math.min(firstLuminance, secondLuminance) + 0.05)
  )
}

describe.each(['light', 'dark'] as const)('%s live status', (theme) => {
  it.each(['page-bg', 'surface-muted'])(
    'clears 4.5:1 on %s',
    (background) => {
      expect(
        contrastRatio(
          themeVariable(theme, 'live'),
          themeVariable(theme, background),
        ),
      ).toBeGreaterThanOrEqual(4.5)
    },
  )
})
