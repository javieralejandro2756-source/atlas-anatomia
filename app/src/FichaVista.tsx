// Ficha anatómica de la estructura seleccionada: origen, inserción, inervación, raíces, irrigación y función.
import type { Ficha } from "./datos";

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

export function UnaFicha({ f }: { f: Ficha }) {
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
    </article>
  );
}

export default function FichaVista({ fichas }: { fichas: Ficha[] }) {
  if (!fichas.length) {
    return <p className="f-vacio f-sin">Esta estructura todavía no tiene ficha.</p>;
  }
  return (
    <div className="f-lista">
      {fichas.length > 1 && <p className="f-aviso">Esta malla reúne {fichas.length} músculos; aquí están sus fichas.</p>}
      {fichas.map((f) => <UnaFicha key={f.id} f={f} />)}
    </div>
  );
}
