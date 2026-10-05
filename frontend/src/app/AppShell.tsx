import { useState } from 'react'
import { modules, type ModuleId } from './config'
import { useTankWorkspace } from './state/useTankWorkspace'
import ModuleWorkspace from '../modules/ModuleWorkspace'
import ResultInspector from '../inspector/ResultInspector'
import CalculationInspector from '../inspector/CalculationInspector'
import Toast from '../shared/Toast'

export default function AppShell() {
  const state = useTankWorkspace()
  const [navCollapsed, setNavCollapsed] = useState(false)
  const projectLabel = state.draftInputs?.project?.tank_tag || 'T-78'
  const busyLabel = state.busyAction === 'saving' ? 'Guardando...' : state.busyAction === 'validating' ? 'Validando...' : state.busyAction === 'calculating' ? 'Calculando...' : state.busyAction === 'loading' ? 'Cargando...' : undefined
  const navigate = (module: ModuleId) => state.navigate(module)
  const groups = [...new Set(modules.map(item => item.group))]
  const completed = state.draftInputs ? 12 : 0

  return <div className={`app-shell ${navCollapsed ? 'nav-collapsed' : ''}`}>
    <header className="topbar">
      <div className="brand"><div className="brand-mark">T6</div><div><strong>TANK650 ENGINE</strong><span>Engineering calculation & parametric model</span></div></div>
      <div className="project-context">
        <div><span>Proyecto</span><strong>{projectLabel}</strong></div>
        <div><span>Escenario</span><strong>{state.revision ? `BASELINE · R${state.revision}` : 'BORRADOR'}</strong></div>
        <div><span>Perfil</span><strong>API650_12E_T78</strong></div>
        {state.dirty && <div className="top-dirty"><span>ESTADO</span><strong>● Cambios sin guardar</strong></div>}
      </div>
      <div className="header-actions"><button className="secondary" onClick={state.saveRevision} disabled={!state.draftInputs || Boolean(state.busyAction)} title="Crear una revisión inmutable del borrador">{state.busyAction === 'saving' ? 'Guardando...' : 'Guardar revisión'}</button><button className="primary" onClick={state.calculate} disabled={!state.draftInputs || Boolean(state.busyAction)} title="Validar y ejecutar el motor de cálculo">{busyLabel || 'Calcular'}</button></div>
    </header>

    <aside className="module-navigation panel">
      <div className="nav-head"><div><span className="eyebrow">WORKSPACES</span><strong>Diseño</strong></div><button onClick={() => setNavCollapsed(value => !value)} title={navCollapsed ? 'Expandir navegación' : 'Contraer navegación'}>{navCollapsed ? '›' : '‹'}</button></div>
      <button className="load-example" onClick={() => state.loadExample(false)} disabled={Boolean(state.busyAction)} title="Restablecer todos los datos al caso verificado T-78"><span>＋</span><b>Cargar ejemplo T-78</b></button>
      <div className="completion"><span><i style={{ width: `${completed / 13 * 100}%` }} /></span><b>{completed}/13</b></div>
      <nav>{groups.map(group => <div className="nav-group" key={group}><span>{group}</span>{modules.filter(item => item.group === group).map(item => <button key={item.id} className={state.activeModule === item.id ? 'active' : ''} onClick={() => navigate(item.id)} title={item.label} aria-current={state.activeModule === item.id ? 'page' : undefined}><i>{item.icon}</i><b>{item.label}</b>{state.activeModule === item.id && <em />}</button>)}</div>)}</nav>
    </aside>

    <ModuleWorkspace state={state} activeModule={state.activeModule} onNavigate={navigate} />

    <ResultInspector result={state.result} activeModule={state.activeModule} selected={state.selectedEntity} onSelect={state.selectEntity} onOpenTrace={state.openTrace} onNavigate={navigate} />

    <footer className="statusbar"><span className="system-ok">● Motor {state.result?.engine_version || '0.2.0'} listo</span><span className="status-message">{state.statusMessage}</span><span>{state.activeRun ? `${state.activeRun.persisted ? 'RUN' : 'DRAFT'} ${state.activeRun.id.slice(0, 12)}` : 'Sin run'} · SQLite local · API /api/v1</span></footer>

    <CalculationInspector trace={state.selectedTrace} entity={state.selectedEntity} state={state.calculationInspector} onChange={state.setCalculationInspector} />
    <Toast toast={state.toast} onClose={() => state.setToast(undefined)} />
  </div>
}
