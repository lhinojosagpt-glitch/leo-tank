import { useEffect, useMemo, useState } from 'react'
import Status from '../shared/Status'

async function json(url: string, init?: RequestInit) {
  const response = await fetch(url, init)
  if (!response.ok) throw new Error((await response.json().catch(() => ({})))?.detail || `HTTP ${response.status}`)
  return response.json()
}

export default function DesignAssistant({ state }: { state: any }) {
  const resolution = state.designResolution
  const [analysis, setAnalysis] = useState<any>()
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [studyId, setStudyId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [target, setTarget] = useState(1)
  const check = resolution.check
  const persisted = state.activeRun?.persisted
  const detail = useMemo(() => analysis?.failed_checks?.find((row: any) => row.check_id === check?.check_id), [analysis, check?.check_id])

  useEffect(() => {
    setAnalysis(undefined); setRecommendations([]); setStudyId(''); setError('')
    if (!resolution.open || !check || !persisted) return
    void json(`/api/v1/runs/${state.activeRun.id}/design-assistant/analyze`, { method: 'POST' }).then(setAnalysis).catch((reason: Error) => setError(reason.message))
  }, [resolution.open, check?.check_id, persisted, state.activeRun?.id])

  if (!resolution.open || !check) return null
  const runStudy = async () => {
    setBusy(true); setError('')
    try {
      const variables = detail?.adjustable_variables?.map((row: any) => row.id) || []
      const created = await json(`/api/v1/runs/${state.activeRun.id}/design-assistant/studies`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ check_id: check.check_id, objective: target === 1 ? 'MINIMUM_CHANGE_PASS' : `TARGET_UTILIZATION_${Math.round(target * 100)}`, variables, target_utilization: target, max_simulations: 500 }) })
      setStudyId(created.study_id)
      const value = await json(`/api/v1/design-studies/${created.study_id}/recommendations`)
      setRecommendations(value.recommendations || [])
    } catch (reason: any) { setError(String(reason.message || reason)) } finally { setBusy(false) }
  }
  const useDraft = async (candidate: any, partial = false) => {
    const selected_variables = partial ? Object.keys(candidate.changes).slice(0, 1) : undefined
    const applied = await json(`/api/v1/design-studies/${studyId}/recommendations/${candidate.id}/apply`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ selected_variables }) })
    state.applyDraftChanges(applied.draft_changes)
    state.setDesignResolution({ open: false })
  }
  return <div className="assistant-backdrop" role="dialog" aria-modal="true" aria-label="Design Resolution">
    <section className="assistant-drawer">
      <header><div><span className="eyebrow">ENGINEERING DESIGN ASSISTANT</span><h2>Resolver: {check.title}</h2><p>Simulación determinista y auditable. El ingeniero conserva la decisión final.</p></div><button onClick={() => state.setDesignResolution({ open: false })} aria-label="Cerrar">×</button></header>
      <div className="assistant-grid">
        <section><span className="section-label">POR QUÉ NO CUMPLE</span><div className="failure-card"><Status value={check.status} /><dl><div><dt>Demanda</dt><dd>{check.demand?.toFixed(4)} {check.unit}</dd></div><div><dt>Límite / capacidad</dt><dd>{check.capacity?.toFixed(4)} {check.unit}</dd></div><div><dt>Diferencia</dt><dd>+{Math.max(0, check.demand - check.capacity).toFixed(4)} {check.unit}</dd></div><div><dt>Utilización</dt><dd>{(check.utilization * 100).toFixed(2)}%</dd></div></dl><p>{check.description || check.message}</p><small>{check.standard_reference}</small></div></section>
        <section><span className="section-label">VARIABLES QUE INFLUYEN</span>{detail?.adjustable_variables?.map((row: any) => <article className="variable-card" key={row.id}><div><strong>{row.name}</strong><span>{row.classification}</span></div><b>{row.current_value} {row.unit}</b><small>{row.influence} · editable</small></article>)}{detail?.fixed_variables?.map((row: any) => <article className="variable-card fixed" key={row.id}><div><strong>🔒 {row.name}</strong><span>{row.classification}</span></div><b>{row.current_value} {row.unit}</b><small>No se modifica para obtener PASS</small></article>)}</section>
      </div>
      {!persisted && <div className="assistant-notice">Guarde una revisión y calcúlela para ejecutar estudios con trazabilidad de `run_id`.</div>}
      {persisted && <section className="study-config"><div><span className="section-label">OBJETIVO DEL ESTUDIO</span><select value={target} onChange={event => setTarget(Number(event.target.value))}><option value={1}>Cambio mínimo para PASS</option><option value={0.95}>Utilización ≤ 95%</option><option value={0.9}>Utilización ≤ 90%</option></select></div><button className="primary" onClick={runStudy} disabled={busy || !detail?.adjustable_variables?.length}>{busy ? 'Ejecutando simulaciones…' : 'Buscar alternativas'}</button></section>}
      {error && <div className="assistant-error">{error}</div>}
      {recommendations.length > 0 ? <section className="candidate-list"><span className="section-label">ALTERNATIVAS SIMULADAS</span>{recommendations.map((candidate: any, index) => <article key={candidate.id}><div><b>#{index + 1} {candidate.label}</b><Status value={candidate.target_check.status} compact /></div><p>{Object.entries(candidate.changes).map(([path, value]) => `${path}: ${value}`).join(' · ')}</p><dl><div><dt>Resultado</dt><dd>{candidate.target_check.demand?.toFixed(4)} / {candidate.target_check.capacity?.toFixed(4)}</dd></div><div><dt>Utilización</dt><dd>{(candidate.target_check.utilization * 100).toFixed(2)}%</dd></div><div><dt>Run</dt><dd>{candidate.candidate_run_id.slice(0, 12)}</dd></div></dl><footer><button className="primary" onClick={() => useDraft(candidate)}>Usar como borrador</button><button className="secondary" onClick={() => useDraft(candidate, true)}>Aplicar parcialmente</button></footer></article>)}</section> : !busy && persisted && detail && <div className="assistant-notice">{studyId ? 'No se encontró una solución PASS dentro del espacio de diseño evaluado. El anclaje mecánico existente continúa siendo la ruta válida cuando sus verificaciones cumplen.' : 'Configure el objetivo y ejecute el estudio. No se modificará la revisión activa.'}</div>}
      <footer className="assistant-footer"><button className="secondary" onClick={() => state.setDesignResolution({ open: false })}>Ignorar / cerrar</button><span>SIMULATION PREVIEW · NOT SAVED</span></footer>
    </section>
  </div>
}
