// Thin content layer: the site is static, so all data comes from the bundled JSON.
// To use a backend again, swap these functions for API calls (keeping the same shapes).
import roadmap from './data/roadmap.json'

export const ENABLED_TRACKS = ['use']

const tracks = roadmap.tracks.filter((t) => ENABLED_TRACKS.includes(t.id))
const stages = roadmap.stages
  .filter((s) => ENABLED_TRACKS.includes(s.track))
  .sort((a, b) => a.order - b.order)

export const getTracks = () => tracks

/** Stages of one track, in order. */
export const getStages = (trackId) => stages.filter((s) => s.track === trackId)

/** `{ track, stages }` for an enabled track, or null. */
export function getMindmap(trackId) {
  const track = tracks.find((t) => t.id === trackId)
  return track ? { track, stages: getStages(trackId) } : null
}

/** Full stage (summary, example, resources…), or null if it doesn't exist. */
export const getStage = (id) => stages.find((s) => s.id === id) ?? null
