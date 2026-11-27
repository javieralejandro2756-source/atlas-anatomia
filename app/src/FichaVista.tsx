// Ficha anatómica de la estructura seleccionada: origen, inserción, inervación, raíces, irrigación y función.
import { AREAS, type Ficha, type FichaEncefalo, type Lesion } from "./datos";

const ESTADO: Record<string, { texto: string; clase: string }> = {
  verificado: { texto: "Verificada", clase: "ok" },
  "por revisar": { texto: "Por revisar", clase: "pend" },
};

function Campo({ titulo, texto }: { titulo: string; texto?: string | null }) {
  return (
    <div className="f-campo">
      <dt>{titulo}</dt>
      <dd>{texto && texto.trim() ? texto : <span className="f-vacio">Sin dato</span>}</dd>
    </div>
  );
}

export function UnaFicha({ f, lesiones = [] }: { f: Ficha; lesiones?: Lesion[] }) {
  const propias = lesiones.filter((l) => l.fichas.includes(f.id) && l.estado !== "rechazada");
  const est = ESTADO[f.estado] ?? { texto: f.estado, clase: "pend" };
  const principal = new Set(f.raiz_principal ?? []);
  return (
    <article className="f-ficha">
      <header className="f-cab">
        <h3>{f.nombre}</h3>
        <span className={`f-estado ${est.clase}`}>{est.texto}</span>
      </header>
      {f.estado !== "verificado" && (
        <p className="f-aviso">Esta ficha aún no está verificada: tómala con cautela.</p>
      )}
      <dl>
        <Campo titulo="Origen" texto={f.origen} />
        <Campo titulo="Inserción" texto={f.insercion} />
        <Campo titulo="Inervación" texto={f.inervacion} />
        <div className="f-campo">
          <dt>Raíces nerviosas</dt>
          <dd>
            {f.raices?.length ? (
              <span className="f-raices">
                {f.raices.map((r) => (
                  <b key={r} className={principal.has(r) ? "principal" : ""} title={principal.has(r) ? "Raíz principal (Snell)" : undefined}>{r}</b>
                ))}
              </span>
            ) : f.inervacion_segmentaria ? (
              "Inervación segmentaria (ramos posteriores)"
            ) : f.pares_craneales?.length ? (
              `Par craneal ${f.pares_craneales.join(", ")}`
            ) : (
              <span className="f-vacio">Sin dato</span>
            )}
            {principal.size > 0 && <span className="f-leyenda">Resaltada: raíz principal</span>}
          </dd>
        </div>
        <Campo titulo="Irrigación" texto={f.irrigacion} />
        <Campo titulo="Función" texto={f.funcion} />
      </dl>
      {f.fuente_cotejo && <p className="f-fuente">Cotejada con {f.fuente_cotejo}.</p>}
      <section className="f-lesiones">
        <h4>Lesiones frecuentes</h4>
        {propias.length ? (
          propias.map((l) => (
            <div key={l.n} className="f-lesion">
              <div className="f-lesion-cab">
                <strong>{l.diagnostico}</strong>
                {l.estado !== "aprobada" && <span className="f-estado pend">Propuesta: por revisar</span>}
              </div>
              <div className="f-lesion-valor">{l.medida}: {l.valor}</div>
              <div className="f-lesion-pob">Población: {l.poblacion}</div>
              <div className="f-lesion-cita">
                {l.cita}. PMID {l.pmid}.{" "}
                <a href={`https://doi.org/${l.doi}`} target="_blank" rel="noreferrer">doi:{l.doi}</a>
              </div>
            </div>
          ))
        ) : (
          <p className="f-vacio">Sin datos epidemiológicos verificados para esta estructura.</p>
        )}
      </section>
    </article>
  );
}

export default function FichaVista({ fichas, lesiones = [] }: { fichas: Ficha[]; lesiones?: Lesion[] }) {
  if (!fichas.length) {
    return <p className="f-vacio f-sin">Esta estructura todavía no tiene ficha.</p>;
  }
  return (
    <div className="f-lista">
      {fichas.length > 1 && <p className="f-aviso">Esta malla reúne {fichas.length} músculos; aquí están sus fichas.</p>}
      {fichas.map((f) => <UnaFicha key={f.id} f={f} lesiones={lesiones} />)}
    </div>
  );
}

// ---------- Sistema nervioso ----------

const NOMBRE_AREA = Object.fromEntries(AREAS.map((a) => [a.id, a]));

export function FichaEncefaloVista({ f }: { f: FichaEncefalo }) {
  const est = ESTADO[f.estado] ?? { texto: f.estado, clase: "pend" };
  return (
    <div className="f-lista">
      <article className="f-ficha">
        <header className="f-cab">
          <h3>{f.nombre}</h3>
          <span className={`f-estado ${est.clase}`}>{est.texto}</span>
        </header>
        <p className="f-fuente">{f.grupo}</p>
        {f.areas.length > 0 && (
          <div className="f-areas">
            {f.areas.map((a) => (
              <span key={a} style={{ borderColor: NOMBRE_AREA[a]?.color }}>
                <i style={{ background: NOMBRE_AREA[a]?.color }} />
                {NOMBRE_AREA[a]?.nombre ?? a}
              </span>
            ))}
          </div>
        )}
        <dl>
          {f.componentes && <Campo titulo="Componentes" texto={f.componentes} />}
          {f.brodmann && (
            <div className="f-campo">
              <dt>Áreas de Brodmann</dt>
              <dd>{f.brodmann}<span className="f-leyenda">Ubicación aproximada: las áreas no coinciden exactamente con los giros.</span></dd>
            </div>
          )}
          <Campo titulo="Función" texto={f.funcion} />
          {f.salida && <Campo titulo="Salida del cráneo" texto={f.salida} />}
          {f.lesion && <Campo titulo="Si se lesiona" texto={f.lesion} />}
        </dl>
        <p className="f-fuente">Fuente: {f.fuente}.</p>
      </article>
    </div>
  );
}

/** Botones para resaltar un área funcional del sistema nervioso. */
export function FiltroAreas({ activa, onElegir }: { activa: string | null; onElegir: (a: string | null) => void }) {
  return (
    <div className="f-filtro-areas">
      {AREAS.map((a) => (
        <button key={a.id} aria-pressed={activa === a.id} onClick={() => onElegir(activa === a.id ? null : a.id)}>
          <i style={{ background: a.color }} />
          {a.nombre}
        </button>
      ))}
    </div>
  );
}
