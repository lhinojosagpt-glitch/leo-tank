import { useCallback, useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

type DisplayMode = 'solid' | 'transparent' | 'edges' | 'section'
type ColorMode = 'thickness' | 'utilization' | 'material'
type RoofMode = 'panels-frame' | 'frame' | 'transparent'
type ModelMode = 'physical' | 'analysis'

type Props = {
  spec?: any
  selected?: any
  hiddenIds?: Set<string>
  isolateId?: string
  onSelect?: (entity: any) => void
}

const typeOf = (entity: any) => entity?.entity_type || entity?.entityType

function utilizationColor(value?: number) {
  if (value == null) return new THREE.Color('#84aeb8')
  const hue = Math.max(0, Math.min(120, 120 - value * 120))
  return new THREE.Color(`hsl(${hue} 55% 46%)`)
}

function thicknessColor(value: number) {
  const min = 8, max = 25
  const t = Math.max(0, Math.min(1, (value - min) / (max - min)))
  return new THREE.Color().lerpColors(new THREE.Color('#9fc7d1'), new THREE.Color('#15596d'), t)
}

function materialColor(name?: string) {
  return new THREE.Color(name?.includes('Group II') ? '#386f84' : '#73a5b2')
}

export default function TankViewer({ spec, selected, hiddenIds = new Set(), isolateId, onSelect }: Props) {
  const mount = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<any>(null)
  const [projection, setProjection] = useState<'perspective' | 'orthographic'>('perspective')
  const [displayMode, setDisplayMode] = useState<DisplayMode>('solid')
  const [colorMode, setColorMode] = useState<ColorMode>('thickness')
  const [roofMode, setRoofMode] = useState<RoofMode>('panels-frame')
  const [modelMode, setModelMode] = useState<ModelMode>('physical')
  const [sectionAxis, setSectionAxis] = useState<'x' | 'y' | 'z'>('x')
  const [sectionPosition, setSectionPosition] = useState(0)
  const [visualScale, setVisualScale] = useState(10)

  const isVisible = useCallback((entity: any) => {
    if (hiddenIds.has(entity.id) || hiddenIds.has(`course-${entity.course}`)) return false
    if (!isolateId) return true
    if (entity.id === isolateId) return true
    if (isolateId.startsWith('course-') && entity.course === Number(isolateId.split('-')[1])) return true
    if (isolateId === 'shell' && ['shell_plate', 'shell_course'].includes(typeOf(entity))) return true
    if (isolateId === 'anchors' && typeOf(entity) === 'anchor') return true
    return false
  }, [hiddenIds, isolateId])

  useEffect(() => {
    if (!mount.current || !spec) return
    const el = mount.current
    const scene = new THREE.Scene()
    scene.background = new THREE.Color('#edf3f6')
    const aspect = Math.max(el.clientWidth, 1) / Math.max(el.clientHeight, 1)
    const perspective = new THREE.PerspectiveCamera(34, aspect, 0.1, 500)
    const ortho = new THREE.OrthographicCamera(-34 * aspect, 34 * aspect, 34, -34, 0.1, 500)
    const camera = projection === 'perspective' ? perspective : ortho
    camera.position.set(42, 28, 42)
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(el.clientWidth, el.clientHeight)
    renderer.localClippingEnabled = true
    renderer.shadowMap.enabled = true
    el.replaceChildren(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.target.set(0, spec.shell_height_m * 0.48, 0)
    controls.enableDamping = true
    controls.dampingFactor = 0.08
    controls.minDistance = 16
    controls.maxDistance = 120

    const tankGroup = new THREE.Group()
    scene.add(tankGroup)
    const pickables: THREE.Object3D[] = []
    const radius = spec.nominal_diameter_m / 2
    const clippingNormal = sectionAxis === 'x' ? new THREE.Vector3(-1, 0, 0) : sectionAxis === 'y' ? new THREE.Vector3(0, -1, 0) : new THREE.Vector3(0, 0, -1)
    const clipping = displayMode === 'section' ? [new THREE.Plane(clippingNormal, sectionPosition)] : []
    const selectedType = typeOf(selected)

    const baseOpacity = displayMode === 'transparent' ? 0.3 : 0.94
    spec.courses.forEach((course: any) => {
      course.plates.forEach((plate: any) => {
        if (!isVisible(plate)) return
        const plateSelected = selected?.id === plate.id
        const courseSelected = selectedType === 'shell_course' && selected?.course === plate.course
        const anythingSelected = Boolean(selected?.id)
        const dimmed = anythingSelected && !plateSelected && !courseSelected
        const color = colorMode === 'utilization' ? utilizationColor(plate.utilization) : colorMode === 'material' ? materialColor(plate.material) : thicknessColor(plate.thickness_mm)
        if (plateSelected || courseSelected) color.lerp(new THREE.Color('#ec9f36'), plateSelected ? 0.8 : 0.48)
        const visualThickness = Math.max(plate.thickness_mm / 1000 * visualScale, 0.075)
        const geometry = new THREE.CylinderGeometry(radius + visualThickness, radius + visualThickness, plate.height_m - 0.018, 8, 1, true, THREE.MathUtils.degToRad(plate.start_angle_deg), THREE.MathUtils.degToRad(plate.angle_deg - 0.08))
        const material = new THREE.MeshStandardMaterial({ color, roughness: 0.58, metalness: 0.22, transparent: true, opacity: dimmed ? 0.14 : baseOpacity, side: THREE.DoubleSide, clippingPlanes: clipping })
        const mesh = new THREE.Mesh(geometry, material)
        mesh.position.y = course.elevation_m + course.height_m / 2
        mesh.userData.entity = plate
        mesh.castShadow = true
        tankGroup.add(mesh)
        pickables.push(mesh)
        if (displayMode === 'edges' || plateSelected || courseSelected) {
          const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry, 5), new THREE.LineBasicMaterial({ color: plateSelected ? '#ff8a1d' : courseSelected ? '#e8a547' : '#315d6c', transparent: true, opacity: dimmed ? 0.12 : 0.9, clippingPlanes: clipping }))
          edges.position.copy(mesh.position)
          tankGroup.add(edges)
        }
      })
    })

    const annularOuter = radius
    const annularInner = radius - spec.bottom.annular_width_mm / 1000
    const annularEntity = { ...spec.bottom, id: 'bottom-annular', name: 'Annular bottom', entity_type: 'bottom_annular' }
    if (isVisible(annularEntity)) {
      const annular = new THREE.Mesh(new THREE.RingGeometry(annularInner, annularOuter, 96, 1), new THREE.MeshStandardMaterial({ color: selected?.id === 'bottom-annular' ? '#e99b34' : '#667f8c', roughness: 0.68, side: THREE.DoubleSide, clippingPlanes: clipping }))
      annular.rotation.x = -Math.PI / 2
      annular.position.y = -0.025
      annular.userData.entity = annularEntity
      tankGroup.add(annular); pickables.push(annular)
    }
    const centralEntity = { ...spec.bottom, id: 'bottom-central', name: 'Central bottom', entity_type: 'bottom_central' }
    if (isVisible(centralEntity)) {
      const central = new THREE.Mesh(new THREE.CircleGeometry(annularInner, 96), new THREE.MeshStandardMaterial({ color: selected?.id === 'bottom-central' ? '#e99b34' : '#8da3ac', roughness: 0.72, side: THREE.DoubleSide, clippingPlanes: clipping }))
      central.rotation.x = -Math.PI / 2
      central.position.y = -0.035
      central.userData.entity = centralEntity
      tankGroup.add(central); pickables.push(central)
      const seamMaterial = new THREE.LineBasicMaterial({ color: '#526e7a', transparent: true, opacity: 0.5, clippingPlanes: clipping })
      for (let z = -annularInner + 2.4; z < annularInner; z += 2.4) {
        const half = Math.sqrt(Math.max(0, annularInner ** 2 - z ** 2))
        const points = [new THREE.Vector3(-half, 0.01, z), new THREE.Vector3(half, 0.01, z)]
        tankGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), seamMaterial))
      }
      const sump = new THREE.Mesh(new THREE.CylinderGeometry(spec.bottom.sump_diameter_m / 2, spec.bottom.sump_diameter_m / 2, 0.25, 32), new THREE.MeshStandardMaterial({ color: '#455f6d', clippingPlanes: clipping }))
      sump.position.y = -0.13
      tankGroup.add(sump)
    }

    if (modelMode === 'physical') {
      const roof = spec.physical_roof
      const thetaEnd = Math.asin(roof.base_radius_m / roof.sphere_radius_m)
      const centerY = roof.springline_z_m - roof.sphere_radius_m * Math.cos(thetaEnd)
      const roofEntity = { ...roof, id: 'roof', name: 'Aluminum geodesic dome' }
      if (isVisible(roofEntity)) {
        const roofGeometry = new THREE.SphereGeometry(roof.sphere_radius_m, roof.azimuth_segments, roof.frequency, 0, Math.PI * 2, 0, thetaEnd)
        if (roofMode !== 'frame') {
          const roofMaterial = new THREE.MeshPhysicalMaterial({ color: selected?.id === 'roof' ? '#f0ad4b' : '#b7cbd0', metalness: 0.5, roughness: 0.34, transparent: true, opacity: roofMode === 'transparent' ? 0.28 : 0.78, side: THREE.DoubleSide, clippingPlanes: clipping })
          const roofMesh = new THREE.Mesh(roofGeometry, roofMaterial)
          roofMesh.position.y = centerY
          roofMesh.userData.entity = roofEntity
          tankGroup.add(roofMesh); pickables.push(roofMesh)
        }
        const frame = new THREE.LineSegments(new THREE.EdgesGeometry(roofGeometry, 1), new THREE.LineBasicMaterial({ color: selected?.id === 'roof' ? '#d67c19' : '#e5edf0', transparent: true, opacity: 0.98, clippingPlanes: clipping }))
        frame.position.y = centerY
        frame.userData.entity = roofEntity
        tankGroup.add(frame); pickables.push(frame)
        const hubGeometry = new THREE.SphereGeometry(0.11, 8, 6)
        const hubMaterial = new THREE.MeshStandardMaterial({ color: '#eef5f6', metalness: 0.65, roughness: 0.25, clippingPlanes: clipping })
        const hubs: THREE.Vector3[] = [new THREE.Vector3(0, centerY + roof.sphere_radius_m, 0)]
        for (let ring = 1; ring <= roof.frequency; ring += 1) {
          const theta = thetaEnd * ring / roof.frequency
          const ringRadius = roof.sphere_radius_m * Math.sin(theta)
          const y = centerY + roof.sphere_radius_m * Math.cos(theta)
          for (let j = 0; j < roof.azimuth_segments; j += 1) {
            const angle = j / roof.azimuth_segments * Math.PI * 2 + (ring % 2 ? Math.PI / roof.azimuth_segments : 0)
            hubs.push(new THREE.Vector3(Math.cos(angle) * ringRadius, y, Math.sin(angle) * ringRadius))
          }
        }
        const hubMesh = new THREE.InstancedMesh(hubGeometry, hubMaterial, hubs.length)
        const matrix = new THREE.Matrix4()
        hubs.forEach((position, index) => { matrix.setPosition(position); hubMesh.setMatrixAt(index, matrix) })
        tankGroup.add(hubMesh)
      }
    } else {
      const analysisEntity = { ...spec.analysis_roof, id: 'analysis-roof', name: 'A36 analysis surrogate', entity_type: 'analysis_roof' }
      const surrogate = new THREE.Mesh(new THREE.ConeGeometry(radius, 1.5, 96, 1, false), new THREE.MeshStandardMaterial({ color: '#aeb7bb', metalness: 0.25, roughness: 0.6, transparent: true, opacity: 0.78, clippingPlanes: clipping }))
      surrogate.position.y = spec.shell_height_m + 0.75
      surrogate.userData.entity = analysisEntity
      tankGroup.add(surrogate); pickables.push(surrogate)
    }

    const anchorMaterial = new THREE.MeshStandardMaterial({ color: selectedType === 'anchor_group' ? '#f28c28' : '#bd6a35', roughness: 0.58, clippingPlanes: clipping })
    spec.anchors.forEach((anchor: any) => {
      if (!isVisible(anchor)) return
      const angle = THREE.MathUtils.degToRad(anchor.angle_deg)
      const bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.075, 0.78, 10), selected?.id === anchor.id ? new THREE.MeshStandardMaterial({ color: '#ff9e32', emissive: '#7a3000', emissiveIntensity: 0.45, clippingPlanes: clipping }) : anchorMaterial)
      bolt.position.set(Math.cos(angle) * anchor.radius_m, 0.28, Math.sin(angle) * anchor.radius_m)
      bolt.userData.entity = anchor
      tankGroup.add(bolt); pickables.push(bolt)
    })

    const grid = new THREE.GridHelper(74, 30, '#a4b9c2', '#d5e0e5')
    grid.position.y = -0.28
    scene.add(grid)
    scene.add(new THREE.HemisphereLight('#ffffff', '#5e7d89', 2.15))
    const key = new THREE.DirectionalLight('#fffaf0', 3.4)
    key.position.set(20, 40, 16); key.castShadow = true
    scene.add(key)
    const fill = new THREE.DirectionalLight('#bfe9f1', 1.4)
    fill.position.set(-28, 18, -20); scene.add(fill)

    const raycaster = new THREE.Raycaster()
    const pointer = new THREE.Vector2()
    const pick = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect()
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
      raycaster.setFromCamera(pointer, camera)
      const hit = raycaster.intersectObjects(pickables, false)[0]
      if (hit?.object.userData.entity) onSelect?.({ ...hit.object.userData.entity, entityType: typeOf(hit.object.userData.entity) })
    }
    renderer.domElement.addEventListener('pointerdown', pick)

    const fitModel = () => { camera.position.set(42, 28, 42); controls.target.set(0, spec.shell_height_m * 0.48, 0); controls.update() }
    const fitSelection = () => {
      if (!selected) return fitModel()
      const target = new THREE.Vector3()
      if (selected.course) target.y = (selected.elevation_m ?? (selected.course - 1) * 2.4) + (selected.height_m ?? 2.4) / 2
      else if (selected.id === 'roof') target.y = spec.shell_height_m + spec.physical_roof.cap_height_m * 0.5
      else target.y = 0.5
      if (typeOf(selected) === 'shell_plate') {
        const angle = THREE.MathUtils.degToRad(selected.start_angle_deg + selected.angle_deg / 2)
        target.x = Math.cos(angle) * radius; target.z = Math.sin(angle) * radius
      }
      controls.target.copy(target)
      camera.position.copy(target.clone().add(new THREE.Vector3(16, 10, 16)))
      controls.update()
    }
    const view = (kind: string) => {
      const r = 54, h = spec.shell_height_m * 0.48
      if (kind === 'front') camera.position.set(0, h, r)
      if (kind === 'right') camera.position.set(r, h, 0)
      if (kind === 'top') camera.position.set(0, r + 10, 0.01)
      if (kind === 'iso') camera.position.set(r * .72, r * .5, r * .72)
      controls.target.set(0, h, 0); controls.update()
    }
    sceneRef.current = { camera, controls, spec, view, fitModel, fitSelection }

    const resize = () => {
      const w = Math.max(el.clientWidth, 1), h = Math.max(el.clientHeight, 1)
      perspective.aspect = w / h; perspective.updateProjectionMatrix()
      const span = 34; ortho.left = -span * w / h; ortho.right = span * w / h; ortho.top = span; ortho.bottom = -span; ortho.updateProjectionMatrix()
      renderer.setSize(w, h)
    }
    const observer = new ResizeObserver(resize); observer.observe(el)
    let frame = 0
    const animate = () => { controls.update(); renderer.render(scene, camera); frame = requestAnimationFrame(animate) }
    animate()
    return () => {
      cancelAnimationFrame(frame); observer.disconnect(); renderer.domElement.removeEventListener('pointerdown', pick); controls.dispose(); renderer.dispose()
      scene.traverse((object: any) => { object.geometry?.dispose?.(); if (Array.isArray(object.material)) object.material.forEach((m: any) => m.dispose?.()); else object.material?.dispose?.() })
    }
  }, [spec, selected, projection, displayMode, colorMode, roofMode, modelMode, sectionAxis, sectionPosition, visualScale, isVisible, onSelect])

  useEffect(() => {
    const canvas = mount.current?.querySelector('canvas')
    if (!canvas) return
    const dbl = () => sceneRef.current?.fitSelection?.()
    canvas.addEventListener('dblclick', dbl)
    return () => canvas.removeEventListener('dblclick', dbl)
  }, [selected, spec])

  if (!spec) return <div className="viewer-empty"><div className="wire-tank" /><strong>Modelo no generado</strong><span>Calcule el borrador o una revisión guardada.</span></div>

  return <div className="viewer-shell">
    <div className="viewer-toolbar top">
      <div className="tool-group">{[['front', 'Frente'], ['right', 'Derecha'], ['top', 'Superior'], ['iso', 'Isométrica']].map(([id, label]) => <button key={id} onClick={() => sceneRef.current?.view?.(id)}>{label}</button>)}</div>
      <div className="tool-group"><button onClick={() => sceneRef.current?.fitModel?.()}>Fit model</button><button onClick={() => sceneRef.current?.fitSelection?.()}>Fit selection</button><button onClick={() => setProjection(value => value === 'perspective' ? 'orthographic' : 'perspective')}>{projection === 'perspective' ? 'Perspectiva' : 'Ortográfica'}</button></div>
    </div>
    <div className="viewer-toolbar side">
      <label>Display<select value={displayMode} onChange={event => setDisplayMode(event.target.value as DisplayMode)}><option value="solid">Sólido</option><option value="transparent">Transparente</option><option value="edges">Edges</option><option value="section">Sección</option></select></label>
      <label>Color by<select value={colorMode} onChange={event => setColorMode(event.target.value as ColorMode)}><option value="thickness">Espesor</option><option value="utilization">Utilización</option><option value="material">Material</option></select></label>
      <label>Modelo<select value={modelMode} onChange={event => setModelMode(event.target.value as ModelMode)}><option value="physical">Físico</option><option value="analysis">Análisis</option></select></label>
      {modelMode === 'physical' && <label>Domo<select value={roofMode} onChange={event => setRoofMode(event.target.value as RoofMode)}><option value="panels-frame">Paneles + frame</option><option value="frame">Solo frame</option><option value="transparent">Panel transparente</option></select></label>}
      <label>Espesor visual <span>×{visualScale}</span><input type="range" min="1" max="20" value={visualScale} onChange={event => setVisualScale(Number(event.target.value))} /></label>
      {displayMode === 'section' && <><label>Plano<select value={sectionAxis} onChange={event => setSectionAxis(event.target.value as any)}><option value="x">Section X</option><option value="y">Section Y</option><option value="z">Section Z</option></select></label><label>Posición<input type="range" min="-25" max="25" step="0.5" value={sectionPosition} onChange={event => setSectionPosition(Number(event.target.value))} /></label></>}
    </div>
    <div ref={mount} className="viewer-canvas" aria-label="Modelo 3D de ingeniería del tanque" />
    <div className="viewer-caption"><span><i /> Visual thickness ×{visualScale} · no altera cálculo</span><span>{modelMode === 'physical' ? 'Geodesic roof: REPRESENTATIVE · Supplier scope' : 'Conservative A36 surrogate · TANK-2016 reconstruction'}</span></div>
    <div className="color-legend"><span>{colorMode === 'thickness' ? '8 mm' : colorMode === 'utilization' ? '0%' : 'A36 I'}</span><i className={colorMode} /><span>{colorMode === 'thickness' ? '25 mm' : colorMode === 'utilization' ? '100%' : 'A36 II'}</span></div>
  </div>
}
