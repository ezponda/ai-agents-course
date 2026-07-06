# Guion — Project 3: AI Expense Assistant (workflow `12_expense_assistant.json`)

## Concepto
Le has dado al agente **herramientas** (P1) y un **intérprete de código** (P2). Ahora le das **ojos.**
Sueltas la **foto de un recibo** en el chat y el agente lo **lee** (comercio, fecha, importe, categoría), comprueba que se ve bien, que no es un duplicado y que cumple la política, y lo **registra** — hablándote si algo está mal ("no leo el total, súbela más clara" / "esto parece un duplicado, ¿lo registro?").
**La capacidad nueva:** entrada **multimodal**. Y es un agente de verdad: **ve**, **decide** qué herramienta usar (buscar duplicados / guardar) y **conversa**.

## Flujo del workflow
```
When chat message received ──▶ Expense Agent ──▶ (responde en el chat)
 (Chat Trigger, uploads ON)   (ve la foto, comprueba, registra)
                                    ┊ sub-nodos
                    ┌───────────────┼──────────────┬───────────────┐
               Chat Model        Memory      Find Similar      Log Expense
              (multimodal)                  (Data Table get)  (Data Table insert)
```
**Requisitos:** OpenRouter con modelo **multimodal** (`gpt-4o-mini`) + **n8n 1.113+**. Sin Google/Gmail.

---

## 🗺️ Los nodos de un vistazo (léelo primero)

Al importar el workflow, **ya está todo conectado**. Esto es lo que hay:

| Nodo | Qué es |
|------|--------|
| **When chat message received** | La entrada: el usuario sube la foto y escribe |
| **Expense Agent** | El cerebro: ve la foto y decide qué hacer |
| **OpenRouter Chat Model** | El modelo con "ojos" (multimodal) |
| **Simple Memory** | Recuerda la conversación (re-subir, confirmar) |
| **Find Similar Expenses** | **LEE** la tabla → busca duplicados |
| **Log Expense** | **ESCRIBE** en la tabla → guarda el gasto |

La **tabla `expenses`** (la creas tú) = la libreta donde se guardan los gastos. **Find Similar** y **Log Expense** NO son dos tablas: son dos nodos que usan **esa misma tabla** (uno lee, otro escribe).

**Solo tienes que hacer 2 cosas para que funcione** (todo lo demás ya viene cableado): **(1)** crear la tabla `expenses`, **(2)** poner tu modelo en OpenRouter Chat Model. Ambas están abajo, en Preparación.

---

## 🔧 Preparación ANTES de grabar (checklist)

1. **Importa** el workflow (Import from URL): `https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/12_expense_assistant.json`
2. **🔴 CREA LA TABLA (obligatorio, una sola vez).** Las Data Tables NO viajan en el JSON — viven en tu n8n, así que hay que crearla:
   - **Overview → pestaña Data Tables → Create Data Table.**
   - Nombre **exactamente** `expenses` (minúsculas).
   - 6 columnas, **todas tipo String**: `vendor` · `expense_date` · `total` · `currency` · `category` · `status`.
   - Los nodos **Find Similar** y **Log Expense** ya apuntan a ella **por nombre** → NO hay que seleccionar nada. **Si no la creas, esos dos nodos salen en rojo** ("Data table not found").
3. **Modelo multimodal** en OpenRouter Chat Model: `openai/gpt-4o-mini` (lee imágenes). Con un modelo de solo texto NO ve nada.
4. **Ya activado en el JSON:** *Allow File Uploads* (Chat Trigger → Parameters → Options) y *Automatically Passthrough Binary Images* (agente → Options). Confírmalo si quieres.
5. **Los 4 recibos** están en el repo → ábrelos con `open courses/n8n_no_code/book/_static/data/receipts/` y déjalos a mano: `receipt_cafe_valid.png`, `receipt_cafe_duplicate.png`, `receipt_incomplete.png`, `receipt_dinner_policy.png`.
6. **Ejecución de prueba** con el café válido para calentar.

> ⚠️ **Cómo se envía una foto en el chat de n8n:** NO puedes mandar solo el archivo. Tienes que **adjuntar la imagen (clip 📎) Y escribir una línea de texto** (aunque sea "aquí tienes") y pulsar Enviar. El agente ignora ese texto y trabaja con la imagen.

## 🔗 URLs para tener a mano

| Para qué | URL |
|----------|-----|
| n8n docs — Chat Trigger (file uploads) | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/ |
| n8n docs — AI Agent | https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/ |
| n8n docs — Data Tables | https://docs.n8n.io/data-tables/ |
| OpenRouter (modelos multimodales) | https://openrouter.ai/models |

---

# 🎬 GUION DE GRABACIÓN (de arriba abajo)

## 0 · (Opcional) Cold open — el gancho (20s)
> Grábalo al final. En pantalla: una foto de recibo ya soltada en el chat y la respuesta "Registrado: Café Central, 12,40 € (Meals) ✅".
- **Di:** *"He soltado la foto de un recibo en un chat y se ha registrado solo — comercio, fecha, importe, categoría. Sin teclear nada. El agente lo ha LEÍDO. Vamos a montarlo."*

## 1 · La idea: le damos ojos (1.5 min)
- **Di:** *"Hasta ahora el agente usaba herramientas y escribía código. Hoy le damos **ojos**: un modelo multimodal que lee imágenes. Y el caso perfecto son los recibos — porque un recibo es una FOTO, y teclear los datos a mano es justo el rollo que queremos quitar."*
- **Di (por qué chat y no formulario):** *"¿Por qué un chat y no un formulario de subir archivo? Porque un formulario es de un solo tiro: no te puede decir 'oye, esta foto está borrosa, súbela otra vez' ni '¿seguro? esto parece un duplicado'. Un agente con memoria SÍ — ve, juzga, te habla, y tú resuelves en la misma conversación."*

## 2 · El Chat Trigger que acepta fotos (45s)
- **[Click en `When chat message received` → Options]**
- **Di:** *"El Chat Trigger de siempre, con una opción clave: **Allow File Uploads**. Con eso, en el chat aparece un clip para adjuntar. La foto que subes llega al workflow como **binario**."*

## 3 · El agente que ve (2.5 min)
- **[Click en `Expense Agent` → Options]**
- **Di (la opción que da los ojos):** *"Aquí está la magia, y es un solo toggle: **Automatically Passthrough Binary Images**. Si el mensaje trae una imagen, el agente la reenvía al modelo. No hay nodo de OCR, no hay que parsear nada — el agente lee el recibo como lo leerías tú. Eso sí: el Chat Model tiene que ser **multimodal** (gpt-4o-mini vale; uno de solo texto no ve nada)."*
- **[Options → System Message]** — recórrelo como un checklist:
  1. **LEER:** comercio, fecha, total, moneda, categoría.
  2. **VALIDAR:** *"si no puedes leer el total o el comercio, NO lo registres — di qué falta y pide una foto mejor."* ← el camino de "vuelve a subirla".
  3. **DUPLICADOS:** *"llama a Find Similar con el comercio; si hay una con misma fecha e importe, pide confirmación."*
  4. **POLÍTICA:** *"comidas >50 piden justificación; alcohol no se reembolsa; >200 va a revisión → status review."*
  5. **REGISTRAR:** *"solo cuando esté limpio, llama a Log Expense y confirma en una línea."*
- **Di:** *"Fijaos: no hay ningún truco de 'saca exactamente una palabra'. El agente habla normal, y los datos estructurados viajan en la **llamada a la herramienta** de registrar."*

## 3b · ¿Qué es una Data Table? (y crea la tuya) 🗄️

> Es la **primera vez** que aparecen en el curso (en P7 se usan a lo grande). Aquí toca **entender qué son** y **crear la tabla**. Los dos nodos que la usan (Find Similar / Log Expense) los detallamos uno a uno en la **sección 4** — que no son dos tablas: son dos nodos que usan **la misma** tabla.

**Qué es una Data Table (dilo):**
> *"Una Data Table es una **tabla de base de datos que vive DENTRO de n8n**. Filas y columnas, como una hoja de cálculo — pero pensada para que los nodos la lean y escriban. Y lo importante: **persiste**. Aunque cierres el workflow o reinicies n8n, los datos siguen ahí. Es la libreta donde el agente va apuntando los gastos."*

**Características (menciónalas):**
- Tú defines las **columnas** y su **tipo** (Texto, Número, Booleano, Fecha). Nosotros usamos **todo Texto** por simplicidad.
- Cada fila insertada recibe un **`id` automático**.
- Se lee y escribe con nodos **Data Table**, que además pueden ser **herramientas de un agente** — justo lo que hacemos: *Find Similar* lee, *Log Expense* escribe.

**Por qué ESTO y no otra cosa (la parte que da criterio):**

| | Google Sheets / Airtable | Base de datos real (Postgres…) | **Data Tables de n8n** |
|---|---|---|---|
| Credenciales | OAuth de Google / API key | Servidor + conexión | **Ninguna** |
| Montaje | Cuenta externa | Instalar / hostear | **Cero — ya está en n8n** |
| Persiste (reinicios) | Sí | Sí | **Sí** |
| Para el alumno | En otra app | Técnico | **En la misma pantalla de n8n** |

> *"Podríamos guardar los gastos en Google Sheets, pero eso pide conectar tu cuenta de Google. O en una base de datos de verdad, pero eso es montar un servidor. Las Data Tables son el punto dulce: **cero credenciales, cero montaje, y persisten** — perfectas para 'la pequeña base de datos de una app'."*

**Lo honesto (limitaciones, dilo):** *"No son para millones de filas ni para consultas complejas con joins, y no se leen desde un nodo Code. Para eso irías a una BD de verdad. Pero para gastos, citas o un registro, van sobradas."*

**Crear la tabla (solo una vez):**

1. Barra lateral izquierda → **Overview** → abajo, pestaña **Data tables** → botón **Create Data Table**.
2. En el diálogo *Create new data table*: **Data table name** = `expenses` (minúsculas). Ahora eliges cómo poner las columnas:

   **⚡ Rápido (recomendado) — Import CSV:** marca **Import CSV**, sube `expenses_template.csv` (en el repo, `_static/data/`) → te crea las **6 columnas de golpe** → **Create**.

   **✋ A mano — From scratch:** marca **From scratch** → **Create** → luego **Add Column** seis veces, todas **String**: `vendor` · `expense_date` · `total` · `currency` · `category` · `status`.

3. **Listo — para siempre** (se guarda sola).

> ✅ **Comprueba:** vuelve al workflow → abre **Find Similar Expenses** → el rojo *"Error fetching options"* ha **desaparecido** y en **Column** ya puedes elegir `vendor`. Ese error solo salía porque la tabla no existía; los nodos la encuentran por su nombre.

> *"Y fijaos: NO hay que tocar los nodos. Find Similar y Log Expense ya apuntan a la tabla `expenses` por su nombre — con crearla, se conectan solos."*

> 💡 Si ya la creaste en la preparación, aquí solo la **enseñas** ya hecha y explicas. Si quieres el momento "crear en vivo" a cámara, bórrala antes y recréala aquí.

---

## 4 · Los dos nodos + qué ves al ejecutar (2 min)

Los dos usan la **misma tabla `expenses`** — uno LEE, otro ESCRIBE.

### 🔍 Find Similar Expenses — LEE (detecta duplicados)
- **Qué hace:** consulta la tabla filtrando por comercio (operación *Get*).
- **Cuándo se dispara:** cuando el agente quiere saber si ese gasto ya existe.
- **Qué ves al ejecutar:** en **Expense Agent → Logs**, una llamada a *Find Similar Expenses* con el `vendor` que buscó y, debajo, las filas que devolvió (vacío si no hay).
- **Di:** *"Antes de guardar, el agente mira en la tabla: '¿tengo algo de este comercio?'. Detecta duplicados con datos reales, no adivinando."*

### 💾 Log Expense — ESCRIBE (guarda el gasto)
- **Qué hace:** inserta una fila nueva (operación *Insert*); el agente rellena cada columna con `$fromAI()`.
- **Cuándo se dispara:** solo cuando el recibo es válido, no duplicado y con la política resuelta.
- **Qué ves al ejecutar:** en los Logs, la llamada a *Log Expense* con los valores (vendor, total…); y en **Data tables → `expenses`**, una **fila nueva**.
- **Di:** *"Este apunta el gasto. Las columnas son `$fromAI()` → el agente las rellena con lo que leyó en la foto. La llamada a la tool ES la salida estructurada, sin ningún parser."*

> **La imagen mental:** una libreta (`expenses`) y dos manos — una mira si ya está apuntado (Find Similar), la otra lo apunta (Log Expense).

## 5 · DEMO — los cuatro recibos, paso a paso (4-5 min)

**Cómo enviar CADA recibo (repetirás estos 3 gestos):**
1. Pulsa **Open chat** (en el Chat Trigger o el botón de chat del editor).
2. Pulsa el **clip 📎** → elige el archivo del recibo.
3. Escribe la **línea de texto** (copia-pega abajo) y pulsa **Enviar**.
> Recuerda: n8n **exige texto**, no puedes mandar solo la foto. La frase da igual; el agente trabaja con la imagen.

Hazlo **todo en la misma sesión de chat** (así la memoria recuerda el café para detectar el duplicado). Entre paso y paso, abre **`Expense Agent → Logs`** para enseñar que ha leído la imagen y qué herramienta ha llamado.

---

### Recibo 1 · Limpio → se registra ✅
**Adjunta** `receipt_cafe_valid.png` y **escribe:**
```
Aquí tienes un recibo
```
**Qué pasa:** lo lee (Café Central, 12,40 €), llama a *Find Similar* (no hay nada), sin flags → llama a *Log Expense*. Responde algo como *"Registrado: Café Central, 12.40 EUR (Meals) ✅"*.

**Enseña:** abre la pestaña **Data Tables → `expenses`** → la fila está ahí.
> **Di:** *"He soltado una foto y se ha registrado sola: comercio, fecha, importe, categoría. Sin teclear un dato. El agente ha LEÍDO la imagen. Miradlo en los Logs: ahí está el recibo que ha visto y la llamada a Log Expense."*

---

### Recibo 2 · El mismo otra vez → duplicado 🟡
**Adjunta** `receipt_cafe_duplicate.png` y **escribe:**
```
Y este otro
```
**Qué pasa:** llama a *Find Similar* con "Café Central", ve la fila de antes (misma fecha e importe) y **te pregunta** antes de guardar: *"Esto parece un duplicado del recibo de Café Central del 2026-03-12 (12,40 €). ¿Lo registro igual?"*

**Tú respondes (copia-pega):**
```
No, no lo registres
```
**Qué pasa:** no lo guarda.
> **Di:** *"Fijaos: no lo ha metido a ciegas. Ha mirado en la tabla, ha visto que ya existía, y me ha preguntado. Eso es memoria + una herramienta de lectura. Un formulario nunca podría."*

---

### Recibo 3 · Ilegible → te pide otra foto 🔴
**Adjunta** `receipt_incomplete.png` y **escribe:**
```
Otro gasto
```
**Qué pasa:** no ve el total (está tachado) → **no se inventa un cero**. Responde algo como *"No consigo leer el importe total de este recibo, ¿me puedes enviar una foto más clara?"*.
> **Di:** *"Este es el momento clave. En vez de guardar basura, el agente para y me pide una foto mejor. Ese ida y vuelta — 'esto está mal, súbela otra vez' — es justo por lo que necesitamos un chat con memoria y no un formulario."*

---

### Recibo 4 · Rompe política → a revisión 🟠
**Adjunta** `receipt_dinner_policy.png` y **escribe:**
```
Cena de trabajo
```
**Qué pasa:** 85 € (comida > 50) **y** lleva vino (alcohol) → lo marca y **te pide una justificación**: *"Esta comida supera el límite de 50 € e incluye alcohol. ¿Me das una breve justificación? La registraré para revisión."*

**Tú respondes (copia-pega):**
```
Cena con un cliente para cerrar el contrato
```
**Qué pasa:** lo registra con **status `review`** (no approved).

**Enseña:** la tabla `expenses` → esa fila con `status = review`.
> **Di:** *"La política, aplicada sola: importe alto + alcohol → no lo aprueba, pide contexto y lo deja marcado para que una persona lo revise."*

---

> **🎁 Wow extra (opcional):** saca una foto a un recibo REAL con el móvil y súbela con un `Aquí va otro`. Lee manuscritos, monedas raras y papel arrugado sorprendentemente bien — ahí se ve que no es un truco con imágenes preparadas.

---

## 6 · 🧭 De dónde vive cada cosa (mapa mental, 1 min)

| Comportamiento | Dónde vive |
|----------------|-----------|
| Ver la foto | **Modelo multimodal** + toggle **Passthrough Binary Images** del agente |
| Leer, validar, política, cuándo pedir re-subida | **System prompt** del agente |
| Detectar duplicados (dato exacto) | **Data Table** (Find Similar) — no el prompt |
| Guardar el gasto (datos estructurados) | **Log Expense** con `$fromAI()` |
| Que la conversación fluya (re-subir, confirmar) | **Simple Memory** |

> **Regla:** el modelo ve, el prompt decide, la tabla recuerda y garantiza, la memoria mantiene la charla.

---

## 7 · Cierre (30s)
- **Multimodal** — el agente lee una foto directamente, sin OCR
- **Chat con memoria** — puede pedirte re-subir o confirmar; un formulario no
- **Decide qué tool usar** — buscar duplicado / registrar → es un agente
- **`$fromAI()`** — la llamada a la herramienta ES la salida estructurada
- **Garantías en la BD, no en el prompt** — el duplicado es un lookup exacto

---

## 📋 Análisis del prompt (y mejoras, 2 min)
**Bien:** procedimiento numerado (leer→validar→dedup→política→registrar) que mantiene a raya a un modelo hablador; el "no registres si no lo lees" (re-subida); "solo una vez Log Expense".
**Mejoras:** un **ejemplo** de cada caso (válido / ilegible / duplicado) clavaría el criterio; `category` podría cerrarse con un JSON Schema si quieres categorías fijas; la comparación de duplicado la hace el modelo sobre las filas devueltas — para máxima fiabilidad, podrías filtrar también por fecha+total en la tool.
> **Meta-punto:** reglas para lo binario (política, re-subir), ejemplos para lo sutil, y las garantías duras (el lookup de duplicados) fuera del prompt.

---

# 🎬 PARTE 2 — Variaciones (para alargar el vídeo)

> Cada variación es una receta corta: **qué nodo tocar → abrirlo → qué cambiar.** Los nombres en `código` son los nodos tal cual salen en el canvas.

## Variación 1 — "Pregunta a tus gastos" (4 min) ⭐

**Qué logras:** el mismo asistente **captura** recibos (subes foto) Y **responde** preguntas ("¿cuánto llevo en Meals?").

> **Ojo (dos trampas):** al copiar `Log Expense` heredas su descripción ("Adds one expense row…"), que es de **escritura** → hay que **reescribirla** para lectura o el agente no sabe qué hace. Y **no filtres por categoría**: un filtro `equals` exacto falla con "total" y con cualquier diferencia de mayúsculas. Devuelve **todas** las filas y deja que el agente sume.

- **1.** Copia el nodo `Log Expense` (clic → Ctrl+C → Ctrl+V) y renómbralo `List Expenses`.
- **2.** Ábrelo → **Operation:** `Insert Row` → **`Get Row(s)`**, y **deja el filtro vacío** (que devuelva todas las filas).
- **3.** **Reescribe la Description** (esto es lo que lee el agente) — pega:

```
Look up expenses already saved. Returns ALL expense rows (vendor, expense_date, total, currency, category, status). Use it whenever the user asks how much they have spent — a grand total, a total by category, a count or a list. Do the adding/filtering yourself from the rows returned.
```

- **4.** **Settings** (pestaña de arriba) → activa **Always Output Data** (si la tabla está vacía, devuelve `[]` en vez de parar el flujo).
- **5.** Conéctalo al `Expense Agent` (arrastra desde el punto de **tools**, línea punteada, como las otras).
- **6.** Abre `Expense Agent` → **System Message** y añade al final:

```
If the user asks about their spending (a total, a category total, a count or a list), call List Expenses to fetch all saved rows, then compute the answer yourself.
```

- **7.** **Di:** *"Cierra el círculo: construyes los datos VIÉNDOLOS y los consultas HABLANDO."*

> **Si responde "no tienes gastos":** revisa en **Overview → Data tables → `expenses`** que hay filas y con qué `category` se guardaron. El filtro exacto por texto era justo lo que fallaba; por eso aquí devolvemos todo.

## Variación 1B — Gasto entre fechas (2 min) 📅

**Qué logras:** *"¿cuánto gasté en marzo de 2026?"* o *"entre el 1 y el 15 de abril"*.

> **No hace falta ningún nodo nuevo.** Como `List Expenses` (Variación 1) ya devuelve **todas** las filas, solo hay que decirle al agente que puede filtrar por fecha. Las fechas se guardan como `YYYY-MM-DD` (p.ej. `2026-03-12`), así que ordenan bien como texto: **todo marzo de 2026 empieza por `2026-03`**.

- **1.** Abre `Expense Agent` → **System Message** y añade:

```
You can also answer by date range. expense_date is YYYY-MM-DD. For "March 2026" use rows from 2026-03-01 to 2026-03-31; for a custom range use the from/to dates the user gives. Sum only the rows inside the range.
```

- **2.** *(Opcional)* añade la misma pista al final de la **Description** de `List Expenses`: *"…also supports totals for a date range (dates are YYYY-MM-DD)."*
- **3.** **Prueba:** *"¿Cuánto gasté en marzo de 2026?"* → *"¿y entre el 10 y el 20 de marzo?"*
- **4.** **Di:** *"Como el agente ya tiene todas las filas, filtrar por fecha es solo pedírselo — sin tocar el workflow."*

> **Para una tabla grande:** convierte `expense_date` a columna **Date** y filtra en el propio nodo con `>=` / `<=` usando `$fromAI('from')` y `$fromAI('to')`, así no traes todo. Para el curso, filtrar en el agente es más simple y fiable.

## Variación 2 — Botones de Aprobar/Rechazar (HITL real) (6 min) 🛡️

**Qué logras:** un humano aprueba los gastos `review` **antes** de guardarlos; los limpios pasan solos.

> **Clave (importante):** para poder ramificar por `status` necesitas que el agente devuelva **datos estructurados**, no solo texto. Sin parser, `$json.output` es la frase de respuesta y `.status` **no existe**. Así que añades un **Structured Output Parser** (el mismo patrón del Proyecto 1) y sacas el guardado del agente a un nodo aparte.

- **1.** Al `Expense Agent` activa **Require Specific Output Format** y conéctale un **Structured Output Parser** (sub-nodo, línea punteada) con un **JSON de ejemplo**:

```
{ "reply": "Te registro el café de Café Central.",
  "status": "approved",
  "vendor": "Café Central", "expense_date": "2026-03-12",
  "total": 12.40, "currency": "EUR", "category": "Meals" }
```

`status` será `approved` o `review`. Ahora `$json.output` es un **objeto** → ya existe `$json.output.status`.

- **2.** En el **System Message**: el agente ya **no guarda** — quita Log Expense del flujo; solo decide y rellena esos campos. (Deja `Find Similar Expenses`: sigue detectando duplicados.)
- **3.** Detrás del agente añade un nodo **IF** → condición:

```
{{ $json.output.status }}   equals   review
```

- **4.** Rama **true** (review) → **Chat · Send and Wait for Response (Approval)** con botones **Aprobar / Rechazar** (el de la variación HITL de P1).
- **5.** **Aprobar** → **Data Table · Insert Row** en `expenses`, mapeando los campos desde `$json.output` (vendor, total…). **Rechazar** → no guarda.
- **6.** Rama **false** (approved) → directo a **Data Table · Insert Row**.
- **7.** **Di:** *"El agente decide y estructura; la persona solo toca lo dudoso, y el guardado vive fuera del agente. Human-in-the-loop de verdad."*

## Variación 3 — Digest semanal (5 min)

**Qué logras:** cada lunes te llega un resumen de los gastos en `review`.

- **1.** Crea un **workflow NUEVO** (no toques este).
- **2.** **Schedule Trigger** → Interval `Weeks` · día `Monday` · hora `8`.
- **3.** **Data Table · Get Row(s)** sobre `expenses` → filtro `status` `equals` `review`.
- **4.** *(Opcional)* un **agente / Edit Fields** que redacte el resumen de esas filas.
- **5.** **Send Email (SMTP)** o **Telegram** → a finanzas.
- **6.** **Di:** *"El Proyecto 4 va justo de esto: agentes que trabajan solos con un horario."*

## Variación 4 — Facturas en PDF (3 min)

**Qué logras:** acepta PDFs de factura, no solo fotos.

- **1.** Abre `Expense Agent` → **Options**.
- **2.** Activa **`Automatically Passthrough Binary PDFs`** (va genial con Gemini).
- **3.** Sube un **PDF** de factura en el chat (mismo clip) → extrae los mismos campos.
- **4.** **Di:** *"Misma tubería, ahora también con documentos, no solo con fotos."*

## Variación 5 — Tu propia política (3 min, solo prompt)

**Qué logras:** adaptar las reglas a un equipo real **sin añadir ni un nodo**.

- **1.** Abre `Expense Agent` → **System Message**.
- **2.** Reescribe la sección de **política**: límites por categoría, campos obligatorios, comercios permitidos.
- **3.** **Prueba** cada regla con un recibo (edita uno de muestra o usa uno tuyo).
- **4.** **Di:** *"Toda la política vive en el prompt: cámbiala y cambia el comportamiento, sin tocar el workflow."*

---

## 🧪 Recibos de prueba (en el repo, `_static/data/receipts/`)
- `receipt_cafe_valid.png` — Café Central, 12,40 € → **approved**
- `receipt_cafe_duplicate.png` — idéntico → **duplicado** (pide confirmar)
- `receipt_incomplete.png` — sin total → **pide re-subir**
- `receipt_dinner_policy.png` — 85 € + vino → **review**

---

## ⚠️ Avisos de grabación
1. **Modelo multimodal obligatorio:** con un modelo de solo texto el agente "no ve" nada y se lo inventa. `gpt-4o-mini` funciona.
2. **La tabla `expenses` creada** (por nombre, 6 columnas String) antes de grabar, o Log Expense/Find Similar fallan.
3. **El orden de la demo importa:** el válido primero (crea la fila) para que el duplicado luego se detecte.
4. **La pantalla clave es `Expense Agent → Logs`:** ahí se ve que ha leído la imagen y ha llamado a las tools.
5. **Sesión de chat:** la re-subida y la confirmación del duplicado dependen de la memoria — hazlas en la misma conversación.
6. **Coste:** cada foto es una llamada con imagen (un pelín más cara que texto), pero con gpt-4o-mini es barato. Pon Max Iterations 5-10 si compartes la URL.
