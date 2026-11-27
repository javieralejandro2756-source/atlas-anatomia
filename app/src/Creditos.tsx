export default function Creditos({ onCerrar }: { onCerrar: () => void }) {
  return (
    <div className="modal" role="dialog" aria-label="Créditos" onClick={onCerrar}>
      <div className="modal-caja" onClick={(e) => e.stopPropagation()}>
        <div className="titulo">
          <strong>Créditos</strong>
          <button className="cerrar" aria-label="Cerrar" onClick={onCerrar}>×</button>
        </div>
        <h3>Modelos 3D</h3>
        <p>
          <b>BodyParts3D</b> - The Database Center for Life Science - CC-BY-SA 2.1 Japan.{" "}
          <a href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html" target="_blank" rel="noreferrer">Modelo original</a>.
        </p>
        <p>
          <b>Z-Anatomy</b> - The libre 3D atlas of anatomy - CC-BY-SA 4.0.{" "}
          <a href="https://github.com/Z-Anatomy/Models-of-human-anatomy" target="_blank" rel="noreferrer">Repositorio</a>.
        </p>
        <p className="tenue">
          Autores del modelo: Kousaku Okubo (BodyParts3D), Gauthier Kervyn (diseño, 3D, anatomía), Marcin Zielinski (complemento de Blender),
          Lluis Vinent (desarrollo). Traducción al español de las estructuras: Carlos Torres Villar.
        </p>
        <p className="tenue">
          Cambios hechos aquí: las mallas se simplificaron (menos triángulos), se separaron por región y sistema y se exportaron a glTF.
          No se incluyen los modelos con licencia no comercial (oído interno y riñón).
        </p>
        <h3>Licencia de este atlas</h3>
        <p>
          Los modelos derivados se distribuyen bajo{" "}
          <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a>.
        </p>
        <h3>Datos de músculos</h3>
        <p className="tenue">
          Fichas del usuario, verificadas contra Snell, <i>Anatomía clínica por regiones</i>, 10.ª ed. (consulta; no se reproduce su texto).
        </p>
      </div>
    </div>
  );
}
