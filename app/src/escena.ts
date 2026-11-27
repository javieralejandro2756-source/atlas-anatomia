// Registro de mallas cargadas y utilidades de escena (materiales, capas, medición).
import * as THREE from "three";
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from "three-mesh-bvh";
import { AREAS, SISTEMAS, base as baseNombre, tipoZona, type Sistema } from "./datos";
import { esVisible, type Estado } from "./estado";

// Raycast acelerado (BVH): selección y "quitar capa" rápidos.
(THREE.BufferGeometry.prototype as any).computeBoundsTree = computeBoundsTree;
(THREE.BufferGeometry.prototype as any).disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

export const mallas = new Map<string, THREE.Mesh>();
// Acceso para pruebas automáticas (sin efecto en el uso normal).
(window as any).__atlas = { mallas, THREE };

function mat(color: string, extra: Partial<THREE.MeshStandardMaterialParameters> = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0, envMapIntensity: 0.55, ...extra });
}

const base: Record<string, THREE.MeshStandardMaterial> = {};
const transp: Record<string, THREE.MeshStandardMaterial> = {};
for (const s of SISTEMAS) {
  base[s.id] = mat(s.color, s.id === "fascias" ? { transparent: true, opacity: 0.55, depthWrite: false } : {});
  transp[s.id] = mat(s.color, { transparent: true, opacity: 0.18, depthWrite: false });
}
base["origen"] = mat("#d64545", { polygonOffset: true, polygonOffsetFactor: -2 });
base["insercion"] = mat("#2f74d0", { polygonOffset: true, polygonOffsetFactor: -2 });
transp["origen"] = mat("#d64545", { transparent: true, opacity: 0.18, depthWrite: false });
transp["insercion"] = mat("#2f74d0", { transparent: true, opacity: 0.18, depthWrite: false });
// Áreas funcionales del sistema nervioso: nombre base de malla -> etiquetas.
let areasDeMalla: Record<string, string[]> = {};
export function definirAreas(m: Record<string, string[]>) { areasDeMalla = m; }
const matArea: Record<string, THREE.MeshStandardMaterial> = {};
for (const a of AREAS) matArea[a.id] = mat(a.color, { emissive: new THREE.Color(a.color), emissiveIntensity: 0.25 });
const atenuado = mat("#8a8f99", { transparent: true, opacity: 0.12, depthWrite: false });

const resaltado = mat("#2ec4b6", { emissive: new THREE.Color("#0f6d66"), emissiveIntensity: 0.6 });

function claveMaterial(m: THREE.Mesh): string {
  const s = m.userData.sistema as Sistema;
  if (s === "inserciones") return tipoZona(m.name) ?? "origen";
  return s;
}

export function registrar(m: THREE.Mesh, sistema: Sistema, region: string, archivo: string) {
  if (typeof m.userData.nombre === "string") m.name = m.userData.nombre;
  m.userData = { ...m.userData, sistema, region, archivo };
  (m.geometry as any).computeBoundsTree?.();
  m.material = base[claveMaterial(m)];
  // Las zonas de origen/inserción se dibujan encima del hueso.
  if (sistema === "inserciones") m.renderOrder = 2;
  mallas.set(m.name, m);
}

export function quitarArchivo(archivo: string) {
  for (const [n, m] of mallas) if (m.userData.archivo === archivo) mallas.delete(n);
}

/** Aplica visibilidad, transparencia y resaltado a todas las mallas. */
export function aplicarEstado(e: Estado) {
  for (const m of mallas.values()) {
    const sis = m.userData.sistema as Sistema;
    const enCapa = e.sistemas.has(sis) && e.regiones.has(m.userData.region);
    m.visible = enCapa && esVisible(m.name, e);
    const k = claveMaterial(m);
    const nervioso = sis === "snc" || sis === "nervios";
    if (e.seleccion === m.name) m.material = resaltado;
    else if (e.area && nervioso) {
      const tags = areasDeMalla[baseNombre(m.name)] ?? [];
      m.material = tags.includes(e.area) ? matArea[e.area] : atenuado;
    } else if (e.transparentes.has(m.name)) m.material = transp[k];
    else m.material = base[k];
  }
}

/** Mallas que el usuario puede ver ahora (visibles y no transparentes). */
export function visiblesOpacas(e: Estado, sistemas?: Sistema[]) {
  return [...mallas.values()].filter(
    (m) => m.visible && !e.transparentes.has(m.name) && (!sistemas || sistemas.includes(m.userData.sistema)),
  );
}

/**
 * Quitar capa: lanza rayos desde 14 direcciones alrededor de lo visible y
 * devuelve las mallas (músculos y fascias) que se ven primero: la capa más superficial.
 */
export function capaSuperficial(e: Estado): string[] {
  const candidatas = visiblesOpacas(e, ["musculos", "fascias"]);
  if (!candidatas.length) return [];
  // Los huesos y ligamentos también tapan rayos (un músculo detrás del hueso no es superficial).
  const obstaculos = visiblesOpacas(e);
  const caja = new THREE.Box3();
  candidatas.forEach((m) => caja.expandByObject(m));
  const centro = caja.getCenter(new THREE.Vector3());
  const radio = caja.getSize(new THREE.Vector3()).length() / 2;
  const dirs: THREE.Vector3[] = [];
  for (const x of [-1, 0, 1]) for (const y of [-1, 0, 1]) for (const z of [-1, 0, 1]) {
    const v = new THREE.Vector3(x, y, z);
    if (v.lengthSq() === 0) continue;
    if (Math.abs(x) + Math.abs(y) + Math.abs(z) === 2) continue; // 6 ejes + 8 diagonales = 14
    dirs.push(v.normalize());
  }
  const ray = new THREE.Raycaster();
  (ray as any).firstHitOnly = true;
  const golpes = new Map<string, number>();
  const N = 48;
  for (const d of dirs) {
    const u = new THREE.Vector3().crossVectors(d, Math.abs(d.y) < 0.9 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0)).normalize();
    const w = new THREE.Vector3().crossVectors(d, u).normalize();
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
      const o = centro.clone()
        .addScaledVector(d, -radio * 1.5)
        .addScaledVector(u, ((i + 0.5) / N - 0.5) * 2 * radio)
        .addScaledVector(w, ((j + 0.5) / N - 0.5) * 2 * radio);
      ray.set(o, d);
      const hit = ray.intersectObjects(obstaculos, false)[0];
      if (hit && candidatas.includes(hit.object as THREE.Mesh)) {
        golpes.set(hit.object.name, (golpes.get(hit.object.name) ?? 0) + 1);
      }
    }
  }
  // Solo cuenta como superficial lo que se ve en una superficie amplia (no un borde que asoma).
  const total = [...golpes.values()].reduce((a, b) => a + b, 0);
  const minimo = Math.max(12, total * 0.006);
  return [...golpes.entries()].filter(([, n]) => n >= minimo).map(([k]) => k);
}

export function triangulosVisibles(): number {
  let t = 0;
  for (const m of mallas.values()) {
    if (!m.visible) continue;
    const g = m.geometry;
    t += (g.index ? g.index.count : g.attributes.position.count) / 3;
  }
  return Math.round(t);
}
