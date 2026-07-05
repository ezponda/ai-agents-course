# Guion — Project 1: Recipe Assistant (workflow `10_recipe_assistant.json`)

## Concepto clave
Un asistente de recetas conversacional montado en n8n sin código. Lo importante no es la receta: es el **patrón**. El agente:
1. busca recetas reales en internet (API pública + Google de fallback),
2. propone **UNA** receta y te deja **refinarla hablando** ("otra", "más occidental"),
3. y cuando confirmas, un **segundo agente** monta la lista de la compra con precios reales.

La pieza que lo une y que quiero que quede grabada: **el agente devuelve un JSON pequeño en cada turno** (`reply`, `recipe`, `build_shopping_list`) y un nodo **IF** lee ese JSON para decidir el camino. El LLM no solo "responde": **dirige la lógica del workflow**.

## Flujo del workflow
```
                       output = { reply, recipe, build_shopping_list }
                                    │
Chat Trigger ─▶ Recipe Agent ─▶ Want Prices? (IF) ──true──▶ Shopping List Agent ─▶ Reply — With Prices
 (lastNode)   (+ Output Parser)        │                          ┊
        ┌────────┬─────┬─────┬──────┐  └────false────▶ Reply — Recipe Only
   Chat Model  Memory HTTP Google Output                (muestra el 'reply')
                    (MealDB)(fallb.) Parser
```

**Credenciales necesarias:** OpenRouter + SerpAPI

**Idea de fondo:** cada mensaje del chat lanza el workflow entero **una vez**. La conversación se sostiene con la **memoria**. Mientras eliges o refinas, `build_shopping_list` va en `false` y solo se te responde; cuando confirmas y pides precios, se pone en `true` y se dispara el segundo agente.

---

## 🔗 URLs para tener a mano (abrir en pestañas antes de grabar)

| Para qué | URL |
|----------|-----|
| **TheMealDB — documentación de la API** (enséñala) | https://www.themealdb.com/api.php |
| **TheMealDB — búsqueda de ejemplo** (enséñala en el navegador) | https://www.themealdb.com/api/json/v1/1/search.php?s=chicken |
| TheMealDB — receta aleatoria (Variación) | https://www.themealdb.com/api/json/v1/1/random.php |
| **SerpAPI — dashboard** (cuota antes de grabar) | https://serpapi.com/dashboard |
| OpenRouter — modelos y créditos | https://openrouter.ai |
| n8n docs — **Structured Output Parser** | https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.outputparserstructured/ |
| n8n docs — Chat Trigger | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/ |
| n8n docs — HTTP Request Tool | https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolhttprequest/ |

> 💡 **Tip:** abre `search.php?s=chicken` en el navegador y enseña el JSON crudo 5 s. Así el alumno **ve** de dónde salen los datos — no es magia, es una API pública que devuelve JSON.

---

## 🔧 Preparación ANTES de grabar

1. **Chat Trigger:** ábrelo y confirma **Options → Response Mode = When Last Node Finishes** (lo explicas en la sección 2). Es el modo por defecto, pero verifícalo.
2. **Cuota SerpAPI:** entra en https://serpapi.com/dashboard — cada demo con lista de compras gasta 1-2 búsquedas.
3. **Ejecución completa de prueba** (buscar → refinar → confirmar → lista): calienta el flujo y confirma credenciales.
4. **TheMealDB vivo:** abre `search.php?s=chicken` — te evita descubrir en directo que la API está caída.
5. **Durabilidad — modelos:** no te recrees en `gpt-4o-mini` a cámara; di "un modelo rápido y barato — el que tengáis". Los nombres caducan antes que el vídeo.
6. **Durabilidad — UI:** nombra funciones, no posiciones ("el botón **Open Chat** del editor"). Verifica nombres de nodo en TU versión (memoria = **Simple Memory**; antes *Window Buffer Memory*).

---

## 🧠 Bloque teórico OBLIGATORIO — Los modos del Chat Trigger (3-4 min)

> Esta sección es la que más valor da al vídeo. Explícala **antes** de la demo, con el nodo abierto a cámara. Es un concepto que confunde a TODO el mundo y casi nadie lo explica bien.

### Primero: el modelo de ejecución (dibújalo)

> "Lo primero que hay que entender de un chat en n8n: **cada mensaje que escribes lanza el workflow ENTERO, de arriba abajo, una vez.** No es una ejecución larga que dura toda la conversación. Son muchas ejecuciones cortas, una por mensaje, **pegadas por la memoria**."

**Dibuja esto en pantalla o en una diapo:**
```
Mensaje 1  →  [ejecución completa]  →  respuesta 1
Mensaje 2  →  [ejecución completa]  →  respuesta 2   (la memoria le recuerda el mensaje 1)
Mensaje 3  →  [ejecución completa]  →  respuesta 3
```

> "Esto es clave para entender por qué el agente devuelve su JsON de control **en cada turno**: porque en cada turno el IF tiene que decidir de nuevo."

### Segundo: ¿dónde se toca? (enséñalo)

**Abre el Chat Trigger → Options → Response Mode.** Despliega el dropdown a cámara.

> "Aquí, en Options del Chat Trigger, está **Response Mode**. Define **cómo y cuándo** el chat te responde. Hay tres opciones, y elegir bien es la diferencia entre que funcione y que no."

### Tercero: las tres formas de responder un chat (tabla visual)

| Modo | Qué hace | Qué nodos necesitas | Cuándo usarlo | Pega / cuidado |
|------|----------|--------------------|--------------|----------------|
| **When Last Node Finishes** (`lastNode`) — **el que usamos** | El chat muestra lo que el **último** nodo ponga en el campo `output` | Ninguno extra. El último nodo DEBE emitir `{ output: "..." }` | Cuando **post-procesas** la respuesta: ramificar, reshapear, correr un 2º agente | Si un nodo se queda colgado esperando (p. ej. un formulario), la conexión caduca a los ~90 s |
| **Streaming** (`streaming`) | El agente **escribe la respuesta directa** en el chat, palabra a palabra, tipo ChatGPT | Ninguno; el agente es el nodo final | Cuando la respuesta **cruda** del agente ES el mensaje final | No puedes tocar la respuesta después. No sirve si el agente devuelve JSON que hay que enrutar |
| **Using Response Nodes** (`responseNodes`) | **Nada** llega al chat salvo que tú lo mandes con un nodo **Chat** | 1 o más nodos **Chat** (Send / Send & Wait) | Cuando quieres control total: **aprobación con botones**, varios mensajes, HITL | Más nodos, y es lo más **nuevo** (menos veterano) |

### Cuarto: por qué en ESTE proyecto usamos `lastNode`

> "Nosotros usamos **When Last Node Finishes**. ¿Por qué? Porque el agente NO devuelve el mensaje final directamente: devuelve un **JSON** que todavía tenemos que **enrutar** con el IF, y a veces pasar por un segundo agente. Necesitamos **post-procesar** antes de decidir qué mostrar. Por eso:
> - **Streaming NO vale**: escribiría el JSON crudo en el chat. Streaming solo sirve cuando la respuesta del agente es, tal cual, lo que quieres mostrar.
> - **Response Nodes sería overkill** aquí: no necesitamos botones ni varios mensajes. Lo veremos en una variación, para cuando SÍ quieras una aprobación con botones.
>
> Con `lastNode`, la regla es simple: **el último nodo que se ejecute tiene que dejar el texto en un campo llamado `output`**, y eso es lo que ve el chat. Por eso las dos ramas terminan en un nodo Set que escribe `output`."

**Dato de durabilidad (dilo):** "`When Last Node Finishes` es el modo más antiguo y estable de n8n — lleva ahí desde el principio. Streaming y Response Nodes son más recientes. Para algo que quiero que dure, tiro de lo veterano."

**(Opcional) El otro ajuste, `Mode`:** "Ojo, no confundir con **Mode**, justo arriba: `Hosted Chat` (el chat que hospeda n8n, el que usamos) vs `Embedded Chat` (para embeberlo en tu web). Eso es *dónde* vive el chat; Response Mode es *cómo* responde."

---

## 🎬 PARTE 1 — Guion paso a paso (comentando el workflow importado)

### 0. Cold open (opcional, 40s)

**Empieza con una conversación ya hecha en pantalla: propuesta de receta → "dame otra" → receta nueva → "sí, con la lista" → lista con precios.**

> "Esto es un asistente de recetas en n8n, sin código. Le pido pollo, me propone una receta; le digo que quiero otra más occidental, me la cambia; y cuando digo que sí, me monta la lista de la compra con precios reales de Google. Todo hablando, en un chat. Vamos a verlo por dentro."

---

### 1. Introducción — Qué vamos a construir (45s)

> "Este es el Project 1: el proyecto que junta casi todo. Seis piezas: un **agente** con herramientas, **memoria**, una **herramienta HTTP** que llama a una API de recetas, una **estrategia de fallback** a Google, **salida estructurada en JSON** que dirige la lógica, y un **segundo agente** para los precios. Lo recorremos nodo a nodo."

**Abre el workflow y haz zoom out. Señala: buscar/proponer → IF → lista.**

---

### 2. Chat Trigger (ya explicado en el bloque teórico, 20s)

**Click en "When chat message received".**

> "Ya hemos hablado de esto: es la entrada del chat, en modo **When Last Node Finishes**, porque vamos a post-procesar la respuesta del agente. Recordad: el último nodo tiene que dejar el texto en `output`."

---

### 3. Recipe Agent — El cerebro (4 min)

**Click en "Recipe Agent". Señala las 5 conexiones de abajo: Chat Model, Memory, Recipe Search, Google Search y — la nueva — el Output Parser.**

> "Este agente tiene cinco cosas conectadas por debajo. Cuatro ya las conocéis; la quinta, el **Output Parser**, es la novedad del proyecto."

#### 3a. System Message

**Click en Options → System Message.** Recórrelo:

1. **Traducción a inglés:** "Convierte la petición a inglés antes de buscar — TheMealDB solo entiende inglés. 'quiero pollo' → busca 'chicken'."
2. **Fallback:** "Primero TheMealDB; solo Google si devuelve `meals: null`."
3. **UNA receta y conversación:** "Fíjate en esta regla: 'presenta UNA sola receta, nunca una lista', y 'después pregunta siempre si quiere esta, otra, o la lista de la compra'. Esto es lo que hace que se pueda **refinar hablando**."
4. **Los tres campos del JSON:** "Y lo más importante: le decimos que SIEMPRE responda con tres campos — `reply`, `recipe` y `build_shopping_list`. Esto conecta con el Output Parser."

#### 3b. Chat Model y Memory

**Click en OpenRouter Chat Model:** "El motor. Un modelo rápido y barato."

**Click en Simple Memory:** "Las últimas 10 interacciones, con `sessionId` del Chat Trigger. Esto es lo que permite decir 'dame otra' sin repetir contexto — el agente recuerda qué propuso."

#### 3c. HTTP Request Tool — Recipe Search (campo por campo, despacio)

**Click en Recipe Search.**

> "La primera vez que usamos el **HTTP Request Tool**: le permite al agente llamar a cualquier URL. Vamos campo por campo."

- **URL:** `https://www.themealdb.com/api/json/v1/1/search.php`
  > "URL base fija. Fíjate que NO lleva `?s=...` incrustado. El `1` de la ruta es la API key de prueba que TheMealDB regala — sin registro ni pago."
- **Send Query Parameters: ON**, parámetro `s`:
  > "Activamos 'Send Query Parameters' y añadimos uno que se llama `s` — en TheMealDB significa 'search'. Una API REST recibe estos parámetros en la URL tras un interrogante: `search.php?s=chicken`."
- **Valor del parámetro — `$fromAI()`:**
  > "El valor NO lo escribimos nosotros: ponemos `$fromAI('query', 'un término de comida en inglés', 'string')`. Le decimos al agente: 'este hueco lo rellenas tú'. Si el usuario pide pollo, pone `chicken`, y la URL final es `search.php?s=chicken`. Tres argumentos: nombre, descripción y tipo."
- **Tool Description:** "La descripción le enseña CUÁNDO usarla y qué esperar: '...si sale `meals:null`, no hay resultados — prueba Google'. Esa frase le enseña el fallback."
- **Optimize Response: ON:** "Recorta el JSON de respuesta para gastar menos tokens."

**Enseña el JSON real** en el navegador (`search.php?s=chicken`), 5 s.

#### 3d. Google Search (SerpAPI) — el plan B

**Click en Google Search:** "El fallback. Si TheMealDB no tiene la receta, el agente se va a Google. Ya lo montamos en el capítulo de AI Agents."

#### 3e. Recipe Format — el Output Parser (2 min, la novedad)

**Click en el nodo "Recipe Format" (Structured Output Parser). Y en el agente, señala el toggle "Require Specific Output Format" en ON.**

> "Aquí está lo nuevo. Por defecto, un agente responde con **texto libre**, un párrafo. Pero un párrafo es dificilísimo de enrutar con un IF. Así que **obligamos al agente a responder en JSON**. Dos cosas lo hacen posible:
> 1. En el agente, activamos **'Require Specific Output Format'**.
> 2. Conectamos un **Structured Output Parser** — este nodo 'Recipe Format' — y le damos un **ejemplo** del JSON que queremos."

**Abre el nodo y enseña el JSON de ejemplo:**
```json
{
  "reply": "Here's a great option — Chicken Handi ... Would you like this recipe, a different one, or a shopping list with price estimates?",
  "recipe": "RECIPE: Chicken Handi\nCategory: Chicken | Cuisine: Indian\nINGREDIENTS:\n- 500g chicken\n...",
  "build_shopping_list": false
}
```

> "De este ejemplo, n8n deduce el esquema y obliga a que TODAS las respuestas tengan estos tres campos:
> - **`reply`**: lo que ve el usuario en el chat.
> - **`recipe`**: la receta limpia, guardada para el segundo agente.
> - **`build_shopping_list`**: `true` solo cuando el usuario confirma Y pide precios."

**El punto que lo cambia todo:**
> "Y aquí está la magia: con el parser conectado, `$json.output` **ya no es un texto — es un objeto**. Por eso el siguiente nodo, el IF, puede leer `$json.output.build_shopping_list`. Sin parser, `output` sería un string y no habría nada que enrutar."

**Auto-Fix — la red de seguridad (importante, dilo a cámara):**
> "Un detalle clave de robustez: los modelos pequeños a veces devuelven el JSON un poco roto — con markdown de más, o mal escapado. Para eso el parser tiene **Auto-Fix Format** activado: si el JSON no cuadra, n8n hace **una llamada extra al modelo para repararlo**. Por eso el parser tiene también un **Chat Model conectado** (el mismo OpenRouter). Es lo que hace que esto no se rompa. Y para ayudar, le pedimos al agente un `reply` **corto** y la receta completa solo en `recipe` — un solo texto grande en el JSON en vez de dos, que es mucho más fácil de generar bien."

> ⚠️ **Al montarlo desde cero:** activa **Auto-Fix Format** en el parser y **arrastra el OpenRouter Chat Model también al conector Model del parser**. Sin ese modelo, Auto-Fix da error de configuración.

---

### 4. Want Prices? — El IF lee el JSON (45s)

**Click en "Want Prices?".**

> "Un IF que lee un booleano del JSON del agente:"

**Señala:** `{{ $json.output.build_shopping_list }}` — Type: Boolean — **is true**.

> "Si el agente puso `true` (confirmaste y pediste precios), va por la rama de arriba al Shopping List Agent. Si no, va directo a devolver el `reply`. El agente actúa como un **router**: su flag decide el camino, en cada turno."

**Dato interesante — el gotcha del `$json`:** "Acordaos: cada mensaje es una ejecución nueva. En el turno donde eliges receta, el flag es `false` y solo se responde. En el turno donde confirmas, es `true`. Mismo workflow, decisión distinta según el JSON."

---

### 5. Shopping List Agent — Precios reales (2 min)

**Click en "Shopping List Agent".**

> "Segundo agente, con una sola herramienta: SerpAPI para precios. Y fíjate: este NO lleva Output Parser — su respuesta es texto plano, la lista, y con eso nos vale."

#### 5a. Su entrada

**Señala Prompt:** `{{ $json.output.recipe }}`
> "Su entrada es el campo `recipe` del JSON del agente anterior. Como el IF deja pasar el item tal cual, aquí `$json.output.recipe` sigue disponible."

#### 5b. Por qué un agente y no un chain
> "Un chain se inventaría los precios. Un agente los **busca** en Google. (En una variación lo veremos fallar en directo.)"

#### 5c. System Message
> "Le pide agrupar todos los ingredientes en UNA búsqueda para ahorrar API, máximo 2, y marcar con `≈` lo que estima."

---

### 6. Reply nodes — Dar forma a `output` (1 min)

> "Recordad: en modo `lastNode`, el chat muestra lo que el último nodo deje en `output`. Cada rama termina en un Set que escribe ese campo."

**Click en "Reply — Recipe Only" (rama false):**
> "Devuelve la receta seguida del `reply` corto del agente. La expresión es un ternario: si hay receta, muestra `recipe` + `reply`; si aún no hay (un saludo inicial), solo el `reply`. Eso es lo que ve el usuario mientras elige."

**Click en "Reply — With Prices" (rama true):**
> "Combina la receta con la lista. Y aquí, OTRO gotcha: después del Shopping List Agent, `$json.output` ya es la LISTA (un texto), no el objeto. Así que para recuperar la receta la pedimos por nombre: `$('Recipe Agent').first().json.output.recipe`. Referenciar un nodo anterior por su nombre, saltándonos lo que hay en medio."

---

### 6b. 🧭 De dónde sale cada comportamiento (mapa mental, 2 min)

> Este es el momento en que se entiende TODO. El comportamiento del asistente vive en **tres sitios distintos**, y hay que saber cuál toca para cada cosa. Explícalo con el Recipe Agent abierto.

**1. System prompt del Recipe Agent = el COMPORTAMIENTO (qué dice y cuándo).** Casi todo vive aquí:

| Comportamiento que ves | Regla en el system prompt |
|------------------------|---------------------------|
| Propone UNA receta, no una lista | *"Present ONE recipe at a time — never a list"* (How to behave) |
| **Te pregunta "¿esta, otra, o la lista de la compra?"** | *"After showing a recipe, ALWAYS ask whether they want THIS, a DIFFERENT one, or a SHOPPING LIST"* (How to behave) ← **esta es la pregunta que mencionas** |
| Si dices "otra" / "más occidental", busca de nuevo | *"If the user asks for a different or more specific recipe... search again"* (How to behave) |
| Solo saca precios cuando confirmas | La regla del campo `build_shopping_list`: *"true ONLY when the user confirmed AND asked for prices"* |
| No se inventa recetas | *"Never invent recipes — only present what you find from the tools"* (Rules). **Ojo:** *cómo* rechaza lo imposible (lapiceros) NO está fijado en el base → lo pulimos en directo en el Reel (sección 8b) |

**2. Recipe Format (Output Parser) = la FORMA, no las palabras.** Solo obliga a que la salida sea `{ reply, recipe, build_shopping_list }`. **No decide qué dice ni cuándo.** Si quitaras el parser, el agente se comportaría igual, pero devolvería texto suelto y el IF no podría leer el flag.

**3. Simple Memory = el CONTEXTO.** Es lo que permite el "dame otra": el agente recuerda qué propuso. Sin memoria, "¿otra de qué?".

> **Regla mnemotécnica:** **el prompt dice QUÉ · el parser dice CON QUÉ FORMA · la memoria dice QUÉ RECUERDA.**
>
> Así que la pregunta "¿esta u otra?" **ya está puesta, en el system prompt** — no hay que tocar nada. El parser solo garantiza que, diga lo que diga, venga empaquetado en ese JSON que el IF sabe leer.

---

### 7. DEMO en vivo (3 min)

**Click en Open Chat.** Escribe:
```
I want a chicken recipe
```

**Cuando responde con UNA receta y la pregunta:**
> "Fijaos: UNA sola receta, y me pregunta si quiero esta, otra, o la lista. Abro el output del Recipe Agent en el panel... mirad el JSON: `build_shopping_list` en `false`. Por eso solo me ha respondido, no ha buscado precios."

**Refina — escribe:**
```
Give me a more Western one
```
> "Sin reiniciar nada, me propone otra. La memoria le dice de qué hablábamos. Sigue en `false`."

**Confirma — escribe:**
```
Perfect, add the shopping list with prices
```
> "Ahora sí. Mirad el JSON: `build_shopping_list` en `true`. El IF dispara el segundo agente, que busca precios en Google... y aquí está la lista. Fijaos qué natural: proponer, refinar, confirmar — todo hablando."

---

### 8. Demo — Fallback a Google (opcional, 1 min)

```
How do I make Spanish fabada asturiana?
```
> "La fabada probablemente no está en TheMealDB. Expandimos la ejecución... veis: primero TheMealDB, `meals: null`, luego Google. El fallback funcionando."

---

### 8b. 🎥 Reel de demos (casos con chicha, 5-6 min)

> Después del happy path, tira estos casos: unos para lucir que funciona, otros para **provocar un fallo y arreglarlo EN DIRECTO**. Los arreglos son líneas que **pegas online en el System Message del Recipe Agent** para demostrarlo — **no los dejes en el JSON del curso**, revierte al acabar.

| Caso | Escribe en el chat | Qué esperar | Momento |
|------|--------------------|-------------|---------|
| **Refinado** | (tras una receta) `No, give me a more Western one` | cambia de receta; `build_shopping_list` sigue `false` | "funciona: memoria + la regla de buscar otra" |
| **Confirmación ambigua** | (tras una receta) `ok` | **NO** dispara la lista | "el guardarraíl del flag: exige confirmación explícita, no un 'ok' suelto" |
| **Lo imposible** | `I want a recipe for pencils` | intenta buscar, no encuentra; puede improvisar | "esto lo arreglamos en directo ↓" |
| **Fuera de tema** | `What's the weather in Madrid?` | el base **puede** contestar (no hay regla de scope) | "otro arreglo en directo ↓" |
| **Idioma** | `Quiero una receta con pollo` | busca en inglés y **responde en inglés** | "arreglo de idioma ↓" |

**Cómo hacer los arreglos:** abre el **System Message** del Recipe Agent, añade la línea en la sección **Rules**, guarda, y vuelve a lanzar el mismo mensaje. El "antes → después" en directo es lo que engancha.

**Arreglo A — lo imposible / no encontrado.** Copia y pega en Rules:
```
- If neither tool returns a real dish (for example the request is not food, like "a pencil recipe"), do NOT invent one: set "recipe" to "", "build_shopping_list" to false, and in "reply" say you couldn't find that recipe and suggest 2-3 real dishes they might like instead.
```
> "Vuelvo a pedir 'receta de lapiceros'... y ahora me dice con elegancia que eso no existe y me propone tres platos reales. He convertido un fallo en una buena experiencia con UNA línea."

*(Variante divertida, si quieres personalidad — pega esta en su lugar):*
```
- If the request is not real food, do NOT invent a recipe: reply with a friendly one-line joke that you only cook real dishes, then suggest a popular recipe. Keep "recipe" empty and "build_shopping_list" false.
```

**Arreglo B — fuera de tema (scope).** Copia y pega en Rules:
```
- You ONLY help with recipes and shopping lists. If asked anything else (weather, math, general chat), politely say that's all you can help with; set "recipe" to "" and "build_shopping_list" to false.
```
> "Le pregunto por el tiempo y ahora, en vez de improvisar, me recuerda educadamente que solo hace recetas. Esto en un asistente real es oro: acota qué sabe hacer."

**Arreglo C — idioma.** Copia y pega en Rules:
```
- Always write "reply" in the same language the user wrote in (keep searching in English internally).
```
> "Le pido en español y ahora me contesta en español, aunque por dentro siga buscando 'chicken' en inglés. El usuario ni se entera del truco."

> 💡 **El patrón, en voz alta:** "Fijaos qué he hecho tres veces seguidas: he visto un comportamiento que no me gusta, y he añadido UNA regla. No he tocado ni un nodo. Así se endurece un prompt en producción — observas, añades la excepción, repites." (Estos tres, recopilados, son también la **Variación 1**.)

**Revertir:** quita las líneas que añadiste, o reimporta el JSON limpio del curso.

---

### 8c. 📋 Análisis de los prompts (y mejoras potenciales, 3 min)

> Un hueco perfecto para enseñar criterio de prompt engineering. Abre los dos System Messages en pantalla.

**Recipe Agent — qué está bien:** tarea clara; estrategia de fallback explícita; regla de "UNA receta"; los tres campos del JSON bien descritos; traducción a inglés antes de buscar; "never invent".

**Recipe Agent — qué mejoraría:**
- **Sin regla de scope, de no-encontrado ni de idioma** — a propósito: son las que demuestras añadiendo en el Reel (8b).
- **`build_shopping_list` con un "sí" ambiguo:** las reglas ayudan, pero para lo sutil (¿cuándo EXACTAMENTE es true?) un par de **ejemplos (few-shot)** de turnos con su JSON serían más fiables que solo texto.
- **Formato de `recipe` en prosa:** un **ejemplo relleno** dentro del prompt mejora la consistencia del modelo pequeño.
- **`reply` sin límite de longitud:** puede enrollarse; añade "1-2 frases".
- **Depende del parser + Auto-Fix** para el JSON válido (bien, pero es una llamada LLM extra cuando falla — ver la nota de tokens).

**Shopping List Agent — qué está bien:** agrupa todo en 1 búsqueda (ahorra API); máximo 2; marca `≈` lo estimado; agrupa por sección; "solo la lista".

**Shopping List Agent — qué mejoraría:**
- **"US grocery prices" y "$" acoplados** → parametriza país/moneda si tu público no es de EEUU (un cambio toca dos sitios).
- **Puede alucinar precios** si la búsqueda no trae nada → refuerza "si de verdad no encuentras un precio, márcalo `≈` y dilo, no lo maquilles".
- **No hace cuentas** de cantidades (2×500 g) → si quieres totales exactos, pídeselo explícitamente.

> **Meta-punto (dilo):** "Un prompt de producción no nace perfecto: nace con lo básico y se endurece. **Reglas** para lo binario (scope, idioma, no inventar); **ejemplos (few-shot)** para lo sutil (cuándo exactamente poner un flag). Y siempre una red de seguridad — aquí, Auto-Fix para el JSON."

---

### 9. Cierre — Qué combina este proyecto (45s)

- **HTTP Request Tool** + **`$fromAI()`** — el agente llama a una API y rellena la URL
- **Fallback** — TheMealDB, luego Google
- **Memoria** — refinar hablando
- **Structured Output Parser** — el agente responde en JSON
- **IF sobre el JSON** — el LLM dirige el flujo
- **Segundo agente** — precios reales
- **`$('Node').first().json.output.field`** — referenciar nodos anteriores

> "El workflow más completo del curso, y con la experiencia de un chat de verdad."

---

## 🎬 PARTE 2 — Variaciones (para alargar el vídeo)

Seis variaciones autocontenidas, de menos a más montaje. Colócalas **antes del cierre** (sección 9).

> ⚠️ **Al terminar de grabar:** revierte o reimporta el JSON limpio del curso, que es el que descargan los alumnos.

---

### Variación 1 — Más prompt engineering por excepciones (4 min, solo prompt) ⭐

**Qué enseña:** completa lo del **Reel (8b)** con dos excepciones más. El mensaje es el mismo: un prompt bueno se **endurece** a base de reglas, cada una nacida de un fallo real. (En el Reel ya provocaste y arreglaste: no-encontrado, fuera de tema e idioma. Aquí van dos que se ven mejor "rompiendo" el prompt actual.)

**Fallo A — Devuelve varias recetas.** Abre el System Message del Recipe Agent y **quita temporalmente** la línea "Present ONE recipe at a time...". Demo: `I want a chicken recipe`.
> "Sin esa regla, mirad: me suelta cuatro recetas de golpe. Confuso. Lo arreglamos volviendo a añadir la excepción:"
Vuelve a poner — copia y pega como primera regla de "How to behave":
```
- Present ONE recipe at a time — the best match — never a list. If the search returns several, pick one and say you can suggest another if they prefer.
```

**Fallo B — Dispara los precios sin confirmar.** Demo: tras una receta, escribe algo ambiguo como `sure` o `vale`.
> "A veces con un 'ok' pone `build_shopping_list` en true antes de tiempo y gasta SerpAPI sin querer. Endurecemos la condición — sustituye la línea del campo por:"
```
- "build_shopping_list": true ONLY when the user EXPLICITLY confirms a specific recipe AND asks for the shopping list or prices. A vague "ok" or "yes" without mentioning the list is NOT enough — ask them to clarify.
```

> "El patrón, otra vez: observo un fallo, añado una regla, sin tocar un nodo. Reglas para lo binario; ejemplos (few-shot) para lo sutil — como en el análisis de prompts."

**Revertir:** restaura el System Message original (está en el notebook y en el JSON).

---

### Variación 2 — Añadir un campo al JSON: `difficulty` (4 min)

**Qué enseña:** que el esquema de salida es tuyo — puedes añadir campos y reaccionar a ellos.

**Pasos:**
1. Abre **Recipe Format** (Output Parser) y añade `"difficulty": "easy"` al JSON de ejemplo — copia y pega el ejemplo entero:
   ```json
   {
     "reply": "Here's a great option — Chicken Handi ... Would you like this recipe, a different one, or a shopping list with price estimates?",
     "recipe": "RECIPE: Chicken Handi\nCategory: Chicken | Cuisine: Indian\nINGREDIENTS:\n- 500g chicken\n...",
     "build_shopping_list": false,
     "difficulty": "easy"
   }
   ```
2. En el System Message del agente, añade en Rules — copia y pega:
   ```
   - "difficulty": estimate the recipe difficulty as "easy", "medium" or "hard".
   ```
3. Demo: pide una receta y abre el output → ahora hay un campo `difficulty`.

> "El esquema lo mando yo. Con un campo más, el agente ya clasifica dificultad, y podría enrutarlo con otro IF o un Switch. La salida estructurada es lo que convierte al LLM en una pieza de lógica, no solo un generador de texto."

**Revertir:** quita el campo del ejemplo y la regla.

---

### Variación 3 — Sin memoria: se rompe el refinado (2 min, sin config)

**Qué enseña:** qué hace la memoria, por ausencia.

**Pasos:**
1. **Desconecta** Simple Memory del Recipe Agent (borra la línea de puntos).
2. `I want a chicken recipe` → propone una.
3. `Give me another one`

> "Sin memoria, no sabe de qué le hablo — 'otra ¿de qué?'. El refinado depende 100% de la memoria: es lo que le reinyecta lo que ya propuso."

4. **Reconecta** y repite → ahora sí.

**Revertir:** ya está al reconectar.

---

### Variación 4 — Agent vs Basic LLM Chain: los precios inventados (4 min)

**Qué enseña:** por qué el Shopping List es un agente y no un chain — viéndolo fallar.

**Pasos:**
1. Añade un **Basic LLM Chain** → `Shopping List (Chain)`. Conéctale el **OpenRouter Chat Model**.
2. Configúralo:
   - **Source for Prompt:** `Define below`
   - **Prompt** (Expression) — copia y pega:
     ```
     {{ $json.output.recipe }}
     ```
   - **System Message** — copia y pega:
     ```
     You are a shopping assistant. From the recipe provided, create a complete shopping list with estimated US grocery prices.

     Rules:
     - Include exact quantities from the recipe
     - Group items by store section (Produce, Meat / Fish, Dairy, Pantry)
     - End with an estimated total
     - Output ONLY the shopping list
     ```
3. **Recablea temporalmente:** salida **true** del IF → `Shopping List (Chain)` → `Reply — With Prices`. En `Reply — With Prices` cambia `$json.output` por `$json.text` (el chain responde en `text`).
4. Demo: receta → confirma con lista.

> "Lista perfecta, precios razonables... e inventados TODOS. Un chain no tiene herramientas, no puede buscar. Genera texto plausible, que es lo peligroso. El agente de verdad va a Google."

5. Señala: "Y ojo: el chain responde en `text`, el agente en `output`. Por eso hubo que cambiar la expresión. Chain → `text`, Agent → `output`."

**Revertir:** reconecta el IF true → **Shopping List Agent** → `Reply — With Prices` (con `$json.output`).

**Bonus:** no gasta SerpAPI.

---

### Variación 5 — Aprobación con botones dentro del chat (Human-in-the-Loop) (6 min)

**Qué enseña:** el modo **Using Response Nodes** y el nodo **Chat (Send & Wait)** — cuando quieres un **portón explícito** antes de una acción cara (aquí, gastar SerpAPI). Conecta con el bloque teórico de modos.

**Pasos:**
1. En el **Chat Trigger** → Options → **Response Mode** → cámbialo a **Using Response Nodes**.
2. Entre el Recipe Agent y el IF, mete un nodo **Chat** → `Confirm Spend`:
   - **Operation:** `Send and Wait for Response`
   - **Message** (Expression) — copia y pega:
     ```
     {{ $json.output.reply }}
     ```
   - **Response Type:** `Approval` → **Approve and Disapprove**
   - **Approve Button Label:** `Yes, shopping list` · **Disapprove Button Label:** `No, just the recipe`
3. Cambia la condición del IF a — copia y pega en Left Value, tipo Boolean, is true:
   ```
   {{ $json.data.approved }}
   ```
4. Como ahora estás en Response Nodes, las ramas ya no muestran nada solas: cambia los dos `Reply` (Set) por nodos **Chat** con **Operation: Send Message** y el mismo texto en **Message**.

> "Aquí el humano aprueba con un botón, dentro del chat, antes de que gastemos búsquedas. Esto es 'Using Response Nodes': nada llega al chat salvo que un nodo Chat lo mande, y el Send & Wait pausa de verdad, sin el timeout de 90 s del modo lastNode. Es el modo para HITL con botones. Más nodos, pero control total."

**Revertir:** Response Mode → **When Last Node Finishes**; quita `Confirm Spend`; IF a `{{ $json.output.build_shopping_list }}`; vuelve a los Set `Reply`. (O reimporta el JSON limpio.)

---

### Variación 6 — Nueva herramienta: Random Recipe (4 min)

**Qué enseña:** añadir una herramienta y ver cómo el agente DECIDE usarla (Challenge 1 del notebook).

**Pasos:**
1. En **Recipe Agent** → **+ Tool** → **HTTP Request Tool** → `Random Recipe`.

| Campo | Valor |
|-------|-------|
| **Method** | `GET` |
| **URL** | `https://www.themealdb.com/api/json/v1/1/random.php` |
| **Send Query Parameters** | OFF |
| **Optimize Response** | ON |

2. **Description** — copia y pega:
   ```
   Returns one random recipe from TheMealDB. Takes no input. Use this only when the user asks to be surprised or wants a random recipe.
   ```
3. En el System Message, añade en "How to behave" — copia y pega:
   ```
   - If the user asks to be surprised or wants a random pick, use Random Recipe (it takes no input).
   ```
4. Demo: `Surprise me!` → usa Random Recipe. Contraste: `I want a chicken recipe` → usa Recipe Search (míralo en los logs).

**Revertir:** opcional (coincide con el Challenge 1).

---

## 🧪 Textos de prueba (copy-paste para el chat)

```
I want a chicken recipe
```
```
Give me a more Western one
```
```
Perfect, add the shopping list with prices
```
```
How do I make Spanish fabada asturiana?
```
```
Quiero algo con pescado
```
```
Surprise me!
```

---

## ⚠️ Cosas a tener en cuenta durante la grabación

1. **Abre el output del Recipe Agent** en el panel durante la demo — ver el JSON (`build_shopping_list` cambiando de false a true) es lo que hace clic en la cabeza del alumno. Es el corazón del proyecto.
2. **`When Last Node Finishes`:** si el chat no muestra nada, revisa que el último nodo de cada rama deja el texto en un campo llamado `output`.
3. **Error "Model output doesn't fit required format":** significa que el modelo devolvió el JSON roto. Verifica que **Auto-Fix Format** está ON en el parser **y** que tiene un **Chat Model conectado**. Con eso, n8n repara el JSON solo. (Si aún falla mucho, prueba un modelo un pelín mejor para el parser.)
3. **SerpAPI tiene límite:** free tier ~100/mes (mira https://serpapi.com/dashboard). Cada lista gasta 1-2 búsquedas.
4. **TheMealDB es limitada:** ~300 recetas en inglés. Lo muy específico o en otro idioma cae al fallback de Google.
5. **Precios aproximados:** vienen de Google, no de una API de supermercado. El agente marca con `≈` lo que estima.
6. **Dos usos de SerpAPI:** Google Search (fallback) y Price Search. Misma credencial, búsquedas separadas.
