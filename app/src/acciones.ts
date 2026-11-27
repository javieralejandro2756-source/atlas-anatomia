// Acciones compartidas por la versión Mac y la versión iPhone.
import { getEstado, setEstado } from "./estado";
import { capaSuperficial } from "./escena";

/** Quita la capa más superficial de músculos. Devuelve cuántas estructuras se quitaron. */
export function quitarCapa(): number {
  const capa = capaSuperficial(getEstado());
  if (!capa.length) return 0;
  setEstado((s) => ({
    capas: [...s.capas, capa],
    ocultas: new Set([...s.ocultas, ...capa]),
    seleccion: capa.includes(s.seleccion ?? "") ? null : s.seleccion,
  }));
  return capa.length;
}

/** Devuelve la última capa quitada. Devuelve cuántas estructuras volvieron. */
export function devolverCapa(): number {
  const s = getEstado();
  const capas = [...s.capas];
  const ultima = capas.pop() ?? [];
  const ocultas = new Set(s.ocultas);
  ultima.forEach((n) => ocultas.delete(n));
  setEstado({ capas, ocultas });
  return ultima.length;
}

export function mostrarTodo() {
  setEstado({ ocultas: new Set(), transparentes: new Set(), aisladas: null, capas: [] });
}

export const enfocar = (nombre?: string) => window.dispatchEvent(new CustomEvent("atlas:enfocar", { detail: nombre }));
export const medir = () => window.dispatchEvent(new CustomEvent("atlas:medir"));
