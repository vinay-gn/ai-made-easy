import { Link } from 'react-router-dom'

/** The "All steps" list under the map: one link per step, with its one-line explanation. */
export default function MindMapOutline({ mindmap }) {
  return (
    <ol className="mm-outline">
      {mindmap.stages.map((stage, i) => (
        <li key={stage.id}>
          <Link className="mm-outline__link" to={`/stages/${stage.id}`}>
            <span className="mm-outline__title">
              <span className="mm-outline__step">Step {i + 1}:</span> {stage.title}
            </span>
            {stage.blurb && <span className="mm-outline__blurb">{stage.blurb}</span>}
          </Link>
        </li>
      ))}
    </ol>
  )
}
