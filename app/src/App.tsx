import { useEffect, useMemo, useState } from "react";
import Visor from "./Visor";
import Creditos from "./Creditos";
import { REGIONES, SISTEMAS, cargarDatos, fichaEncefaloDe, fichasDe, nombreVisible, tipoZona, type Datos } from "./datos";
import FichaVista, { FichaEncefaloVista, FiltroAreas } from "./FichaVista";
import { alternar, getEstado, setEstado, useEstado } from "./estado";
import { capaSuperficial, definirAreas, mallas } from "./escena";

const NOMBRE_SISTEMA = Object.fromEntries(SISTEMAS.map((s) => [s.id, s.nombre]));
const NOMBRE_REGION = Object.fromEntries(REGIONES.map((r) => [r.id, r.nombre]));
const mb = (b: number) => (b / 1e6).toFixed(1) + " MB";

interface Medicion { fps: number; peorMs: number; llamadas: number; triangulos: number; renderer: string }

function definirAreasDe(d: Datos) {
  const m: Record<string, string[]> = {};
  for (const [malla, id] of Object.entries(d.encefalo.mallas)) {
    const f = d.encefalo.fichas.find((x) => x.id === id);
    if (f) m[malla.trim()] = f.areas;
  }
  definirAreas(m);
}

export default function App() {
  const [datos, setDatos] = useState<Datos | null>(null);
  const [error, setError] = useState("");
  const [medicion, setMedicion] = useState<Medicion | null>(null);
  const [midiendo, setMidiendo] = useState(false);
  const [aviso, setAviso] = useState("");
  const e = useEstado((x) => x);

  useEffect(() => {
    cargarDatos().then((d) => { definirAreasDe(d); setDatos(d); }).catch(() => setError("No se pudieron leer los datos de los modelos."));
    let primero = true;
    const alCargar = () => {
      if (primero) { primero = false; setTimeout(() => window.dispatchEvent(new CustomEvent("atlas:enfocar")), 50); }
    };
    const alMedir = (ev: Event) => { setMedicion((ev as CustomEvent).detail); setMidiendo(false); };
    window.addEventListener("atlas:cargado", alCargar);
    window.addEventListener("atlas:medido", alMedir);
    return () => { window.removeEventListener("atlas:cargado", alCargar); window.removeEventListener("atlas:medido", alMedir); };
  }, []);

  const activos = useMemo(() => {
    if (!datos) return [];
    return Object.entries(datos.manifest.archivos).filter(([, a]) => e.regiones.has(a.region) && e.sistemas.has(a.sistema));
  }, [datos, e.regiones, e.sistemas]);

  if (error) return <div className="vacio">{error}</div>;
  if (!datos) return <div className="vacio">Cargando atlas…</div>;

  const sel = e.seleccion ? mallas.get(e.seleccion) : null;
  const nom = e.seleccion ? nombreVisible(e.seleccion, datos.nombres) : null;
  const zona = e.seleccion ? tipoZona(e.seleccion) : null;
  const fichas = e.seleccion ? fichasDe(e.seleccion, datos) : [];
  const conFicha = sel && (sel.userData.sistema === "musculos" || sel.userData.sistema === "inserciones");
  const fichaE = sel && (sel.userData.sistema === "snc" || sel.userData.sistema === "nervios") ? fichaEncefaloDe(sel.name, datos) : null;
  const elegirArea = (a: string | null) =>
    setEstado((s) => ({
      area: a,
      // Al elegir un área se muestran la cabeza y el encéfalo si estaban apagados.
      sistemas: a ? new Set([...s.sistemas, "snc" as const]) : s.sistemas,
      regiones: a ? new Set([...s.regiones, "cabeza-cuello" as const]) : s.regiones,
    }));

  const quitarCapa = () => {
    const capa = capaSuperficial(getEstado());
    if (!capa.length) { setAviso("No queda ninguna capa de músculo visible."); return; }
    setAviso(`Se quitaron ${capa.length} estructuras de la capa superficial.`);
    setEstado((s) => ({ capas: [...s.capas, capa], ocultas: new Set([...s.ocultas, ...capa]), seleccion: capa.includes(s.seleccion ?? "") ? null : s.seleccion }));
  };
  const devolverCapa = () => setEstado((s) => {
    const capas = [...s.capas]; const ultima = capas.pop() ?? [];
    const ocultas = new Set(s.ocultas); ultima.forEach((n) => ocultas.delete(n));
    setAviso(ultima.length ? `Se devolvieron ${ultima.length} estructuras.` : "");
    return { capas, ocultas };
  });

  return (
    <div className={`app${sel ? " con-detalle" : ""}`}>
      <aside className="panel">
        <header>
          <h1>Atlas de anatomía</h1>
          <button className="enlace" onClick={() => setEstado({ mostrarCreditos: true })}>Créditos</button>
        </header>

        <section>
          <h2>Regiones</h2>
          {REGIONES.map((r) => (
            <label key={r.id} className="fila">
              <input type="checkbox" checked={e.regiones.has(r.id)} onChange={() => setEstado((s) => ({ regiones: alternar(s.regiones, r.id) }))} />
              {r.nombre}
            </label>
          ))}
        </section>

        <section>
          <h2>Sistemas</h2>
          {SISTEMAS.map((s) => (
            <label key={s.id} className="fila">
              <input type="checkbox" checked={e.sistemas.has(s.id)} onChange={() => setEstado((x) => ({ sistemas: alternar(x.sistemas, s.id) }))} />
              <i className="muestra" style={{ background: s.color }} />
              {s.nombre}
            </label>
          ))}
          {e.cargando > 0 && <p className="nota">Cargando {e.cargando} archivo{e.cargando > 1 ? "s" : ""}…</p>}
        </section>

        <section>
          <h2>Sistema nervioso: áreas funcionales</h2>
          <FiltroAreas activa={e.area} onElegir={elegirArea} />
          {e.area && <p className="nota">Resaltadas en color las estructuras del área; el resto del sistema nervioso queda tenue.</p>}
        </section>

        <section>
          <h2>Capas</h2>
          <div className="botones">
            <button onClick={quitarCapa}>Quitar capa superficial</button>
            <button onClick={devolverCapa} disabled={!e.capas.length}>Devolver capa</button>
          </div>
          {aviso && <p className="nota">{aviso}</p>}
          <div className="botones">
            <button onClick={() => setEstado({ ocultas: new Set(), transparentes: new Set(), aisladas: null, capas: [] })}
              disabled={!e.ocultas.size && !e.transparentes.size && !e.aisladas}>Mostrar todo</button>
            <button onClick={() => window.dispatchEvent(new CustomEvent("atlas:enfocar"))}>Encuadrar</button>
          </div>
        </section>

        <section>
          <h2>Rendimiento</h2>
          <button onClick={() => { setMidiendo(true); window.dispatchEvent(new CustomEvent("atlas:medir")); }} disabled={midiendo}>
            {midiendo ? "Midiendo 6 s…" : "Medir cuadros por segundo"}
          </button>
          {medicion && (
            <p className="nota">
              {medicion.fps} FPS al girar (peor cuadro {medicion.peorMs} ms) · {medicion.triangulos.toLocaleString("es-MX")} triángulos · {medicion.llamadas} llamadas de dibujo<br />
              <span className="tenue">GPU: {medicion.renderer}</span>
            </p>
          )}
          <details>
            <summary>Archivos cargados ({mb(activos.reduce((t, [, a]) => t + a.bytes, 0))})</summary>
            <ul className="archivos">
              {activos.map(([n, a]) => <li key={n}><span>{n}</span><span>{mb(a.bytes)}</span></li>)}
            </ul>
          </details>
        </section>
      </aside>

      <main className="lienzo">
        <Visor manifest={datos.manifest} />
        <p className="ayuda">Arrastrar: rotar · rueda o pellizco: zoom hacia el cursor · Mayús + arrastrar o flechas: desplazar · clic: seleccionar · doble clic: centrar ahí</p>
      </main>
      {sel && nom && (
        <aside className="detalle" aria-label="Estructura seleccionada">
          <div className="titulo">
            <strong>{nom.es}</strong>
            <button className="cerrar" aria-label="Quitar selección" onClick={() => setEstado({ seleccion: null })}>×</button>
          </div>
          <div className="sub">
            {nom.la && <em>{nom.la}</em>}
            {nom.traducido && <span>{nom.en}</span>}
          </div>
          <div className="sub">
            {NOMBRE_SISTEMA[sel.userData.sistema]}{zona ? ` · ${zona === "origen" ? "zona de origen" : "zona de inserción"}` : ""} · {NOMBRE_REGION[sel.userData.region]}
            {/\.([lr]|[oe]\d*[lr])$/.test(sel.name) ? ` · lado ${/[l]$/.test(sel.name) ? "izquierdo" : "derecho"}` : ""}
          </div>
          <div className="botones">
            <button onClick={() => setEstado((s) => ({ ocultas: alternar(s.ocultas, sel.name), seleccion: null }))}>Ocultar</button>
            <button onClick={() => setEstado((s) => ({ aisladas: s.aisladas ? null : new Set([sel.name]) }))}>{e.aisladas ? "Quitar aislamiento" : "Aislar"}</button>
            <button onClick={() => setEstado((s) => ({ transparentes: alternar(s.transparentes, sel.name) }))}>{e.transparentes.has(sel.name) ? "Opaco" : "Transparentar"}</button>
            <button onClick={() => window.dispatchEvent(new CustomEvent("atlas:enfocar", { detail: sel.name }))}>Enfocar</button>
          </div>
          {conFicha && <FichaVista fichas={fichas} lesiones={datos.lesiones} />}
              {fichaE && <FichaEncefaloVista f={fichaE} />}
        </aside>
      )}
      {e.mostrarCreditos && <Creditos onCerrar={() => setEstado({ mostrarCreditos: false })} />}
    </div>
  );
}
