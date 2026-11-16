export default function Status({ value, compact = false }: { value: string; compact?: boolean }) {
  const normalized = value || 'NOT_CALCULATED'
  const classification = normalized.replaceAll(' ', '_')
  const cls = classification.includes('FAIL') ? 'fail' : classification.includes('REVIEW') || classification.includes('WARNING') || classification.includes('NOT_') ? 'review' : 'pass'
  return <span className={`status ${cls} ${compact ? 'compact' : ''}`}><span aria-hidden>{cls === 'pass' ? '✓' : cls === 'fail' ? '!' : 'i'}</span>{normalized.replaceAll('_', ' ')}</span>
}
