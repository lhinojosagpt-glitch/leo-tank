export default function Status({ value, compact = false }: { value: string; compact?: boolean }) {
  const normalized = value || 'NOT_CALCULATED'
  const cls = normalized.includes('FAIL') ? 'fail' : normalized.includes('REVIEW') || normalized.includes('WARNING') || normalized.includes('NOT_') ? 'review' : 'pass'
  return <span className={`status ${cls} ${compact ? 'compact' : ''}`}><span aria-hidden>{cls === 'pass' ? '✓' : cls === 'fail' ? '!' : 'i'}</span>{normalized.replaceAll('_', ' ')}</span>
}
