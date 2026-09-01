import { NavLink, Route, Routes } from 'react-router-dom'

import './product.css'
import './coverage.css'
import './states.css'
import './theme.css'
import { RouteMetadata } from './RouteMetadata'
import { CurrentGamesPage } from './pages/CurrentGamesPage'
import { GamesPage } from './pages/GamesPage'
import { useTheme } from './theme'

function App() {
  const { resolvedTheme, toggleTheme } = useTheme()

  return (
    <div className="app-shell">
      <RouteMetadata />
      <header className="site-header" aria-label="Hockey Stat Pack">
        <NavLink className="wordmark" to="/" aria-label="Hockey Stat Pack Home">
          Hockey Stat Pack
        </NavLink>
        <div className="header-actions">
          <nav aria-label="Primary">
            <NavLink to="/">Home</NavLink>
            <NavLink to="/games">Games</NavLink>
          </nav>
          <label className="theme-switch">
            <span className="theme-switch-label">Dark mode</span>
            <input
              type="checkbox"
              role="switch"
              checked={resolvedTheme === 'dark'}
              onChange={toggleTheme}
            />
            <span className="theme-switch-track" aria-hidden="true">
              <span className="theme-switch-thumb">
                {resolvedTheme === 'dark' ? '☀' : '☾'}
              </span>
            </span>
          </label>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<CurrentGamesPage />} />
        <Route path="/games" element={<GamesPage />} />
      </Routes>
    </div>
  )
}

export default App
