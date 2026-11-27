# Atlas de anatomía 3D

Atlas personal de anatomía para estudiar Fisioterapia: huesos, músculos, ligamentos y nervios periféricos.

- **Mac:** https://javieralejandro2756-source.github.io/atlas-anatomia/
- **iPhone:** https://javieralejandro2756-source.github.io/atlas-anatomia/iphone/ (en Safari: Compartir → Añadir a pantalla de inicio)

## Contenido

- `app/`: la aplicación (Vite + React + three.js). `npm ci && npm run dev` para trabajar en local.
- `app/public/modelos*/`: modelos 3D en glTF con compresión Draco (versión Mac ligera y versión iPhone de alta calidad).
- `datos/`: fichas de músculos (`musculos.json`), archivo de revisión (`revision_musculos.csv`) y fichas revisadas.
- `scripts/`: aplicación de la revisión, inventario y exportación del atlas con Blender.
- `FASE0_REPORTE.md`: reporte por fase (qué funciona, qué falta, rendimiento).

## Créditos y licencia

Modelos derivados de:

- **BodyParts3D** - The Database Center for Life Science - CC-BY-SA 2.1 Japan
- **Z-Anatomy** - The libre 3D atlas of anatomy - CC-BY-SA 4.0

Los modelos derivados se distribuyen bajo CC BY-SA 4.0.
Los datos anatómicos se verificaron contra Snell, *Anatomía clínica por regiones*, 10.ª ed. (solo consulta; el libro no se incluye).
