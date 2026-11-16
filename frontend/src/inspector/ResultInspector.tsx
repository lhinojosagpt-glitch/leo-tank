import { useEffect, useMemo, useRef, useState } from 'react'
import type { ModuleId } from '../app/config'
import Status from '../shared/Status'
import { displayIdentity } from '../app/displayIdentity'

type Props = {
  result?: any
  activeModule: ModuleId
  selected?: any
  onSelect: (entity: any) => void
  onOpenTrace: (trace: any) => void
  onNavigate: (module: ModuleId) => void
  onResolveCheck: (check: any) => void
}

function display(value: any, key = '') {
  if (typeof value === 'number') {
    if (key.toLowerCase().includes('utilization')) return `${(value * 100).toFixed(2)} %`
    return Math.abs(value) >= 10000 ? value.toLocaleString('en-US', { maximumFractionDigits: 1 }) : value.toFixed(4).replace(/0+$/, '').replace(/\.$/, '')
  }
  return displayIdentity(value ?? '-')
}

export default function ResultInspector({ result, activeModule, selected, onSelect, onOpenTrace, onNavigate, onResolveCheck }: Props) {
  const [tab, setTab] = useState<'summary' | 'properties' | 'checks' | 'calculation'>('summary')
  const previousSelection = useRef(selected?.id)
  useEffect(() => {
    if (selected?.id && selected.id !== previousSelection.current) setTab('properties')
    previousSelection.current = selected?.id
  }, [selected?.id])
  const moduleKey = ['shell', 'bottom', 'wind', 'seismic', 'anchorage'].includes(activeModule) ? activeModule : 'shell'
  const module = result?.modules?.[moduleKey]
  const props = useMemo(() => selected ? Object.entries(selected).filter(([, value]) => ['string', 'number', 'boolean'].includes(typeof value)).slice(0, 16) : [], [selected])
  const maxHoopCourse = result?.modules?.seismic?.values?.hoop?.reduce((a: any, b: any) => !a || b.utilization > a.utilization ? b : a, undefined)
  const openJ = () => {
    const trace = result?.modules?.seismic?.traces?.find((item: any) => item.symbol === 'J')
    if (trace) { onOpenTrace(trace); setTab('calculation') }
  }
  const openHoop = () => {
    const course = maxHoopCourse?.course || 1
    const entity = result?.geometry?.courses?.find((item: any) => item.id === `course-${course}`)
    if (entity) onSelect({ ...entity, course, entityType: 'shell_course' })
    const trace = result?.modules?.seismic?.traces?.find((item: any) => item.symbol === 'sigma_h' && item.inputs?.course === course)
    if (trace) onOpenTrace(trace)
    setTab('calculation')
  }
  const openCheck = (check: any) => {
    if (check.status === 'FAIL') { onResolveCheck(check); return }
    const trace = module?.traces?.find((item: any) => item.formula_id === check.formula_id || (check.related_entity && item.inputs?.course === Number(String(check.related_entity).split('-')[1])))
    if (trace) { onOpenTrace(trace); setTab('calculation') }
  }
  return <aside className="result-inspector panel">
    <div className="inspector-head"><div><span className="eyebrow">INSPECTOR</span><h2>{tab === 'summary' ? 'Resumen ejecutivo' : tab === 'properties' ? 'Propiedades' : tab === 'checks' ? 'Verificaciones' : 'Cálculo'}</h2></div>{result && <Status value={result.overall_status} compact />}</div>
    <div className="inspector-tabs">{(['summary', 'properties', 'checks', 'calculation'] as const).map(value => <button key={value} className={tab === value ? 'active' : ''} onClick={() => setTab(value)}>{value === 'summary' ? 'Resumen' : value === 'properties' ? 'Propiedades' : value === 'checks' ? 'Verificaciones' : 'Cálculo'}</button>)}</div>
    <div className="inspector-scroll">
      {!result ? <div className="inspector-empty"><div>Σ</div><strong>Sin resultados</strong><span>Ejecute el motor para habilitar checks y trazas.</span></div> : tab === 'summary' ? <>
        <div className="kpi-grid"><button onClick={openJ}><span>J sísmico</span><strong>{result.summary.seismic.J.toFixed(4)}</strong><small>Ver estabilidad y ecuación ›</small></button><button onClick={openHoop}><span>Máx. hoop</span><strong>{(result.summary.seismic.max_hoop_utilization * 100).toFixed(1)}%</strong><small>Course {maxHoopCourse?.course} ›</small></button></div>
        <div className="summary-modules">{['shell', 'bottom', 'wind', 'seismic', 'auto_anchor', 'anchorage'].map(key => {
          const value = result.summary[key]
          return <button key={key} onClick={() => onNavigate((key === 'auto_anchor' ? 'anchorage' : key) as ModuleId)}><span>{key.replace('_', ' ')}</span><Status value={value?.status || (value?.required ? 'PASS' : 'REVIEW')} compact /></button>
        })}</div>
        {selected && <div className="selection-summary"><span className="section-label">SELECCIÓN ACTIVA</span><strong>{displayIdentity(selected.name || selected.id)}</strong><p>{displayIdentity(selected.material || selected.entityType || selected.entity_type)}</p><button onClick={() => setTab('properties')}>Ver propiedades ›</button></div>}
      </> : tab === 'properties' ? (!selected ? <div className="inspector-empty"><strong>Ninguna entidad seleccionada</strong><span>Seleccione una plancha, curso, techo, fondo o anclaje.</span></div> : <div className="properties-list"><div className="selection-title"><span>{displayIdentity(selected.id)}</span><h3>{displayIdentity(selected.name || selected.id)}</h3>{selected.status && <Status value={selected.status} compact />}</div>{props.map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{display(value, key)}</strong></div>)}</div>) : tab === 'checks' ? <div className="check-list">{module?.checks?.length ? [...module.checks].sort((a: any, b: any) => (b.utilization || 0) - (a.utilization || 0)).map((check: any) => <button key={check.check_id} onClick={() => openCheck(check)}><div><strong>{displayIdentity(check.title)}</strong><span>{displayIdentity(check.standard_reference)}</span><small>Demanda {display(check.demand)} / Capacidad {display(check.capacity)} {check.unit}</small></div><div><b title={`Raw utilization: ${check.utilization}`}>{check.utilization == null ? '—' : `${(check.utilization * 100).toFixed(1)}%`}</b><Status value={check.status} compact /></div><i className="utilization-bar"><span style={{ width: `${Math.min((check.utilization || 0) * 100, 100)}%` }} /></i></button>) : <div className="inspector-empty"><strong>Sin verificaciones en este módulo</strong><span>Seleccione un módulo de cálculo.</span></div>}</div> : <div className="trace-compact">{module?.traces?.length ? module.traces.map((trace: any, index: number) => <button key={`${trace.formula_id}-${index}`} onClick={() => onOpenTrace(trace)}><span>{trace.symbol}</span><div><strong>{displayIdentity(trace.description)}</strong><small>{trace.display_result} {trace.unit}</small></div><b>›</b></button>) : <div className="inspector-empty"><strong>Sin trazas disponibles</strong><span>El módulo seleccionado no expone ecuaciones.</span></div>}</div>}
    </div>
  </aside>
}
