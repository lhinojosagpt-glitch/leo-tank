import { useCallback, useEffect, useMemo, useState } from 'react'
import { diffInputs, setAtPath } from '../../modules/fieldDefinitions'
import type { ModuleId } from '../config'
import { moduleFromPath, modules } from '../config'
import type { ToastState } from '../../shared/Toast'

const clone = <T,>(value: T): T => JSON.parse(JSON.stringify(value))

async function api<T = any>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) {
    let message = `HTTP ${response.status}`
    try { const body = await response.json(); message = body.detail?.message || body.detail || message } catch { /* response was not JSON */ }
    throw new Error(String(message))
  }
  return response.json()
}

type StoredIds = { projectId: string; scenarioId: string; revisionId?: string | null }

export function useTankWorkspace() {
  const [fixture, setFixture] = useState<any>()
  const [draftInputs, setDraftInputs] = useState<any>()
  const [persistedInputs, setPersistedInputs] = useState<any>()
  const [result, setResult] = useState<any>()
  const [activeRun, setActiveRun] = useState<any>()
  const [activeModule, setActiveModule] = useState<ModuleId>(() => moduleFromPath(window.location.pathname))
  const [activeMode, setActiveMode] = useState<'inputs' | 'results' | 'checks'>('inputs')
  const [selectedEntity, setSelectedEntity] = useState<any>({ entityType: 'shell_course', id: 'course-1', name: 'Course 1', course: 1 })
  const [selectedTrace, setSelectedTrace] = useState<any>()
  const [calculationInspector, setCalculationInspector] = useState({ open: false, pinned: false, maximized: false })
  const [revision, setRevision] = useState(0)
  const [ids, setIds] = useState<StoredIds | undefined>(() => {
    try { return JSON.parse(localStorage.getItem('tank650.ids') || 'null') || undefined } catch { return undefined }
  })
  const [history, setHistory] = useState<any>()
  const [busyAction, setBusyAction] = useState<string>()
  const [statusMessage, setStatusMessage] = useState('Preparando el espacio de ingeniería...')
  const [toast, setToast] = useState<ToastState>()

  const dirtyChanges = useMemo(() => draftInputs ? diffInputs(persistedInputs || {}, draftInputs) : {}, [draftInputs, persistedInputs])
  const dirty = Boolean(draftInputs) && (!persistedInputs || Object.keys(dirtyChanges).length > 0)
  const validation = useMemo(() => {
    const issues: Record<string, string> = {}
    if (!draftInputs) return issues
    if (draftInputs.geometry.design_liquid_height_m > draftInputs.geometry.shell_height_m) issues['geometry.design_liquid_height_m'] = 'La altura de líquido no puede exceder la altura del casco.'
    if (draftInputs.geometry.nominal_diameter_m <= 0) issues['geometry.nominal_diameter_m'] = 'El diámetro debe ser mayor que cero.'
    if (draftInputs.product.specific_gravity <= 0) issues['product.specific_gravity'] = 'La gravedad específica debe ser mayor que cero.'
    if (draftInputs.seismic.Sp < 0) issues['seismic.Sp'] = 'Sp no puede ser negativo.'
    if (draftInputs.anchorage.selected_bolts < 4) issues['anchorage.selected_bolts'] = 'Se requieren al menos cuatro pernos.'
    return issues
  }, [draftInputs])

  const notify = useCallback((tone: ToastState['tone'], title: string, detail?: string) => setToast({ id: Date.now(), tone, title, detail }), [])

  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setToast(undefined), 5200)
    return () => window.clearTimeout(timer)
  }, [toast])

  const refreshHistory = useCallback(async (scenarioId = ids?.scenarioId) => {
    if (!scenarioId) return
    try { setHistory(await api(`/api/v1/scenarios/${scenarioId}/history`)) } catch { /* a deleted local DB can invalidate remembered ids */ }
  }, [ids?.scenarioId])

  const loadExample = useCallback(async (quiet = false) => {
    setBusyAction('loading')
    try {
      const value = await api('/api/v1/fixtures/T78_2019')
      setFixture(value)
      setDraftInputs(clone(value))
      setPersistedInputs(undefined)
      setResult(undefined)
      setActiveRun(undefined)
      setRevision(0)
      setSelectedTrace(undefined)
      setStatusMessage('Fixture T78_2019 cargado. Guarde R1 o calcule un borrador.')
      if (!quiet) notify('success', 'Ejemplo T-78 cargado', 'Todos los módulos de entrada están disponibles.')
    } catch (error: any) {
      setStatusMessage(error.message)
      notify('error', 'No se pudo cargar el ejemplo', error.message)
    } finally { setBusyAction(undefined) }
  }, [notify])

  useEffect(() => { if (!draftInputs) void loadExample(true) }, [draftInputs, loadExample])
  useEffect(() => { void refreshHistory() }, [refreshHistory])

  useEffect(() => {
    const onPop = () => setActiveModule(moduleFromPath(window.location.pathname))
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  const navigate = useCallback((module: ModuleId) => {
    const entry = modules.find(item => item.id === module)!
    window.history.pushState({}, '', `/project/local/${entry.route}`)
    setActiveModule(module)
    setActiveMode(module === 'results' ? 'results' : 'inputs')
  }, [])

  const updateInput = useCallback((path: string, value: any) => {
    setDraftInputs((current: any) => setAtPath(current, path, value))
    setStatusMessage(`Borrador modificado: ${path}`)
  }, [])

  const saveRevision = useCallback(async () => {
    if (!draftInputs) return
    if (ids?.revisionId && !dirty) {
      notify('info', 'No existen cambios', 'No se creó una revisión nueva.')
      return
    }
    setBusyAction('saving')
    try {
      let nextIds = ids
      if (!nextIds?.scenarioId) {
        const project = await api('/api/v1/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: draftInputs.project.name, tank_tag: draftInputs.project.tank_tag, metadata: { client: draftInputs.project.client, location: draftInputs.project.location } }) })
        const scenario = await api(`/api/v1/projects/${project.id}/scenarios`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'BASELINE' }) })
        nextIds = { projectId: project.id, scenarioId: scenario.id, revisionId: null }
      }
      const changes = persistedInputs ? dirtyChanges : { baseline: { old: null, new: 'T78_2019' } }
      const created = await api(`/api/v1/scenarios/${nextIds.scenarioId}/revisions`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ inputs: draftInputs, derived_from_revision_id: nextIds.revisionId || null, changes }) })
      nextIds = { ...nextIds, revisionId: created.id }
      localStorage.setItem('tank650.ids', JSON.stringify(nextIds))
      setIds(nextIds)
      setRevision(created.revision_number)
      setPersistedInputs(clone(draftInputs))
      setStatusMessage(`BASELINE R${created.revision_number} guardada; los runs anteriores permanecen inmutables.`)
      notify('success', `Revisión R${created.revision_number} creada`, `${Object.keys(changes).length} cambio(s) registrados. Los runs anteriores permanecen inmutables.`)
      await refreshHistory(nextIds.scenarioId)
    } catch (error: any) {
      setStatusMessage(error.message)
      notify('error', 'No se pudo guardar la revisión', error.message)
    } finally { setBusyAction(undefined) }
  }, [dirty, dirtyChanges, draftInputs, ids, notify, persistedInputs, refreshHistory])

  const calculate = useCallback(async () => {
    if (!draftInputs) return
    if (Object.keys(validation).length) {
      notify('error', 'Corrija los datos inválidos', Object.values(validation)[0])
      return
    }
    setBusyAction('validating')
    setStatusMessage('Validando entradas...')
    await new Promise<void>(resolve => requestAnimationFrame(() => resolve()))
    setBusyAction('calculating')
    setStatusMessage('Calculando módulos de ingeniería...')
    try {
      let value: any
      let run: any
      if (ids?.revisionId && !dirty) {
        const response = await api(`/api/v1/revisions/${ids.revisionId}/runs`, { method: 'POST' })
        value = response
        run = { id: response.run_id, persisted: true, status: 'COMPLETED' }
      } else {
        value = await api('/api/v1/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ inputs: draftInputs }) })
        run = { id: `draft-${value.input_sha256.slice(0, 8)}`, persisted: false, status: 'COMPLETED' }
      }
      setResult(value)
      setActiveRun(run)
      const firstTrace = value.modules?.shell?.traces?.[0]
      if (firstTrace) setSelectedTrace(firstTrace)
      setStatusMessage(`${run.persisted ? 'Run inmutable' : 'Cálculo de borrador'} completado · ${value.input_sha256.slice(0, 12)}...`)
      notify('success', run.persisted ? `Run ${run.id.slice(0, 8)} completado` : 'Cálculo de borrador completado', run.persisted ? 'Resultado asociado a la revisión activa.' : 'Guarde una revisión para conservar un run inmutable.')
      if (run.persisted) await refreshHistory()
    } catch (error: any) {
      setStatusMessage(error.message)
      notify('error', 'El cálculo no pudo completarse', error.message)
    } finally { setBusyAction(undefined) }
  }, [dirty, draftInputs, ids?.revisionId, notify, refreshHistory, validation])

  const downloadCalculationMemory = useCallback(async () => {
    if (!draftInputs) return
    if (Object.keys(validation).length) {
      notify('error', 'Corrija los datos inválidos', Object.values(validation)[0])
      return
    }
    setBusyAction('reporting')
    setStatusMessage('Recalculando y generando la memoria Word...')
    try {
      const response = await fetch('/api/v1/calculation-memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputs: draftInputs }),
      })
      if (!response.ok) {
        let message = `HTTP ${response.status}`
        try { const body = await response.json(); message = body.detail?.message || body.detail || message } catch { /* response was not JSON */ }
        throw new Error(String(message))
      }
      const disposition = response.headers.get('Content-Disposition') || ''
      const encodedMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i)
      const simpleMatch = disposition.match(/filename="?([^";]+)"?/i)
      const filename = encodedMatch ? decodeURIComponent(encodedMatch[1]) : simpleMatch?.[1] || 'Memoria_Calculo_TANK650.docx'
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      const fingerprint = response.headers.get('X-TANK650-Input-SHA256')
      setStatusMessage(`Memoria Word generada · ${fingerprint?.slice(0, 12) || 'huella disponible en el documento'}...`)
      notify('success', 'Memoria de cálculo descargada', 'El documento corresponde a los parámetros actuales y contiene la trazabilidad de fórmulas.')
    } catch (error: any) {
      setStatusMessage(error.message)
      notify('error', 'No se pudo generar la memoria', error.message)
    } finally { setBusyAction(undefined) }
  }, [draftInputs, notify, validation])

  const selectEntity = useCallback((entity: any) => setSelectedEntity(entity), [])
  const openTrace = useCallback((trace: any) => {
    setSelectedTrace(trace)
    setCalculationInspector(current => ({ ...current, open: true }))
  }, [])

  const selectCourse = useCallback((course: number) => {
    const entity = result?.geometry?.courses?.find((row: any) => Number(row.id.split('-')[1]) === course)
    setSelectedEntity(entity ? { ...entity, course } : { entityType: 'shell_course', id: `course-${course}`, name: `Course ${course}`, course })
  }, [result])

  return {
    fixture, draftInputs, persistedInputs, result, activeRun, activeModule, activeMode, selectedEntity, selectedTrace,
    calculationInspector, revision, ids, history, busyAction, statusMessage, toast, dirty, dirtyChanges, validation,
    loadExample, navigate, setActiveMode, updateInput, saveRevision, calculate, downloadCalculationMemory, selectEntity, selectCourse, openTrace,
    setCalculationInspector, setToast, refreshHistory,
  }
}
