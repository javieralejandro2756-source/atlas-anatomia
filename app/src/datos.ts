// Tipos y carga de los datos estáticos (manifest de modelos y nombres TA2).

export type Sistema = "huesos" | "musculos" | "ligamentos" | "nervios" | "inserciones" | "fascias" | "snc";
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
  { id: "musculos", nombre: "Músculos y tendones", color: "#a8342b" },
  { id: "fascias", nombre: "Fascias, bolsas y vainas", color: "#b9c6cc" },
  { id: "nervios", nombre: "Nervios periféricos y pares craneales", color: "#f0c419" },
  { id: "snc", nombre: "Encéfalo y médula espinal", color: "#d6b1ba" },
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

export interface Ficha {
  id: string;
  nombre: string;
  region: string;
  origen: string;
  insercion: string;
  inervacion: string;
  raices: string[];
  raiz_principal: string[];
  pares_craneales: string[];
  inervacion_segmentaria: boolean;
  irrigacion: string;
  funcion: string;
  estado: string;
  fuente_cotejo: string;
  tipo: string;
}

export interface Lesion {
  n: number;
  fichas: string[];
  estructura: string;
  diagnostico: string;
  poblacion: string;
  medida: string;
  valor: string;
  cita: string;
  pmid: string;
  doi: string;
  estado: string; // "propuesta" hasta que el usuario la apruebe; "aprobada" después
}

export type Area = "motora" | "somatosensorial" | "vision" | "audicion" | "gusto" | "olfato" | "equilibrio" | "lenguaje" | "prefrontal" | "limbico";

export const AREAS: { id: Area; nombre: string; color: string }[] = [
  { id: "motora", nombre: "Motora", color: "#e4572e" },
  { id: "somatosensorial", nombre: "Somatosensorial", color: "#3a86ff" },
  { id: "vision", nombre: "Visión", color: "#9b5de5" },
  { id: "audicion", nombre: "Audición", color: "#f4a259" },
  { id: "gusto", nombre: "Gusto", color: "#e9c46a" },
  { id: "olfato", nombre: "Olfato", color: "#8ac926" },
  { id: "equilibrio", nombre: "Equilibrio", color: "#00b4d8" },
  { id: "lenguaje", nombre: "Lenguaje", color: "#ff70a6" },
  { id: "prefrontal", nombre: "Prefrontal (personalidad, juicio)", color: "#c9a227" },
  { id: "limbico", nombre: "Memoria y emoción (límbico)", color: "#57cc99" },
];

export interface FichaEncefalo {
  id: string;
  nombre: string;
  grupo: string;
  areas: Area[];
  brodmann: string;
  funcion: string;
  lesion: string;
  componentes?: string;
  salida?: string;
  fuente: string;
  estado: string;
}

export interface Encefalo {
  fichas: FichaEncefalo[];
  mallas: Record<string, string>; // nombre base de malla -> id de ficha
}

export function fichaEncefaloDe(nombreMalla: string, d: Datos): FichaEncefalo | null {
  const id = d.encefalo.mallas[base(nombreMalla).replace(/^\s+/, "")] ?? d.encefalo.mallas[base(nombreMalla)];
  return id ? d.encefalo.fichas.find((f) => f.id === id) ?? null : null;
}

export interface Datos {
  encefalo: Encefalo;
  lesiones: Lesion[];
  manifest: Manifest;
  nombres: Nombres;
  fichas: Record<string, Ficha>;
  mapeo: Record<string, string[]>; // nombre base de malla -> ids de ficha
}

/** Fichas ligadas a una malla (también para sus zonas de origen e inserción). */
export function fichasDe(nombreMalla: string, d: Datos): Ficha[] {
  return (d.mapeo[base(nombreMalla)] ?? []).map((id) => d.fichas[id]).filter(Boolean);
}

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

/** carpeta: "./modelos/" (Mac) o "../modelos-iphone/" (iPhone); raiz: "./" o "../". */
export async function cargarDatos(carpeta = "./modelos/", raiz = "./"): Promise<Datos> {
  const [manifest, nombres, lista, mapeo, lesiones, encefalo] = await Promise.all([
    fetch(carpeta + "manifest.json").then((r) => r.json()),
    fetch(carpeta + "nombres.json").then((r) => r.json()),
    fetch(raiz + "datos/fichas.json").then((r) => r.json()),
    fetch(raiz + "datos/mapeo.json").then((r) => r.json()),
    fetch(raiz + "datos/lesiones.json").then((r) => (r.ok ? r.json() : [])).catch(() => []),
    fetch(raiz + "datos/encefalo.json").then((r) => (r.ok ? r.json() : { fichas: [], mallas: {} })).catch(() => ({ fichas: [], mallas: {} })),
  ]);
  const fichas: Record<string, Ficha> = {};
  for (const f of lista as Ficha[]) fichas[f.id] = f;
  return { manifest, nombres, fichas, mapeo, lesiones, encefalo };
}
