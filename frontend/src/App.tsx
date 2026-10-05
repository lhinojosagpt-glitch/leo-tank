import { useCallback, useMemo, useState } from 'react'
import TankViewer from './viewer/TankViewer'

const wizard = ['Proyecto', 'Código', 'Geometría', 'Producto', 'Materiales', 'Casco', 'Fondo', 'Viento', 'Sismo', 'Techo / cargas', 'Anclaje', 'Revisar', 'Calcular']

const deepClone = <T,>(v: T): T => JSON.parse(JSON.stringify(v))

function Status({ value }: { value: string }) {
  const cls = value.includes('FAIL') ? 'fail' : value.includes('REVIEW') || value.includes('WARNING') ? 'review' : 'pass'
  return <span className={`status ${cls}`}><span aria-hidden>{cls === 'pass' ? '✓' : cls === 'fail' ? '!' : 'i'}</span>{value.replaceAll('_', ' ')}</span>
}

export default function App() {
  const [fixture, setFixture] = useState<any>()
  const [inputs, setInputs] = useState<any>()
  const [result, setResult] = useState<any>()
  const [busy, setBusy] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState(1)
  const [activeModule, setActiveModule] = useState('shell')
  const [selectedTrace, setSelectedTrace] = useState<any>()
  const [revision, setRevision] = useState(0)
  const [dirty, setDirty] = useState(false)
  const [message, setMessage] = useState('Cargue el caso verificado T-78 para comenzar.')

  const loadExample = async () => {
    setBusy(true)
    try {
      const response = await fetch('/api/v1/fixtures/T78_2019')
      if (!response.ok) throw new Error('No se pudo cargar el fixture')
      const value = await response.json()
      setFixture(value); setInputs(deepClone(value)); setResult(undefined); setRevision(0); setDirty(false)
      setMessage('Fixture T78_2019 cargado con procedencia documental.')
    } catch (error: any) { setMessage(error.message) } finally { setBusy(false) }
  }

  const calculate = async () => {
    if (!inputs) return
    setBusy(true)
    try {
      const response = await fetch('/api/v1/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ inputs }) })
      if (!response.ok) throw new Error('El cálculo no pudo completarse')
      const value = await response.json()
      setResult(value); setDirty(false); setRevision(r => r || 1)
      setMessage(`Cálculo completado · SHA ${value.input_sha256.slice(0, 12)}…`)
      setSelectedTrace(value.modules.shell.traces[0])
    } catch (error: any) { setMessage(error.message) } finally { setBusy(false) }
  }

  const update = (path: string, value: number) => {
    const next = deepClone(inputs)
    const bits = path.split('.')
    let cursor = next
    bits.slice(0, -1).forEach(k => cursor = cursor[k])
    cursor[bits.at(-1)!] = value
    setInputs(next); setDirty(Boolean(result)); setMessage(result ? 'Entrada modificada: el próximo cálculo debe crear una nueva revisión.' : 'Entrada modificada.')
  }

  const saveRevision = async () => {
    if (!inputs) return
    setBusy(true)
    try {
      let ids = JSON.parse(localStorage.getItem('tank650.ids') || 'null')
      if (!ids) {
        const project = await fetch('/api/v1/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'Tanque T-78', tank_tag: 'T-78' }) }).then(r => r.json())
        const scenario = await fetch(`/api/v1/projects/${project.id}/scenarios`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'BASELINE' }) }).then(r => r.json())
        ids = { projectId: project.id, scenarioId: scenario.id, revisionId: null }
      }
      const revisionResponse = await fetch(`/api/v1/scenarios/${ids.scenarioId}/revisions`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ inputs, derived_from_revision_id: ids.revisionId, changes: dirty ? { note: 'UI edited values; immutable successor revision' } : {} }) }).then(r => r.json())
      ids.revisionId = revisionResponse.id; localStorage.setItem('tank650.ids', JSON.stringify(ids)); setRevision(revisionResponse.revision_number)
      setMessage(`BASELINE R${revisionResponse.revision_number} guardada. Los runs anteriores permanecen inmutables.`)
    } catch (error: any) { setMessage(error.message) } finally { setBusy(false) }
  }

  const geometry = result?.geometry
  const module = result?.modules?.[activeModule]
  const shellRows = result?.modules?.shell?.values?.courses || []
  const selectedRow = shellRows.find((r: any) => r.course === selectedCourse)
  const maxUtil = result?.summary?.seismic?.max_hoop_utilization || 0
  const onSelectCourse = useCallback((course: number) => setSelectedCourse(course), [])
  const projectLabel = inputs?.project?.tank_tag || 'Sin proyecto'
  const revisionLabel = revision ? `BASELINE · R${revision}` : 'BORRADOR'

  const auditInputs = useMemo(() => selectedTrace ? Object.entries(selectedTrace.inputs || {}) : [], [selectedTrace])

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark">T6</div><div><strong>TANK650 ENGINE</strong><span>API 650 Calculation & Parametric Tank Design</span></div></div>
      <div className="run-context"><span>Proyecto <strong>{projectLabel}</strong></span><span>Escenario <strong>{revisionLabel}</strong></span><span>Perfil <strong>API650_12E_T78</strong></span></div>
      <div className="header-actions"><button className="secondary" onClick={saveRevision} disabled={!inputs || busy}>Guardar revisión</button><button className="primary" onClick={calculate} disabled={!inputs || busy}>{busy ? 'Procesando…' : 'Calcular'}</button></div>
    </header>

    <main className="workspace">
      <aside className="wizard-panel panel">
        <div className="panel-title"><div><span className="eyebrow">FLUJO DE DISEÑO</span><h2>Configuración</h2></div><span className="counter">{inputs ? '12/13' : '0/13'}</span></div>
        <button className="load-example" onClick={loadExample} disabled={busy}>＋ Cargar ejemplo T-78</button>
        <nav className="wizard-list">{wizard.map((item, i) => <button key={item} className={`${i === 5 ? 'active' : ''} ${inputs ? (i === 12 && !result ? 'pending' : 'complete') : ''}`}><span className="step-number">{inputs && (i !== 12 || result) ? '✓' : i + 1}</span><span>{item}</span>{i === 5 && <span className="current-dot" />}</button>)}</nav>
      </aside>

      <section className="center-column">
        <section className="input-strip panel">
          <div className="section-heading"><div><span className="eyebrow">CASCO · MÉTODO 1-FOOT</span><h1>Geometría y condición de diseño</h1></div>{dirty && <Status value="NUEVA REVISIÓN REQUERIDA" />}</div>
          <div className="input-grid">
            <label>Diámetro nominal <span>D</span><div><input type="number" step="0.001" value={inputs?.geometry?.nominal_diameter_m ?? ''} onChange={e => update('geometry.nominal_diameter_m', +e.target.value)} disabled={!inputs} /><b>m</b></div><small>TANK 2016 · pág. 3</small></label>
            <label>Altura de líquido <span>H</span><div><input type="number" step="0.001" value={inputs?.geometry?.design_liquid_height_m ?? ''} onChange={e => update('geometry.design_liquid_height_m', +e.target.value)} disabled={!inputs} /><b>m</b></div><small>TANK 2016 · pág. 3</small></label>
            <label>Gravedad específica <span>G</span><div><input type="number" step="0.0001" value={inputs?.product?.specific_gravity ?? ''} onChange={e => update('product.specific_gravity', +e.target.value)} disabled={!inputs} /><b>—</b></div><small>TANK 2016 · pág. 3</small></label>
            <label>Aceleración pico <span>Sp</span><div><input type="number" step="0.01" value={inputs?.seismic?.Sp ?? ''} onChange={e => update('seismic.Sp', +e.target.value)} disabled={!inputs} /><b>g</b></div><small>TANK 2016 · pág. 11</small></label>
          </div>
        </section>

        <section className="viewer-card panel">
          <div className="model-header"><div><span className="eyebrow">GEOMETRÍA PARAMÉTRICA</span><h2>Modelo del tanque</h2></div><div className="segmented"><button className="selected">Sólido</button><button>Transparente</button><button>Sección</button></div></div>
          {geometry ? <TankViewer spec={geometry} selectedCourse={selectedCourse} onSelectCourse={onSelectCourse} /> : <div className="empty-state"><div className="empty-tank" /><h3>Modelo aún no generado</h3><p>Cargue el fixture y ejecute el motor para crear el snapshot geométrico.</p></div>}
          {geometry && <div className="model-tree"><strong>Tank T-78</strong><span>▾ Shell</span>{geometry.courses.map((c: any) => <button key={c.id} className={selectedCourse === +c.id.split('-')[1] ? 'selected' : ''} onClick={() => setSelectedCourse(+c.id.split('-')[1])}>└ {c.name} <b>{c.thickness_mm} mm</b></button>)}<span>▸ Bottom</span><span>▸ Roof</span><span>▸ Anchors · 60</span></div>}
        </section>
      </section>

      <aside className="results-panel panel">
        <div className="panel-title"><div><span className="eyebrow">RESULTADOS</span><h2>Resumen ejecutivo</h2></div>{result && <Status value={result.overall_status} />}</div>
        {!result ? <div className="empty-results"><div className="pulse-icon">∑</div><p>Los resultados, verificaciones y ecuaciones aparecerán después del cálculo.</p></div> : <>
          <div className="kpi-row"><div><span>J sísmico</span><strong>{result.summary.seismic.J.toFixed(4)}</strong><small>anclaje mecánico requerido</small></div><div><span>Máx. hoop</span><strong>{(maxUtil * 100).toFixed(1)}%</strong><small>curso 6</small></div></div>
          <div className="module-list">
            {Object.entries(result.summary).filter(([k]) => ['shell','bottom','wind','seismic','auto_anchor','anchorage'].includes(k)).map(([key, value]: any) => <button key={key} onClick={() => setActiveModule(key === 'auto_anchor' ? 'seismic' : key)} className={activeModule === key ? 'selected' : ''}><span>{key.replace('_',' ')}</span><Status value={value.status || (value.required ? 'PASS' : 'REVIEW')} /></button>)}
          </div>
          <div className="course-detail"><div className="detail-head"><div><span className="eyebrow">CURSO SELECCIONADO</span><h3>Curso {selectedCourse}</h3></div>{selectedRow && <Status value={selectedRow.status} />}</div>{selectedRow && <><div className="measure"><span>Espesor requerido</span><strong>{Math.max(selectedRow.design_mm, selectedRow.hydrotest_mm).toFixed(3)} mm</strong></div><div className="measure"><span>Espesor seleccionado</span><strong>{selectedRow.selected_mm.toFixed(1)} mm</strong></div><div className="util-label"><span>Utilización</span><b>{(selectedRow.utilization * 100).toFixed(1)}%</b></div><div className="util-bar"><i style={{ width: `${Math.min(selectedRow.utilization * 100, 100)}%` }} /></div></>}</div>
          <div className="tabs">{['shell','seismic','anchorage'].map(k => <button className={activeModule === k ? 'active' : ''} onClick={() => setActiveModule(k)} key={k}>{k === 'shell' ? 'Casco' : k === 'seismic' ? 'Sismo' : 'Anclaje'}</button>)}</div>
          <div className="trace-list">{module?.traces?.slice(0, 12).map((trace: any, i: number) => <button key={`${trace.formula_id}-${i}`} className={selectedTrace === trace ? 'selected' : ''} onClick={() => setSelectedTrace(trace)}><span>{trace.symbol}</span><div><strong>{trace.description}</strong><small>{trace.display_result} {trace.unit}</small></div><b>›</b></button>)}</div>
        </>}
      </aside>
    </main>

    <section className="audit-drawer">
      <div className="audit-title"><div><span className="eyebrow">TRAZA DE CÁLCULO</span><h2>{selectedTrace?.formula_id || 'Seleccione un resultado auditable'}</h2></div>{selectedTrace && <Status value={selectedTrace.status} />}</div>
      {selectedTrace ? <div className="audit-grid"><div><span>Ecuación</span><code>{selectedTrace.expression}</code></div><div><span>Referencia</span><strong>{selectedTrace.reference}</strong><small>{selectedTrace.description}</small></div><div><span>Variables de entrada</span><ul>{auditInputs.slice(0, 8).map(([k,v]) => <li key={k}><b>{k}</b><code>{typeof v === 'number' ? v.toFixed(6) : String(v)}</code></li>)}</ul></div><div className="audit-result"><span>Resultado</span><strong>{selectedTrace.display_result}</strong><b>{selectedTrace.unit}</b><small>Raw: {selectedTrace.raw_result}</small></div></div> : <p className="audit-placeholder">Cada cálculo conserva fórmula, variables, unidades, resultado bruto, redondeo y referencia.</p>}
    </section>

    <footer className="statusbar"><span className="system-ok">● Motor {result?.engine_version || '0.1.0'} listo</span><span>{message}</span><span>SQLite local · API /api/v1 · {inputs?.source_documents?.length || 0} fuentes</span></footer>
  </div>
}

