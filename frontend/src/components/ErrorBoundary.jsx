import { Component } from 'react'
import { Link } from 'react-router-dom'
import { SITE_NAME } from '../useDocumentTitle.js'

/** Catches render errors in a page so the site header/nav stay usable. Reset by changing `key`. */
export default class ErrorBoundary extends Component {
  state = { error: null }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('Page crashed:', error, info?.componentStack)
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.state.error && !prevState.error) document.title = `Something went wrong · ${SITE_NAME}`
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <section className="status status--notfound" role="alert" aria-labelledby="crash-title">
        <h1 id="crash-title">Sorry — this page hit a problem</h1>
        <p>Something went wrong while showing this page. Reloading usually fixes it.</p>
        <p>
          <button type="button" className="button" onClick={() => window.location.reload()}>
            Reload the page
          </button>{' '}
          <Link className="button button--ghost" to="/" onClick={() => this.setState({ error: null })}>
            Go to the mind map
          </Link>
        </p>
      </section>
    )
  }
}
