import CopyButton from './CopyButton.jsx'

const LANGUAGE_LABELS = { json: 'JSON', js: 'JavaScript', javascript: 'JavaScript', ts: 'TypeScript', py: 'Python', python: 'Python', bash: 'Terminal', sh: 'Terminal', shell: 'Terminal', powershell: 'PowerShell', md: 'Markdown', markdown: 'Markdown', yaml: 'YAML', yml: 'YAML', toml: 'TOML' }

/** Returns a cleaned example or null when there's nothing worth showing. */
export function normalizeExample(example) {
  if (!example || typeof example !== 'object') return null
  const steps = Array.isArray(example.steps) ? example.steps.filter((s) => typeof s === 'string' && s.trim()) : []
  const code = example.code && typeof example.code.content === 'string' && example.code.content.trim() ? example.code : null
  const prompt = typeof example.prompt === 'string' && example.prompt.trim() ? example.prompt : null
  const ex = {
    title: example.title || 'Worked example',
    scenario: example.scenario || '',
    steps,
    prompt,
    code,
    expected: example.expected_result || '',
  }
  return ex.scenario || steps.length || prompt || code || ex.expected ? ex : null
}

export default function WorkedExample({ example, stageTitle }) {
  const ex = normalizeExample(example)
  if (!ex) return null
  const language = ex.code?.language ?? ''
  const languageLabel = LANGUAGE_LABELS[language.toLowerCase()] ?? (language || 'Code')

  return (
    <section aria-labelledby="example-title" className="example">
      <p className="eyebrow">Try it: worked example</p>
      <h2 id="example-title">{ex.title}</h2>
      {ex.scenario && (
        <p className="example__scenario">
          <strong>The situation:</strong> {ex.scenario}
        </p>
      )}

      {ex.steps.length > 0 && (
        <>
          <h3>Step by step</h3>
          <ol className="example__steps">
            {ex.steps.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </>
      )}

      {ex.prompt && (
        <div className="snippet">
          <div className="snippet__bar">
            <span>Prompt to paste into your assistant</span>
            <CopyButton text={ex.prompt} label="Copy prompt" />
          </div>
          <pre className="snippet__body snippet__body--prompt" tabIndex={0} aria-label={`Prompt for ${stageTitle}`}>
            {ex.prompt}
          </pre>
        </div>
      )}

      {ex.code && (
        <div className="snippet">
          <div className="snippet__bar">
            <span>{languageLabel}</span>
            <CopyButton text={ex.code.content} label="Copy code" />
          </div>
          <pre className="snippet__body" tabIndex={0} aria-label={`${languageLabel} snippet for ${stageTitle}`}>
            <code>{ex.code.content}</code>
          </pre>
        </div>
      )}

      {ex.expected && (
        <p className="example__expected">
          <strong>What you should see:</strong> {ex.expected}
        </p>
      )}
    </section>
  )
}
