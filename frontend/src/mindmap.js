import { getMindmap, getTracks } from './content.js'
import { resolveTrack } from './tracks.js'
import { firstSentences } from './text.js'

function normalizeStage(s) {
  const blurb = s.takeaway?.trim() || firstSentences(s.summary, 1)
  return { id: s.id, title: s.title, blurb: blurb || '' }
}

/** Returns { tracks, trackId, mindmap: { track, stages } }. Unknown/disabled tracks fall back to the default. */
export function buildMindmap(requested) {
  const tracks = getTracks()
  const trackId = resolveTrack(requested, tracks)
  const { track, stages } = getMindmap(trackId) ?? { track: undefined, stages: [] }
  return { tracks, trackId, mindmap: { track, stages: stages.map(normalizeStage) } }
}

/** Greedy word wrap into at most `maxLines` lines of ~`maxChars` characters. */
export function wrapText(text, maxChars, maxLines) {
  const words = (text ?? '').split(/\s+/).filter(Boolean)
  const lines = []
  let line = ''
  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word
    if (candidate.length <= maxChars || !line) {
      line = candidate
    } else {
      lines.push(line)
      line = word
    }
  }
  if (line) lines.push(line)
  if (lines.length > maxLines) {
    const kept = lines.slice(0, maxLines)
    kept[maxLines - 1] = `${kept[maxLines - 1].replace(/[\s,.;:]+$/, '')}…`
    return kept
  }
  return lines
}

export const STAGE_W = 240
export const CENTER_W = 250

// Soft pastel branch colours (strokes only); nodes get a very light tint of their branch colour.
export const BRANCH_COLORS = ['#a78bfa', '#7cb8f2', '#6fcf9f', '#f5a66b', '#f08fb0', '#e6c25a', '#6ccad8', '#c49be6', '#93aef0', '#9bd38f']

const mix = (hex, amount) => {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16))
  return `#${c.map((v) => Math.round(v * amount + 255 * (1 - amount)).toString(16).padStart(2, '0')).join('')}`
}

/** Centreline of a smooth XMind-style S-curve (leaves the centre horizontally, enters the node horizontally). */
function curve(s, e, steps = 40) {
  const mx = s.x + (e.x - s.x) * 0.5
  const c1 = { x: mx, y: s.y }
  const c2 = { x: mx, y: e.y }
  const pts = []
  for (let k = 0; k <= steps; k++) {
    const t = k / steps
    const u = 1 - t
    pts.push({
      t,
      x: u * u * u * s.x + 3 * u * u * t * c1.x + 3 * u * t * t * c2.x + t * t * t * e.x,
      y: u * u * u * s.y + 3 * u * u * t * c1.y + 3 * u * t * t * c2.y + t * t * t * e.y,
    })
  }
  return pts
}

/** Filled outline of a branch that tapers from `w0` (centre) to `w1` (node). */
function taperedPath(pts, w0 = 10, w1 = 2.5) {
  const left = []
  const right = []
  pts.forEach((p, k) => {
    const a = pts[Math.max(0, k - 1)]
    const b = pts[Math.min(pts.length - 1, k + 1)]
    const len = Math.hypot(b.x - a.x, b.y - a.y) || 1
    const nx = -(b.y - a.y) / len
    const ny = (b.x - a.x) / len
    const half = (w0 + (w1 - w0) * p.t) / 2
    left.push(`${(p.x + nx * half).toFixed(1)},${(p.y + ny * half).toFixed(1)}`)
    right.push(`${(p.x - nx * half).toFixed(1)},${(p.y - ny * half).toFixed(1)}`)
  })
  return `M${left.join(' L')} L${right.reverse().join(' L')} Z`
}

/**
 * Mind map layout. Wide screens: radial (title in the centre, stages fanned out on both sides). `compact` (phones):
 * title on top and stages in one column, each joined by a branch peeling off a shared trunk, so it fits ~340px wide.
 */
export function layoutMindmap(stages, title = '', { compact = false } = {}) {
  return compact ? layoutCompact(stages, title) : layoutRadial(stages, title)
}

function layoutCompact(stages, title) {
  const n = Math.max(stages.length, 1)
  const W = 340
  const step = 5
  const trunk0 = 12
  const nodeX1 = trunk0 + (n - 1) * step + 28
  const nodeFont = 15
  const nodeLineH = 20
  const centerFont = 18
  const centerLineH = 24
  const centerLines = wrapText(title, 22, 2)
  const centerH = 34 + centerLines.length * centerLineH
  const centerBox = { x1: 0, y1: 0, x2: W, y2: centerH }
  let top = centerH + 28

  const nodes = stages.map((stage, i) => {
    const titleLines = wrapText(stage.title, 26, 2)
    const height = 22 + titleLines.length * nodeLineH
    const box = { x1: nodeX1, y1: top, x2: W, y2: top + height }
    const y = top + height / 2
    top += height + 12
    const bx = trunk0 + (n - 1 - i) * step
    const sy = centerH - 8
    const R = 28
    const pts = []
    const vSteps = Math.max(2, Math.ceil((y - R - sy) / 12))
    for (let k = 0; k < vSteps; k++) pts.push({ x: bx, y: sy + ((y - R - sy) * k) / vSteps })
    const c2x = bx + (nodeX1 - bx) * 0.35
    for (let k = 0; k <= 16; k++) {
      const t = k / 16
      const u = 1 - t
      pts.push({
        x: u * u * u * bx + 3 * u * u * t * bx + 3 * u * t * t * c2x + t * t * t * nodeX1,
        y: u * u * u * (y - R) + 3 * u * u * t * y + 3 * u * t * t * y + t * t * t * y,
      })
    }
    pts.forEach((p, k) => (p.t = k / (pts.length - 1)))
    const color = BRANCH_COLORS[i % BRANCH_COLORS.length]
    return { stage, x: (box.x1 + box.x2) / 2, y, height, box, titleLines, color, tint: mix(color, 0.14), points: pts, branch: taperedPath(pts, 4, 2.5) }
  })

  const pad = 6
  const viewBox = [-pad, -pad, W + pad * 2, top - 12 + pad * 2]
  const center = { x: (centerBox.x1 + centerBox.x2) / 2, y: centerH / 2 }
  return { center, centerBox, centerLines, nodes, viewBox, nodeFont, nodeLineH, nodeAnchor: 'start', centerFont, centerLineH }
}

function layoutRadial(stages, title) {
  const n = Math.max(stages.length, 1)
  const scale = 1 + Math.max(0, n - 8) * 0.08
  const rx = 200 * scale
  const ry = 260 * scale
  const gap = 36
  const centerLines = wrapText(title, 18, 2)
  const centerH = 44 + centerLines.length * 26
  const centerBox = { x1: -CENTER_W / 2, y1: -centerH / 2, x2: CENTER_W / 2, y2: centerH / 2 }
  const bounds = { ...centerBox }
  const grow = (b) => {
    bounds.x1 = Math.min(bounds.x1, b.x1)
    bounds.y1 = Math.min(bounds.y1, b.y1)
    bounds.x2 = Math.max(bounds.x2, b.x2)
    bounds.y2 = Math.max(bounds.y2, b.y2)
  }

  const rightCount = Math.ceil(stages.length / 2)
  const leftCount = Math.max(stages.length - rightCount, 1)

  const nodes = stages.map((stage, i) => {
    // First half fans down the right side, the rest continues up the left (clockwise), evenly within each side.
    const right = i < rightCount
    const angle = right
      ? -Math.PI / 2 + ((i + 0.5) * Math.PI) / rightCount
      : Math.PI / 2 + ((i - rightCount + 0.5) * Math.PI) / leftCount
    const side = right ? 1 : -1
    const cos = Math.cos(angle)
    const inner = CENTER_W / 2 + gap + rx * Math.abs(cos)
    const titleLines = wrapText(stage.title, 22, 2)
    const height = 26 + titleLines.length * 22 // matches nodeLineH below
    const x = side * (inner + STAGE_W / 2)
    const y = ry * Math.sin(angle)
    const box = { x1: x - STAGE_W / 2, y1: y - height / 2, x2: x + STAGE_W / 2, y2: y + height / 2 }
    grow(box)
    const color = BRANCH_COLORS[i % BRANCH_COLORS.length]
    const points = curve({ x: side * (CENTER_W / 2 - 24), y: 0 }, { x: side * inner, y })
    return { stage, x, y, height, box, titleLines, color, tint: mix(color, 0.14), points, branch: taperedPath(points) }
  })

  const pad = 28
  const viewBox = [bounds.x1 - pad, bounds.y1 - pad, bounds.x2 - bounds.x1 + pad * 2, bounds.y2 - bounds.y1 + pad * 2]
  return { center: { x: 0, y: 0 }, centerBox, centerLines, nodes, viewBox, nodeFont: 17, nodeLineH: 22, nodeAnchor: 'middle', centerFont: 22, centerLineH: 26 }
}
