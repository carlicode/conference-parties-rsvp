# Cómo se comporta cada plataforma de registro

Notas aprendidas llenando formularios reales de conferenceparties.com. Léelas cuando un formulario no se deje enviar o no sepas si quedó registrado.

## Luma (luma.com) — suele ser la mitad de los eventos
- Las preguntas se leen sin login con `scripts/luma_questions.py`.
- Se puede registrar sin sesión, como invitada: abre el evento, haz clic en Register / Request to Join (en español, Inscribirse / Solicitar unirse) y llena el cuadro con nombre, correo y las preguntas del evento. Usa el correo que escribas, así que el alias del correo sí aplica. Funcionó en re:Invent 2026 con decenas de eventos.
- Los campos de texto se llenan bien con el setter nativo de `value` más eventos `input` y `change`. Los desplegables, las casillas de términos y los multi-select de Luma no son campos normales: ábrelos con un clic real.
- Si un evento exige sesión, la persona entra una vez en luma.com con su correo y el código que le llega. Comprueba la sesión con `fetch('https://api.lu.ma/user',{credentials:'include'})` desde una pestaña de luma.com: 200 = con sesión, 401 = sin sesión. Mientras tanto, avanza con los formularios que no son de Luma.
- Eventos con "Require approval" muestran "Registro pendiente": van en `por-aprobar`, no en `enviado`.
- Algunos sitios propios (ej. kubeauto.day) son en realidad un evento de Luma: busca el link "Open registration on Luma" y súmalo a la lista de Luma.
- Links tipo `luma.com/user/...` son perfiles, no eventos: revisa el perfil para ver si tiene el evento.

## HubSpot (hubs.li, hubs.ly, páginas con formularios `hs-form`)
- Valida el teléfono: solo números y símbolos de teléfono. Usa `+59170000000` sin espacios.
- Éxito: aparece "Your submission was successful" o "Thank you" en la misma página.

## Marketo (newrelic, trendaisecurity, muchos `go.` / `pages.` / `events.`)
- Al elegir país a veces aparecen campos nuevos (estado, consentimiento): vuelve a correr el llenador.
- Éxito: la URL termina con `?aliId=...` o redirige a una página de "thank you".

## Cvent (web.cvent.com)
- Es de varios pasos: elegir sesión → datos personales → resumen → enviar.
- Si una sesión dice "Capacity Full", el botón es "Join Waitlist" (úsalo si la persona aceptó listas de espera).
- Suele tener 2 casillas obligatorias (contacto para el evento, aviso de fotos) y 1 opcional de marketing: deja la opcional sin marcar.
- En el resumen el botón final puede estar más abajo: desplázate hasta "Submit" / "Complete Registration".

## Swoogo (*.swoogo.com)
- Campo de teléfono con selector de país: elige el país y escribe el número completo.
- Éxito: redirige a `...-confirmation`.

## Eventbrite, Meetup
- Piden cuenta propia. No crees cuentas ni pongas contraseñas: déjalos en la lista "Necesita a la persona".

## Google Forms, Microsoft Forms
- Se llenan normalmente; revisa todas las páginas del formulario antes de enviar.

## Portales oficiales (reinvent-planner, portal de la conferencia)
- Requieren la entrada oficial y su login. Si la persona no tiene entrada, se descartan.

## Páginas propias de empresas (Next.js, Webflow, etc.)
- Desplegables personalizados: haz clic en el campo y elige la opción visible en la captura.
- Campos de texto sin etiqueta y vacíos al final de un formulario suelen ser trampas anti-bot (honeypot): déjalos vacíos.
- Algunos muestran "Registration closed" o "Capacity full": regístralo como cerrado.
- Si el formulario se vacía sin mensaje, márcalo como "dudoso" en el registro.

## Correo con alias (tu+etiqueta@...)
- Casi todos los sitios lo aceptan. Si uno lo rechaza (mensaje de correo inválido o el formulario no avanza), reintenta con el correo original y anótalo como `OK (sin alias)`.

## CAPTCHA
- Nunca lo resuelvas. Deja el formulario lleno y pásalo a la lista "Necesita a la persona".
