import { getTracks } from './content.js'

export const DEFAULT_TRACK = 'use'

export const trackOf = (item) => item?.track ?? DEFAULT_TRACK

// Home (`/`) is the mind map plus the "All steps" list.
export const mapHref = (id) => (id === DEFAULT_TRACK ? '/' : `/?track=${id}`)

export function isTrackId(value, tracks = getTracks()) {
  return tracks.some((t) => t.id === value)
}

/** The requested track if it's enabled; otherwise the default (or first available) track. */
export function resolveTrack(requested, tracks = getTracks()) {
  if (requested && isTrackId(requested, tracks)) return requested
  return isTrackId(DEFAULT_TRACK, tracks) ? DEFAULT_TRACK : tracks[0]?.id ?? DEFAULT_TRACK
}

export function findTrack(id, tracks = getTracks()) {
  return tracks.find((t) => t.id === id)
}
