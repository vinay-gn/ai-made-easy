import { Link } from 'react-router-dom'

/**
 * Link-based track switcher. Each option is a real link so the choice lives in the URL.
 * `options` = [{ id, title, count? }], `hrefFor(id)` builds the target URL.
 */
export default function TrackTabs({ label, options, current, hrefFor }) {
  // Nothing to choose between: hide the switcher (it reappears if the API offers more tracks).
  if (options.length <= 1) return null
  return (
    <nav aria-label={label} className="track-tabs">
      <ul>
        {options.map((opt) => (
          <li key={opt.id}>
            <Link
              to={hrefFor(opt.id)}
              className="track-tabs__tab"
              aria-current={opt.id === current ? 'page' : undefined}
            >
              {opt.title}
              {typeof opt.count === 'number' && <span className="track-tabs__count">{opt.count}</span>}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}
