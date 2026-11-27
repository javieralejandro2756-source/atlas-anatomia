"""Fichas del sistema nervioso central y de los pares craneales.

Uso: python datos_encefalo.py  -> datos/encefalo.json y app/public/datos/encefalo.json

Cada entrada se liga a una o varias mallas de Z-Anatomy (nombre base en inglés).
Contenido redactado a partir de Snell, Neuroanatomía clínica 7.ª ed. (capítulo indicado)
y de la tabla 12-6 de Snell, Anatomía clínica por regiones 10.ª ed. (pares craneales).
No se copia texto del libro: son resúmenes propios con su fuente. Todo queda "por revisar".

Áreas de Brodmann: Z-Anatomy no trae las áreas como mallas. Se asignan al giro que las
contiene según la descripción de Snell (cap. 8); son aproximadas, porque los límites
citoarquitectónicos no coinciden exactamente con los giros.
Etiquetas de área (filtro de la app): motora, somatosensorial, vision, audicion, gusto,
olfato, equilibrio, lenguaje, prefrontal, limbico.
"""
import json, os

S = "Snell, Neuroanatomía clínica 7.ª ed., cap. "
T126 = "Snell, Anatomía clínica por regiones 10.ª ed., tabla 12-6"

E = []
def e(mallas, nombre, grupo, funcion, areas=(), brodmann="", lesion="", fuente=""):
    E.append({"mallas": list(mallas), "nombre": nombre, "grupo": grupo, "areas": list(areas),
              "brodmann": brodmann, "funcion": funcion, "lesion": lesion, "fuente": fuente,
              "estado": "por revisar"})

# ---------- Lóbulo frontal ----------
e(["Precentral gyrus"], "Giro precentral", "Lóbulo frontal",
  "Su parte posterior es el área motora primaria: ejecuta los movimientos voluntarios aislados del lado contrario del cuerpo. "
  "El cuerpo está representado invertido (homúnculo motor): deglución y lengua abajo; mano y dedos, amplios; cadera, rodilla y tobillo arriba. "
  "Su parte anterior pertenece al área premotora.",
  ["motora"], "4 (área motora primaria); 6 en la parte anterior (premotora)",
  "Debilidad o parálisis del lado contrario en la región correspondiente del homúnculo.", S + "8")
e(["Paracentral gyrus and sulcus*", "Paracentral sulcus"], "Lobulillo paracentral", "Lóbulo frontal y parietal (cara medial)",
  "Continúa en la cara medial las áreas motora y somatosensitiva primarias: movimientos y sensibilidad de pierna y pie, "
  "y control de los esfínteres anal y vesical.",
  ["motora", "somatosensorial"], "4 (parte anterior); 3, 1 y 2 (parte posterior)",
  "", S + "8")
e(["Superior frontal gyrus", "Superior frontal sulcus"], "Giro frontal superior", "Lóbulo frontal",
  "Su parte posterior pertenece al área premotora, que guarda programas motores aprendidos y controla movimientos posturales gruesos. "
  "En la cara medial, por delante del lobulillo paracentral, está el área motora suplementaria. El resto es corteza prefrontal.",
  ["motora", "prefrontal"], "6 (posterior); 9 y 10 (prefrontal)", "", S + "8")
e(["Middle frontal gyrus", "Inferior frontal sulcus"], "Giro frontal medio", "Lóbulo frontal",
  "Contiene el campo ocular frontal: movimientos voluntarios conjugados de los ojos hacia el lado opuesto. "
  "Su parte posterior es premotora y la anterior, prefrontal.",
  ["motora", "prefrontal"], "6, 8 y 9 (campo ocular frontal); 9 y 10 (prefrontal)", "", S + "8")
e(["Opercular part of inferior frontal gyrus", "Triangular part of inferior frontal gyrus", "Lat_Fis-ant-Horizont", "Lat_Fis-ant-Vertical"],
  "Porciones opercular y triangular del giro frontal inferior (área de Broca)", "Lóbulo frontal",
  "Área motora del lenguaje de Broca, en el hemisferio dominante (el izquierdo en ~96 % de los adultos): forma las palabras "
  "coordinando laringe, boca, lengua, paladar blando y músculos respiratorios.",
  ["lenguaje", "motora"], "44 y 45",
  "En el hemisferio dominante: afasia de expresión (parálisis del lenguaje); en el no dominante no afecta el lenguaje.", S + "8")
e(["Orbital part of  inferior frontal gyrus", "Orbital gyri", "Orbital gyri (Frontomarginal gyrus and sulcus*)",
   "Orbital sulci (H-shaped orbital sulci*)", "Orbital sulci (Lateral Orbital sulcus*)", "Straight gyrus (Gyrus rectus)",
   "Transverse frontopolar gyrus and sulcus*", "Olfactory sulcus"],
  "Corteza prefrontal orbitaria y polo frontal", "Lóbulo frontal",
  "Corteza prefrontal: participa en la personalidad, regula la profundidad de los sentimientos e influye en la iniciativa y el juicio.",
  ["prefrontal"], "9, 10, 11 y 12 (prefrontal)", "", S + "8")
e(["Precentral sulcus (Superior part)*", "Precentral sulcus (inferior part)*"], "Surco precentral", "Lóbulo frontal",
  "Limita por delante al giro precentral (área motora primaria).", [], "", "", S + "7")
e(["Central sulcus"], "Surco central", "Surco interlobular",
  "Separa el lóbulo frontal (giro precentral, motor) del parietal (giro poscentral, somatosensitivo).", ["motora", "somatosensorial"], "", "", S + "7")

# ---------- Lóbulo parietal ----------
e(["Postcentral gyrus", "Postcentral sulcus"], "Giro poscentral", "Lóbulo parietal",
  "Área somestésica primaria: recibe la sensibilidad del lado contrario del cuerpo desde los núcleos ventral posterolateral y posteromedial del tálamo. "
  "Representación invertida (homúnculo sensitivo): faringe, lengua y mandíbula abajo; cara, labios, pulgar e índice con áreas grandes. "
  "Su extremo inferior, junto a la ínsula, corresponde al área del gusto.",
  ["somatosensorial", "gusto"], "3, 1 y 2 (somestésica primaria); 43 en el extremo inferior (gusto)",
  "Pérdida de sensibilidad del lado contrario en la región correspondiente.", S + "8")
e(["Superior parietal lobule", "Precuneus", "Intraparietal sulcus", "Subparietal sulcus"], "Lobulillo parietal superior y precúneo", "Lóbulo parietal",
  "Área de asociación somestésica: integra las distintas modalidades sensitivas y permite reconocer un objeto en la mano sin verlo (estereognosia). "
  "La corteza parietal posterior organiza también la imagen del cuerpo.",
  ["somatosensorial"], "5 y 7", "", S + "8")
e(["Supramarginal gyrus", "Angular gyrus", "Sulcus interm_prim-Jensen", "Lat_Fis-post"], "Giros supramarginal y angular", "Lóbulo parietal",
  "Rodean el extremo posterior del surco lateral, donde se extiende el área de Wernicke en el hemisferio dominante. "
  "Integran información visual, auditiva y somática (corteza parietal posterior).",
  ["lenguaje", "somatosensorial"], "", "", S + "8")

# ---------- Lóbulo occipital ----------
e(["Calcarine sulcus", "Cuneus", "Lingual gyrus", "Occipital pole"], "Corteza visual primaria (surco calcarino, cúneo y giro lingual)", "Lóbulo occipital",
  "Área visual primaria en las paredes del surco calcarino. Recibe las fibras del cuerpo geniculado lateral: la mitad derecha del campo visual se representa "
  "en el hemisferio izquierdo y viceversa. La pared superior del surco recibe el campo visual inferior y la inferior, el superior. La mácula ocupa la parte posterior (cerca del polo).",
  ["vision"], "17 (visual primaria); 18 y 19 alrededor (visual secundaria)",
  "Pérdida del campo visual contralateral (hemianopsia homónima).", S + "8")
e(["Lateral occipital gyrus (Middle occipital gyrus*)", "Superior occipital gyri", "Inferior occipital gyrus and sulcus*",
   "Transverse occipital sulcus", "Lunate sulcus", "Anterior occipital sulcus*"], "Giros occipitales laterales", "Lóbulo occipital",
  "Área visual secundaria: relaciona lo que se ve con experiencias visuales previas para reconocerlo. Contiene el campo ocular occipital (seguimiento reflejo de objetos).",
  ["vision"], "18 y 19", "", S + "8")
e(["Parieto-occipital sulcus"], "Surco parietooccipital", "Surco interlobular", "Separa en la cara medial los lóbulos parietal y occipital.", [], "", "", S + "7")

# ---------- Lóbulo temporal ----------
e(["Transverse temporal gyri"], "Giros temporales transversos (de Heschl)", "Lóbulo temporal",
  "Área auditiva primaria, en la pared inferior del surco lateral. Recibe la radiación auditiva del cuerpo geniculado medial. "
  "La parte anterior recibe sonidos graves y la posterior, agudos.",
  ["audicion"], "41 y 42",
  "Lesión unilateral: sordera parcial de ambos oídos, mayor en el contralateral.", S + "8")
e(["Temporal plane"], "Plano temporal", "Lóbulo temporal",
  "Por detrás del área auditiva primaria: área auditiva secundaria, necesaria para interpretar los sonidos. En el hemisferio dominante forma parte del área de Wernicke.",
  ["audicion", "lenguaje"], "22", "", S + "8")
e(["Superior temporal gyrus (Lateral part)", "Superior temporal sulcus"], "Giro temporal superior", "Lóbulo temporal",
  "Área auditiva secundaria y, en el hemisferio dominante, área sensitiva del lenguaje de Wernicke: comprensión del lenguaje hablado y escrito. "
  "Se conecta con el área de Broca por el fascículo arcuato. Cerca está el área vestibular (postura y movimiento de la cabeza).",
  ["audicion", "lenguaje", "equilibrio"], "22",
  "En el hemisferio dominante: afasia de comprensión (de Wernicke).", S + "8")
e(["Middle temporal gyrus", "Inferior temporal gyrus", "Inferior temporal sulcus", "Temporal pole",
   "Lateral occipitotemporal gyrus", "Occipitotemporal sulcus (Lateral part*)"], "Giros temporales medio e inferior y polo temporal", "Lóbulo temporal",
  "Corteza temporal anterior de asociación: almacena experiencias sensitivas previas; su estimulación evoca objetos vistos o música oída antes.",
  [], "", "", S + "8")

# ---------- Ínsula y lóbulo límbico ----------
e(["Insula (Subcentral gyrus and ant. and post. sulci*)", "Circular sulcus of insula"], "Ínsula", "Ínsula",
  "Corteza oculta en el fondo del surco lateral. Junto con el extremo inferior del giro poscentral forma el área del gusto; "
  "se cree importante para planear los movimientos articulatorios del lenguaje.",
  ["gusto", "lenguaje"], "43 (área del gusto, adyacente)", "", S + "8")
e(["Cingulate gyrus and sulcus (Middle anterior part)", "Cingulate gyrus and sulcus (Middle posterior part)",
   "Cingulate gyrus and sulcus (Posterior dorsal part)", "Cingulate gyrus (Posteroventral part*)", "Cingulate sulcus (Marginal part*)"],
  "Giro del cíngulo", "Lóbulo límbico",
  "Forma parte del sistema límbico (conducta emocional). Su mitad anterior se incluye en la corteza prefrontal.",
  ["limbico", "prefrontal"], "", "", S + "8 y 9")
e(["Hippocampus", "Hippocampal commissure"], "Hipocampo", "Sistema límbico",
  "Participa en convertir la memoria reciente en memoria a largo plazo.",
  ["limbico"], "",
  "Amnesia anterógrada: no se forman recuerdos nuevos; se conservan los del pasado remoto.", S + "9")
e(["Medial occipitotemporal gyrus (Parahippocampal*)", "Collateral sulcus", " Posterior transverse collateral sulcus"],
  "Giro parahipocampal", "Sistema límbico",
  "Parte de la formación del hipocampo; termina por delante en el uncus. Se relaciona con la memoria.",
  ["limbico"], "", "", S + "7 y 9")
e(["Amygdaloid body"], "Cuerpo amigdalino", "Sistema límbico",
  "Núcleo del lóbulo temporal cercano al uncus. Influye en la conducta emocional, en especial el miedo; con el hipocampo, en la memoria.",
  ["limbico"], "", "Lesión junto con el hipocampo: pérdida de memoria mayor que cada una por separado.", S + "9")
e(["Fornix", "Mamillary body", "Septal nuclei", "Stria terminalis", "Habenula", "Stria medullaris thalami"],
  "Fórnix y otras vías límbicas", "Sistema límbico",
  "Vías y núcleos que conectan el hipocampo y la amígdala con el hipotálamo (cuerpos mamilares) y el tálamo dentro del sistema límbico.",
  ["limbico"], "", "", S + "9")

# ---------- Sustancia blanca y ventrículos ----------
e(["Corpus callosum", "Anterior commissure", "Posterior commissure"], "Cuerpo calloso y comisuras", "Sustancia blanca",
  "Fibras comisurales que pasan información de un hemisferio al otro.", [], "", "", S + "7 y 8")
e(["White matter of telencephalon"], "Sustancia blanca del telencéfalo", "Sustancia blanca",
  "Fibras de asociación, comisurales y de proyección (como la cápsula interna) de los hemisferios.", [], "", "", S + "7")
e(["Lateral ventricle", "Third ventricle", "Fourth ventricle", "Aqueduct of midbrain", "Choroid plexus", "Septum pellucidum", "Central canal", "Central canal'"],
  "Sistema ventricular", "Ventrículos",
  "Cavidades que contienen líquido cefalorraquídeo, producido sobre todo por los plexos coroideos.", [], "", "", S + "16")
e(["Falx cerebri", "Tentorium cerebelli", "Spinal dura"], "Duramadre", "Meninges",
  "Meninge externa. La hoz del cerebro separa los hemisferios; la tienda del cerebelo separa cerebro y cerebelo.", [], "",
  "Herniación del uncus a través de la tienda: compresión del mesencéfalo.", S + "15")

# ---------- Núcleos basales ----------
e(["Caudate nucleus", "Putamen", "Globus pallidus", "Lentiform nucleus"], "Núcleos basales (caudado, putamen, globo pálido)", "Núcleos basales",
  "Reciben información de la corteza, el tálamo y el tronco encefálico, y por el globo pálido influyen sobre las áreas motoras de la corteza. "
  "Regulan el movimiento voluntario y el aprendizaje de habilidades motoras; no actúan directamente sobre la médula.",
  ["motora"], "", "Lesiones del cuerpo estriado: corea, atetosis, distonía; parkinsonismo.", S + "10")

# ---------- Diencéfalo ----------
e(["Thalamus"], "Tálamo", "Diencéfalo",
  "Gran masa de sustancia gris que releva casi toda la información sensitiva hacia la corteza (núcleos ventral posterolateral y posteromedial hacia el giro poscentral).",
  ["somatosensorial"], "", "", S + "12")
e(["Hypothalamus"], "Hipotálamo", "Diencéfalo",
  "Controla el sistema nervioso autónomo y el sistema endocrino a través de la hipófisis; participa en la conducta emocional del sistema límbico.",
  ["limbico"], "", "", S + "13")
e(["Lateral geniculate body"], "Cuerpo geniculado lateral", "Diencéfalo",
  "Estación de relevo de la vía visual: recibe el tracto óptico y envía la radiación óptica al área visual primaria.",
  ["vision"], "", "", S + "8")
e(["Medial geniculate body"], "Cuerpo geniculado medial", "Diencéfalo",
  "Estación de relevo de la vía auditiva hacia el área auditiva primaria; recibe información de ambos oídos, sobre todo del contralateral.",
  ["audicion"], "", "", S + "8")
e(["Optic chiasm", "Optic tract"], "Quiasma y tracto óptico", "Vía visual",
  "En el quiasma se cruzan las fibras de la mitad nasal de cada retina; el tracto óptico lleva la información de la mitad contraria del campo visual.",
  ["vision"], "", "Lesión del quiasma: hemianopsia bitemporal.", S + "11")

# ---------- Tronco encefálico ----------
e(["Midbrain", "Base of peduncle", "Interpeduncular fossa", "Red nucleus"], "Mesencéfalo", "Tronco encefálico",
  "Contiene los núcleos de los pares III y IV, el núcleo rojo y las fibras descendentes de la base del pedúnculo.", ["motora"], "", "", S + "5")
e(["Superior colliculus"], "Colículo superior", "Tronco encefálico",
  "Centro de reflejos visuales; se conecta con los núcleos de los músculos extraoculares y recibe del campo ocular frontal.", ["vision"], "", "", S + "5 y 8")
e(["Inferior colliculus"], "Colículo inferior", "Tronco encefálico", "Estación de la vía auditiva.", ["audicion"], "", "", S + "5")
e(["Pons"], "Puente", "Tronco encefálico", "Contiene núcleos de los pares V a VIII y conecta la corteza con el cerebelo.", [], "", "", S + "5")
e(["Medulla oblongata", "Olive"], "Bulbo raquídeo (médula oblongada)", "Tronco encefálico",
  "Contiene núcleos de los pares IX a XII y centros vitales; la oliva se relaciona con el cerebelo.", [], "", "", S + "5")
e(["Pyramid of medulla oblongata"], "Pirámide bulbar", "Tronco encefálico",
  "Fibras corticoespinales; en su parte inferior la mayoría se cruza (decusación de las pirámides).", ["motora"], "", "", S + "4 y 5")
for malla, par, nombre in [("Nucleus of oculomotor nerve", "III", "Núcleo del nervio oculomotor"), ("Accessory nucleus of oculomotor nerve", "III", "Núcleo accesorio del oculomotor (parasimpático)"),
                           ("Nucleus of trochlear nerve", "IV", "Núcleo del nervio troclear"), ("Nucleus of abducens nerve", "VI", "Núcleo del nervio abducens"),
                           ("Motor nucleus of facial nerve", "VII", "Núcleo motor del nervio facial"), ("Superior salivatory nucleus", "VII", "Núcleo salival superior"),
                           ("Vestibular nuclei", "VIII", "Núcleos vestibulares"), ("Anterior cochlear nucleus", "VIII", "Núcleo coclear anterior"),
                           ("Posterior cochlear nucleus", "VIII", "Núcleo coclear posterior"), ("Inferior salivatory nucleus", "IX", "Núcleo salival inferior"),
                           ("Nucleus ambiguus", "IX, X y XI", "Núcleo ambiguo"), ("Posterior nucleus of vagus nerve", "X", "Núcleo posterior del vago"),
                           ("Nucleus of hypoglossal nerve", "XII", "Núcleo del nervio hipogloso"), ("Nucleus of accessory nerve", "XI", "Núcleo del nervio accesorio")]:
    areas = ["equilibrio"] if "estibular" in nombre else ["audicion"] if "coclear" in nombre else []
    e([malla], nombre, "Núcleos de pares craneales", f"Núcleo del par craneal {par}.", areas, "", "", S + "11")

# ---------- Cerebelo ----------
e(["Anterior quadrangular lobule", "Posterior quadrangular lobule", "Superior semilunar lobule", "Inferior semilunar lobule", "Biventral lobule",
   "Gracile lobule", "Tonsil of cerebellum", "Central lobule", "Wing of central lobule", "Culmen", "Declive", "Folium of vermis", "Tuber of vermis",
   "Pyramis of vermis", "Uvula of vermis", "Lingula of cerebellum", "Superior cerebellar peduncle"], "Cerebelo", "Cerebelo",
  "Recibe información del movimiento voluntario (corteza, músculos, tendones, articulaciones) y del equilibrio; coordina el movimiento a través de sus núcleos profundos, "
  "sin conexión directa con las motoneuronas. El vermis proyecta al núcleo del fastigio y la parte lateral del hemisferio, al dentado.",
  ["motora", "equilibrio"], "", "Temblor intencional y falta de coordinación (enfermedad cerebelosa).", S + "6")
e(["Flocculus", "Nodule of vermis", "Peduncle of flocculus"], "Lóbulo floculonodular", "Cerebelo",
  "Recibe información del nervio vestibular: equilibrio.", ["equilibrio"], "", "", S + "6")

# ---------- Médula espinal ----------
e(["Lateral corticospinal tract", "Anterior corticospinal tract"], "Tractos corticoespinales", "Médula espinal",
  "Vía motora voluntaria desde la corteza hacia las motoneuronas de la médula.", ["motora"], "", "", S + "4")
e(["Lateral spinothalamic tract"], "Tracto espinotalámico lateral", "Médula espinal", "Conduce dolor y temperatura hacia el tálamo.", ["somatosensorial"], "", "", S + "4")
e(["Anterior spinothalamic tract"], "Tracto espinotalámico anterior", "Médula espinal", "Conduce tacto grueso y presión hacia el tálamo.", ["somatosensorial"], "", "", S + "4")
e(["Gracile fasciculus", "Cuneate fasciculus"], "Fascículos grácil y cuneiforme", "Médula espinal",
  "Cordón posterior: tacto discriminativo, sentido de posición y vibración (el grácil desde el miembro inferior; el cuneiforme desde el superior).",
  ["somatosensorial"], "", "", S + "4")
e(["Anterior spinocerebellar tract", "Posterior spinocerebellar tract"], "Tractos espinocerebelosos", "Médula espinal",
  "Llevan al cerebelo información propioceptiva inconsciente de músculos y articulaciones.", ["equilibrio"], "", "", S + "4")
e(["Rubrospinal tract", "Tectospinal tract", "Lateral vestibulospinal tract", "Medial vestibulospinal tract", "Lateral reticulospinal tract", "Medial reticulospinal tract"],
  "Tractos descendentes extrapiramidales", "Médula espinal",
  "Vías desde el tronco encefálico (núcleo rojo, colículo superior, núcleos vestibulares, formación reticular) que modulan el tono y la postura.",
  ["motora", "equilibrio"], "", "", S + "4")
e(["Spinotectal tract"], "Tracto espinotectal", "Médula espinal", "Información sensitiva hacia el colículo superior (reflejos espinovisuales).", [], "", "", S + "4")
e(["Anterior horn of spinal cord"], "Asta anterior", "Médula espinal", "Motoneuronas inferiores de los músculos esqueléticos.", ["motora"], "", "", S + "4")
e(["Posterior horn of spinal cord", "Nucleus proprius", "Spinal reticular process", "Posterolateral tract"], "Asta posterior", "Médula espinal",
  "Recibe la sensibilidad que entra por las raíces posteriores.", ["somatosensorial"], "", "", S + "4")
e(["Intermediolateral nucleus", "Intermediomedial nucleus", "Lateral intermediate substance"], "Zona intermedia", "Médula espinal",
  "Contiene neuronas autonómicas (columna intermediolateral).", [], "", "", S + "4 y 14")
e(["White matter of spinal cord", "Anterior fasciculus proprius", "Lateral fasciculus proprius", "Posterior fasciculus proprius"], "Sustancia blanca de la médula", "Médula espinal",
  "Cordones con los tractos ascendentes y descendentes.", [], "", "", S + "4")

# ---------- Ojo ----------
e(["Retina"], "Retina", "Ojo", "Capa sensitiva del ojo: inicia la vía visual. La mácula es el área de visión más perfecta.", ["vision"], "", "", S + "8 y 11")
e(["Cornea", "Lens", "Iris", "Sclera", "Vitreous body", "Anterior chamber of eyeball", "Anterior segment of eyeball", "Posterior segment of eyeball",
   "Zonular fibres", "Suspensory ligament of eyeball"], "Globo ocular", "Ojo", "Estructuras ópticas y de sostén del ojo.", ["vision"], "", "", S + "11")
e(["Lacrimal gland", "Lacrimal sac", "Lacrimal canaliculus", "Ampulla of lacrimal canaliculus", "Nasolacrimal duct"], "Aparato lagrimal", "Ojo",
  "Produce y drena las lágrimas; la glándula lagrimal recibe fibras secretomotoras del facial.", [], "", "", T126)

# ---------- Pares craneales (tabla 12-6) ----------
PC = [
 ("Olfactory nerve (I)", "I. Olfatorio", "Sensitivo", "Olfato.", "Forámenes de la lámina cribosa del etmoides", ["olfato"]),
 ("Optic nerve (II)", "II. Óptico", "Sensitivo", "Visión.", "Canal óptico", ["vision"]),
 ("Oculomotor nerve (III)", "III. Oculomotor", "Motor", "Eleva el párpado superior; gira el globo ocular hacia abajo, arriba y medialmente; constricción pupilar; acomodación.", "Fisura orbitaria superior", []),
 ("Trochlear nerve (IV)", "IV. Troclear", "Motor", "Ayuda a rotar el globo ocular en sentido inferolateral.", "Fisura orbitaria superior", []),
 ("Trigeminal nerve (V)", "V. Trigémino", "Sensitivo (V1, V2, V3) y motor (V3)",
  "Sensibilidad de la cara, córnea, cuero cabelludo, dientes, mucosas nasal y oral y dos tercios anteriores de la lengua; "
  "motor de los músculos de la masticación, milohioideo, vientre anterior del digástrico, tensor del velo del paladar y tensor del tímpano.",
  "V1: fisura orbitaria superior; V2: foramen redondo; V3: foramen oval", ["somatosensorial"]),
 ("Abducens nerve (VI)", "VI. Abducens", "Motor", "Músculo recto lateral: rota el globo ocular hacia lateral.", "Fisura orbitaria superior", []),
 ("Facial nerve (VII)", "VII. Facial", "Motor, sensorial y parasimpático",
  "Músculos de la expresión facial, estapedio, estilohioideo y vientre posterior del digástrico; gusto de los dos tercios anteriores de la lengua; "
  "glándulas submandibular, sublingual y lagrimal.", "Meato acústico interno, canal facial, foramen estilomastoideo", ["gusto"]),
 ("Vestibulocochlear nerve (VIII)", "VIII. Vestibulococlear", "Sensitivo", "Vestibular: posición y movimiento de la cabeza. Coclear: audición.", "Meato acústico interno", ["audicion", "equilibrio"]),
 ("Glossopharyngeal nerve (IX)", "IX. Glosofaríngeo", "Motor, parasimpático y sensitivo",
  "Estilofaríngeo (deglución); glándula parótida; sensibilidad general y gusto del tercio posterior de la lengua y la faringe; seno y cuerpo carotídeos.", "Foramen yugular", ["gusto"]),
 ("Vagus nerve (X)", "X. Vago", "Motor y sensitivo",
  "Constrictores de la faringe y músculos intrínsecos de la laringe; músculo liso de tráquea, bronquios y tubo digestivo hasta la flexura esplénica; corazón; gusto en epiglotis y valécula.",
  "Foramen yugular", ["gusto"]),
 ("Accessory nerve (XI)", "XI. Accesorio", "Motor", "Raíz craneal: paladar blando, faringe y laringe. Raíz espinal: esternocleidomastoideo y trapecio.", "Foramen yugular (la raíz espinal entra por el foramen magno)", []),
 ("Hypoglossal nerve (XII)", "XII. Hipogloso", "Motor", "Músculos de la lengua (excepto el palatogloso).", "Canal hipogloso", []),
]
for malla, nombre, comp, func, salida, areas in PC:
    E.append({"mallas": [malla], "nombre": nombre, "grupo": "Pares craneales", "areas": areas, "brodmann": "",
              "componentes": comp, "funcion": func, "salida": salida, "lesion": "", "fuente": T126, "estado": "por revisar"})
for malla, base in [("Cochlear nerve", "VIII"), ("Vestibular nerve", "VIII"), ("Ophthalmic nerve", "V"), ("Maxillary nerve", "V"),
                    ("Anterior division of mandibular nerve", "V"), ("Posterior division of mandibular nerve", "V"),
                    ("Motor root of trigeminal nerve", "V"), ("Sensory root of trigeminal nerve", "V"), ("Chorda tympani", "VII")]:
    pass  # ramas: la app muestra la ficha del par por su nombre base (ver mapeo abajo)

RAMAS = {"Cochlear nerve": "Vestibulocochlear nerve (VIII)", "Vestibular nerve": "Vestibulocochlear nerve (VIII)",
         "Ophthalmic nerve": "Trigeminal nerve (V)", "Maxillary nerve": "Trigeminal nerve (V)", "Meningeal branch of maxillary nerve": "Trigeminal nerve (V)",
         "Anterior division of mandibular nerve": "Trigeminal nerve (V)", "Posterior division of mandibular nerve": "Trigeminal nerve (V)",
         "Motor root of trigeminal nerve": "Trigeminal nerve (V)", "Sensory root of trigeminal nerve": "Trigeminal nerve (V)",
         "Buccal nerve": "Trigeminal nerve (V)", "Lingual nerve": "Trigeminal nerve (V)", "Inferior alveolar nerve": "Trigeminal nerve (V)",
         "Mental nerve": "Trigeminal nerve (V)", "Nerve to mylohyoid muscle": "Trigeminal nerve (V)", "Chorda tympani": "Facial nerve (VII)"}
for i, x in enumerate(E):
    x["id"] = f"e{i:03d}"
indice = {}
for x in E:
    for m in x["mallas"]:
        indice[m] = x["id"]
for rama, padre in RAMAS.items():
    indice[rama] = indice[padre]

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
salida = {"fichas": E, "mallas": indice}
for r in ("datos/encefalo.json", "app/public/datos/encefalo.json"):
    json.dump(salida, open(os.path.join(AQUI, r), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("fichas:", len(E), "mallas ligadas:", len(indice))
