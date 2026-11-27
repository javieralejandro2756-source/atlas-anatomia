// Estado global mínimo con useSyncExternalStore (sin dependencias extra).
import { useSyncExternalStore } from "react";
import type { Region, Sistema } from "./datos";

export interface Estado {
  regiones: Set<Region>;
  sistemas: Set<Sistema>;
  seleccion: string | null; // nombre de la malla
  ocultas: Set<string>;
  transparentes: Set<string>;
  aisladas: Set<string> | null; // si no es null, solo estas se ven
  capas: string[][]; // pila de capas quitadas (para restaurar)
  cargando: number;
  mostrarCreditos: boolean;
}

let estado: Estado = {
  regiones: new Set<Region>(["miembro-inferior"]),
  sistemas: new Set<Sistema>(["huesos", "musculos"]),
  seleccion: null,
  ocultas: new Set(),
  transparentes: new Set(),
  aisladas: null,
  capas: [],
  cargando: 0,
  mostrarCreditos: false,
};

const oyentes = new Set<() => void>();

export function getEstado() {
  return estado;
}

export function setEstado(cambio: Partial<Estado> | ((e: Estado) => Partial<Estado>)) {
  const parcial = typeof cambio === "function" ? cambio(estado) : cambio;
  estado = { ...estado, ...parcial };
  oyentes.forEach((f) => f());
}

export function useEstado<T>(sel: (e: Estado) => T): T {
  return useSyncExternalStore(
    (f) => {
      oyentes.add(f);
      return () => oyentes.delete(f);
    },
    () => sel(estado),
  );
}

export function alternar<T>(conjunto: Set<T>, valor: T): Set<T> {
  const n = new Set(conjunto);
  if (n.has(valor)) n.delete(valor);
  else n.add(valor);
  return n;
}

/** ¿Se dibuja esta malla? Lo oculto no se dibuja. */
export function esVisible(nombre: string, e: Estado): boolean {
  if (e.ocultas.has(nombre)) return false;
  if (e.aisladas && !e.aisladas.has(nombre)) return false;
  return true;
}
