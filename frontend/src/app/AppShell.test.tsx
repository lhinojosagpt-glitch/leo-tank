import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fixture from '../../../data/fixtures/T78_2019.json'
import AppShell from './AppShell'

vi.mock('../viewer/TankViewer', () => ({
  default: ({ onSelect }: any) => <div data-testid="tank-viewer"><button onClick={() => onSelect?.({ id: 'C01-P05', name: 'Plate C01-P05', entityType: 'shell_plate', course: 1, plate: 5, thickness_mm: 25, selected_mm: 25, required_design_mm: 24.2226, utilization: .9689, status: 'PASS', material: 'ASTM A36 Group II' })}>Mock plate C01-P05</button></div>,
}))

const courseRows = fixture.shell.courses.map((course, index) => ({ course: index + 1, height_m: course.height_m, design_mm: fixture.golden.shell_design_mm[index], hydrotest_mm: fixture.golden.shell_hydrotest_mm[index], selected_mm: course.thickness_mm, utilization: fixture.golden.shell_design_mm[index] / course.thickness_mm, status: 'PASS' }))
const shellTraces = courseRows.flatMap(row => [{ formula_id: 'API650_12E_5_6_3_2_ONE_FOOT_DESIGN', symbol: 'td', description: `Course ${row.course}: One-foot design shell thickness`, reference: 'API 650 12th Ed. 5.6.3.2', expression: '(2.6*D*(H-1)*G/(Sd*E)+CA)*25.4', inputs: { course: row.course, D_ft: 150, H_ft: 61, G: .8778 }, raw_result: row.design_mm, display_result: row.design_mm, unit: 'mm', status: 'CALCULATED' }])
const courses = fixture.shell.courses.map((course, index) => ({ id: `course-${index + 1}`, name: `Course ${index + 1}`, entity_type: 'shell_course', course: index + 1, elevation_m: index * 2.4, height_m: 2.4, thickness_mm: course.thickness_mm, selected_mm: course.thickness_mm, required_design_mm: courseRows[index].design_mm, utilization: courseRows[index].utilization, status: 'PASS', material: course.material, plate_count: 24, plates: Array.from({ length: 24 }, (_, plate) => ({ id: `C${String(index + 1).padStart(2, '0')}-P${String(plate + 1).padStart(2, '0')}`, name: `Plate C${String(index + 1).padStart(2, '0')}-P${String(plate + 1).padStart(2, '0')}`, entity_type: 'shell_plate', course: index + 1, plate: plate + 1 })) }))
const jTrace = { formula_id: 'API650_12E_E_6_2_1_1_J', symbol: 'J', description: 'Anchorage ratio', reference: 'API 650 Annex E.6.2.1.1.1-1', expression: 'Mrw/(D²*(wt*(1-0.4Av)+wa-0.4wint))', inputs: { Mrw: 1, D: 2 }, raw_result: 2.40587, display_result: 2.4059, unit: '1', status: 'CALCULATED' }
const autoAnchorCheck = { check_id: 'AUTO_ANCHORAGE', module: 'seismic', title: 'Self-anchored stability', short_title: 'Auto-anchor', description: 'Mechanical anchorage required.', demand: 2.4059, capacity: 1.54, unit: 'ratio', utilization: 2.4059 / 1.54, margin: 1.54 - 2.4059, status: 'FAIL', standard_reference: 'API 650 Annex E.6.2.1.1', formula_id: 'API650_12E_E_6_2_1_1_J', fail_classification: 'ALTERNATIVE_PATH_FAIL' }
const result: any = {
  engine_version: '2.0.0', input_sha256: 'abcdef0123456789', overall_status: 'PASS_WITH_MECHANICAL_ANCHORAGE',
  summary: { shell: { status: 'PASS', max_utilization: .9963 }, bottom: { status: 'PASS' }, wind: { status: 'PASS' }, seismic: { status: 'PASS', J: 2.4059, max_hoop_utilization: .959 }, auto_anchor: { status: 'FAIL' }, anchorage: { status: 'PASS', required: true, selected_bolts: 60 } },
  modules: {
    shell: { status: 'PASS', values: { courses: courseRows }, checks: [], traces: shellTraces },
    bottom: { status: 'PASS', values: {}, checks: [], traces: [] }, wind: { status: 'PASS', values: {}, checks: [], traces: [] },
    seismic: { status: 'PASS', values: { J: 2.4059, hoop: courseRows.map(row => ({ course: row.course, utilization: row.course === 6 ? .959 : .5 })) }, checks: [autoAnchorCheck], traces: [jTrace, { ...jTrace, formula_id: 'API650_HOOP', symbol: 'sigma_h', description: 'Course 6 hoop stress', inputs: { course: 6 }, display_result: 203920, unit: 'kPa' }] },
    anchorage: { status: 'PASS', values: {}, checks: [], traces: [] },
  },
  geometry: { tank_tag: 'T-78', nominal_diameter_m: 45.725, shell_height_m: 19.2, courses, bottom: { id: 'bottom', entity_type: 'bottom' }, physical_roof: { id: 'roof', entity_type: 'roof' }, anchors: [], plate_layout: { total_shell_plates: 192 } },
}

function response(body: any, ok = true) { return Promise.resolve({ ok, status: ok ? 200 : 500, json: async () => body } as Response) }

describe('TANK650 v2.0 engineering workflow', () => {
  afterEach(() => cleanup())
  beforeEach(() => {
    localStorage.clear()
    window.history.replaceState({}, '', '/')
    let revision = 0
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/fixtures/T78_2019')) return response(fixture)
      if (url === '/api/v1/projects') return response({ id: 'project-1' })
      if (url.includes('/projects/project-1/scenarios')) return response({ id: 'scenario-1' })
      if (url.includes('/scenarios/scenario-1/revisions')) return response({ id: `revision-${++revision}`, revision_number: revision })
      if (url.includes('/scenarios/scenario-1/history')) return response({ scenario: { id: 'scenario-1', name: 'BASELINE' }, revisions: [] })
      if (url.includes('/revisions/revision-') && url.endsWith('/runs')) return response({ run_id: 'run-0042', ...result })
      if (url.endsWith('/calculate')) return response(result)
      return response({})
    }))
  })

  it('navigates, records dirty edits, saves revisions, calculates and opens trace/property inspectors', async () => {
    const user = userEvent.setup()
    render(<AppShell />)
    expect(await screen.findByRole('heading', { name: 'Centro de diseño T-160MB' })).toBeInTheDocument()

    await user.click(screen.getByTitle('Sismo'))
    expect(screen.getByRole('heading', { name: 'Diseño sísmico' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Guardar revisión' }))
    expect(await screen.findByText('Revisión R1 creada')).toBeInTheDocument()
    expect(screen.queryByText('● CAMBIOS SIN GUARDAR')).not.toBeInTheDocument()

    const sp = document.querySelector('#seismic-Sp') as HTMLInputElement
    fireEvent.change(sp, { target: { value: '0.50' } })
    expect(screen.getByText('● CAMBIOS SIN GUARDAR')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Guardar revisión' }))
    expect(await screen.findByText('Revisión R2 creada')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Calcular' }))
    expect(await screen.findByText('Run run-0042 completado')).toBeInTheDocument()
    expect(screen.getByText('2.4059')).toBeInTheDocument()

    await user.click(screen.getAllByRole('button', { name: 'Verificaciones' })[0])
    expect(screen.getAllByText('Self-anchored stability').length).toBeGreaterThan(0)
    expect(document.querySelector('.checks-workspace')?.textContent).toContain('Demanda 2.4059 ratio')
    expect(document.querySelector('.checks-workspace')?.textContent).toContain('Capacidad 1.54 ratio')

    await user.click(screen.getByRole('button', { name: /J SÍSMICO/i }))
    expect(await screen.findByText('CALCULATION INSPECTOR')).toBeInTheDocument()
    expect(screen.getAllByText('Anchorage ratio').length).toBeGreaterThan(0)
    await user.click(screen.getByTitle('Cerrar inspector'))

    await user.click(screen.getByTitle('Casco'))
    await user.click(screen.getByRole('button', { name: 'Mock plate C01-P05' }))
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Propiedades' })).toBeInTheDocument())
    expect(screen.getAllByText('Plate C01-P05').length).toBeGreaterThan(0)

    await user.click(screen.getByRole('button', { name: /15\.368/ }))
    expect((await screen.findAllByText(/Course 4: One-foot design shell thickness/)).length).toBeGreaterThan(0)
  })

  it('does not render meaningless result/check tabs for configuration workspaces', async () => {
    const user = userEvent.setup()
    render(<AppShell />)
    await screen.findByRole('heading', { name: 'Centro de diseño T-160MB' })
    await user.click(screen.getAllByTitle('Código').at(-1)!)
    expect(document.querySelectorAll('.workspace-tabs button')).toHaveLength(0)
    await user.click(screen.getAllByTitle('Geometría').at(-1)!)
    expect(screen.queryByText('No calculation run selected.')).not.toBeInTheDocument()
  })
})
