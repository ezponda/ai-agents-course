# Guion — Project 5: Deploy to Production (workflow `13_deploy_to_production.json`)

## Concepto clave
Llevar un workflow del portátil a un servidor que corre 24/7: cualquiera con el enlace chatea con tu IA. El workflow es mínimo a propósito (Chat Trigger → LLM → Output) porque la lección no es el workflow — es el **deploy**: publicar, `WEBHOOK_URL`, credenciales por instancia, y el historial de ejecuciones como debugger.

## Flujo del workflow
```
Chat Trigger (público) ──▶ Answer Question (Basic LLM Chain) ──▶ Output (text → output)
                                 ┊
                          OpenRouter Chat Model
```

**Credenciales necesarias:** solo OpenRouter (y habrá que re-introducirla EN el servidor — eso es parte de la lección).

---

## 🧭 GUÍA DE DECISIÓN — ¿Con qué grabamos el vídeo?

Precios verificados el 2026-07-05 (di siempre "a fecha de grabación" a cámara):

| Opción | Precio | Setup | ¿Enseña la lección? | Veredicto para el vídeo |
|--------|--------|-------|---------------------|------------------------|
| **Railway** ⭐ | **$5/mes** (Hobby, incluye $5 de uso) + **$5 de crédito trial al registrarte** → el vídeo te sale gratis | 1-click template, ~3 min | ✅ Sí: obliga a configurar `WEBHOOK_URL` (la lección estrella) | **LA ELEGIDA** |
| n8n Cloud | €20/mes anual, €24/mes mensual (Starter, 2.500 ejecuciones) | 2 min, cero config | ❌ A medias: `WEBHOOK_URL` automático — desaparece la lección | Nómbrala: "la más fácil, la más cara" |
| Sliplane (managed n8n) | €9/mes | ~5 min | ❌ Similar: te lo dan hecho | Nómbrala de pasada como alternativa gestionada |
| VPS + Docker (Hetzner ~€5) | El más barato a largo plazo | 30-60 min, terminal | ✅ Pero requiere Linux/Docker | Nómbrala: "máximo control, fuera del alcance del curso" |
| Render | **$25/mes** (el servicio de 2GB, 2026) | — | — | Ya no compite en precio — ni la menciones |

**Por qué Railway** (dilo así a cámara): *"Un click, cinco dólares — y de hecho el primer mes gratis con el crédito de prueba — y nos obliga a tocar la única pieza de configuración de producción que de verdad hay que entender: el WEBHOOK_URL. Las alternativas más fáciles nos la esconderían."*

---

## ✅ CHECKLIST DE ALTAS — Antes de grabar (haz esto HOY, no en el vídeo)

**No hay que instalar NADA.** Todo el proyecto va por navegador — ni Docker, ni CLI, ni terminal. Dilo a cámara: es un selling point.

| ✓ | Alta / preparación | Enlace | Notas |
|---|--------------------|--------|-------|
| ☐ | **Cuenta GitHub** (ya la tienes) | [github.com](https://github.com) | Se usa para el login de Railway |
| ☐ | **Cuenta Railway** — "Login with GitHub" → autorizar | [railway.com](https://railway.com/) | Al registrarte: **$5 de crédito trial** sin tarjeta. Para pasar a Hobby ($5/mes) pedirá tarjeta — para el vídeo el trial basta |
| ☐ | **API key de OpenRouter** (ya la tienes) | [openrouter.ai/keys](https://openrouter.ai/keys) | Tenla A MANO en un gestor — la vas a pegar en el servidor durante el vídeo. ⚠️ NUNCA visible en pantalla |
| ☐ | **Deploy de prueba COMPLETO la víspera** | [railway.com/deploy/n8n](https://railway.com/deploy/n8n) | Hazlo entero una vez (deploy → WEBHOOK_URL → publish → chat). Bórralo después y en el vídeo lo repites limpio. Así sabes los tiempos y qué pantallas salen |
| ☐ | Workflow local funcionando | — | El chat local responde antes de empezar a grabar |
| ☐ | Móvil a mano | — | El plano final: chatear con tu servidor desde el móvil |

**⚠️ Seguridad en pantalla (vídeo de deploy = máximo riesgo):**
- La API key de OpenRouter: pégala con la pantalla fuera de grabación o difumina en edición.
- La URL de tu instancia Railway saldrá en pantalla → cualquiera del público podrá chatear y gastar TUS tokens. Opciones: (a) borra el proyecto tras grabar, (b) límites de uso en OpenRouter, (c) la variación 2 (proteger con contraseña).

---

## 🎬 PARTE 1 — Guion paso a paso

### 0. Cold open (40s)

**Empezar con el móvil en mano, cámara al móvil: abrir una URL y chatear con tu IA.**

> "Esto no es ChatGPT — es MI inteligencia artificial, corriendo en MI servidor, y esta URL se la puedo pasar a cualquiera. Hace veinte minutos esto solo existía en mi portátil. Hoy vamos a hacer exactamente ese viaje: del portátil a producción, sin escribir una línea de código y por cinco dólares al mes."

---

### 1. La decisión — dónde desplegar (1.5 min)

**Enseñar la tabla de comparación (del notebook o de este guion).**

> "Tres formas de poner n8n en internet. n8n Cloud: la oficial, dos minutos, pero es la más cara — unos veinte euros al mes — y te lo da todo tan hecho que no aprendes lo que pasa por debajo. Un VPS con Docker: lo más barato a largo plazo y máximo control, pero necesitas manejarte con Linux — fuera del alcance de este curso. Y Railway: cinco dólares, un click... y nos deja UNA pieza de configuración manual. Esa pieza es justo la lección de hoy, así que Railway."

> "Precios a fecha de grabación — compruébalos en las páginas de pricing, que esto cambia."

---

### 2. El workflow — mínimo a propósito (1.5 min)

**Enseñar el workflow local: 3 nodos.**

> "El workflow más simple que puede ser útil: chat, LLM, respuesta. Lo hago mínimo a propósito — hoy la estrella no es el workflow, es el viaje al servidor. Todo lo que aprendáis hoy vale para CUALQUIER workflow del curso que tenga Chat Trigger o Webhook."

**Señalar 2 detalles:**
1. **Chat Trigger con Public ON** — "esto genera una página de chat alojada".
2. **El nodo Output** — "el chain deja su respuesta en `text` y el chat necesita `output` — este Set solo renombra. Os suena, ¿no?"

**Probar en local (botón Chat):** `What is n8n?` → funciona.

> "Funciona en mi portátil. Pero si ahora cierro n8n... muerto. Nadie más puede usarlo. Vamos a arreglarlo."

---

### 3. Deploy en Railway — el click (3 min)

**Pantalla: [railway.com/deploy/n8n](https://railway.com/deploy/n8n)** *(ojo: /deploy/n8n — la URL vieja /template/n8n ya no existe)*

1. **Click "Deploy Now"** → login con GitHub si no lo está.
2. > "Railway monta dos cosas: el contenedor de n8n y una base de datos Postgres para guardar workflows y credenciales. Todo automático."
3. **Mientras despliega (2-3 min)** — rellenar la espera:
   > "Esto que está pasando ahora — crear un servidor, instalar n8n, conectarle una base de datos, ponerle HTTPS — era un día de trabajo de un administrador de sistemas. Ahora son dos minutos y una barra de progreso. Y ojo al precio: el plan son cinco dólares al mes que INCLUYEN cinco dólares de uso — n8n parado casi no consume. Y al registrarte te regalan cinco de crédito: este vídeo me está saliendo gratis."
4. **Deploy verde → click en la URL pública** (`tu-app.up.railway.app`) → **crear la cuenta admin de n8n**.
   > "Primera lección de producción: esta es OTRA instancia de n8n. Recién nacida. No tiene mis workflows, no tiene mis credenciales. Todo lo que tenía en local, aquí no existe."

---

### 4. WEBHOOK_URL — LA lección (2.5 min) ⭐

> "Y ahora la única pieza de configuración que de verdad hay que entender. n8n genera URLs para sus webhooks y chats. ¿Con qué dominio las genera? Si no le decimos nada, con localhost — y localhost en un servidor significa 'yo mismo': nadie de fuera podrá entrar. Hay que decirle: 'tu dirección pública es ESTA'."

**En Railway: click en el servicio n8n → pestaña Variables → añadir:**

| Variable | Valor |
|----------|-------|
| `WEBHOOK_URL` | `https://tu-app.up.railway.app/` |

**Señalar dos trampas a cámara:**
1. "Con `https://` delante y **barra al final** — la barra importa."
2. "Es TU URL de Railway, la del paso anterior — cópiala, no la escribas."

> "Al guardar, Railway redespliega solo. Esta variable es EL concepto: en n8n Cloud os la configuran ellos, en un VPS la pondríais igual. Donde sea que despleguéis n8n, WEBHOOK_URL es la diferencia entre un chat que funciona y uno que apunta a ninguna parte."

---

### 5. Importar, credencial y Publish (2.5 min)

1. **Workflows → Import from URL** — copia y pega:
   ```
   https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/13_deploy_to_production.json
   ```
2. **Credencial OpenRouter** en el nodo del Chat Model:
   > "Segunda lección de producción: las credenciales viven POR instancia. Mi API key de local no ha viajado — y es lo correcto: las claves no deben viajar dentro de los workflows."
   *(⚠️ pega la key en un corte o difumínala en edición)*
3. **Publish** (arriba a la derecha):
   > "Tercera lección: un workflow importado es un borrador. Los borradores solo corren cuando pulsas Execute TÚ. Para que el chat exista para el mundo, se publica. Click en Publish... y ya está vivo."

---

### 6. El momento — probarlo desde fuera (2 min)

1. **Click en el nodo Chat Trigger → copiar la Production URL.**
2. **Abrirla en el móvil** (o en una ventana de incógnito) y chatear:
   ```
   Recommend me 3 books about artificial intelligence
   ```
3. > "Fijaos en lo que acaba de pasar: esto NO es mi portátil. Puedo apagar el ordenador ahora mismo y este chat sigue funcionando. Está en el servidor, veinticuatro-siete, y cualquiera con la URL puede usarlo."

---

### 7. Execution History — tu debugger de producción (1.5 min)

**En la instancia de Railway: sidebar → Executions.**

> "Cada mensaje del chat es una ejecución, y aquí quedan todas. En local depurábamos mirando el output de cada nodo; en producción se depura AQUÍ. Si mañana alguien os dice 'tu bot no me contestó', este es el primer sitio donde mirar: veréis la ejecución en rojo y exactamente qué nodo falló."

**Abrir una ejecución y enseñar los datos fluyendo por los 3 nodos.**

---

### 8. Cierre (45s)

> "El viaje completo: workflow local → servidor en Railway con un click → WEBHOOK_URL para que las URLs apunten al mundo → credencial en la instancia → Publish → chat público. Cinco pasos, cero código."

- **Publish**: los borradores no existen para el mundo
- **WEBHOOK_URL**: la variable que lo cambia todo (con barra final)
- **Credenciales por instancia**: las claves no viajan
- **Executions**: tu debugger de producción
- **Vale para todo el curso**: cualquier workflow con Chat Trigger o Webhook se despliega igual

> "Y un aviso: URL pública significa que cualquiera puede gastar vuestros tokens. En las variaciones le ponemos contraseña."

---

## 🎬 PARTE 2 — Variaciones (para alargar el vídeo)

Recomendadas: **1 + 2 + 3** (~9 min extra). Colócalas antes del cierre si las grabas.

---

### Variación 1 — ¿Cuánto cuesta esto DE VERDAD? (2 min, sin config)

**Qué enseña:** leer el dashboard de uso de Railway — que el miedo al coste se va con datos.

**Pasos:**
1. En Railway: click en el proyecto → **Usage** (o el estimado de coste del servicio).
2. Enseñar el consumo real tras la demo:

> "Después de todo lo que hemos hecho, mirad el contador: céntimos. n8n parado consume casi nada — pagas sobre todo por tener el servidor encendido, no por ejecución. Comparad con los veinte euros del plan Starter de n8n Cloud: para aprender y para proyectos pequeños, esto es imbatible. Eso sí: los tokens del LLM van aparte, por OpenRouter."

---

### Variación 2 — Ponle contraseña al chat (3 min) 🔒

**Qué enseña:** cerrar el grifo — que "público" no tenga que significar "gratis para todo internet".

**Pasos:**
1. En el workflow desplegado, abre **When chat message received**.
2. **Authentication** → `Basic Auth` → crea una credencial:

| Campo | Valor |
|-------|-------|
| **User** | `demo` |
| **Password** | (una que puedas decir en el vídeo, p. ej. `curso2026`) |

3. **Publish** de nuevo (los cambios en producción se re-publican — otra mini-lección).
4. Abre la Production URL en incógnito → pide usuario y contraseña → entra con `demo`.

> "Ahora la URL se puede compartir en un grupo cerrado sin que un curioso cualquiera os vacíe el crédito de OpenRouter. Para algo serio: rate limiting con un proxy delante — eso ya es capítulo de Guardrails."

**Revertir:** Authentication → None (o déjalo con contraseña, más seguro).

---

### Variación 3 — Un servidor, N workflows (3-4 min)

**Qué enseña:** el servidor no es "del workflow" — es TU plataforma. Desplegar un segundo proyecto del curso cuesta 2 minutos y 0 dólares extra.

**Pasos:**
1. En la instancia de Railway: **Workflows → Import from URL** — copia y pega (el Proyecto 2, Ask Your Data):
   ```
   https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/11_ask_your_data.json
   ```
2. Selecciona tu credencial de OpenRouter en su Chat Model (ya existe en esta instancia — segunda vez que NO hay que crearla: las credenciales son de la instancia, no del workflow).
3. **Publish** → copiar su Production URL → probar:
   ```
   Which song has the most streams?
   ```

> "Mismo servidor, mismos cinco dólares — y ahora tengo DOS productos publicados: un chat genérico y un analista de datos. El coste de Railway es por servidor, no por workflow. Vuestra instancia es una plataforma: cada proyecto del curso que tenga Chat Trigger se publica aquí igual."

**Revertir:** despublica el workflow extra si no lo quieres activo.

---

### Variación 4 — Error Workflow: que los fallos te avisen (4 min)

**Qué enseña:** el nivel 2 de manejo de errores del Appendix B, en producción.

**Pasos:**
1. Crea un workflow nuevo en la instancia: **Error Handler**.
2. Añade un nodo **Error Trigger** (se dispara cuando OTRO workflow falla).
3. Añade un **Edit Fields** → `Format Error Info` con tres campos String:

| Campo | Valor (Expression) |
|-------|--------------------|
| `failed_workflow` | `{{ $json.workflow.name }}` |
| `error_message` | `{{ $json.execution.error.message }}` |
| `execution_url` | `{{ $json.execution.url }}` |

4. Publica el Error Handler.
5. En el workflow del chat: **⋯ → Settings → Error Workflow** → selecciona `Error Handler`.
6. Provoca un fallo (p. ej. rompe temporalmente la credencial del Chat Model escribiendo un carácter de más) → chatea → mira las Executions del Error Handler: ahí está el aviso con el nombre del workflow y el error.
7. **Arregla la credencial.**

> "En producción los fallos son cuándo, no si. Con un Error Workflow, cada fallo de cualquier workflow de la instancia deja un registro estructurado — y en producción de verdad ese Edit Fields sería un mensaje de Slack o un email."

**Revertir:** nada que revertir (deja el Error Handler — es buena práctica).

---

### Variación 5 — Dominio propio (3 min, opcional)

**Qué enseña:** que `tu-app.up.railway.app` puede ser `chat.tudominio.com`.

**Pasos:**
1. Railway: servicio n8n → **Settings → Networking → Custom Domain** → añade `chat.tudominio.com`.
2. En tu DNS: el registro CNAME que Railway te indique.
3. **Actualiza `WEBHOOK_URL`** a `https://chat.tudominio.com/` — ¡la lección del vídeo, otra vez! Si cambias el dominio y no cambias la variable, las URLs nuevas seguirán apuntando al dominio viejo.

> "Requiere tener un dominio (~10€/año). Si no tienes, salta esta — la URL de Railway funciona perfectamente."

---

## 🧪 Textos de prueba (copy-paste para el chat)

```
What is n8n?
```
```
Recommend me 3 books about artificial intelligence
```
```
Explain what a webhook is, in one sentence
```
**En español (para el plano del móvil):**
```
¿Qué es un agente de IA? Explícalo en 2 frases
```
**Para la variación 3 (Ask Your Data):**
```
Which song has the most streams?
```

---

## ⚠️ Cosas a tener en cuenta durante la grabación

1. **⚠️ API keys en pantalla:** es un vídeo de deploy — vas a pegar credenciales. Pégalas fuera de grabación o difumina en edición. Revisa el material ANTES de publicar el vídeo.
2. **La URL de tu instancia queda expuesta** en el vídeo. Plan: borrar el proyecto de Railway tras grabar (Settings → Danger → Delete project), o dejarlo con la contraseña de la variación 2 y límites de gasto en OpenRouter.
3. **Precios = "a fecha de grabación":** di las cifras con esa coletilla y enseña las páginas de pricing en vez de fiarte de memoria ([railway.com/pricing](https://railway.com/pricing), [n8n.io/pricing](https://n8n.io/pricing/)). Verificado 2026-07-05: Railway $5 Hobby + $5 trial; n8n Cloud €20 anual / €24 mensual.
4. **La URL de la plantilla es [railway.com/deploy/n8n](https://railway.com/deploy/n8n)** — la vieja `/template/n8n` da 404 (ya corregida en el notebook).
5. **El deploy tarda 2-3 min:** ten preparado el relleno de la sección 3 (qué está montando Railway + el precio). No cortes el clip: la espera real da credibilidad.
6. **UI de Railway cambia a menudo:** nombra funciones ("la pestaña Variables del servicio"), no posiciones. Si tu pantalla difiere del guion, di la función y búscala en directo con naturalidad.
7. **Haz el ensayo la víspera** con un proyecto desechable y bórralo — así el día de grabación Railway no te sorprende con pantallas nuevas de onboarding.
8. **Si el chat público no responde:** el 90% de las veces es (a) workflow sin publicar o (b) `WEBHOOK_URL` sin la barra final o sin poner. Son LAS dos lecciones del vídeo — si te pasa en directo, úsalo como momento didáctico.
