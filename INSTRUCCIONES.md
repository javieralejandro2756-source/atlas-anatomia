# Atlas de anatomía 3D: instrucciones del proyecto

Vas a construir un atlas de anatomía 3D para web, de uso personal, para un
estudiante de Fisioterapia. Referencia de experiencia: Complete Anatomy.
Alcance: cuerpo completo. Sistemas: huesos, músculos, ligamentos, tendones
y nervios periféricos con sus plexos y raíces.

## Reglas centrales

1. No dibujes ni generes geometría anatómica. Toda la geometría sale de un
   atlas abierto. Si una estructura no existe en la fuente, se omite y se
   reporta.
2. Ningún dato anatómico se inventa. Lo que no puedas verificar queda vacío
   y marcado "por revisar".
3. No corrijas datos en silencio. Toda corrección pasa por el archivo de
   revisión y la decide el usuario.

## Archivos que te entrega el usuario (carpeta `datos/`)

- `musculos.json`: 205 fichas extraídas de una tabla que el usuario hizo en
  la carrera (201 músculos, 4 entradas que no son músculos). El texto está
  tal cual lo escribió, con sus errores. Campos: id, nombre,
  nombre_original, tipo, region, origen, insercion, inervacion, raices
  (extraídas del texto de inervación), pares_craneales,
  inervacion_segmentaria, raices_propuestas (sugeridas por otro modelo, sin
  verificar), irrigacion, funcion, duplicado_de, estado.
- `revision_musculos.csv`: 212 observaciones sobre esas fichas: errores de
  contenido, filas corridas, erratas, duplicados, raíces faltantes, campos
  vacíos y músculos ausentes. La columna `decision` la llena el usuario:
  "aceptar", "rechazar" o un texto propio que sustituye a la propuesta.
- `fuentes/`: libros del usuario ya convertidos a archivos pequeños. No
  abras ni pidas los PDF originales; todo lo necesario está aquí. Son
  material de consulta: no copies su texto ni sus figuras a la app, y cita
  la tabla o el archivo cuando verifiques un dato.
  - `fuentes/snell-tablas/`: tablas de Snell, Anatomía clínica por
    regiones, 10.a ed., como imágenes .jpg (una por tabla), con un índice
    en `00-indice-tablas.csv`. Es la fuente principal para verificar
    origen, inserción, nervio, raíz y acción. Las tablas de los capítulos 3
    y 11 marcan en negrita la raíz predominante: úsala para el campo "raíz
    principal". Lee cada dato en la imagen. Los archivos `.ocr.txt` son un
    borrador con errores; sirven solo para buscar, nunca como dato.
  - `fuentes/snell-anatomia-por-regiones/`: texto del mismo libro, un
    archivo por capítulo (01-introducción a 12-cabeza-y-cuello, más el
    índice alfabético). Úsalo para recorridos nerviosos, relaciones y notas
    clínicas. Busca con grep en lugar de leer capítulos completos.
  - `fuentes/snell-neuroanatomia/`: texto de Snell, Neuroanatomía clínica,
    7.a ed., por rangos de páginas. Úsalo para dermatomas, reflejos e
    inervación segmentaria.
- Prioridad de fuentes cuando no coincidan: la decisión del usuario en el
  CSV, después las tablas de Snell por regiones, después el resto. Si dos
  fuentes difieren en una raíz, no elijas tú: agrégalo como fila nueva al
  CSV de revisión.

## Cómo aplicar la revisión

- Escribe un script que lea el CSV y aplique a `musculos.json` solo las
  filas con decisión. "alcance = fragmento" reemplaza `texto_actual` por la
  propuesta dentro del campo; "campo completo" sustituye el campo entero.
- Tras aplicar, vuelve a calcular `raices` desde el texto de inervación.
  `raices_propuestas` solo pasa a `raices` si su fila fue aceptada.
- Una ficha pasa a estado "verificado" solo cuando no le quedan filas
  pendientes. El resto sigue "por revisar" y la app lo muestra con una
  marca visible.
- Las filas sin decisión no se aplican. Reporta cuántas quedan.

## Fuente de modelos 3D

- Usa Z-Anatomy (github.com/Z-Anatomy, archivo .blend, derivado de
  BodyParts3D). Antes de descargar, lee su licencia y confirma al usuario
  los términos de atribución; crea una página "Créditos" que los cumpla.
- Primero haz un inventario del .blend: qué colecciones trae, cuántas
  estructuras por sistema, en qué idiomas vienen los nombres, si incluye
  nervios con su recorrido y si incluye zonas de origen e inserción sobre
  el hueso. Entrega ese inventario antes de exportar nada.
- Con Blender en línea de comandos (script de Python), exporta a glTF
  (.glb) con compresión Draco: una malla por estructura, conservando el
  nombre anatómico, un archivo por región y sistema (ej. muslo-músculos).
  Simplifica las mallas hasta que el conjunto corra fluido.
- Liga cada malla de músculo con su ficha de `musculos.json`. Entrega la
  lista de mallas sin ficha y de fichas sin malla; no fuerces coincidencias
  dudosas.

## Rendimiento

- Carga bajo demanda por región y sistema; nunca todo el cuerpo de golpe.
- Lo oculto no se dibuja.
- Debe correr fluido en una MacBook sin tarjeta gráfica dedicada. Mide los
  cuadros por segundo y el peso de cada archivo, y repórtalos por fase.

## Stack

Vite + React + TypeScript + React Three Fiber (three.js) + drei.
Todo local, sin backend. Progreso del usuario en IndexedDB.

## Modelo de datos

- Músculo: el de `musculos.json`, más nombre en latín y malla asociada.
- Nervio: plexo, raíces que lo forman, músculos que inerva, territorio
  cutáneo. Se construye a partir de las fichas de músculos ya revisadas.
- Hueso y ligamento: nombre, qué une, qué movimiento limita. Estas fichas
  no existen todavía; créalas vacías y márcalas "por revisar".

## Funciones, en este orden

1. Visor: rotar, zoom, desplazar; clic selecciona una estructura, la
   resalta y muestra su nombre.
2. Capas: mostrar y ocultar por sistema y por región; ocultar, aislar y
   transparentar la selección; quitar capas de superficial a profundo.
3. Ficha de la estructura seleccionada, con su estado visible.
4. Filtro por raíz nerviosa: el usuario elige una o varias raíces (C5, L4,
   S1...) y solo quedan visibles los músculos que inervan; el resto
   desaparece. Los huesos quedan en transparencia como referencia. Los
   músculos de inervación segmentaria y los de pares craneales tienen su
   propio filtro. Opción para incluir o excluir raíces propuestas aún sin
   verificar.
5. Filtro por nervio: el usuario elige un nervio y se muestra su recorrido
   completo más los músculos que inerva; lo demás desaparece.
6. Origen e inserción sobre el hueso: si la fuente trae esas zonas,
   úsalas. Si no, calcula la zona de contacto entre los extremos del
   músculo y el hueso y márcala como "aproximada".
7. Buscador por nombre con enfoque de cámara.
8. Modo examen: identificar la estructura resaltada, ubicar una por su
   nombre y preguntas de raíz ("¿qué músculos inerva L5?"). Solo pregunta
   sobre fichas verificadas. Repetición espaciada sobre los errores.

## Forma de trabajo

- Fase 0: inventario del atlas y aplicación de la revisión que ya tenga
  decisión. Espera aprobación.
- Fase 1: visor con cuerpo completo cargado, seleccionable y con capas
  (funciones 1 y 2). Sin fichas todavía.
- Fase 2: fichas y filtros (3, 4 y 5) solo para miembro inferior, como
  región piloto.
- Fases siguientes: una región por fase (miembro superior, tronco, cabeza
  y cuello), cada una después de que el usuario revise sus fichas.
- Funciones 6 a 8 después de la región piloto.
- Al final de cada fase: qué funciona, qué falta, qué estructuras no se
  pudieron exportar, cuántas fichas siguen "por revisar" y el rendimiento
  medido.
