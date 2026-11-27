import { Suspense, useEffect, useMemo, useRef } from "react";
import { Canvas, useThree, useFrame, type ThreeEvent } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import type { Manifest } from "./datos";
import { getEstado, setEstado, useEstado } from "./estado";
import { aplicarEstado, mallas, quitarArchivo, registrar, triangulosVisibles } from "./escena";

export interface Perfil {
  carpeta: string; // ruta de los modelos
  draco: string; // ruta del decodificador Draco
  dpr: [number, number];
  tactil: boolean; // en el iPhone no hay doble clic (choca con el zoom de Safari)
}

export const PERFIL_MAC: Perfil = { carpeta: "./modelos/", draco: "./draco/", dpr: [1, 1.5], tactil: false };

function Archivo({ archivo, info, perfil }: { archivo: string; info: Manifest["archivos"][string]; perfil: Perfil }) {
  const { scene } = useGLTF(`${perfil.carpeta}${archivo}`, perfil.draco);
  const invalidate = useThree((s) => s.invalidate);
  useEffect(() => {
    scene.traverse((o) => {
      if ((o as THREE.Mesh).isMesh) registrar(o as THREE.Mesh, info.sistema, info.region, archivo);
    });
    aplicarEstado(getEstado());
    invalidate();
    window.dispatchEvent(new CustomEvent("atlas:cargado", { detail: archivo }));
    return () => quitarArchivo(archivo);
  }, [scene, archivo, info, invalidate]);
  return <primitive object={scene} />;
}

function Contador({ archivo }: { archivo: string }) {
  // Marca la carga como pendiente mientras el Suspense espera.
  useEffect(() => {
    setEstado((e) => ({ cargando: e.cargando + 1 }));
    return () => setEstado((e) => ({ cargando: Math.max(0, e.cargando - 1) }));
  }, [archivo]);
  return null;
}

/** Luz ambiental de estudio (generada, sin descargar nada): da relieve a fibras y bordes. */
function Ambiente() {
  const { gl, scene, invalidate } = useThree();
  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const tex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = tex;
    invalidate();
    return () => { scene.environment = null; tex.dispose(); pmrem.dispose(); };
  }, [gl, scene, invalidate]);
  return null;
}

// Cámara y tamaño actuales, para la selección tolerante al dedo.
const ctx3 = { camera: null as THREE.Camera | null, size: { width: 1, height: 1 } };
function Contexto() {
  const camera = useThree((s) => s.camera);
  const size = useThree((s) => s.size);
  ctx3.camera = camera;
  ctx3.size = size;
  return null;
}

/** Busca la estructura visible más cercana alrededor del punto tocado (radio en px). */
function buscarCerca(cx: number, cy: number, radio: number): string | null {
  const cam = ctx3.camera;
  if (!cam) return null;
  const visibles = [...mallas.values()].filter((m) => m.visible);
  const ray = new THREE.Raycaster();
  (ray as any).firstHitOnly = true;
  for (const r of [radio / 3, (radio * 2) / 3, radio]) {
    for (let k = 0; k < 12; k++) {
      const a = (k / 12) * Math.PI * 2;
      const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
      ray.setFromCamera(new THREE.Vector2((x / ctx3.size.width) * 2 - 1, -(y / ctx3.size.height) * 2 + 1), cam);
      const h = ray.intersectObjects(visibles, false)[0];
      if (h) return h.object.name;
    }
  }
  return null;
}

/** Aplica el estado a la escena cada vez que cambia y pide un cuadro nuevo. */
function Sincronizar() {
  const invalidate = useThree((s) => s.invalidate);
  const e = useEstado((x) => x);
  useEffect(() => {
    aplicarEstado(e);
    invalidate();
  }, [e, invalidate]);
  return null;
}

/** Enfoca la cámara en la selección al hacer doble clic o al pedirlo desde el panel. */
function Enfoque() {
  const { camera, controls, invalidate } = useThree() as any;
  (window as any).__atlas = { ...(window as any).__atlas, camera };
  useEffect(() => {
    const f = (ev: Event) => {
      const nombre = (ev as CustomEvent).detail as string | undefined;
      const caja = new THREE.Box3();
      if (nombre && mallas.get(nombre)) caja.expandByObject(mallas.get(nombre)!);
      else mallas.forEach((m) => m.visible && caja.expandByObject(m));
      if (caja.isEmpty() || !controls) return;
      const c = caja.getCenter(new THREE.Vector3());
      const r = Math.max(caja.getSize(new THREE.Vector3()).length() / 2, 0.04);
      const dir = camera.position.clone().sub(controls.target).normalize();
      controls.target.copy(c);
      // Distancia para que quepa en el lado más angosto de la pantalla (en el iPhone vertical, el ancho).
      const vfov = (camera.fov * Math.PI) / 180;
      const hfov = 2 * Math.atan(Math.tan(vfov / 2) * camera.aspect);
      const t = caja.getSize(new THREE.Vector3());
      const ancho = Math.max(t.x, t.z);
      const dist = Math.max(t.y / 2 / Math.tan(vfov / 2), ancho / 2 / Math.tan(hfov / 2)) * 1.12 + ancho / 2;
      camera.position.copy(c.clone().addScaledVector(dir, dist));
      camera.near = r / 50;
      camera.updateProjectionMatrix();
      controls.update();
      invalidate();
    };
    window.addEventListener("atlas:enfocar", f);
    return () => window.removeEventListener("atlas:enfocar", f);
  }, [camera, controls, invalidate]);
  return null;
}

/** Medición de rendimiento: gira la cámara 6 s y cuenta cuadros. */
function Medidor() {
  const { gl, controls, invalidate } = useThree() as any;
  const midiendo = useRef<{ t0: number; frames: number; peor: number; ultimo: number } | null>(null);
  useEffect(() => {
    const f = () => {
      midiendo.current = { t0: performance.now(), frames: 0, peor: 0, ultimo: performance.now() };
      invalidate();
    };
    window.addEventListener("atlas:medir", f);
    return () => window.removeEventListener("atlas:medir", f);
  }, [invalidate]);
  useFrame(() => {
    const m = midiendo.current;
    if (!m) return;
    const ahora = performance.now();
    m.frames++;
    m.peor = Math.max(m.peor, ahora - m.ultimo);
    m.ultimo = ahora;
    if (controls) {
      const t = controls.target as THREE.Vector3;
      const cam = controls.object as THREE.Camera;
      cam.position.sub(t).applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.02).add(t);
      controls.update();
    }
    if (ahora - m.t0 > 6000) {
      const fps = (m.frames * 1000) / (ahora - m.t0);
      const r = gl.info.render;
      window.dispatchEvent(new CustomEvent("atlas:medido", {
        detail: { fps: Math.round(fps), peorMs: Math.round(m.peor), llamadas: r.calls, triangulos: triangulosVisibles(), renderer: rendererName(gl) },
      }));
      midiendo.current = null;
    } else invalidate();
  });
  return null;
}

function rendererName(gl: THREE.WebGLRenderer) {
  try {
    const ctx = gl.getContext();
    const ext = ctx.getExtension("WEBGL_debug_renderer_info");
    return ext ? String(ctx.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : "desconocido";
  } catch {
    return "desconocido";
  }
}

export default function Visor({ manifest, perfil = PERFIL_MAC }: { manifest: Manifest; perfil?: Perfil }) {
  const regiones = useEstado((e) => e.regiones);
  const sistemas = useEstado((e) => e.sistemas);
  // Carga bajo demanda: solo los archivos de las regiones y sistemas activos.
  const archivos = useMemo(
    () => Object.entries(manifest.archivos).filter(([, a]) => regiones.has(a.region) && sistemas.has(a.sistema)),
    [manifest, regiones, sistemas],
  );

  const alClic = (ev: ThreeEvent<MouseEvent>) => {
    if (ev.delta > (perfil.tactil ? 10 : 4)) return; // fue un arrastre, no un toque
    const hit = ev.intersections.find((i) => i.object.visible && (i.object as THREE.Mesh).isMesh);
    ev.stopPropagation();
    // El rayo pudo tocar solo mallas ocultas (capas quitadas): se busca alrededor del dedo.
    const cerca = hit ? null : buscarCerca(ev.nativeEvent.offsetX, ev.nativeEvent.offsetY, perfil.tactil ? 18 : 6);
    setEstado({ seleccion: hit ? hit.object.name : cerca });
  };
  const alDobleClic = (ev: ThreeEvent<MouseEvent>) => {
    const hit = ev.intersections.find((i) => i.object.visible);
    ev.stopPropagation();
    if (hit) window.dispatchEvent(new CustomEvent("atlas:enfocar", { detail: hit.object.name }));
  };

  return (
    <Canvas
      frameloop="demand"
      dpr={perfil.dpr}
      gl={{ antialias: true, powerPreference: "high-performance", toneMapping: THREE.NeutralToneMapping }}
      camera={{ position: [0.9, 0.8, 1.6], fov: 35, near: 0.01, far: 50 }}
      onPointerMissed={(ev) => {
        // Toque fuera de todo: con el dedo se busca alrededor antes de quitar la selección.
        const cerca = perfil.tactil ? buscarCerca(ev.offsetX, ev.offsetY, 18) : null;
        setEstado({ seleccion: cerca });
      }}
    >
      <color attach="background" args={["#14171c"]} />
      <Ambiente />
      <Contexto />
      <hemisphereLight args={["#ffffff", "#3a3f48", 0.45]} />
      <directionalLight position={[2, 3, 2]} intensity={1.4} />
      <directionalLight position={[-2, 1, -2]} intensity={0.45} />
      <group onClick={alClic} onDoubleClick={perfil.tactil ? undefined : alDobleClic}>
        {archivos.map(([archivo, info]) => (
          <Suspense key={archivo} fallback={<Contador archivo={archivo} />}>
            <Archivo archivo={archivo} info={info} perfil={perfil} />
          </Suspense>
        ))}
      </group>
      <OrbitControls makeDefault target={[0, 0.5, 0]} enableDamping={false} />
      <Sincronizar />
      <Enfoque />
      <Medidor />
    </Canvas>
  );
}
