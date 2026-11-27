// Tipos y carga de los datos estáticos (manifest de modelos y nombres TA2).

export type Sistema = "huesos" | "musculos" | "ligamentos" | "nervios" | "inserciones" | "fascias";
export type Region = "miembro-inferior" | "miembro-superior" | "tronco" | "cabeza-cuello";

export const REGIONES: { id: Region; nombre: string }[] = [
  { id: "cabeza-cuello", nombre: "Cabeza y cuello" },
  { id: "tronco", nombre: "Tronco" },
  { id: "miembro-superior", nombre: "Miembro superior" },
  { id: "miembro-inferior", nombre: "Miembro inferior" },
];

export const SISTEMAS: { id: Sistema; nombre: string; color: string }[] = [
  { id: "huesos", nombre: "Huesos", color: "#e9dfc9" },
  { id: "ligamentos", nombre: "Ligamentos y articulaciones", color: "#c9c08e" },
  { id: "musculos", nombre: "Músculos y tendones", color: "#b8463c" },
  { id: "fascias", nombre: "Fascias, bolsas y vainas", color: "#b9c6cc" },
  { id: "nervios", nombre: "Nervios periféricos", color: "#f0c419" },
  { id: "inserciones", nombre: "Orígenes e inserciones", color: "#7a5cc7" },
];

export interface MallaInfo {
  nombre: string;
  archivo: string;
  sistema: Sistema;
  region: Region;
  lado: "izquierdo" | "derecho" | "medial";
  tris_original: number;
  tris?: number;
}

export interface ArchivoInfo {
  region: Region;
  sistema: Sistema;
  mallas: number;
  tris: number;
  bytes: number;
}

export interface Manifest {
  archivos: Record<string, ArchivoInfo>;
  mallas: MallaInfo[];
}

export type Nombres = Record<string, { es: string; la: string }>;

/** Nombre sin el sufijo de lado (.l, .r, .j) ni el de origen/inserción (.ol, .e2r...). */
export function base(nombre: string): string {
  return nombre.replace(/\.(l|r|j|[oe]\d*[lr])$/, "").trim();
}

/** "o" = origen, "e" = inserción (convención de Z-Anatomy), o null. */
export function tipoZona(nombre: string): "origen" | "insercion" | null {
  const m = nombre.match(/\.([oe])\d*[lr]$/);
  if (!m) return null;
  return m[1] === "o" ? "origen" : "insercion";
}

export function nombreVisible(nombre: string, nombres: Nombres) {
  const b = base(nombre);
  const t = nombres[b] ?? nombres[b.replace(/^[([]|[)\]]$/g, "")];
  const es = t?.es ? t.es.replace(/^Hueso\s+/, "") : "";
  return { es: es || b, en: b, la: t?.la ?? "", traducido: Boolean(es) };
}

/** carpeta: "./modelos/" (Mac) o "../modelos-iphone/" (iPhone). */
export async function cargarDatos(carpeta = "./modelos/"): Promise<{ manifest: Manifest; nombres: Nombres }> {
  const [manifest, nombres] = await Promise.all([
    fetch(carpeta + "manifest.json").then((r) => r.json()),
    fetch(carpeta + "nombres.json").then((r) => r.json()),
  ]);
  return { manifest, nombres };
}
