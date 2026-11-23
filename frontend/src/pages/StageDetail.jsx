import { Link, useParams } from 'react-router-dom'
import { getStage, getStages } from '../content.js'
import { useDocumentTitle } from '../useDocumentTitle.js'
import { mapHref, trackOf } from '../tracks.js'
import { firstSentences } from '../text.js'
import { NotFound } from '../components/Status.jsx'
import WorkedExample from '../components/WorkedExample.jsx'

export default function StageDetail() {
  const { stageId } = useParams()
  const stage = getStage(stageId)
  useDocumentTitle(stage?.title ?? 'Step not found')

  if (!stage) {
    return <NotFound title="Step not found" message={`There is no step called “${stageId}”.`} />
  }

  const trackId = trackOf(stage)
  const siblings = getStages(trackId)
  const index = siblings.findIndex((s) => s.id === stage.id)
  const prev = index > 0 ? siblings[index - 1] : null
  const next = index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : null
  const stepLabel = index >= 0 ? `Step ${index + 1} of ${siblings.length}` : null
  const explanation = firstSentences(stage.summary, 3)

  return (
    <article className="stage-detail">
      <nav aria-label="Breadcrumb" className="breadcrumb">
        <Link to={mapHref(trackId)}>Mind map</Link> <span aria-hidden="true">›</span>{' '}
        <span aria-current="page">{stepLabel ? `Step ${index + 1}` : stage.title}</span>
      </nav>
      <header className="stage-detail__header">
        {stepLabel && <p className="eyebrow">{stepLabel}</p>}
        <h1>{stage.title}</h1>
        {explanation && <p className="lead">{explanation}</p>}
      </header>

      {stage.details?.length > 0 && (
        <div className="stage-details">
          {stage.details.map((d) => (
            <section key={d.heading} className="stage-details__section">
              <h2>{d.heading}</h2>
              <p>{d.body}</p>
            </section>
          ))}
        </div>
      )}

      <WorkedExample example={stage.example} stageTitle={stage.title} />

      {stage.resources.length > 0 && (
        <section aria-labelledby="learn-more-title" className="learn-more">
          <h2 id="learn-more-title">Learn more</h2>
          <ul>
            {stage.resources.map((r) => (
              <li key={r.id}>
                <a href={r.url} target="_blank" rel="noopener noreferrer">
                  {r.title}
                  <span className="visually-hidden"> (opens in a new tab)</span>
                </a>
                {r.provider && <span className="learn-more__source"> · {r.provider}</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      <nav aria-label="Stage navigation" className="pager">
        {prev ? (
          <Link to={`/stages/${prev.id}`} className="pager__link">
            Previous: {prev.title}
          </Link>
        ) : (
          <span />
        )}
        {next && (
          <Link to={`/stages/${next.id}`} className="pager__link pager__link--next">
            Next: {next.title}
          </Link>
        )}
      </nav>
    </article>
  )
}
