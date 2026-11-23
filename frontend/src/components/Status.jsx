import { Link } from 'react-router-dom'
import { useDocumentTitle } from '../useDocumentTitle.js'

export function NotFound({ title = 'Page not found', message = "We couldn't find what you were looking for." }) {
  useDocumentTitle(title)
  return (
    <section className="status status--notfound" aria-labelledby="notfound-title">
      <h1 id="notfound-title">{title}</h1>
      <p>{message}</p>
      <Link className="button" to="/">
        Go to the mind map
      </Link>
    </section>
  )
}
