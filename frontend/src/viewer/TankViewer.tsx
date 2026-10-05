import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

type Props = { spec?: any; selectedCourse?: number; onSelectCourse?: (course: number) => void }

export default function TankViewer({ spec, selectedCourse = 1, onSelectCourse }: Props) {
  const mount = useRef<HTMLDivElement>(null)
  const [projection, setProjection] = useState<'perspective' | 'orthographic'>('perspective')
  const sceneRef = useRef<any>(null)

  useEffect(() => {
    if (!mount.current || !spec) return
    const el = mount.current
    const scene = new THREE.Scene()
    scene.background = new THREE.Color('#eef4f7')
    const perspective = new THREE.PerspectiveCamera(36, el.clientWidth / el.clientHeight, 0.1, 500)
    perspective.position.set(43, 30, 43)
    const ortho = new THREE.OrthographicCamera(-32, 32, 22, -22, 0.1, 500)
    ortho.position.set(43, 30, 43)
    const camera = projection === 'perspective' ? perspective : ortho
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(el.clientWidth, el.clientHeight)
    renderer.localClippingEnabled = true
    el.replaceChildren(renderer.domElement)
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.target.set(0, spec.shell_height_m * 0.45, 0)
    controls.enableDamping = true
    const tankGroup = new THREE.Group()
    scene.add(tankGroup)
    const colors = ['#376d83', '#477f92', '#5a91a3', '#70a4b3', '#88b5c0', '#9fc3ca', '#b7d0d4', '#cddfe1']
    const courseMeshes: THREE.Mesh[] = []
    spec.courses.forEach((course: any, i: number) => {
      const thickness = Math.max(course.thickness_mm / 1000, 0.12)
      const geometry = new THREE.CylinderGeometry(spec.nominal_diameter_m / 2 + thickness, spec.nominal_diameter_m / 2 + thickness, course.height_m, 96, 1, true)
      const material = new THREE.MeshStandardMaterial({ color: colors[i], roughness: 0.62, metalness: 0.16, transparent: i + 1 !== selectedCourse, opacity: i + 1 === selectedCourse ? 1 : 0.77, side: THREE.DoubleSide })
      const mesh = new THREE.Mesh(geometry, material)
      mesh.position.y = course.elevation_m + course.height_m / 2
      mesh.userData.course = i + 1
      tankGroup.add(mesh)
      courseMeshes.push(mesh)
    })
    const bottom = new THREE.Mesh(new THREE.CylinderGeometry(spec.nominal_diameter_m / 2, spec.nominal_diameter_m / 2, 0.15, 96), new THREE.MeshStandardMaterial({ color: '#738a96', roughness: 0.7 }))
    bottom.position.y = -0.075
    tankGroup.add(bottom)
    const roof = new THREE.Mesh(new THREE.SphereGeometry(spec.nominal_diameter_m / 2, 96, 24, 0, Math.PI * 2, 0, Math.PI / 5), new THREE.MeshStandardMaterial({ color: '#b9c9cd', roughness: 0.45, metalness: 0.18, transparent: true, opacity: 0.92 }))
    roof.scale.y = 0.34
    roof.position.y = spec.shell_height_m
    tankGroup.add(roof)
    const anchorMaterial = new THREE.MeshStandardMaterial({ color: '#bf6b34', roughness: 0.6 })
    spec.anchors.forEach((anchor: any) => {
      const angle = THREE.MathUtils.degToRad(anchor.angle_deg)
      const bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.8, 10), anchorMaterial)
      bolt.position.set(Math.cos(angle) * anchor.radius_m, 0.2, Math.sin(angle) * anchor.radius_m)
      tankGroup.add(bolt)
    })
    const grid = new THREE.GridHelper(75, 30, '#9fb4bf', '#d6e0e5')
    scene.add(grid)
    scene.add(new THREE.HemisphereLight('#ffffff', '#72909c', 2.2))
    const key = new THREE.DirectionalLight('#fff8e7', 3.1)
    key.position.set(20, 38, 15)
    scene.add(key)
    const raycaster = new THREE.Raycaster()
    const pointer = new THREE.Vector2()
    const click = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect()
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
      raycaster.setFromCamera(pointer, camera)
      const hit = raycaster.intersectObjects(courseMeshes)[0]
      if (hit) onSelectCourse?.(hit.object.userData.course)
    }
    renderer.domElement.addEventListener('pointerdown', click)
    const resize = () => {
      const w = el.clientWidth, h = el.clientHeight
      perspective.aspect = w / h; perspective.updateProjectionMatrix()
      const span = 32; ortho.left = -span * w / h; ortho.right = span * w / h; ortho.top = span; ortho.bottom = -span; ortho.updateProjectionMatrix()
      renderer.setSize(w, h)
    }
    window.addEventListener('resize', resize)
    let frame = 0
    const animate = () => { controls.update(); renderer.render(scene, camera); frame = requestAnimationFrame(animate) }
    animate()
    sceneRef.current = { camera, controls, spec }
    return () => { cancelAnimationFrame(frame); window.removeEventListener('resize', resize); renderer.domElement.removeEventListener('pointerdown', click); controls.dispose(); renderer.dispose(); scene.traverse((o: any) => { o.geometry?.dispose?.(); o.material?.dispose?.() }) }
  }, [spec, projection, selectedCourse, onSelectCourse])

  const view = (kind: string) => {
    const x = sceneRef.current
    if (!x) return
    const r = 52, h = x.spec.shell_height_m * 0.45
    if (kind === 'front') x.camera.position.set(0, h, r)
    if (kind === 'side') x.camera.position.set(r, h, 0)
    if (kind === 'top') x.camera.position.set(0, r + 10, 0.01)
    if (kind === 'iso') x.camera.position.set(r * .72, r * .5, r * .72)
    x.controls.target.set(0, h, 0); x.controls.update()
  }

  return <div className="viewer-shell">
    <div className="viewer-toolbar" aria-label="Controles de vista">
      {['front', 'side', 'top', 'iso'].map(v => <button key={v} onClick={() => view(v)}>{v === 'iso' ? 'Isométrica' : v === 'front' ? 'Frente' : v === 'side' ? 'Lateral' : 'Superior'}</button>)}
      <button onClick={() => setProjection(p => p === 'perspective' ? 'orthographic' : 'perspective')}>{projection === 'perspective' ? 'Perspectiva' : 'Ortográfica'}</button>
    </div>
    <div ref={mount} className="viewer-canvas" aria-label="Modelo 3D paramétrico del tanque" />
    <div className="viewer-legend"><span className="legend-dot" /> Espesor exagerado para inspección · selección: curso {selectedCourse}</div>
  </div>
}

