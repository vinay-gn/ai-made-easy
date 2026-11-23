import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useDocumentTitle } from '../useDocumentTitle.js'
import { DEFAULT_TRACK, mapHref } from '../tracks.js'
import { buildMindmap } from '../mindmap.js'
import TrackTabs from '../components/TrackTabs.jsx'
import MindMapSvg from '../components/MindMapSvg.jsx'
import MindMapOutline from '../components/MindMapOutline.jsx'

// Below this width the radial map can't keep labels readable, so a compact one-column tree is shown instead.
const COMPACT = '(max-width: 760px)'

function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches)
  useEffect(() => {
    const mql = window.matchMedia(query)
    const onChange = () => setMatches(mql.matches)
    mql.addEventListener('change', onChange)
    return () => mql.removeEventListener('change', onChange)
  }, [query])
  return matches
}

export default function MindMap() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const compact = useMediaQuery(COMPACT)
  const requested = params.get('track')
  const { tracks, trackId, mindmap } = useMemo(() => buildMindmap(requested), [requested])
  const canvasRef = useRef(null)
  const hasStages = mindmap.stages.length > 0

  // Between the compact breakpoint and the map's min width it pans horizontally: start at its centre.
  useEffect(() => {
    const el = canvasRef.current
    if (hasStages && el) el.scrollLeft = (el.scrollWidth - el.clientWidth) / 2
  }, [hasStages, mindmap, compact])

  const trackTitle = mindmap.track?.title
  const isDefault = trackId === DEFAULT_TRACK
  const heading = isDefault ? 'AI Made Easy — mind map' : `${trackTitle ?? 'Mind map'} — mind map`
  useDocumentTitle(isDefault ? null : `Mind map · ${trackTitle ?? trackId}`)

  return (
    <section className="mindmap" aria-labelledby="mm-title">
      <h1 id="mm-title" className="visually-hidden">
        {heading}
      </h1>

      <TrackTabs
        label="Choose a track"
        current={trackId}
        hrefFor={mapHref}
        options={tracks.map((t) => ({ id: t.id, title: t.title }))}
      />

      {!hasStages && <p className="status">Steps for this track are coming soon.</p>}

      {hasStages && (
        <>
          <div className="mm-canvas" ref={canvasRef}>
            <MindMapSvg
              mindmap={mindmap}
              compact={compact}
              labelledBy="mm-title"
              onOpenStage={(stage) => navigate(`/stages/${stage.id}`)}
            />
          </div>

          <section className="mm-steps" aria-labelledby="mm-steps-title">
            <h2 id="mm-steps-title">All steps</h2>
            <MindMapOutline mindmap={mindmap} />
          </section>
        </>
      )}
    </section>
  )
}
