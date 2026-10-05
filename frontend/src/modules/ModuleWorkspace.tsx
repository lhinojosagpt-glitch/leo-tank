import { useMemo, useState } from 'react'
import type { ModuleId } from '../app/config'
import { moduleMeta } from '../app/config'
import { fieldsByModule, getAtPath, type FieldDef } from './fieldDefinitions'
import ModelBrowser from '../viewer/ModelBrowser'
import TankViewer from '../viewer/TankViewer'
import Status from '../shared/Status'

type Props = {
  state: any
  activeModule: ModuleId
  onNavigate: (module: ModuleId) => void
}

function Field({ field, value, error, onChange }: { field: FieldDef; value: any; error?: string; onChange: (value: any) => void }) {
  const id = field.path.replaceAll('.', '-')
  return <label className={`engineering-field ${field.readOnly ? 'readonly' : ''} ${error ? 'invalid' : ''}`} htmlFor={id}>
    <div><span>{field.label}</span>{field.symbol && <button type="button" className="symbol" title={field.help || field.label}>{field.symbol}</button>}<em>{field.kind}</em></div>
    <div className="field-control"><input id={id} type={field.type || 'number'} step={field.step} value={value ?? ''} readOnly={field.readOnly} onChange={event => onChange(field.type === 'text' ? event.target.value : Number(event.target.value))} /><b>{field.unit}</b></div>
    <small>Fuente: {field.source}</small>
    {error && <p>{error}</p>}
  </label>
}

function InputGrid({ module, inputs, validation, onUpdate }: { module: ModuleId; inputs: any; validation: Record<string, string>; onUpdate: (path: string, value: any) => void }) {
  const fields = fieldsByModule[module] || []
  return <div className="input-form"><div className="form-section-head"><div><span className="section-label">PARÁMETROS DEL MÓDULO</span><strong>{fields.length} valores inspeccionables</strong></div><span className="value-legend"><i className="user" /> User input <i className="standard" /> Standard / reference</span></div><div className="field-grid">{fields.map(field => <Field key={field.path} field={field} value={getAtPath(inputs, field.path)} error={validation[field.path]} onChange={value => onUpdate(field.path, value)} />)}</div></div>
}

function CourseTable({ state, edit = false }: { state: any; edit?: boolean }) {
  const courses = state.result?.modules?.shell?.values?.courses || state.draftInputs?.shell?.courses?.map((course: any, index: number) => ({ course: index + 1, height_m: course.height_m, selected_mm: course.thickness_mm, status: 'NOT_CALCULATED' })) || []
  const select = (course: number) => state.selectCourse(course)
  const openDesign = (course: number) => {
    select(course)
    const trace = state.result?.modules?.shell?.traces?.find((item: any) => item.symbol === 'td' && item.description.startsWith(`Course ${course}:`))
    if (trace) state.openTrace(trace)
  }
  return <div className="data-table-wrap"><table className="engineering-table"><thead><tr><th>Course</th><th>Height</th><th>Material</th><th>CA</th><th>Required design</th><th>Required test</th><th>Selected</th><th>Util.</th><th>Status</th></tr></thead><tbody>{courses.map((row: any, index: number) => {
    const source = state.draftInputs.shell.courses[index]
    return <tr key={row.course} className={state.selectedEntity?.course === row.course ? 'selected' : ''} onClick={() => select(row.course)}><td><button onClick={() => select(row.course)}>C{String(row.course).padStart(2, '0')}</button></td><td>{edit ? <input type="number" value={source.height_m} onChange={event => state.updateInput(`shell.courses[${index}].height_m`, Number(event.target.value))} /> : `${row.height_m.toFixed(3)} m`}</td><td>{edit ? <input value={source.material} onChange={event => state.updateInput(`shell.courses[${index}].material`, event.target.value)} /> : source.material.replace('ASTM ', '')}</td><td>{state.draftInputs.shell.corrosion_allowance_mm.toFixed(1)} mm</td><td><button className="calculation-link" onClick={event => { event.stopPropagation(); openDesign(row.course) }}>{row.design_mm != null ? `${row.design_mm.toFixed(4)} mm` : '-'}</button></td><td>{row.hydrotest_mm != null ? `${row.hydrotest_mm.toFixed(4)} mm` : '-'}</td><td>{edit ? <div className="cell-input"><input type="number" value={source.thickness_mm} onChange={event => state.updateInput(`shell.courses[${index}].thickness_mm`, Number(event.target.value))} /><span>mm</span></div> : `${row.selected_mm.toFixed(1)} mm`}</td><td>{row.utilization != null ? `${(row.utilization * 100).toFixed(1)}%` : '-'}</td><td><Status value={row.status} compact /></td></tr>
  })}</tbody></table></div>
}

function EngineeringModel({ state, showBrowser = true }: { state: any; showBrowser?: boolean }) {
  const [hiddenIds, setHiddenIds] = useState<Set<string>>(new Set())
  const [isolateId, setIsolateId] = useState<string>()
  const toggleHidden = (id: string) => setHiddenIds(current => { const next = new Set(current); next.has(id) ? next.delete(id) : next.add(id); return next })
  return <div className={`engineering-model ${showBrowser ? '' : 'viewer-only'}`}>
    {showBrowser && <ModelBrowser spec={state.result?.geometry} selected={state.selectedEntity} hiddenIds={hiddenIds} isolateId={isolateId} onSelect={state.selectEntity} onToggleHidden={toggleHidden} onIsolate={setIsolateId} />}
    <TankViewer spec={state.result?.geometry} selected={state.selectedEntity} hiddenIds={hiddenIds} isolateId={isolateId} onSelect={state.selectEntity} />
  </div>
}

function ResultValues({ state, module }: { state: any; module: ModuleId }) {
  const resultModule = state.result?.modules?.[module]
  if (!resultModule) return <div className="workspace-empty"><strong>No calculation run selected.</strong><span>Calcule para ver resultados de {moduleMeta[module].title}.</span></div>
  if (module === 'shell') return <CourseTable state={state} />
  if (module === 'seismic') {
    const v = resultModule.values
    const groups = [
      ['SPECTRUM', ['Sp', 'Ss', 'S1', 'Fa', 'Fv', 'Ts_s', 'SDS', 'Ai', 'Ac', 'Tc_s']],
      ['DYNAMIC LIQUID RESPONSE', ['Wi_N', 'Wc_N', 'Vi_N', 'Vc_N', 'V_N', 'Xi_m', 'Xc_m']],
      ['STABILITY', ['Mrw_Nm', 'Ms_Nm', 'Av', 'Ge', 'wa_N_cm', 'wt_N_cm', 'J']],
    ]
    return <div className="result-groups">{groups.map(([title, keys]: any) => <section key={title}><span className="section-label">{title}</span><div>{keys.map((key: string) => <button key={key} onClick={() => { const trace = resultModule.traces.find((item: any) => item.symbol === key.replace('_s', '').replace('_N', '').replace('_Nm', '').replace('_m', '') || item.formula_id.endsWith(`_${key.toUpperCase()}`)); if (trace) state.openTrace(trace) }}><span>{key}</span><strong>{typeof v[key] === 'number' ? v[key].toLocaleString('en-US', { maximumFractionDigits: 4 }) : '-'}</strong></button>)}</div></section>)}</div>
  }
  const flat = Object.entries(resultModule.values || {}).filter(([, value]) => ['number', 'string', 'boolean'].includes(typeof value))
  return <div className="metric-grid">{flat.map(([key, value]: any) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{typeof value === 'number' ? value.toLocaleString('en-US', { maximumFractionDigits: 4 }) : String(value)}</strong></div>)}</div>
}

function ChecksView({ state, module }: { state: any; module: ModuleId }) {
  const checks = state.result?.modules?.[module]?.checks || []
  if (!checks.length) return <div className="workspace-empty"><strong>Sin verificaciones disponibles</strong><span>Ejecute el cálculo o seleccione un módulo con checks.</span></div>
  return <div className="checks-workspace">{checks.map((check: any) => <article key={check.check_id}><div><span className="section-label">{check.reference}</span><h3>{check.name}</h3><p>{check.note}</p></div><div className="check-measures"><span>Demanda <b>{check.demand.toLocaleString('en-US', { maximumFractionDigits: 4 })} {check.unit}</b></span><span>Capacidad <b>{check.capacity.toLocaleString('en-US', { maximumFractionDigits: 4 })} {check.unit}</b></span><span>Utilización <b>{(check.utilization * 100).toFixed(2)}%</b></span><Status value={check.status} /></div></article>)}</div>
}

function Overview({ state, onNavigate }: { state: any; onNavigate: (module: ModuleId) => void }) {
  return <div className="overview-grid"><section className="hero-panel"><span className="eyebrow">TANK T-78 · ENGINEERING WORKSPACE</span><h2>Diseño, cálculo y geometría en un mismo modelo de información.</h2><p>Trabaje por disciplina, seleccione entidades físicas y acceda a la traza correspondiente sin abandonar el viewport.</p><div><button className="primary" onClick={() => onNavigate('shell')}>Abrir casco</button><button className="secondary" onClick={() => onNavigate('review')}>Revisar inputs</button></div></section><section className="overview-status"><span className="section-label">ESTADO ACTUAL</span><div><span>Revisión</span><strong>{state.revision ? `BASELINE R${state.revision}` : 'Borrador sin guardar'}</strong></div><div><span>Run</span><strong>{state.activeRun?.id?.slice(0, 12) || 'No calculado'}</strong></div><div><span>Inputs</span><strong>{Object.keys(state.validation).length ? `${Object.keys(state.validation).length} errores` : 'Completos'}</strong></div><div><span>Modelo 3D</span><strong>{state.result ? '192 shell plates' : 'Pendiente de cálculo'}</strong></div></section><section className="quick-modules">{(['geometry', 'shell', 'seismic', 'anchorage', 'results', 'history'] as ModuleId[]).map(id => <button key={id} onClick={() => onNavigate(id)}><span>{moduleMeta[id].eyebrow}</span><strong>{moduleMeta[id].title}</strong><p>{moduleMeta[id].description}</p></button>)}</section></div>
}

function Review({ state, onNavigate }: { state: any; onNavigate: (module: ModuleId) => void }) {
  const items = [
    ['Inputs complete', !Object.keys(state.validation).length, 'geometry'],
    ['Geometry consistent', !state.validation['geometry.design_liquid_height_m'], 'geometry'],
    ['Materials complete', Boolean(state.draftInputs?.materials?.shell?.name), 'materials'],
    ['Wind parameters', Boolean(state.draftInputs?.wind?.velocity_m_s), 'wind'],
    ['Seismic parameters', Boolean(state.draftInputs?.seismic?.Sp), 'seismic'],
    ['Anchorage', Boolean(state.draftInputs?.anchorage?.selected_bolts), 'anchorage'],
  ] as const
  return <div className="review-workspace"><div className="review-score"><span>DESIGN READINESS</span><strong>{items.filter(([, ok]) => ok).length}/{items.length}</strong><p>{Object.keys(state.validation).length ? 'Existen datos que requieren corrección.' : 'El borrador está listo para cálculo.'}</p></div><div className="review-list">{items.map(([label, ok, module]) => <button key={label} onClick={() => onNavigate(module as ModuleId)}><span className={ok ? 'ok' : 'warning'}>{ok ? '✓' : '!'}</span><div><strong>{label}</strong><small>{ok ? 'Completado' : 'Requiere atención'}</small></div><b>›</b></button>)}</div><div className="review-warning"><strong>2 advertencias de alcance</strong><p>Viento conserva resultados de reconstrucción y el diseño estructural del domo geodésico pertenece al proveedor.</p></div></div>
}

function GlobalResults({ state, onNavigate }: { state: any; onNavigate: (module: ModuleId) => void }) {
  if (!state.result) return <div className="workspace-empty"><strong>No calculation run selected.</strong><span>Ejecute el motor para generar el resumen global.</span></div>
  return <div className="global-results"><div className="overall-banner"><div><span>OVERALL</span><h2>{state.result.overall_status.replaceAll('_', ' ')}</h2><p>Perfil API650_12E_T78 · Motor {state.result.engine_version}</p></div><Status value={state.result.overall_status} /></div><div className="global-card-grid">{['shell', 'bottom', 'wind', 'seismic', 'anchorage'].map(key => <button key={key} onClick={() => onNavigate(key as ModuleId)}><span>{key}</span><Status value={state.result.summary[key].status || 'PASS'} /><strong>{key === 'seismic' ? `J ${state.result.summary.seismic.J.toFixed(4)}` : key === 'shell' ? `${(state.result.summary.shell.max_utilization * 100).toFixed(1)}% max` : key === 'anchorage' ? `${state.result.summary.anchorage.selected_bolts} bolts` : 'Ver resultados'}</strong><small>Abrir módulo ›</small></button>)}</div></div>
}

function History({ state }: { state: any }) {
  if (!state.ids?.scenarioId) return <div className="workspace-empty"><strong>Sin historial persistido</strong><span>Guarde la primera revisión para iniciar el árbol BASELINE.</span></div>
  return <div className="history-workspace"><div className="history-head"><div><span className="section-label">ESCENARIO</span><h3>{state.history?.scenario?.name || 'BASELINE'}</h3></div><button className="secondary" onClick={() => state.refreshHistory()}>Actualizar</button></div><div className="revision-tree">{state.history?.revisions?.map((revision: any) => <article key={revision.id}><div className="revision-node"><span>R{revision.revision_number}</span></div><div><div className="revision-title"><strong>BASELINE · R{revision.revision_number}</strong>{revision.locked && <Status value="LOCKED" compact />}</div><p>{Object.keys(revision.changes || {}).length} cambio(s) · {new Date(revision.created_at).toLocaleString()}</p><div className="run-list">{revision.runs.length ? revision.runs.map((run: any) => <div key={run.id}><span>RUN</span><code>{run.id.slice(0, 12)}</code><Status value={run.status} compact /></div>) : <span>Sin runs asociados</span>}</div></div></article>) || <div className="workspace-empty">Cargando historial...</div>}</div></div>
}

function Variants({ state }: { state: any }) {
  const [rows, setRows] = useState([{ name: 'Sp 0.50', path: 'seismic.Sp', value: 0.5 }, { name: 'SG 0.90', path: 'product.specific_gravity', value: 0.9 }])
  const [matrix, setMatrix] = useState<any[]>([])
  const [running, setRunning] = useState(false)
  const paths = ['seismic.Sp', 'product.specific_gravity', 'geometry.design_liquid_height_m', 'bottom.annular_selected_mm', 'anchorage.selected_bolts', 'shell.courses[5].thickness_mm']
  const run = async () => {
    setRunning(true)
    try { const response = await fetch('/api/v1/variant-batches', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'UX parametric study', baseline_inputs: state.draftInputs, variants: rows.map(row => ({ name: row.name, changes: { [row.path]: row.value } })) }) }); if (!response.ok) throw new Error('Variant batch failed'); setMatrix((await response.json()).matrix) } finally { setRunning(false) }
  }
  return <div className="variants-workspace"><div className="variant-editor"><div className="form-section-head"><div><span className="section-label">VARIANT DEFINITIONS</span><strong>Baseline: {state.revision ? `R${state.revision}` : 'draft'}</strong></div><button className="secondary" onClick={() => setRows([...rows, { name: `Variante ${rows.length + 1}`, path: 'seismic.Sp', value: 0.45 }])}>+ Variante</button></div>{rows.map((row, index) => <div className="variant-row" key={index}><input value={row.name} onChange={event => setRows(rows.map((item, i) => i === index ? { ...item, name: event.target.value } : item))} /><select value={row.path} onChange={event => setRows(rows.map((item, i) => i === index ? { ...item, path: event.target.value } : item))}>{paths.map(path => <option key={path}>{path}</option>)}</select><input type="number" value={row.value} onChange={event => setRows(rows.map((item, i) => i === index ? { ...item, value: Number(event.target.value) } : item))} /><button onClick={() => setRows(rows.filter((_, i) => i !== index))}>×</button></div>)}<button className="primary" onClick={run} disabled={running || !rows.length}>{running ? 'Calculando variantes...' : 'Ejecutar batch'}</button></div>{matrix.length > 0 && <div className="data-table-wrap"><table className="engineering-table"><thead><tr><th>Variante</th><th>Estado</th><th>J</th><th>Shell máx.</th><th>Hoop máx.</th><th>Bolts</th></tr></thead><tbody>{matrix.map(row => <tr key={row.variant_id}><td>{row.variant_name}</td><td><Status value={row.status} compact /></td><td>{row.J.toFixed(4)}</td><td>{(row.max_shell_utilization * 100).toFixed(1)}%</td><td>{(row.max_seismic_hoop_utilization * 100).toFixed(1)}%</td><td>{(row.bolt_utilization * 100).toFixed(1)}%</td></tr>)}</tbody></table></div>}</div>
}

export default function ModuleWorkspace({ state, activeModule, onNavigate }: Props) {
  const meta = moduleMeta[activeModule]
  const showTabs = !['overview', 'review', 'results', 'variants', 'history'].includes(activeModule)
  const modelModule = ['geometry', 'shell', 'bottom', 'roof', 'anchorage'].includes(activeModule)
  const mainContent = useMemo(() => {
    if (!state.draftInputs) return <div className="workspace-empty"><strong>Cargando datos del proyecto...</strong></div>
    if (activeModule === 'overview') return <Overview state={state} onNavigate={onNavigate} />
    if (activeModule === 'review') return <Review state={state} onNavigate={onNavigate} />
    if (activeModule === 'results') return <GlobalResults state={state} onNavigate={onNavigate} />
    if (activeModule === 'history') return <History state={state} />
    if (activeModule === 'variants') return <Variants state={state} />
    if (activeModule === 'code') return <div className="code-capabilities"><InputGrid module="code" inputs={state.draftInputs} validation={state.validation} onUpdate={state.updateInput} /><section><span className="section-label">CALCULATION CAPABILITIES</span>{[['Shell One-Foot', 'IMPLEMENTED'], ['Seismic Annex E · T-78', 'IMPLEMENTED'], ['Wind coefficient chain', 'REVIEW'], ['Geodesic roof structural design', 'NOT IMPLEMENTED'], ['Nozzles / API 653 / FEA', 'NOT IMPLEMENTED']].map(([name, status]) => <div key={name}><strong>{name}</strong><Status value={status} compact /></div>)}</section></div>
    if (activeModule === 'shell' && state.activeMode === 'inputs') return <div className="shell-inputs"><InputGrid module="shell" inputs={state.draftInputs} validation={state.validation} onUpdate={state.updateInput} /><CourseTable state={state} edit /></div>
    if (state.activeMode === 'inputs') return <InputGrid module={activeModule} inputs={state.draftInputs} validation={state.validation} onUpdate={state.updateInput} />
    if (state.activeMode === 'results') return <ResultValues state={state} module={activeModule} />
    return <ChecksView state={state} module={activeModule} />
  }, [activeModule, onNavigate, state])

  return <section className="main-workspace panel">
    <header className="workspace-header"><div><span className="eyebrow">{meta.eyebrow}</span><h1>{meta.title}</h1><p>{meta.description}</p></div><div className="workspace-command">{state.dirty && <span className="dirty-badge">● CAMBIOS SIN GUARDAR</span>}{showTabs && <button className="secondary" onClick={() => state.setActiveMode('inputs')}>Editar todos los parámetros</button>}</div></header>
    {showTabs && <div className="workspace-tabs">{(['inputs', 'results', 'checks'] as const).map(mode => <button key={mode} className={state.activeMode === mode ? 'active' : ''} onClick={() => state.setActiveMode(mode)}>{mode}</button>)}</div>}
    <div className={`workspace-content ${modelModule ? 'with-model' : ''}`}>
      {modelModule ? <><div className="module-data-pane">{mainContent}</div><div className="module-model-pane"><EngineeringModel state={state} showBrowser={activeModule === 'geometry' || activeModule === 'shell'} />{activeModule === 'roof' && <div className="model-scope-note"><strong>Geodesic roof geometry: REPRESENTATIVE</strong><span>Detailed structural design: SUPPLIER SCOPE / NOT IMPLEMENTED</span></div>}</div></> : mainContent}
    </div>
  </section>
}
