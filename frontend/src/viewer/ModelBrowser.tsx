import { useState } from 'react'
import { displayIdentity } from '../app/displayIdentity'

type Props = {
  spec?: any
  selected?: any
  hiddenIds: Set<string>
  isolateId?: string
  onSelect: (entity: any) => void
  onToggleHidden: (id: string) => void
  onIsolate: (id?: string) => void
}

const entityType = (entity: any) => entity?.entity_type || entity?.entityType

export default function ModelBrowser({ spec, selected, hiddenIds, isolateId, onSelect, onToggleHidden, onIsolate }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['shell', 'course-1']))
  const [menu, setMenu] = useState<{ x: number; y: number; entity: any }>()
  if (!spec) return <div className="model-browser empty-mini">Ejecute un cálculo para generar el árbol físico.</div>

  const toggle = (id: string) => setExpanded(current => {
    const next = new Set(current)
    next.has(id) ? next.delete(id) : next.add(id)
    return next
  })
  const select = (entity: any) => onSelect({ ...entity, entityType: entityType(entity) })
  const context = (event: React.MouseEvent, entity: any) => { event.preventDefault(); setMenu({ x: event.clientX, y: event.clientY, entity }) }
  const row = (entity: any, label: string, level = 0, expandable = false, open = false) => <div className={`tree-row level-${level} ${selected?.id === entity.id ? 'selected' : ''}`} onContextMenu={event => context(event, entity)}>
    {expandable ? <button className="tree-expander" onClick={() => toggle(entity.id)} aria-label={`${open ? 'Contraer' : 'Expandir'} ${label}`}>{open ? '▾' : '▸'}</button> : <span className="tree-spacer" />}
    <button className="tree-label" onClick={() => select(entity)} title={label}><span className={`entity-icon ${entityType(entity)}`}>{entityType(entity) === 'shell_plate' ? '▱' : entityType(entity) === 'roof' ? '⌒' : '◇'}</span><span>{label}</span></button>
    <button className={`tree-eye ${hiddenIds.has(entity.id) ? 'off' : ''}`} onClick={() => onToggleHidden(entity.id)} aria-label={`${hiddenIds.has(entity.id) ? 'Mostrar' : 'Ocultar'} ${label}`}>{hiddenIds.has(entity.id) ? '○' : '●'}</button>
  </div>

  return <div className="model-browser" onClick={() => menu && setMenu(undefined)}>
    <div className="browser-heading"><div><span>MODEL BROWSER</span><strong>{displayIdentity(spec.tank_tag)}</strong></div>{isolateId && <button onClick={() => onIsolate(undefined)}>Mostrar todo</button>}</div>
    <div className="tree-scroll">
      {row({ id: 'shell', entity_type: 'shell', name: 'Shell' }, `Shell · ${spec.courses.length} cursos`, 0, true, expanded.has('shell'))}
      {expanded.has('shell') && spec.courses.map((course: any) => <div key={course.id}>
        {row(course, `${course.name} · ${course.plate_count} planchas`, 1, true, expanded.has(course.id))}
        {expanded.has(course.id) && course.plates.map((plate: any) => <div key={plate.id}>{row(plate, plate.id, 2)}</div>)}
      </div>)}
      {row(spec.bottom, 'Bottom · central + annular', 0)}
      {row(spec.physical_roof, 'Roof · geodesic dome', 0)}
      {row({ id: 'anchors', entity_type: 'anchor_group', name: 'Anchors', count: spec.anchors.length }, `Anchors · ${spec.anchors.length}`, 0, true, expanded.has('anchors'))}
      {expanded.has('anchors') && spec.anchors.map((anchor: any) => <div key={anchor.id}>{row(anchor, anchor.name, 1)}</div>)}
    </div>
    {menu && <div className="context-menu" style={{ left: Math.min(menu.x, window.innerWidth - 180), top: Math.min(menu.y, window.innerHeight - 150) }} onClick={event => event.stopPropagation()}>
      <button onClick={() => { onIsolate(menu.entity.id); select(menu.entity); setMenu(undefined) }}>Isolate</button>
      <button onClick={() => { onToggleHidden(menu.entity.id); setMenu(undefined) }}>Hide / Show</button>
      <button onClick={() => { select(menu.entity); setMenu(undefined) }}>Properties</button>
    </div>}
  </div>
}
