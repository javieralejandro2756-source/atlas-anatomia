// Versión iPhone: pantalla completa, hoja inferior para el pulgar, modelos de alta calidad.
import { useEffect, useMemo, useState } from "react";
import Visor, { type Perfil } from "../Visor";
import Creditos from "../Creditos";
import { REGIONES, SISTEMAS, cargarDatos, fichasDe, nombreVisible, tipoZona, type Datos } from "../datos";
import FichaVista from "../FichaVista";
import { alternar, setEstado, useEstado } from "../estado";
import { mallas } from "../escena";
import { devolverCapa, enfocar, medir, mostrarTodo, quitarCapa } from "../acciones";

const PERFIL_IPHONE: Perfil = { carpeta: "../modelos-iphone/", draco: "../draco/", dpr: [1, 3], tactil: true };
const NOMBRE_SISTEMA = Object.fromEntries(SISTEMAS.map((s) => [s.id, s.nombre]));
const NOMBRE_REGION = Object.fromEntries(REGIONES.map((r) => [r.id, r.nombre]));
const mb = (b: number) => (b / 1e6).toFixed(1) + " MB";

type Pestana = "capas" | "mas";
interface Medicion { fps: number; peorMs: number; llamadas: number; triangulos: number; renderer: string }

const instalada = () =>
  window.matchMedia?.("(display-mode: standalone)").matches || (navigator as any).standalone === true;

export default function AppIphone() {
  const [datos, setDatos] = useState<Datos | null>(null);
  const [fichaAbierta, setFichaAbierta] = useState(false);
  const [error, setError] = useState("");
  const [abierta, setAbierta] = useState(false);
  const [pestana, setPestana] = useState<Pestana>("capas");
  const [aviso, setAviso] = useState("");
  const [medicion, setMedicion] = useState<Medicion | null>(null);
  const [midiendo, setMidiendo] = useState(false);
  const e = useEstado((x) => x);

  useEffect(() => {
    cargarDatos(PERFIL_IPHONE.carpeta, "../").then(setDatos).catch(() => setError("No se pudieron leer los modelos. Revisa la conexión."));
    let primero = true;
    const alCargar = () => { if (primero) { primero = false; setTimeout(() => enfocar(), 60); } };
    const alMedir = (ev: Event) => { setMedicion((ev as CustomEvent).detail); setMidiendo(false); };
    window.addEventListener("atlas:cargado", alCargar);
    window.addEventListener("atlas:medido", alMedir);
    return () => { window.removeEventListener("atlas:cargado", alCargar); window.removeEventListener("atlas:medido", alMedir); };
  }, []);

  useEffect(() => { if (!aviso) return; const t = setTimeout(() => setAviso(""), 3500); return () => clearTimeout(t); }, [aviso]);

  const activos = useMemo(() => {
    if (!datos) return [];
    return Object.entries(datos.manifest.archivos).filter(([, a]) => e.regiones.has(a.region) && e.sistemas.has(a.sistema));
  }, [datos, e.regiones, e.sistemas]);

  if (error) return <div className="i-vacio">{error}</div>;
  if (!datos) return <div className="i-vacio">Cargando atlas…</div>;

  const sel = e.seleccion ? mallas.get(e.seleccion) : null;
  const nom = e.seleccion ? nombreVisible(e.seleccion, datos.nombres) : null;
  const zona = e.seleccion ? tipoZona(e.seleccion) : null;
  const fichas = e.seleccion ? fichasDe(e.seleccion, datos) : [];
  const conFicha = sel && (sel.userData.sistema === "musculos" || sel.userData.sistema === "inserciones");
  const lado = sel && /\.([lr]|[oe]\d*[lr])$/.test(sel.name) ? (sel.name.endsWith("l") ? "izquierdo" : "derecho") : "";

  return (
    <div className="i-app">
      <Visor manifest={datos.manifest} perfil={PERFIL_IPHONE} />

      <div className="i-arriba">
        <span className="i-marca">Atlas</span>
        {e.cargando > 0 && <span className="i-cargando">Cargando {e.cargando}…</span>}
      </div>

      {/* Botones flotantes al alcance del pulgar */}
      <div className="i-flotantes">
        <button aria-label="Quitar capa superficial" onClick={() => { const n = quitarCapa(); setAviso(n ? `Capa quitada: ${n} estructuras` : "No quedan músculos visibles"); }}>
          <span aria-hidden>⤓</span>Capa
        </button>
        <button aria-label="Devolver capa" disabled={!e.capas.length} onClick={() => { const n = devolverCapa(); setAviso(`Devueltas: ${n}`); }}>
          <span aria-hidden>⤒</span>Volver
        </button>
        <button aria-label="Encuadrar" onClick={() => enfocar()}><span aria-hidden>⌖</span>Encuadrar</button>
      </div>

      {aviso && <div className="i-aviso" role="status">{aviso}</div>}

      {/* Ficha de la selección: compacta (no tapa el modelo) o desplegada para leer */}
      {sel && nom && (
        <div className={`i-ficha${fichaAbierta ? " abierta" : ""}`} role="dialog" aria-label="Estructura seleccionada">
          <div className="i-ficha-cab">
            <button className="i-ficha-titulo" aria-expanded={fichaAbierta} onClick={() => setFichaAbierta(!fichaAbierta)}>
              <strong>{nom.es}</strong>
              <span className="i-sub">{fichaAbierta ? "Ocultar ficha ▾" : conFicha ? "Ver ficha: origen, inserción, raíces ▴" : "Ver detalles ▴"}</span>
            </button>
            <button className="i-x" aria-label="Quitar selección" onClick={() => { setEstado({ seleccion: null }); setFichaAbierta(false); }}>×</button>
          </div>
          {fichaAbierta && (
            <div className="i-ficha-cuerpo">
              <div className="i-sub">{nom.la}{nom.traducido && nom.la ? " · " : ""}{nom.traducido ? nom.en : ""}</div>
              <div className="i-sub">
                {NOMBRE_SISTEMA[sel.userData.sistema]}{zona ? ` · ${zona === "origen" ? "zona de origen" : "zona de inserción"}` : ""} · {NOMBRE_REGION[sel.userData.region]}{lado ? ` · ${lado}` : ""}
              </div>
              <div className="i-acciones">
                <button onClick={() => { setFichaAbierta(false); enfocar(sel.name); }}>Enfocar</button>
                <button onClick={() => setEstado((s) => ({ aisladas: s.aisladas ? null : new Set([sel.name]) }))}>{e.aisladas ? "Ver todo" : "Aislar"}</button>
                <button onClick={() => setEstado((s) => ({ transparentes: alternar(s.transparentes, sel.name) }))}>{e.transparentes.has(sel.name) ? "Opaco" : "Transparente"}</button>
                <button onClick={() => { setEstado((s) => ({ ocultas: alternar(s.ocultas, sel.name), seleccion: null })); setFichaAbierta(false); }}>Ocultar</button>
              </div>
              {conFicha && <FichaVista fichas={fichas} lesiones={datos.lesiones} />}
            </div>
          )}
        </div>
      )}

      {/* Hoja inferior */}
      <div className={`i-hoja${abierta ? " abierta" : ""}`}>
        <button className="i-asa" aria-expanded={abierta} onClick={() => setAbierta(!abierta)}>
          <i />
          <span>{abierta ? "Cerrar" : "Regiones, sistemas y más"}</span>
        </button>
        {abierta && (
          <div className="i-hoja-cuerpo">
            <div className="i-pestanas" role="tablist">
              <button role="tab" aria-selected={pestana === "capas"} onClick={() => setPestana("capas")}>Capas</button>
              <button role="tab" aria-selected={pestana === "mas"} onClick={() => setPestana("mas")}>Más</button>
            </div>

            {pestana === "capas" && (
              <>
                <h2>Regiones</h2>
                <div className="i-chips">
                  {REGIONES.map((r) => (
                    <button key={r.id} aria-pressed={e.regiones.has(r.id)} onClick={() => setEstado((s) => ({ regiones: alternar(s.regiones, r.id) }))}>{r.nombre}</button>
                  ))}
                </div>
                <h2>Sistemas</h2>
                <div className="i-chips">
                  {SISTEMAS.map((s) => (
                    <button key={s.id} aria-pressed={e.sistemas.has(s.id)} onClick={() => setEstado((x) => ({ sistemas: alternar(x.sistemas, s.id) }))}>
                      <i style={{ background: s.color }} />{s.nombre}
                    </button>
                  ))}
                </div>
                <div className="i-chips">
                  <button onClick={() => { mostrarTodo(); setAviso("Todo visible"); }} disabled={!e.ocultas.size && !e.transparentes.size && !e.aisladas}>Mostrar todo</button>
                </div>
              </>
            )}

            {pestana === "mas" && (
              <>
                <h2>Rendimiento</h2>
                <button className="i-ancho" disabled={midiendo} onClick={() => { setMidiendo(true); setAbierta(false); medir(); }}>
                  {midiendo ? "Midiendo 6 s…" : "Medir cuadros por segundo"}
                </button>
                {medicion && (
                  <p className="i-nota">
                    {medicion.fps} FPS · peor cuadro {medicion.peorMs} ms · {medicion.triangulos.toLocaleString("es-MX")} triángulos · {medicion.llamadas} llamadas<br />
                    <span className="i-tenue">{medicion.renderer}</span>
                  </p>
                )}
                <p className="i-nota i-tenue">Cargado ahora: {mb(activos.reduce((t, [, a]) => t + a.bytes, 0))} en {activos.length} archivos.</p>
                {!instalada() && (
                  <>
                    <h2>Instalar en el iPhone</h2>
                    <p className="i-nota">En Safari toca <b>Compartir</b> y luego <b>Añadir a pantalla de inicio</b>. Instalada, se abre a pantalla completa, funciona sin internet con lo que ya cargaste y iOS no borra tu progreso.</p>
                  </>
                )}
                <button className="i-ancho" onClick={() => setEstado({ mostrarCreditos: true })}>Créditos y licencia</button>
              </>
            )}
          </div>
        )}
      </div>

      {e.mostrarCreditos && <Creditos onCerrar={() => setEstado({ mostrarCreditos: false })} />}
    </div>
  );
}
