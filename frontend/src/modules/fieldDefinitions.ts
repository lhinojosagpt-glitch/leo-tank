import type { ModuleId } from '../app/config'

export type FieldDef = {
  path: string
  label: string
  symbol?: string
  unit?: string
  source: string
  kind?: 'USER INPUT' | 'STANDARD VALUE' | 'REFERENCE VALUE' | 'DERIVED'
  readOnly?: boolean
  type?: 'number' | 'text'
  step?: string
  help?: string
}

const f = (path: string, label: string, symbol: string, unit: string, source: string, extra: Partial<FieldDef> = {}): FieldDef => ({ path, label, symbol, unit, source, kind: 'USER INPUT', type: 'number', step: 'any', ...extra })

export const fieldsByModule: Partial<Record<ModuleId, FieldDef[]>> = {
  project: [
    f('project.name', 'Nombre del proyecto', '', '', 'Fixture T-160MB', { type: 'text' }),
    f('project.tank_tag', 'Tag del tanque', '', '', 'Planos T-160MB', { type: 'text' }),
    f('project.client', 'Cliente', '', '', 'Memoria de cálculo', { type: 'text' }),
    f('project.location', 'Ubicación', '', '', 'Memoria de cálculo', { type: 'text' }),
  ],
  code: [
    f('standard_profile.standard', 'Norma', '', '', 'Perfil congelado', { type: 'text', readOnly: true, kind: 'STANDARD VALUE' }),
    f('standard_profile.edition', 'Edición', '', '', 'Perfil congelado', { type: 'text', readOnly: true, kind: 'STANDARD VALUE' }),
    f('standard_profile.id', 'Perfil', '', '', 'Motor', { type: 'text', readOnly: true, kind: 'STANDARD VALUE' }),
    f('shell.method', 'Método de casco', '', '', 'TANK 2016', { type: 'text', readOnly: true, kind: 'STANDARD VALUE' }),
  ],
  geometry: [
    f('geometry.nominal_diameter_m', 'Diámetro nominal', 'D', 'm', 'TANK 2016 - pág. 3', { help: 'Diámetro nominal del tanque.' }),
    f('geometry.internal_diameter_m', 'Diámetro interior', 'Di', 'm', 'Plano del cilindro'),
    f('geometry.shell_height_m', 'Altura del casco', 'Hs', 'm', 'TANK 2016 - pág. 3'),
    f('geometry.design_liquid_height_m', 'Altura de líquido', 'H', 'm', 'TANK 2016 - pág. 3'),
    f('geometry.course_height_m', 'Altura nominal de curso', 'Hc', 'm', 'Plano del cilindro'),
    f('geometry.bottom_slope_percent', 'Pendiente del fondo', 's', '%', 'Plano del fondo - cortes 4 y 5'),
  ],
  product: [
    f('product.specific_gravity', 'Gravedad específica', 'G', '-', 'TANK 2016 - pág. 3', { step: '0.0001' }),
    f('geometry.design_liquid_height_m', 'Nivel de diseño', 'H', 'm', 'TANK 2016 - pág. 3'),
    f('product.design_temperature_C', 'Temperatura de diseño', 'Td', '°C', 'TANK 2016'),
    f('product.design_pressure_kPa', 'Presión de diseño', 'Pd', 'kPa', 'TANK 2016'),
  ],
  materials: [
    f('materials.shell.name', 'Material del casco', '', '', 'TANK 2016', { type: 'text' }),
    f('materials.shell.design_stress_psi', 'Esfuerzo admisible de diseño', 'Sd', 'psi', 'TANK 2016 - tabla de materiales'),
    f('materials.shell.hydrotest_stress_psi', 'Esfuerzo admisible de prueba', 'St', 'psi', 'TANK 2016 - tabla de materiales'),
    f('materials.shell.yield_strength_psi', 'Fluencia del casco', 'Fy', 'psi', 'ASTM A36 / TANK 2016'),
    f('materials.shell.ultimate_strength_psi', 'Resistencia última', 'Fu', 'psi', 'ASTM A36 / TANK 2016'),
    f('materials.bottom.name', 'Material del fondo', '', '', 'TANK 2016', { type: 'text' }),
    f('materials.bottom.yield_strength_psi', 'Fluencia del fondo', 'Fy', 'psi', 'ASTM A36 / TANK 2016'),
    f('materials.anchors.name', 'Material de pernos', '', '', 'TANK 2016', { type: 'text' }),
    f('materials.anchors.yield_strength_kPa', 'Fluencia de pernos', 'Fy', 'kPa', 'ASTM F1554 Gr. 36'),
    f('materials.weld.name', 'Material de soldadura', '', '', 'TANK 2016', { type: 'text' }),
    f('materials.weld.yield_strength_psi', 'Fluencia de soldadura', 'Fyw', 'psi', 'E60xx / TANK 2016'),
  ],
  shell: [
    f('shell.joint_efficiency', 'Eficiencia de junta', 'E', '-', 'TANK 2016 - pág. 3'),
    f('shell.corrosion_allowance_mm', 'Corrosión admisible', 'CA', 'mm', 'TANK 2016 - pág. 3'),
    f('shell.minimum_nominal_thickness_mm', 'Espesor nominal mínimo', 'tmin', 'mm', 'API 650 §5.6.1.1', { kind: 'STANDARD VALUE' }),
    f('geometry.nominal_diameter_m', 'Diámetro nominal', 'D', 'm', 'TANK 2016 - pág. 3'),
    f('geometry.design_liquid_height_m', 'Altura de líquido', 'H', 'm', 'TANK 2016 - pág. 3'),
    f('product.specific_gravity', 'Gravedad específica', 'G', '-', 'TANK 2016 - pág. 3'),
  ],
  bottom: [
    f('bottom.central_required_mm', 'Fondo central requerido', 'tr', 'mm', 'API 650 / TANK 2016', { readOnly: true, kind: 'REFERENCE VALUE' }),
    f('bottom.central_selected_mm', 'Fondo central seleccionado', 'ts', 'mm', 'Plano del fondo'),
    f('bottom.annular_required_mm', 'Anular requerido', 'tar', 'mm', 'TANK 2016 - pág. 9', { readOnly: true, kind: 'REFERENCE VALUE' }),
    f('bottom.annular_selected_mm', 'Anular seleccionado', 'tas', 'mm', 'Memoria - pág. 22 / plano'),
    f('bottom.annular_corrosion_allowance_mm', 'Corrosión anular', 'CA', 'mm', 'Memoria de cálculo'),
    f('bottom.annular_effective_thickness_mm', 'Espesor anular efectivo', 'tae', 'mm', 'Cadena sísmica', { readOnly: true, kind: 'DERIVED' }),
    f('bottom.annular_required_width_mm', 'Ancho anular requerido', 'Lar', 'mm', 'TANK 2016 - pág. 9', { readOnly: true, kind: 'REFERENCE VALUE' }),
    f('bottom.annular_selected_width_mm', 'Ancho anular seleccionado', 'Las', 'mm', 'Memoria - pág. 22 / plano'),
  ],
  wind: [
    f('wind.velocity_m_s', 'Velocidad básica', 'V', 'm/s', 'TANK 2016 - pág. 7'),
    f('wind.Kz', 'Coeficiente de exposición', 'Kz', '-', 'TANK 2016 - pág. 7'),
    f('wind.Kzt', 'Factor topográfico', 'Kzt', '-', 'TANK 2016 - pág. 7'),
    f('wind.Kd', 'Factor direccional', 'Kd', '-', 'TANK 2016 - pág. 7'),
    f('wind.importance', 'Factor de importancia', 'I', '-', 'TANK 2016 - pág. 7'),
    f('wind.gust_factor', 'Factor de ráfaga', 'Gf', '-', 'TANK 2016 - pág. 7'),
    f('wind.pressure_kPa', 'Presión de referencia', 'q', 'kPa', 'TANK 2016 - reconstrucción', { kind: 'REFERENCE VALUE' }),
    f('wind.exposed_area_m2', 'Área expuesta', 'A', 'm²', 'TANK 2016 - reconstrucción', { kind: 'REFERENCE VALUE' }),
    f('wind.overturning_moment_Nm', 'Momento volcador', 'Mw', 'N·m', 'TANK 2016 - reconstrucción', { kind: 'REFERENCE VALUE' }),
    f('wind.resisting_moment_Nm', 'Momento resistente', 'Mr', 'N·m', 'TANK 2016 - reconstrucción', { kind: 'REFERENCE VALUE' }),
  ],
  seismic: [
    f('seismic.Sp', 'Aceleración pico', 'Sp', 'g', 'TANK 2016 - pág. 11', { step: '0.01', help: 'Peak ground acceleration used by the frozen T-160MB profile.' }),
    f('seismic.site_class', 'Clase de sitio', '', '', 'TANK 2016 - pág. 11', { type: 'text' }),
    f('seismic.seismic_use_group', 'Grupo de uso sísmico', 'SUG', '-', 'TANK 2016 - pág. 11'),
    f('seismic.Fa', 'Coeficiente de período corto', 'Fa', '-', 'TANK 2016 - pág. 11'),
    f('seismic.Fv', 'Coeficiente de 1 segundo', 'Fv', '-', 'TANK 2016 - pág. 11'),
    f('seismic.K', 'Coeficiente K', 'K', '-', 'TANK 2016 - pág. 11'),
    f('seismic.Q', 'Factor de escala', 'Q', '-', 'TANK 2016 - pág. 11'),
    f('seismic.TL_s', 'Período largo', 'TL', 's', 'TANK 2016 - pág. 11'),
    f('seismic.importance_factor', 'Importancia sísmica', 'I', '-', 'TANK 2016 - pág. 11'),
    f('seismic.Rwi', 'Modificación impulsiva', 'Rwi', '-', 'TANK 2016 - pág. 11'),
    f('seismic.Rwc', 'Modificación convectiva', 'Rwc', '-', 'TANK 2016 - pág. 11'),
    f('seismic.Ai_lower_bound', 'Límite inferior Ai', 'Ai,min', 'g', 'API 650 Annex E'),
    f('seismic.internal_pressure_line_load_lb_ft', 'Carga lineal por presión', 'wint', 'lb/ft', 'TANK 2016'),
    f('seismic.shear_resistance_N', 'Resistencia al corte', 'Vr', 'N', 'TANK 2016'),
    f('seismic.required_freeboard_m', 'Freeboard requerido', 'hfr', 'm', 'TANK 2016', { kind: 'REFERENCE VALUE' }),
  ],
  roof: [
    f('roof.physical_roof.type', 'Tipo físico', '', '', 'Proyecto T-160MB', { type: 'text', readOnly: true, kind: 'REFERENCE VALUE' }),
    f('roof.physical_roof.design_scope', 'Alcance estructural', '', '', 'Proveedor', { type: 'text', readOnly: true, kind: 'REFERENCE VALUE' }),
    f('roof.analysis_roof.type', 'Modelo sustituto', '', '', 'Reconstrucción TANK 2016', { type: 'text', readOnly: true, kind: 'REFERENCE VALUE' }),
    f('roof.analysis_roof.material', 'Material sustituto', '', '', 'TANK 2016', { type: 'text' }),
    f('roof.analysis_roof.thickness_mm', 'Espesor sustituto', 'tr', 'mm', 'TANK 2016'),
  ],
  anchorage: [
    f('anchorage.selected_bolts', 'Número de pernos', 'n', 'und', 'TANK 2016 - pág. 25'),
    f('anchorage.diameter_mm', 'Diámetro nominal', 'db', 'mm', 'TANK 2016 - pág. 25'),
    f('anchorage.effective_area_mm2', 'Área efectiva roscada', 'Ab', 'mm²', 'TANK 2016 - pág. 25'),
    f('anchorage.offset_m', 'Offset radial', 'e', 'm', 'Plano del cilindro'),
    f('anchorage.corrosion_allowance_mm', 'Corrosión del perno', 'CA', 'mm', 'TANK 2016'),
    f('anchor_chair.gusset_thickness_mm', 'Espesor de cartela', 'tg', 'mm', 'TANK 2016 - pág. 28'),
    f('anchor_chair.gusset_height_mm', 'Altura de cartela', 'hg', 'mm', 'TANK 2016 - pág. 28'),
    f('anchor_chair.top_plate_thickness_mm', 'Placa superior seleccionada', 'tc', 'mm', 'TANK 2016 - pág. 28'),
    f('anchor_chair.eccentricity_mm', 'Excentricidad', 'e', 'mm', 'TANK 2016 - pág. 28'),
    f('anchor_chair.bolt_load_N', 'Carga de diseño del perno', 'P', 'N', 'TANK 2016 - pág. 28'),
  ],
}

export function getAtPath(source: any, path: string): any {
  return path.replaceAll(']', '').replaceAll('[', '.').split('.').reduce((value, key) => value == null ? undefined : value[Array.isArray(value) ? Number(key) : key], source)
}

export function setAtPath(source: any, path: string, value: any): any {
  const next = JSON.parse(JSON.stringify(source))
  const parts = path.replaceAll(']', '').replaceAll('[', '.').split('.')
  let cursor = next
  parts.slice(0, -1).forEach(key => { cursor = cursor[Array.isArray(cursor) ? Number(key) : key] })
  const leaf = parts.at(-1)!
  cursor[Array.isArray(cursor) ? Number(leaf) : leaf] = value
  return next
}

export function diffInputs(before: any, after: any, prefix = ''): Record<string, { old: any; new: any }> {
  const changes: Record<string, { old: any; new: any }> = {}
  const keys = new Set([...Object.keys(before || {}), ...Object.keys(after || {})])
  keys.forEach(key => {
    const path = prefix ? `${prefix}.${key}` : key
    const a = before?.[key], b = after?.[key]
    if (a && b && typeof a === 'object' && typeof b === 'object' && !Array.isArray(a) && !Array.isArray(b)) Object.assign(changes, diffInputs(a, b, path))
    else if (JSON.stringify(a) !== JSON.stringify(b)) changes[path] = { old: a, new: b }
  })
  return changes
}
