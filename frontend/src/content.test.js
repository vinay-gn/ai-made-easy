// Content length limits for the bundled roadmap (formerly enforced by the backend). Run with `npm test`.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const data = JSON.parse(readFileSync(new URL('./data/roadmap.json', import.meta.url), 'utf8'))
const words = (s) => s.trim().split(/\s+/).filter(Boolean).length
const sentences = (s) => s.trim().split(/(?<=[.!?])\s+/).filter(Boolean).length

test('data has the use track and its stages', () => {
  assert.ok(data.tracks.some((t) => t.id === 'use'))
  assert.ok(data.stages.length > 0)
  assert.equal(new Set(data.stages.map((s) => s.id)).size, data.stages.length, 'stage ids are unique')
})

for (const stage of data.stages) {
  test(`stage "${stage.id}" stays short and plain`, () => {
    const { summary, example } = stage
    assert.ok(stage.title, 'has a title')
    assert.ok(words(summary) <= 60, `summary ${words(summary)} words > 60`)
    assert.ok(sentences(summary) >= 2 && sentences(summary) <= 3, `summary has ${sentences(summary)} sentences`)

    assert.ok(example, 'has an example')
    assert.ok(words(example.scenario) <= 25, `scenario ${words(example.scenario)} words > 25`)
    const maxSteps = stage.id === 'mcp' ? 8 : 5
    assert.ok(example.steps.length <= maxSteps, `${example.steps.length} steps > ${maxSteps}`)
    example.steps.forEach((step, i) => assert.ok(words(step) <= 20, `step ${i + 1} has ${words(step)} words > 20`))
    if (example.prompt != null) assert.ok(words(example.prompt) <= 40, `prompt ${words(example.prompt)} words > 40`)
    assert.equal(sentences(example.expected_result), 1, 'expected_result is one sentence')
    assert.ok(words(example.expected_result) <= 25, `expected_result ${words(example.expected_result)} words > 25`)

    const { details } = stage
    assert.ok(Array.isArray(details), 'has details')
    assert.ok(details.length >= 3 && details.length <= 4, `${details.length} detail sections, want 3–4`)
    details.forEach(({ heading, body }, i) => {
      assert.ok(heading && words(heading) <= 5, `details[${i}] heading "${heading}" > 5 words`)
      assert.ok(sentences(body) >= 2 && sentences(body) <= 4, `details[${i}] body has ${sentences(body)} sentences`)
    })
    const total = details.reduce((n, d) => n + words(d.body), 0)
    assert.ok(total >= 150 && total <= 250, `details total ${total} words, want 150–250`)
  })
}
