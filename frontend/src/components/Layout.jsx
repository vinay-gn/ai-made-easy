import { useEffect } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import ErrorBoundary from './ErrorBoundary.jsx'
import { SITE_NAME, TAGLINE } from '../useDocumentTitle.js'

export default function Layout() {
  const { pathname, search } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <div className="container site-header__inner">
          <Link to="/" className="brand">
            {SITE_NAME}
          </Link>
        </div>
      </header>
      <main id="main" className="container" tabIndex={-1}>
        <ErrorBoundary key={pathname + search}>
          <Outlet />
        </ErrorBoundary>
      </main>
      <footer className="site-footer">
        <div className="container">
          {SITE_NAME} — {TAGLINE}
        </div>
      </footer>
    </>
  )
}
