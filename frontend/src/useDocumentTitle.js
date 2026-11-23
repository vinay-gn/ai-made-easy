import { useEffect } from 'react'

export const SITE_NAME = 'AI Made Easy'
export const TAGLINE = 'Learn how to use AI, step by step — free, no jargon.'

export function useDocumentTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} · ${SITE_NAME}` : SITE_NAME
  }, [title])
}
