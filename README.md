# Conference Parties RSVP

Una skill para Claude que te anota en **todas las fiestas, cenas y desayunos** de una conferencia publicados en [conferenceparties.com](https://conferenceparties.com) (AWS re:Invent, KubeCon, Google Next…).

Tú llenas tus datos **una sola vez** en una página en español. Claude revisa cada link, llena cada formulario **en inglés** y te dice en cuáles quedaste.

![Página donde llenas tus datos](docs/pagina-datos.png)

---

## Qué necesitas

- **Claude Code** (app de escritorio o terminal). El navegador integrado de la app es donde Claude llena los formularios.
- **Python 3**, que ya viene en Mac.
- 10 minutos para llenar tus datos y luego dejar que Claude trabaje.

## Instalar (una vez)

**Opción A: descargar el archivo `.skill`**
Descarga `conference-parties-rsvp.skill` desde [Releases](https://github.com/carlicode/conference-parties-rsvp/releases/latest) y ábrelo en Claude. Toca **Guardar skill**.

**Opción B: copiar la carpeta**

```bash
git clone https://github.com/carlicode/conference-parties-rsvp.git
```

```bash
cp -r conference-parties-rsvp/skills/conference-parties-rsvp ~/.claude/skills/
```

Reinicia Claude Code y listo.

---

## Cómo se usa, paso a paso (ejemplo con datos ficticios)

En este ejemplo **Ana Rojas**, de la empresa ficticia **Andes Data**, va a AWS re:Invent 2026.

### 1. Pega el link

Ana le escribe a Claude:

> Anótame en todas las fiestas de https://conferenceparties.com/reinvent2026/

### 2. Claude revisa todos los links

Claude abre la página, saca cada evento y revisa qué piden los formularios. Le responde algo así:

> Hay **207 eventos** con **171 links**, del domingo 29/11 al viernes 4/12. 72 son de Luma. 3 ya están llenos, 1 es pagado (US$500) y unos 36 son solo para ejecutivos. Casi todos piden: nombre, cargo, empresa, correo de trabajo, celular, LinkedIn, país, tamaño de empresa y relación con AWS.

### 3. Ana llena la página de datos

Claude le pasa un link a una página como la de arriba. Ana la llena en español:

| Campo | Lo que escribe Ana |
|---|---|
| Nombre / Apellido | Ana / Rojas |
| Cargo | Ingeniera de datos |
| Celular | +591 70000000 |
| Empresa | Andes Data |
| Correo | ana@andesdata.example |
| Alias del correo | Sí, etiqueta `riv26` → los formularios reciben `ana+riv26@andesdata.example` |
| Qué hace la empresa | Startup que ayuda a cooperativas a analizar sus datos de ventas con IA |
| Restricciones alimentarias | Vegetariana |
| Por qué quiere ir | Aprender cómo otros llevan IA a producción y conocer gente de datos |
| Días en Las Vegas | Lun 30, Mar 1, Mié 2 |
| Eventos solo para ejecutivos | No |
| Lista de espera si está lleno | Sí |
| Correos de marketing | No |

Toca **Guardar** y le dice a Claude: *"listo, ya guardé"*.

> Si quieres ver la página con estos datos de ejemplo, abre [`docs/ejemplo-pagina.html`](docs/ejemplo-pagina.html) en tu navegador.

### 4. Claude lo pasa al inglés

Los formularios son de empresas de EE. UU., así que Claude traduce y completa las frases:

- "Ingeniera de datos" → **Data Engineer**
- "Vegetariana" → **Vegetarian**
- "Aprender y conocer gente" → *"I'm a Data Engineer at Andes Data, a startup that helps cooperatives analyze their sales data with AI. I'm coming to learn how other teams take AI to production and to meet people working in data."*

El ejemplo completo está en [`docs/ejemplo-perfil.json`](docs/ejemplo-perfil.json).

### 5. Claude filtra según lo que elegiste

Con los días de Ana y sin eventos para ejecutivos, quedan **unos 90 eventos**. Claude le muestra la lista de los que descartó y por qué.

### 6. Entras a Luma (solo una vez)

Luma pide iniciar sesión. Claude le dice a Ana:

> Abre el navegador (Cmd+Shift+B) y entra a luma.com con tu correo y el código que te llega.

Mientras Ana lo hace, Claude ya va llenando los formularios de otros sitios.

### 7. Claude llena formulario por formulario

En cada link Claude:
1. Abre la página y el formulario.
2. Llena los datos comunes y responde las preguntas propias de ese evento.
3. Acepta **solo** las casillas obligatorias (términos, mayor de 21). Las de marketing quedan sin marcar.
4. Envía y confirma que apareció el "Thank you".
5. Lo anota en el registro.

Cada 10 formularios te cuenta cuántos van.

### 8. Reporte final

Al terminar, Ana recibe algo así:

| Estado | Cantidad |
|---|---|
| ✅ Enviados | 74 |
| ⏳ En lista de espera | 6 |
| 🚫 Cerrados o llenos | 3 |
| ✋ Necesitan a Ana (login de Eventbrite/Meetup o CAPTCHA) | 5 |

Y le van llegando los correos de confirmación.

---

## Lo que Claude **no** hace

- No escribe contraseñas ni crea cuentas: tú inicias sesión.
- No resuelve CAPTCHAs: los deja listos para que tú toques enviar.
- No paga entradas.
- No acepta correos de marketing salvo que lo marques.
- No envía nada hasta que digas que sí.

## Preguntas frecuentes

**¿Dónde quedan mis datos?** En la página privada que crea Claude (solo tú la ves) y en tu computadora mientras dura la sesión. Se envían únicamente a los formularios de los eventos.

**¿Cómo separo los correos de los eventos?** Activa el alias en la página de datos. Los formularios reciben `tu+riv26@empresa.com`, que llega a tu bandeja normal. Después, en Gmail, busca `to:(tu+riv26@empresa.com)` para encontrarlos todos y crea un filtro para etiquetarlos o borrarlos. En Outlook, usa una regla "enviado a" esa dirección. Funciona en Gmail, Google Workspace y Outlook / Microsoft 365; con otros proveedores, mándate un correo de prueba antes. En Luma, entra con la dirección con alias para que también aplique ahí.

**¿Puedo usarla para otra conferencia?** Sí, cualquier página de conferenceparties.com: pega su link.

**¿Puedo anotarme solo en algunos eventos?** Sí. Elige tus días en la página o dile a Claude cuáles quieres.

**¿Cuánto tarda?** Unos 2 o 3 minutos por formulario. Para 100 eventos, déjalo trabajando un buen rato.

---

## Qué hay en este repo

```
conference-parties-rsvp/
├── README.md                     ← estás aquí
├── docs/
│   ├── pagina-datos.png          ← captura de la página de datos
│   ├── ejemplo-pagina.html       ← la página con datos ficticios
│   └── ejemplo-perfil.json       ← ejemplo: español → inglés
└── skills/conference-parties-rsvp/   ← la skill (esto es lo que se instala)
    ├── SKILL.md                  ← instrucciones para Claude
    ├── assets/perfil.html        ← plantilla de la página de datos
    ├── scripts/
    │   ├── extract_events.py     ← saca todos los eventos de la página
    │   ├── luma_questions.py     ← lee las preguntas de Luma
    │   └── filter_events.py      ← filtra por tus días y preferencias
    └── references/
        ├── filler.js             ← llena los campos comunes de un formulario
        └── plataformas.md        ← trucos para Luma, HubSpot, Cvent, etc.
```
