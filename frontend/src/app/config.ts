export type ModuleId = 'overview' | 'project' | 'code' | 'geometry' | 'product' | 'materials' | 'shell' | 'bottom' | 'wind' | 'seismic' | 'roof' | 'anchorage' | 'review' | 'results' | 'variants' | 'history'

export const modules: Array<{ id: ModuleId; label: string; group: string; icon: string; route: string }> = [
  { id: 'overview', label: 'Inicio', group: 'Proyecto', icon: '⌂', route: 'overview' },
  { id: 'project', label: 'Proyecto', group: 'Proyecto', icon: 'P', route: 'project' },
  { id: 'code', label: 'Código', group: 'Proyecto', icon: '§', route: 'code' },
  { id: 'geometry', label: 'Geometría', group: 'Diseño', icon: '◇', route: 'design/geometry' },
  { id: 'product', label: 'Producto', group: 'Diseño', icon: '◒', route: 'design/product' },
  { id: 'materials', label: 'Materiales', group: 'Diseño', icon: 'M', route: 'design/materials' },
  { id: 'shell', label: 'Casco', group: 'Diseño', icon: '▥', route: 'design/shell' },
  { id: 'bottom', label: 'Fondo', group: 'Diseño', icon: '⊥', route: 'design/bottom' },
  { id: 'wind', label: 'Viento', group: 'Cargas', icon: '≈', route: 'design/wind' },
  { id: 'seismic', label: 'Sismo', group: 'Cargas', icon: '∿', route: 'design/seismic' },
  { id: 'roof', label: 'Techo / cargas', group: 'Diseño', icon: '⌒', route: 'design/roof' },
  { id: 'anchorage', label: 'Anclaje', group: 'Diseño', icon: '⌖', route: 'design/anchorage' },
  { id: 'review', label: 'Revisar', group: 'Control', icon: '✓', route: 'review' },
  { id: 'results', label: 'Resultados', group: 'Control', icon: 'Σ', route: 'results' },
  { id: 'variants', label: 'Variantes', group: 'Control', icon: '⇄', route: 'variants' },
  { id: 'history', label: 'Historial', group: 'Control', icon: '↺', route: 'history' },
]

export const moduleMeta: Record<ModuleId, { title: string; eyebrow: string; description: string }> = {
  overview: { title: 'Centro de diseño T-78', eyebrow: 'PROYECTO', description: 'Estado del modelo, revisión activa y accesos de ingeniería.' },
  project: { title: 'Datos del proyecto', eyebrow: 'IDENTIFICACIÓN', description: 'Identificación, cliente, ubicación y notas del tanque.' },
  code: { title: 'Código y capacidades', eyebrow: 'PERFIL NORMATIVO', description: 'Alcance congelado, edición y madurez de cálculo.' },
  geometry: { title: 'Geometría del tanque', eyebrow: 'MODELO FÍSICO', description: 'Dimensiones principales y navegador de entidades.' },
  product: { title: 'Producto y condición de diseño', eyebrow: 'CONTENIDO', description: 'Gravedad específica, nivel, temperatura y presión.' },
  materials: { title: 'Materiales y esfuerzos admisibles', eyebrow: 'PROPIEDADES', description: 'Materiales del casco, fondo, pernos y soldadura.' },
  shell: { title: 'Casco - método One-Foot', eyebrow: 'API 650 §5.6.3.2', description: 'Cursos, planchas, espesores y utilización.' },
  bottom: { title: 'Fondo y anillo anular', eyebrow: 'API 650 §5.4', description: 'Zonas, espesores, ancho anular y layout AFC.' },
  wind: { title: 'Acción de viento', eyebrow: 'CARGA LATERAL', description: 'Coeficientes, presión, cortante y estabilidad.' },
  seismic: { title: 'Diseño sísmico', eyebrow: 'API 650 ANNEX E', description: 'Espectro, respuesta dinámica, estabilidad y checks.' },
  roof: { title: 'Techo físico y modelo de análisis', eyebrow: 'ALUMINUM GEODESIC DOME', description: 'Geometría representativa separada del surrogate A36.' },
  anchorage: { title: 'Anclajes y sillas', eyebrow: 'MECHANICAL ANCHORAGE', description: 'Pernos, casos de carga, utilización y geometría de silla.' },
  review: { title: 'Revisión de diseño', eyebrow: 'PRE-CALCULATION', description: 'Completitud, consistencia y advertencias antes del run.' },
  results: { title: 'Resultados globales', eyebrow: 'EXECUTIVE RESULT', description: 'Estado general y acceso directo a cálculos críticos.' },
  variants: { title: 'Comparación de variantes', eyebrow: 'PARAMETRIC STUDY', description: 'Evaluación de cambios sin alterar la revisión base.' },
  history: { title: 'Historial inmutable', eyebrow: 'REVISIONS & RUNS', description: 'Revisiones persistidas y ejecuciones asociadas.' },
}

export function moduleFromPath(pathname: string): ModuleId {
  const hit = modules.find(item => pathname.endsWith(`/${item.route}`))
  return hit?.id || 'overview'
}
