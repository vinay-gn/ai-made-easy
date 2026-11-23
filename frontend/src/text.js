/** First `count` sentences of `text` (keeps short explanations short). */
export function firstSentences(text, count) {
  const sentences = (text ?? '').match(/[^.!?]+[.!?]+(\s|$)|[^.!?]+$/g) ?? []
  return sentences.slice(0, count).join('').trim()
}
