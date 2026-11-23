import { useState } from 'react'
import { layoutMindmap } from '../mindmap.js'

const FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

function activate(handler) {
  return (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handler(e)
    }
  }
}

/** Mind map: radial on wide screens, a compact one-column tree on phones (`compact`). */
export default function MindMapSvg({ mindmap, onOpenStage, labelledBy, compact = false }) {
  const title = mindmap.track?.title ?? 'AI Made Easy'
  const layout = layoutMindmap(mindmap.stages, title, { compact })
  const { center, centerBox, centerLines, nodes, viewBox, nodeFont, nodeLineH, nodeAnchor, centerFont, centerLineH } = layout
  const [active, setActive] = useState(null)
  const centerH = centerBox.y2 - centerBox.y1

  return (
    <svg
      className={`mm-svg${compact ? ' mm-svg--compact' : ''}${active ? ' mm-svg--focus' : ''}`}
      viewBox={viewBox.join(' ')}
      role="group"
      aria-labelledby={labelledBy}
      fontFamily={FONT}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g aria-hidden="true">
        {nodes.map(({ stage, branch, color }) => (
          <path
            key={stage.id}
            className={`mm-branch${active === stage.id ? ' mm-branch--active' : ''}`}
            d={branch}
            fill={color}
          />
        ))}
      </g>

      <g aria-hidden="true" className="mm-center">
        <rect
          x={centerBox.x1}
          y={centerBox.y1}
          width={centerBox.x2 - centerBox.x1}
          height={centerH}
          rx={centerH / 2}
          fill="#ffffff"
          stroke="#c4b5fd"
          strokeWidth="2"
        />
        {centerLines.map((line, i) => (
          <text
            key={line}
            x={center.x}
            y={center.y + centerFont * 0.36 + (i - (centerLines.length - 1) / 2) * centerLineH}
            textAnchor="middle"
            fontSize={centerFont}
            fontWeight="700"
            fill="#18181b"
          >
            {line}
          </text>
        ))}
      </g>

      {nodes.map(({ stage, box, height, titleLines, color, tint }, i) => (
        <g
          key={stage.id}
          className="mm-node"
          role="link"
          tabIndex={0}
          aria-label={`Step ${i + 1}: ${stage.title}. Open this step to learn it, with an example.`}
          onClick={() => onOpenStage(stage)}
          onKeyDown={activate(() => onOpenStage(stage))}
          onMouseEnter={() => setActive(stage.id)}
          onMouseLeave={() => setActive(null)}
          onFocus={() => setActive(stage.id)}
          onBlur={() => setActive(null)}
        >
          <title>{`Step ${i + 1}: ${stage.title}`}</title>
          <rect
            className="mm-node__box"
            x={box.x1}
            y={box.y1}
            width={box.x2 - box.x1}
            height={height}
            rx="16"
            fill={tint}
            stroke={color}
            strokeWidth="1.5"
          />
          {titleLines.map((line, k) => (
            <text
              key={k}
              x={nodeAnchor === 'start' ? box.x1 + 14 : (box.x1 + box.x2) / 2}
              y={box.y1 + (height - titleLines.length * nodeLineH) / 2 + nodeLineH / 2 + nodeFont * 0.36 + k * nodeLineH}
              textAnchor={nodeAnchor}
              fontSize={nodeFont}
              fontWeight="600"
              fill="#18181b"
            >
              {line}
            </text>
          ))}
        </g>
      ))}
    </svg>
  )
}
