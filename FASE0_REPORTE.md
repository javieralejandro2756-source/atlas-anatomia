# Fase 0: reporte (2026-11-26)

## 1. Revisión de `musculos.json`

Script: `scripts/aplicar_revision.py` → genera `datos/musculos_revisado.json` y `datos/reporte_revision.json`.

| Concepto | Valor |
|---|---|
| Filas en el CSV | 212 |
| Filas con decisión | **0** (columna `decision` vacía) |
| Aplicadas / rechazadas | 0 / 0 |
| Filas pendientes | 212 |
| Fichas con filas pendientes ("por revisar") | 114 |
| Fichas sin ninguna observación | 91 |

- El recálculo de `raices` desde el texto coincide con el JSON en las 205 fichas (acepta `C5-C7`, `C5–C7` y `C5_C7`; `C5_C1` da vacío por ser un rango imposible).
- Las filas de alcance "ficha" (fusionar duplicados, mover no-músculos, capturar ausentes) no se aplican automáticamente: el script las lista para hacerlas a mano.
- **Decisión pendiente:** aplicada al pie de la letra, la regla marca como "verificado" a las 91 fichas que no tienen observaciones, aunque nadie las haya revisado. Opciones: (a) dejarlo así o (b) exigir una marca explícita tuya por ficha.

## 2. Inventario de Z-Anatomy

Fuente: github.com/Z-Anatomy/Models-of-human-anatomy → `Z-Anatomy.zip` (83 MB) → `Startup.blend` (307 MB, Blender 3.5). Se leyó con Blender 5.2 (bpy) por línea de comandos.

| Concepto | Valor |
|---|---|
| Objetos | 7 184 (4 569 mallas, 951 curvas, 1 660 textos/etiquetas) |
| Triángulos totales | 4,10 M |
| Idioma de nombres | Inglés (Terminologia Anatomica). `TA2.csv` trae la equivalencia en latín y español |
| Lado | Sufijo `.l` / `.r`; los `.j`, `.g`, `.t`, `.s` e `.i` son nodos de jerarquía, etiquetas o puntos de referencia sin geometría |

Colecciones principales:

| Colección | Mallas | Curvas | Triángulos |
|---|---|---|---|
| 1 Skeletal system | 1 244 | – | 0,60 M |
| 2 Muscular insertions | 705 | – | 0,06 M |
| 3 Joints (ligamentos, cápsulas, meniscos) | 480 | – | 0,16 M |
| 4 Muscular system | 789 (670 con geometría, 338 nombres únicos) | – | 2,14 M |
| 5 Cardiovascular | 60 | 654 | – |
| 7 Nervous system & sense organs | 460 | 249 | 0,79 M (sobre todo el SNC) |
| 6, 8, 9 | linfoide, vísceras, regiones | | |

Hallazgos que importan para el proyecto:

- **Origen e inserción: sí vienen en la fuente.** La colección "Muscular insertions" trae zonas sobre el hueso (`.o` = origen, `.e` = inserción, numeradas si hay varias). Cubren 203 de 338 músculos. En los demás se calculará la zona de contacto marcada como "aproximada" (función 6).
- **Nervios periféricos: sí traen recorrido**, como curvas con grosor (247 de 249). Ejemplos: femoral, ciático, tibial, peroneo común, obturador, mediano, cubital, radial, musculocutáneo y axilar, además de troncos, divisiones y fascículos del plexo braquial.
- **Raíces por segmento: no vienen.** "Roots of brachial plexus" es un solo objeto y no hay curvas C5, L4, etc. Tampoco hay objetos para los plexos lumbar o sacro. El filtro por raíz (función 4) funciona con los datos de las fichas; el filtro por nervio (función 5) sí puede mostrar el recorrido.
- **Tendones:** no hay colección propia; vienen dentro de las mallas musculares y en "Tendon sheaths" (vainas).
- Para el visor hay que simplificar: solo los músculos suman 2,1 M de triángulos.

## 3. Licencia y créditos

- Z-Anatomy: **CC BY-SA 4.0** (`License.txt`). Atribuciones obligatorias:
  - "BodyParts3D - The Database Center for Life Science - CC-BY-SA 2.1 Japan"
  - "Z-Anatomy - The libre 3D atlas of anatomy - CC-BY-SA 4.0"
- ShareAlike: los `.glb` derivados y cualquier redistribución de la app llevan la misma licencia.
- **Partes no comerciales (NC):** oído interno (Dundee, CC-BY-NC-SA) y riñón (Cowley, CC-BY-NC). Quedan fuera del alcance (huesos, músculos, ligamentos y nervios) y no se exportan. Así, el material queda libre de NC aunque después lo uses para tu contenido o tu clínica.
- La página "Créditos" incluirá las dos atribuciones obligatorias y la lista de autores del archivo.

## 4. Cotejo con Snell: miembro inferior (2026-11-27)

Fuentes: tablas 6-2 y 11-1 a 11-9 de Snell, *Anatomía clínica por regiones*, 10.ª ed. Cada dato se leyó en la imagen, no en el OCR.
Script: `scripts/filas_snell_miembro_inferior.py`. El CSV original quedó respaldado en `datos/revision_musculos.original.csv`.

Al CSV se agregaron **68 filas nuevas** (n.º 213 a 280), todas sin decisión:

- **17 filas por raíces que difieren** entre tu ficha y Snell:
  - aductor largo y corto (m161 y m159)
  - porción isquiotibial del aductor mayor (m162)
  - tensor de la fascia lata
  - piriforme
  - flexor largo de los dedos y flexor largo del dedo gordo
  - extensor largo del dedo gordo
  - peroneos largo y corto
  - extensor corto de los dedos
  - flexor corto de los dedos, cuadrado plantar, abductor del dedo gordo y flexor corto del dedo gordo
  - tibial anterior y tibial posterior (estas dos sin propuesta)
- **51 filas de "raíz principal"**, tomada de las raíces en negrita de Snell. Es un campo nuevo: `raiz_principal`.

Las raíces del gemelo superior ya tenían propuesta en la fila 58, y coincide con Snell (L5, S1).

**Erratas de Snell que no se usan como dato:**

- Tibial anterior y tibial posterior: dice «L4; S5». S5 no es plausible.
- Fibular largo: da como origen «cara lateral del cuerpo del fémur».
- Tabla 6-2: el psoas se origina en «T12 y L5», mientras la tabla 11-2 dice «T12 y las cinco lumbares».

**Comparado:** raíces y raíz principal.
**No comparado todavía:** origen, inserción y acción. La fase 2 lo requiere.

Estado tras el cotejo (sin decisiones aplicadas):

| Concepto | Valor |
|---|---|
| Filas en el CSV | 280 |
| Filas pendientes | 280 |
| Fichas "por revisar" | 148 |
| Fichas sin observaciones ("verificadas" por la regla actual) | 57 |

Prueba del script con todas las filas decididas: 225 aplicadas, 24 rechazadas, 0 fallidas.

## 5. Faltantes

- No se exportó nada (lo pide la fase 0).

# Fase 1: visor (2026-11-27)

## Decisiones del miembro inferior

Por indicación del usuario, se decidió con Snell como prioridad. El registro de cada decisión y su fuente está en `datos/decisiones_miembro_inferior.json`. Las mismas decisiones se cargaron en la página de revisión, donde el usuario puede cambiar cualquiera.

| Concepto | Valor |
|---|---|
| Filas decididas del miembro inferior | 116 de 117 |
| Pendiente | fila 171: irrigación del psoas menor, sin fuente disponible |
| Mantenidas contra Snell | tibial anterior y tibial posterior (Snell imprime «L4; S5») |
| Plantar | se conservan las dos lecturas |
| Duplicados fusionados | 6; se conservó la ficha con nervio e irrigación en su campo |
| Cuádriceps | ficha de grupo |
| Pata de ganso y tracto iliotibial | pasan a "estructura" |

Regla de "verificado" aplicada (opción B): sin filas pendientes **y** cotejada con una fuente (`datos/cotejo.json`).

| Concepto | Valor |
|---|---|
| Fichas verificadas en total | 56 |
| Fichas por revisar | 143 |
| Fichas fusionadas | 6 |

En el miembro inferior quedan por revisar: psoas menor, articular de la rodilla y extensor corto del dedo gordo. Ninguno aparece en las tablas de Snell.

No hubo acceso a Wikipedia: el dominio está bloqueado en este entorno. Las filas que esperan confirmación web están marcadas en su nota.

## Exportación (scripts/exportar_glb.py)

- Blender 5.2 por línea de comandos, glTF con Draco: una malla por estructura con su nombre anatómico.
- 2306 mallas, 0 omitidas.
- **Total: 1,196,303 triángulos y 21.9 MB** (el original tenía 4,1 M de triángulos).
- Nombres en español y latín tomados de `TA2.csv` de Z-Anatomy: 92 % de las estructuras traducidas.

| Archivo | Mallas | Triángulos | Peso |
|---|---|---|---|
| cabeza-cuello-fascias.glb | 6 | 2,000 | 0.04 MB |
| cabeza-cuello-huesos.glb | 83 | 68,237 | 1.17 MB |
| cabeza-cuello-inserciones.glb | 129 | 31,682 | 0.58 MB |
| cabeza-cuello-ligamentos.glb | 26 | 14,968 | 0.28 MB |
| cabeza-cuello-musculos.glb | 143 | 76,422 | 1.30 MB |
| cabeza-cuello-nervios.glb | 50 | 48,316 | 0.84 MB |
| miembro-inferior-fascias.glb | 110 | 49,090 | 0.89 MB |
| miembro-inferior-huesos.glb | 64 | 21,224 | 0.37 MB |
| miembro-inferior-inserciones.glb | 223 | 60,354 | 1.09 MB |
| miembro-inferior-ligamentos.glb | 176 | 56,910 | 1.03 MB |
| miembro-inferior-musculos.glb | 120 | 84,902 | 1.40 MB |
| miembro-inferior-nervios.glb | 64 | 23,976 | 0.42 MB |
| miembro-superior-fascias.glb | 50 | 19,387 | 0.37 MB |
| miembro-superior-huesos.glb | 64 | 33,796 | 0.60 MB |
| miembro-superior-inserciones.glb | 195 | 68,990 | 1.32 MB |
| miembro-superior-ligamentos.glb | 146 | 28,200 | 0.58 MB |
| miembro-superior-musculos.glb | 102 | 52,588 | 0.88 MB |
| miembro-superior-nervios.glb | 88 | 24,120 | 0.43 MB |
| tronco-fascias.glb | 16 | 7,644 | 0.17 MB |
| tronco-huesos.glb | 66 | 99,506 | 1.62 MB |
| tronco-inserciones.glb | 158 | 46,858 | 0.87 MB |
| tronco-ligamentos.glb | 61 | 45,686 | 0.88 MB |
| tronco-musculos.glb | 122 | 183,039 | 3.94 MB |
| tronco-nervios.glb | 44 | 48,408 | 0.82 MB |

## Qué funciona

- **Carga:** bajo demanda por región y sistema. Por defecto, miembro inferior con huesos y músculos.
- **Visor:** rota, hace zoom y desplaza. El clic selecciona y resalta; el doble clic enfoca.
- **Tarjeta de la selección:** nombre en español, latín e inglés, sistema, región y lado.
- **Acciones sobre la selección:** ocultar, aislar, transparentar y enfocar. Botón "Mostrar todo".
- **Capas:**
  - "Quitar capa superficial": detecta con rayos desde 14 direcciones qué músculos se ven primero y los oculta.
  - "Devolver capa": repone la última capa quitada.
  - Lo oculto no se dibuja.
- **Medición de rendimiento** desde la app: gira 6 s y reporta FPS, peor cuadro, triángulos, llamadas de dibujo y GPU.
- **Página de Créditos** con las atribuciones de la licencia.

## Rendimiento medido

Medido en este servidor, sin GPU (SwiftShader, render por software). **No es representativo de la MacBook**: hay que repetir la medición en ella con el botón de la app.

| Escena | FPS | Triángulos | Llamadas de dibujo | Peso |
|---|---|---|---|---|
| Miembro inferior: huesos + músculos | 32 | 106 mil | 184 | 1,8 MB |
| Cuerpo completo: huesos + músculos | 11 | 620 mil | 764 | 11,3 MB |
| Cuerpo completo + ligamentos + nervios | 8 | 910 mil | 1 419 | 16,6 MB |

Riesgo para la MacBook Air 2017: las llamadas de dibujo (una por malla) pesan más que los triángulos. Si en la MacBook el cuerpo completo baja de 30 FPS, el siguiente paso es agrupar las mallas que no están seleccionadas.

## Qué falta

- Medir en la MacBook.
- Empaquetar como app de escritorio (Tauri), lo que requiere el repositorio de GitHub.
- Fase 2: fichas y filtros del miembro inferior.
- No se exportaron, por estar fuera de alcance:
  - vasos;
  - vísceras;
  - sistema nervioso central;
  - oído interno y riñón (licencia NC).
- Tendones: no vienen como estructura separada; van dentro de cada músculo, más el tendón calcáneo y las vainas.

# Versión iPhone (2026-11-27)

Es una versión propia para el iPhone 16 Pro Max, sobre el mismo código que la de Mac, con dos diferencias: modelos de alta calidad e interfaz táctil.

## Modelos

| Versión | Triángulos | Peso |
|---|---|---|
| iPhone (`app/public/modelos-iphone/`) | 3,3 M | 55 MB |
| Mac | 1,2 M | 22 MB |
| Original del atlas | 4,1 M | — |

- Músculos al 60 % del original y huesos al 75 %. Los nervios con curvas más suaves.
- Se exportan con el mismo script: `scripts/exportar_glb.py <blend> <salida> iphone`.

## Interfaz (`app/iphone/`, `app/src/iphone/`)

- Pantalla completa, respetando la isla dinámica y la barra de inicio.
- Tocar selecciona; la ficha aparece abajo con Enfocar, Aislar, Transparente y Ocultar.
- Al alcance del pulgar:
  - botones flotantes: Capa, Volver y Encuadrar;
  - hoja inferior con regiones, sistemas, medición, instalación y créditos.
- Instalable con "Añadir a pantalla de inicio": ícono, pantalla completa y service worker.
- Sin internet funciona con los modelos ya vistos.
- Probado con emulación de iPhone 15 Pro Max (440 × 956). La medición de FPS hay que hacerla en el iPhone real.
