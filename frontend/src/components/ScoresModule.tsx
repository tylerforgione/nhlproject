import { useId } from 'react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import type { GameSummary } from '../api/game-types'

interface GameLink {
  to: string
  ariaLabel: string
}

interface ScoresModuleProps {
  games: readonly GameSummary[]
  eyebrow: string
  heading: string
  headingLevel: 1 | 2
  officialDate: string
  gamesLabel: string
  getGameLink?: (game: GameSummary) => GameLink | null
  children?: ReactNode
}

function formatStartTime(startTimeUtc: string | null): string {
  if (!startTimeUtc) return 'Time unavailable'

  return new Intl.DateTimeFormat(undefined, {
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  }).format(new Date(startTimeUtc))
}

function formatStatus(game: GameSummary): string {
  if (game.state === 'scheduled') return 'Scheduled'
  if (game.state === 'live') return 'Live'
  if (game.state === 'final') return 'Final'
  return 'Status unavailable'
}

function Team({ game, side }: { game: GameSummary; side: 'away' | 'home' }) {
  const team = side === 'away' ? game.away_team : game.home_team
  const score = side === 'away' ? game.away_score : game.home_score

  return (
    <div className="team-row">
      <span className="team-abbreviation" aria-hidden="true">
        {team.abbreviation}
      </span>
      <span className="team-name">{team.name}</span>
      {score === null ? (
        <span className="team-score" aria-label="Score unavailable">
          —
        </span>
      ) : (
        <strong className="team-score">{score}</strong>
      )}
    </div>
  )
}

function GameCard({ game, link }: { game: GameSummary; link: GameLink | null }) {
  const card = (
    <article className="game-card">
      <div className="game-meta">
        <span>{formatStartTime(game.start_time_utc)}</span>
        <span className={`game-state game-state-${game.state}`}>
          {formatStatus(game)}
        </span>
      </div>
      <Team game={game} side="away" />
      <Team game={game} side="home" />
      {game.venue && <p className="venue">{game.venue}</p>}
    </article>
  )

  if (!link) return card

  return (
    <Link
      className="game-card-link"
      to={link.to}
      aria-label={link.ariaLabel}
    >
      {card}
    </Link>
  )
}

export function ScoresModule({
  games,
  eyebrow,
  heading,
  headingLevel,
  officialDate,
  gamesLabel,
  getGameLink,
  children,
}: ScoresModuleProps) {
  const headingId = useId()

  return (
    <section className="scores-section" aria-labelledby={headingId}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          {headingLevel === 1 ? (
            <h1 id={headingId}>{heading}</h1>
          ) : (
            <h2 id={headingId}>{heading}</h2>
          )}
        </div>
        <time dateTime={officialDate}>
          {new Intl.DateTimeFormat(undefined, {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            timeZone: 'UTC',
          }).format(new Date(`${officialDate}T12:00:00Z`))}
        </time>
      </div>
      <div className="scores-content">
        {children}
        {games.length > 0 && (
          <div
            className="scores-scroll"
            role="region"
            tabIndex={0}
            aria-label={gamesLabel}
          >
            {games.map((game) => (
              <GameCard
                game={game}
                key={game.id}
                link={getGameLink?.(game) ?? null}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
