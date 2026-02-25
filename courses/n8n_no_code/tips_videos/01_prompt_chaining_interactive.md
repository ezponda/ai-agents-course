# Clase: Prompt Chaining → Chatbot Interactivo

**Workflow base:** `01_prompt_chaining.json` (ya importado)
**Pre-requisito:** Credenciales configuradas (ver vídeo `00_configurar_credenciales`)

Dos partes:
- **Parte 1 (Vídeo grabado):** Explicar el workflow base + hacerlo interactivo con Chat Trigger + HTTP Request
- **Parte 2 (Streaming):** Los alumnos construyen un agente conversacional con dos herramientas de búsqueda

---

# PARTE 1 — Vídeo Grabado

## Paso 0: Mostrar el workflow base

1. Abrir `01_prompt_chaining.json`
2. Zoom out para ver la estructura completa
3. Ejecutar una vez → mostrar el resultado de cada nodo

**Qué decir:**

> "Este workflow transforma una receta en tres pasos: simplifica, adapta para niños, y genera lista de la compra. Funciona, pero la receta está hardcoded en el nodo Input. Si quieres otra receta, tienes que entrar y cambiarla a mano. Vamos a hacerlo interactivo."

---

## Paso 1: Cambiar a Chat Trigger

1. Duplicar el workflow (click derecho → Duplicate)
2. Eliminar **Manual Trigger**
3. Añadir **Chat Trigger** (buscar "When chat message received")
4. Conectar Chat Trigger → Input — Recipe
5. Abrir **Input — Recipe**, cambiar el campo `recipe`:
   - Click en el valor → click en **Expression** (icono `{{ }}`)
   - Pegar:

📋
```
{{ $json.chatInput }}
```

6. Click en **Chat** → pegar una receta → ejecutar

**Qué decir:**

> "El Chat Trigger nos da una interfaz de chat. Lo que el usuario escribe llega en `chatInput`. Ahora el usuario puede pegar cualquier receta y el workflow la procesa."
>
> "Pero tenemos un problema: el nombre de la receta sigue hardcoded. Y si el usuario escribe algo como 'Tengo una paella, mis hijos tienen 6 años', todo va al campo recipe mezclado. Vamos a arreglar eso más adelante. Ahora quiero enseñaros otra cosa: cómo buscar recetas en internet."

---

## Paso 2: HTTP Request — buscar recetas en TheMealDB

**Qué es una API (explicar brevemente):**

> "Antes de meternos con el nodo, tres conceptos rápidos que vamos a usar todo el rato."
>
> "**API** significa *Application Programming Interface*. Es una forma de que dos programas hablen entre sí. Cuando usáis Google Maps en una app de delivery, esa app está llamando a la API de Google Maps. No abre el navegador — hace una petición directa y recibe datos."
>
> "Una API es como una máquina expendedora de Coca-Cola: metes una moneda, pulsas un botón, y te sale la lata. No necesitas saber cómo funciona por dentro — ni el motor, ni el refrigerador, ni el mecanismo. Solo necesitas saber qué botón pulsar y qué moneda meter. Con una API es igual: le mandas una petición con los datos correctos (la moneda + el botón) y te devuelve lo que pediste (la lata)."
>
> "**HTTPS** es el protocolo que usa tu navegador para comunicarse con servidores. La *S* significa *Secure* — los datos van cifrados. Cuando veis un candado en el navegador, es HTTPS. Todas las APIs modernas usan HTTPS."

**Qué es una petición HTTP (explicar brevemente):**

> "Cuando abres una web en el navegador, tu navegador hace una petición HTTP al servidor. Hay varios tipos, pero los dos principales:"
>
> - **GET** = pedir datos (como abrir una página o buscar algo). No cambia nada en el servidor.
> - **POST** = enviar datos (como enviar un formulario o crear algo nuevo).
>
> "Vamos a usar GET para buscar recetas en una API gratuita. Es lo mismo que hace el navegador cuando escribís una URL — solo que lo hacemos desde n8n."

### Añadir el nodo HTTP Request

1. Añadir **HTTP Request** (el nodo normal, NO el tool)
2. Ponerlo entre **Chat Trigger** y **Input — Recipe**
3. Configurar:

| Campo | Valor |
|-------|-------|
| **Method** | GET |
| **URL** | (pegar abajo) |

📋
```
https://www.themealdb.com/api/json/v1/1/search.php
```

4. Activar **Send Query Parameters** → Using Fields Below
5. Añadir un parámetro:

| Name | Value |
|------|-------|
| `s` | 📋 `{{ $json.chatInput }}` (Expression) |

6. Ejecutar con el chat escribiendo: `chicken`

**Qué decir:**

> "TheMealDB es una API gratuita de recetas. No necesita API key. Le pasamos un término de búsqueda y devuelve recetas en formato JSON."
>
> "Fijaos en la URL: tiene una parte fija y un parámetro `s` que es lo que busca. Esto es lo que pasa cuando buscáis algo en Google: la URL lleva `q=lo-que-buscas`. Mismo concepto."

### Otros endpoints de TheMealDB (para mencionar)

La API tiene más endpoints además de buscar por nombre. Todos usan la misma base URL: `https://www.themealdb.com/api/json/v1/1/`

| Endpoint | URL | Parámetro | Qué hace |
|----------|-----|-----------|----------|
| Buscar por nombre | `/search.php` | `s=chicken` | El que usamos nosotros |
| Buscar por letra | `/search.php` | `f=a` | Todas las recetas que empiezan por "a" |
| Receta aleatoria | `/random.php` | (ninguno) | Devuelve una receta al azar |
| Filtrar por ingrediente | `/filter.php` | `i=chicken_breast` | Recetas que usan ese ingrediente |
| Filtrar por categoría | `/filter.php` | `c=Seafood` | Recetas de esa categoría |
| Filtrar por país | `/filter.php` | `a=Spanish` | Recetas de esa cocina |
| Listar categorías | `/list.php` | `c=list` | Todas las categorías disponibles |
| Detalle por ID | `/lookup.php` | `i=52772` | Receta completa por su ID |

**Qué decir:**

> "Nosotros usamos `/search.php?s=...` pero la API tiene más opciones. Podéis filtrar por ingrediente, por país, o incluso pedir una receta aleatoria. La documentación completa está en [themealdb.com/api.php](https://www.themealdb.com/api.php)."
>
> "Lo importante es entender el patrón: misma base URL, distinto endpoint y parámetro. Esto es así en casi todas las APIs."

7. Mostrar el output del HTTP Request — enseñar el JSON con los campos `meals[0].strMeal`, `strInstructions`, etc.

### Conectar al workflow

8. Abrir **Input — Recipe**, cambiar los campos:

| Campo | Modo | Valor |
|-------|------|-------|
| `recipe_name` | Expression | 📋 `{{ $json.meals[0].strMeal }}` |
| `recipe` | Expression | 📋 `{{ $json.meals[0].strInstructions }}` |

9. Ejecutar → escribir `lasagna` → ver cómo busca la receta online y la transforma

**Qué decir:**

> "Ahora el usuario escribe un nombre de plato, el workflow busca la receta en internet, y la pasa por los tres pasos de transformación. De workflow estático a workflow conectado a internet."

### Diagrama final Parte 1

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│    Chat      │────▶│ HTTP Request │────▶│ Input — Recipe │────▶│ Step 1  │────▶│ Step 2  │────▶│ Step 3  │
│   Trigger    │     │ (TheMealDB)  │     │                │     │Simplify │     │ Kids    │     │Shopping │
└──────────────┘     └──────────────┘     └────────────────┘     └─────────┘     └─────────┘     └─────────┘
```

**Workflow expandido:** `expanded_workflows/01_prompt_chaining_chat_http.json`

---

# PARTE 2 — Streaming (los alumnos construyen)

**Objetivo:** Crear un agente conversacional que pregunte edades y alergias, con dos herramientas de búsqueda: TheMealDB (recetas comunes) y Google/SerpAPI (recetas regionales o específicas).

---

### Diferencia clave: Prompt Chaining vs AI Agent

En la Parte 1 hemos encadenado nodos a mano: Chat Trigger → HTTP Request → LLM 1 → LLM 2 → LLM 3. **Nosotros** decidimos el orden y el flujo de datos.

Con un **AI Agent** es diferente: hay **un solo nodo** (el Agent) que tiene acceso a **herramientas** (tools) y **decide por sí mismo** cuál usar y cuándo. Nosotros le damos instrucciones en el **System Message** y el agente razona sobre qué hacer.

### Anatomía de un nodo AI Agent en n8n

El nodo AI Agent tiene **4 slots** (conexiones punteadas, no sólidas):

```
                    AI Agent
                   ┌────────┐
                   │        │
           ┌──────┤  Agent ├──────┐  ← salida principal (línea sólida)
           │      │        │      │
           │      └───┬────┘      │
           │          │           │
     ┌─────┴─┐   ┌───┴───┐   ┌──┴──────┐
     │ Chat  │   │Memory │   │ Tools   │  ← sub-nodos (líneas punteadas)
     │ Model │   │       │   │(1 o más)│
     └───────┘   └───────┘   └─────────┘
```

| Slot | Qué es | Obligatorio |
|------|--------|-------------|
| **Chat Model** | El LLM que usa el agente (OpenRouter, OpenAI...) | Si |
| **Memory** | Historial de conversacion (Window Buffer Memory) | No, pero necesario para chat |
| **Tool** (x N) | Herramientas que el agente puede llamar | No, pero es lo que le da superpoderes |

> **Importante:** Las conexiones a sub-nodos son **lineas punteadas**, no sólidas. Si ves una línea sólida, está mal conectado. Para conectar, arrastra desde el slot correspondiente del Agent (Chat Model, Memory, Tool).

---

## Paso 1: Crear workflow nuevo

1. **Workflows** → **Add Workflow** → renombrar a "Recipe Chat Agent"

## Paso 2: Chat Trigger + AI Agent

1. Eliminar el **Manual Trigger** que viene por defecto
2. Buscar **"chat"** en el panel de nodos → añadir **"When chat message received"** (Chat Trigger)
3. Buscar **"agent"** en el panel de nodos → añadir **"AI Agent"**
   - Ojo: busca exactamente "agent", no "AI Agent" — aparece como **Agent** en las versiones recientes de n8n
4. Conectar **Chat Trigger → AI Agent** con una línea **sólida** (arrastrar del output del trigger al input del agent)

### Configurar el AI Agent

5. Abrir el nodo **AI Agent** (doble click)
6. En la parte superior del panel, buscar **"Source for Prompt"** → seleccionar **`Define below`**
7. Aparece un campo **"Text"** → click en el campo → click en **Expression** (icono `{{ }}`) → pegar:

📋
```
{{ $json.chatInput }}
```

> Esto pasa el mensaje del usuario al agente. `chatInput` es el campo que genera automáticamente el Chat Trigger.

8. Más abajo en el panel, buscar la sección **Options** (puede estar colapsada — click para expandir) → click en **"Add Option"** → seleccionar **"System Message"** → pegar:

📋
```
You are a friendly recipe assistant for families with kids.

## What you do
Help users find and adapt recipes for children.

## Information you need
Before transforming any recipe, collect:
1. Kid ages (required — ask if missing)
2. Allergies or dislikes (ask once, optional)

## How you work
- If the user gives a common dish name (chicken, pasta, lasagna...), use Recipe Search (TheMealDB)
- If TheMealDB returns no results, or the dish is regional/specific (croquetas, tortilla de patatas, pad thai), use Google Search
- If the user pastes a full recipe, use it directly — no need to search
- Once you have the recipe + kid ages, transform it:
  1. Simplify for beginners
  2. Adapt for kids (fun names, safety notes, age-appropriate portions)
  3. Generate a shopping list with estimated cost
- After presenting the result, ask if they want changes

## Rules
- Always ask for kid ages before transforming
- Never invent recipes — search or ask the user to paste one
- Recipe Search terms must be in English and simple (e.g. 'chicken', 'lasagna')
- Be conversational, not robotic
```

> **Fíjate:** El system prompt menciona herramientas por nombre: `Recipe Search (TheMealDB)` y `Google Search`. Estos nombres **deben coincidir exactamente** con el campo `Name` de cada tool que añadiremos luego. Si el system prompt dice "Recipe Search" pero la tool se llama "Search Recipes", el agente se confunde.

## Paso 3: Añadir Chat Model + Memory (sub-nodos)

> Estos se conectan como **sub-nodos** (líneas punteadas). En el nodo AI Agent, verás los slots abajo o a la izquierda.

1. En el nodo **AI Agent**, buscar el slot **"Chat Model"** (icono `+` debajo del nodo, o en el panel lateral) → click **+ Chat Model** → seleccionar **OpenRouter Chat Model** → configurar:
   - **Model**: `openai/gpt-4o-mini`
   - Seleccionar la credencial de OpenRouter (configurada en el vídeo de credenciales)
   - Verificar que se ve una **línea punteada** entre el Chat Model y el Agent

2. Click **+ Memory** → seleccionar **Window Buffer Memory** → configurar:
   - **Window Size**: `10` (recuerda los últimos 10 mensajes)
   - Verificar línea punteada entre Memory y Agent

## Paso 4: Añadir HTTP Request Tool (TheMealDB)

> **Cuidado:** Hay dos nodos que se llaman parecido:
> - **HTTP Request** (nodo normal) — lo usamos en la Parte 1 para llamar a la API directamente
> - **HTTP Request Tool** — versión especial **para agentes**. Aparece cuando buscas "HTTP Request" dentro de los tools del Agent
>
> Aquí usamos el **Tool**, no el nodo normal. La diferencia: el Tool tiene campos `Name`, `Description` y `Placeholders` que el agente lee para decidir cuándo y cómo usarlo.

1. En el nodo **AI Agent**, click en **+ Tool** (slot inferior) → buscar **"HTTP Request"** → seleccionar **"HTTP Request Tool"**
   - Verificar que se conecta con **línea punteada** al Agent
2. Configurar los campos básicos:

| Campo | Dónde está | Valor |
|-------|-----------|-------|
| **Name** | Primer campo del panel | 📋 `Recipe Search` |
| **Description** | Segundo campo | (pegar abajo) |
| **Method** | Sección HTTP | `GET` |
| **URL** | Sección HTTP | (pegar abajo) |

> **El campo `Name` es crítico.** Es el nombre que el agente ve internamente. Cuando en el system prompt escribimos "use Recipe Search (TheMealDB)", el agente busca una tool que se llame `Recipe Search`. Si aquí pones otro nombre (como "TheMealDB" o "Search"), no coincide y el agente puede no usarla correctamente.

**Description** (pegar tal cual — NO dejar vacío):

📋
```
Search for common recipes in TheMealDB database. Search terms MUST be in English and simple (e.g. 'chicken', 'lasagna', 'beef stew'). If the dish is regional or not found here, use Google Search instead.
```

> La **Description** es la "documentación" que lee el agente para decidir cuándo usar esta tool. Fíjate que incluye instrucciones sobre cuándo NO usarla ("if regional, use Google Search instead"). Esto guía la decisión del agente. **Si la Description está vacía, el agente no sabe para qué sirve la tool y manda cualquier cosa (como "5 años").**

**URL:**

📋
```
https://www.themealdb.com/api/json/v1/1/search.php
```

3. **⚠️ PASO CRÍTICO — Activar el botón ✨ (sparkle/AI) en los campos que rellena el agente:**

   Al lado de cada campo del HTTP Request Tool hay un icono ✨ (estrella/sparkle). Hacer click en ✨ marca ese campo como **"filled by AI"** — es decir, el agente lo rellena en vez de usar un valor fijo.

   **Sin hacer click en ✨, n8n ignora la Description y los Placeholders, y pasa el chatInput crudo a la tool.** Esto causa "Invalid URL" y es el error más común.

   → Hacer click en el **✨ del campo URL** (debe ponerse morado/activo)

   > **Verificación:** El banner amarillo "No parameters are set up to be filled by AI" debe desaparecer después de hacer click en ✨. Si sigue apareciendo, el agente NO podrá rellenar la URL.

4. Activar **Send Query Parameters** → seleccionar **"Using Fields Below"** → click **"Add Parameter"**:

| Name | Value |
|------|-------|
| `s` | 📋 `{query}` |

   → Hacer click también en el **✨ del campo Value** del query parameter (para que el agente rellene `{query}`)

> `{query}` (con llaves simples) es un **placeholder**: el agente lo sustituye por el término de búsqueda real en cada llamada. NO es una expression de n8n (`{{ }}`), es sintaxis propia del HTTP Request Tool.

5. Scroll down hasta **Placeholder Definitions** → click **"Add Placeholder"**:

| Name | Description |
|------|-------------|
| `query` | 📋 `The search term for the recipe (e.g. 'chicken', 'pasta'). ONLY food terms in English, never user messages like ages or preferences.` |

> El nombre del placeholder (`query`) debe coincidir exactamente con lo que pusiste en el query parameter (`{query}`). La description le dice al agente qué tipo de valor poner ahí.

6. Activar **Optimize Response** (reduce el JSON de respuesta para no gastar tokens innecesarios)

> **Checklist antes de continuar:**
> - [ ] Name = `Recipe Search`
> - [ ] Description rellena (NO el texto gris de placeholder)
> - [ ] ✨ activado en URL (y en Value del query parameter)
> - [ ] Banner "No parameters are set up to be filled by AI" ha desaparecido
> - [ ] Placeholder `query` definido
> - [ ] Optimize Response activado

## Paso 5: Ampliar la tool description con más endpoints

Ahora mismo Recipe Search solo busca por nombre (`/search.php?s=...`). Pero TheMealDB tiene más endpoints. ¿Y si el usuario pide "una receta aleatoria" o "algo con pollo"? Podemos enseñarle al agente a usar esos endpoints **sin añadir nodos nuevos** — solo cambiando la description.

**Qué decir:**

> "¿Dónde ponemos esta información? Tenemos tres sitios posibles: el system prompt del agente, la tool description, o los placeholder definitions. La respuesta es la **tool description**. El system prompt dice cómo debe comportarse el agente en general. La tool description dice cómo usar una herramienta concreta. Si mañana cambiamos la API, solo tocamos la description de esa tool."

1. Abrir **Recipe Search** (doble click en el sub-nodo HTTP Request Tool)
2. Cambiar la **URL** — borrar la anterior y pegar (el ✨ debe seguir activo en la URL):

📋
```
https://www.themealdb.com/api/json/v1/1/{endpoint}
```

> Ahora la URL tiene un placeholder `{endpoint}` en vez de un endpoint fijo. El agente decidirá qué endpoint usar.

3. Borrar la Description anterior y pegar la nueva **Description**:

📋
```
Search for recipes in TheMealDB. All search terms MUST be in English.

IMPORTANT: {endpoint} must be a valid URL path. Use URL encoding for spaces (replace spaces with %20 or use underscores for ingredients).

Available endpoints (use as {endpoint}):
- search.php?s={query} → search by meal name. Supports multiple words (e.g. 'search.php?s=beef%20stew', 'search.php?s=pad%20thai'). Use simple terms.
- random.php → get a random recipe (no query needed)
- filter.php?i={query} → filter by ingredient. Use underscores for multi-word ingredients (e.g. 'filter.php?i=chicken_breast')
- filter.php?c={query} → filter by category (e.g. 'filter.php?c=Seafood', 'filter.php?c=Dessert')
- filter.php?a={query} → filter by area (e.g. 'filter.php?a=Spanish', 'filter.php?a=Italian')

Default: use search.php?s={query} for name searches.
If the dish is regional or not found, use Google Search instead.
NEVER pass user messages (like ages, allergies) as search queries — only food terms.
```

> Ahora la description incluye una "mini-documentación" de la API con formato URL. El agente lee esto y decide qué endpoint poner en `{endpoint}`. La línea final ("NEVER pass user messages...") evita que el agente mande cosas como "5 años" como búsqueda.

4. En **Placeholder Definitions**:
   - **Eliminar** el placeholder `query` (click en la X)
   - **Cambiar** (o añadir) el placeholder `endpoint`:

| Name | Description |
|------|-------------|
| `endpoint` | 📋 `The API endpoint path with query parameter. Must be a valid URL path — use %20 for spaces in meal names, underscores for ingredient names. Examples: 'search.php?s=chicken', 'search.php?s=beef%20stew', 'random.php', 'filter.php?i=chicken_breast', 'filter.php?a=Spanish'. ONLY use food-related search terms, never user messages like ages or allergies.` |

> Ahora solo hay **un placeholder** (`endpoint`). El query va incluido dentro del endpoint (p.ej. `search.php?s=chicken`). Antes teníamos dos (`query` + query parameter `s`), ahora es más flexible.

5. **Desactivar** "Send Query Parameters" (toggle off) — los parámetros ahora van en la URL directamente, no como query parameters separados

6. Probar en el chat:
   - `Surprise me with a random recipe` → el agente usa `random.php`
   - `Something with chicken breast` → el agente usa `filter.php?i=chicken_breast`
   - `A Spanish dish` → el agente usa `filter.php?a=Spanish`

**Qué decir:**

> "No hemos tocado el system prompt ni hemos añadido nodos. Solo hemos cambiado la description de la tool. El agente lee esa description y decide qué endpoint usar. Esto es clave: **la tool description es la documentación que lee el agente**."

---

## Paso 6: Añadir SerpAPI Tool (Google Search)

1. En el nodo **AI Agent**, click **+ Tool** → buscar **"SerpAPI"** → seleccionar **SerpAPI**
   - Verificar línea punteada al Agent
2. Seleccionar la credencial de SerpAPI (configurada en el vídeo de credenciales)
3. El campo **Name** por defecto es `Google Search` — verificar que dice exactamente eso:

| Campo | Valor |
|-------|-------|
| **Name** | 📋 `Google Search` |

> **Importante:** Este nombre debe coincidir con lo que dice el system prompt ("use Google Search"). No cambiar a "SerpAPI" ni "Web Search".

No necesita más configuración — SerpAPI ya sabe cómo buscar. El agente le pasa el query automáticamente.

**Qué decir:**

> "Ahora el agent tiene dos herramientas de búsqueda. TheMealDB es una base de datos de recetas comunes — funciona bien para 'chicken' o 'lasagna'. Pero si le pedís 'croquetas de jamón' o 'tortilla de patatas', no va a encontrar nada. Para eso está Google Search."
>
> "Lo interesante es que el agent decide cuál usar. En la tool description le decimos cuándo usar cada una. Fijaos: Recipe Search dice 'if the dish is regional, use Google Search instead'. Esa frase es la que guía la decisión."

### Resumen: qué tiene el Agent ahora

```
AI Agent "Recipe Chat Agent"
├── Chat Model: OpenRouter (gpt-4o-mini)     ← línea punteada
├── Memory: Window Buffer Memory (10 msgs)   ← línea punteada
├── Tool 1: Recipe Search (HTTP Request Tool) ← línea punteada
│   └── Name: "Recipe Search"
│   └── URL: themealdb.com/api/json/v1/1/{endpoint}
│   └── Placeholder: endpoint
└── Tool 2: Google Search (SerpAPI)           ← línea punteada
    └── Name: "Google Search"
```

> Si algo no funciona, lo primero que hay que verificar:
> 1. Que las 4 líneas punteadas existen (Chat Model, Memory, 2 Tools)
> 2. Que los nombres de las tools coinciden con el system prompt
> 3. Que las credenciales están seleccionadas (OpenRouter y SerpAPI)

## Paso 7: Añadir Output

1. Buscar **"Edit Fields"** en el panel de nodos (nodo normal, no tool) → añadir → renombrar a `Output`
2. Conectar **Agent → Output** con línea **sólida** (es flujo de datos principal, no sub-nodo)
3. En el nodo Output, añadir un campo:

| Name | Type | Value (Expression) |
|------|------|-------|
| `output` | String | 📋 `{{ $json.output }}` |

> El AI Agent devuelve su respuesta en un campo llamado `output`. El Chat Trigger espera que el último nodo tenga un campo `output` para mostrarlo en el chat. Si el campo se llama otra cosa, el chat mostrará JSON en vez de texto.

## Paso 8: Probar

Abrir el chat y probar esta conversación:

**Turno 1:**
```
Quiero hacer algo con pollo para mis hijos
```
→ El agent usa **Recipe Search** (TheMealDB) y pregunta edades/alergias

**Turno 2:**
```
Tienen 5 y 9 años, sin alergias
```
→ El agent devuelve la receta adaptada + lista de la compra

**Turno 3:**
```
¿Y unas croquetas de jamón?
```
→ El agent usa **Google Search** (porque TheMealDB no tiene croquetas) y recuerda las edades

## Paso 9: Logging a Google Sheets (observabilidad básica)

**Objetivo:** Guardar cada interacción en Google Sheets — input, output, y las herramientas que el agente usó. Esto da visibilidad sobre qué hace el agente internamente.

### Crear la Google Sheet

1. Crear una nueva Google Sheet
2. Escribir estos headers en la fila 1:

| A | B | C | D | E |
|---|---|---|---|---|
| `session_id` | `timestamp` | `input` | `output` | `tools_used` |

3. Copiar la URL de la Sheet

### Añadir credencial de Google Sheets en n8n

1. **Settings** → **Credentials** → **Add Credential** → buscar "Google Sheets"
2. Seguir el flujo OAuth2 (conectar con tu cuenta de Google)
3. **Save**

### Modificar el system prompt del Agent

Añadir al final del system message existente:

📋
```

## Logging
At the end of every response, add on a new line:
---
Tools used: [list each tool you called in order, comma-separated, or "none"]
```

**Qué decir:**

> "Le pedimos al agente que al final de cada respuesta nos diga qué herramientas usó. Esto es lo que se llama *self-reporting* — el agente nos cuenta lo que hizo. ¿Es fiable? No siempre. A veces se olvida de una herramienta, o dice que usó una que no usó. Por eso en producción se usan herramientas de observabilidad externas como Langfuse o LangSmith. Pero para entender qué pasa dentro del agente, esto nos sirve."

### Añadir Prepare Log (Edit Fields)

1. Añadir **Edit Fields** entre el Agent y Output → renombrar a `Prepare Log`
2. Añadir cinco campos:

| Name | Type | Value (Expression) |
|------|------|---------------------|
| `session_id` | String | 📋 `{{ $('When chat message received').first().json.sessionId }}` |
| `timestamp` | String | 📋 `{{ $now.toFormat('yyyy-MM-dd HH:mm:ss') }}` |
| `input` | String | 📋 `{{ $('When chat message received').first().json.chatInput }}` |
| `output` | String | 📋 `{{ $json.output.split('\n---')[0].trim() }}` |
| `tools_used` | String | 📋 `{{ $json.output.includes('Tools used:') ? $json.output.split('Tools used:').pop().trim() : 'unknown' }}` |

**Qué decir:**

> "Fíjate en dos cosas: `output` corta todo lo que hay después de `---` — así el usuario del chat no ve la línea de logging. Y `tools_used` extrae lo que viene después de 'Tools used:'. Si el agente no incluye esa línea, ponemos 'unknown'."

### Añadir Log to Google Sheets

1. Añadir **Google Sheets** después de Prepare Log → renombrar a `Log to Google Sheets`
2. Configurar:

| Campo | Valor |
|-------|-------|
| **Operation** | Append Row |
| **Document** | (pegar la URL de tu Google Sheet) |
| **Sheet** | Sheet1 |
| **Mapping Mode** | Auto-Map Input Data |

3. **Importante:** En el nodo, activar **Settings** → **Continue On Error** → para que si Google Sheets falla, el chat siga respondiendo

4. Conectar: Agent → Prepare Log → Log to Google Sheets → Output

### Probar y revisar la Sheet

1. Ejecutar varias conversaciones en el chat
2. Abrir la Google Sheet — debería verse algo así:

| session_id | timestamp | input | output | tools_used |
|------------|-----------|-------|--------|------------|
| abc-123 | 2025-02-04 15:30:22 | Quiero hacer pollo | ¿Qué edades tienen tus hijos?... | none |
| abc-123 | 2025-02-04 15:31:05 | 5 y 9 años | Aquí tienes la receta... | Recipe Search |
| abc-123 | 2025-02-04 15:32:18 | ¿Y croquetas? | Aquí tienes las croquetas... | Google Search |

**Qué decir:**

> "Mirad la Sheet. En la primera respuesta no usó ninguna herramienta — solo preguntó las edades. En la segunda usó Recipe Search. En la tercera, Google Search. Esto es lo que pasa dentro del agente y normalmente es invisible."
>
> "¿Es perfecto? No. La columna `tools_used` es lo que el agente *dice* que usó, no lo que *realmente* usó. Si queréis la traza real, podéis hacer click en el nodo del agente en n8n y ver cada paso. Pero para un dashboard rápido, esto funciona."

---

### Diagrama final

```
┌──────────────┐     ┌──────────────────────┐     ┌─────────────┐     ┌────────────────┐     ┌──────────┐
│    Chat      │────▶│   Recipe Chat        │────▶│ Prepare Log │────▶│ Log to Google  │────▶│  Output  │
│   Trigger    │     │   Agent              │     │   (Set)     │     │    Sheets      │     │          │
└──────────────┘     └──────────────────────┘     └─────────────┘     └────────────────┘     └──────────┘
                              ┊ sub-nodes
                     ┌────────┼────────┬────────┐
                     ┊        ┊        ┊        ┊
                Chat Model  Memory  Recipe    Google
                                    Search    Search
                                  (TheMealDB) (SerpAPI)
```

**Workflow expandido:** `expanded_workflows/01_recipe_chat_agent.json`

---

---

# PARTE 3 — Bonus: compartir con la clase (demo en vivo)

**Objetivo:** Que los alumnos puedan interactuar con el workflow desde su navegador o desde Telegram. Dos opciones según el nivel de la clase.

---

## Qué es ngrok

**Para explicar a los alumnos:**

> "Cuando ejecutáis n8n en vuestro ordenador, está en `localhost:5678`. Eso significa que solo vosotros podéis acceder. Si yo quiero que vosotros abráis mi workflow, necesito hacer que mi `localhost` sea accesible desde internet. Eso es lo que hace ngrok."
>
> "ngrok crea un túnel: conecta una URL pública temporal (tipo `https://abc123.ngrok-free.app`) con vuestro `localhost:5678`. Mientras ngrok esté corriendo, cualquiera con esa URL puede acceder a vuestro n8n."

### Instalar ngrok

1. Ir a [ngrok.com](https://ngrok.com/) → **Sign up** (gratis)
2. Descargar para tu OS:

**macOS (Homebrew):**
```bash
brew install ngrok
```

**O descarga directa:** [ngrok.com/download](https://ngrok.com/download)

3. Conectar tu cuenta (una sola vez):
```bash
ngrok config add-authtoken TU_TOKEN_AQUI
```
(El token aparece en el dashboard de ngrok después de registrarte)

### Usar ngrok

```bash
# Terminal 1: arrancar n8n
n8n start

# Terminal 2: crear el túnel
ngrok http 5678
```

ngrok muestra algo como:
```
Forwarding   https://a1b2c3d4.ngrok-free.app -> http://localhost:5678
```

Esa URL (`https://a1b2c3d4.ngrok-free.app`) es tu n8n accesible desde internet. Cambia cada vez que arrancas ngrok.

> **Importante:** Para que n8n use correctamente esta URL en webhooks, arranca n8n con la variable de entorno:
> ```bash
> WEBHOOK_URL=https://a1b2c3d4.ngrok-free.app n8n start
> ```
> Sustituye la URL por la que te dé ngrok.

> **n8n Cloud:** Si usas n8n Cloud, **no necesitas ngrok**. Tu instancia ya tiene una URL pública (tipo `https://tu-nombre.app.n8n.cloud`). Todo lo que viene abajo funciona directamente.

---

## Opción A: Compartir el Chat Trigger (sin instalar nada)

La forma más rápida. Los alumnos abren una URL en el navegador y ven un chat.

### Cómo funciona

El Chat Trigger de n8n genera una interfaz de chat en una URL. Cuando el workflow está **activado**, esa URL es pública:

```
https://TU_URL/webhook/WEBHOOK_ID/chat
```

### Pasos

1. Abrir el workflow de la Parte 1 o Parte 2 (el que tenga Chat Trigger)
2. **Activar el workflow** (toggle "Active" en la esquina superior derecha)
3. Click en el nodo **Chat Trigger**
4. En el panel derecho, buscar la **Production URL** — copiarla
5. Compartir esa URL con los alumnos (proyectar en pantalla, enviar por el chat de clase, etc.)

### Con n8n Cloud

Si usas n8n Cloud, la URL ya funciona. Los alumnos la abren y ven el chat. No necesitas nada más.

```
https://tu-nombre.app.n8n.cloud/webhook/WEBHOOK_ID/chat
```

### Con n8n local + ngrok

1. Arrancar ngrok: `ngrok http 5678`
2. Arrancar n8n con la URL de ngrok:
```bash
WEBHOOK_URL=https://a1b2c3d4.ngrok-free.app n8n start
```
3. Activar el workflow en n8n
4. La URL de chat sería:
```
https://a1b2c3d4.ngrok-free.app/webhook/WEBHOOK_ID/chat
```
5. Compartir esa URL

### Probar

1. Abrir la URL en el navegador (o en el móvil)
2. Escribir `chicken` o `lasagna`
3. Ver que el workflow se ejecuta y responde en el chat

**Qué decir:**

> "Esto es exactamente como funciona un chatbot en producción. Una URL pública, un Chat Trigger que escucha, y un workflow que procesa. La diferencia con ChatGPT o similares es que vosotros controláis todo el pipeline: qué busca, cómo transforma, qué devuelve."

---

## Opción B: Bot de Telegram

Más impresionante para la clase: los alumnos abren Telegram en su móvil y hablan con un bot. El workflow responde automáticamente.

### Crear el bot en Telegram (5 minutos, solo el profesor)

1. Instalar Telegram ([telegram.org](https://telegram.org/)) en el móvil o desktop
2. Buscar `@BotFather` en Telegram → abrir el chat
3. Enviar `/newbot`
4. BotFather pregunta el nombre → escribir: `Recetas UCM` (o lo que quieras)
5. BotFather pregunta el username → escribir: `recetas_ucm_bot` (debe ser único y terminar en `bot`)
6. BotFather responde con un **token** tipo:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```
7. Copiar ese token — lo necesitas para n8n

> El username del bot determina el link para compartir: `t.me/recetas_ucm_bot`

### Configurar la credencial en n8n

1. Abrir n8n → ir a **Settings → Credentials**
2. Click **Add Credential** → buscar "Telegram"
3. En **Access Token**, pegar el token de BotFather
4. **Save**

### El workflow

Mismo concepto que la Parte 1, pero con Telegram Trigger y Telegram Send:

```
Telegram      HTTP Request     Input       Step 1      Step 2      Step 3      Telegram
Trigger  ───▶ (TheMealDB) ───▶ Recipe ───▶ Simplify ─▶ Kids ────▶ Shopping ─▶  Send
   │                              │
   │                         (si no hay resultados)
   │                              │
   │                              ▼
   │                        Telegram Send
   │                       ("Recipe not found")
```

1. Importar el workflow: `expanded_workflows/01_prompt_chaining_telegram.json`
2. En los nodos **Telegram Trigger** y **Telegram Send**, seleccionar la credencial de Telegram
3. **Activar el workflow** (toggle Active)

> **Requisito:** n8n debe ser accesible desde internet (ngrok o n8n Cloud). Telegram envía webhooks a tu n8n cuando alguien escribe al bot.

### Guardrails (proteger contra abusos)

1. **Modelo gratuito (DeepSeek):** coste = 0, no necesitas más protección de tokens
2. **Filtro de resultados:** el workflow incluye un If node que comprueba si TheMealDB devolvió resultados. Si no, responde "No encontré esa receta" sin llamar a los LLMs (ahorra tokens si el modelo no es gratuito)
3. **Si quieres más protección:** añadir un If node al principio que rechace mensajes muy largos (`{{ $json.message.text.length > 200 }}`) o que no contengan palabras de comida

### Activar y compartir con la clase

1. Asegurarse de que ngrok está corriendo (o usar n8n Cloud)
2. En n8n, activar el workflow
3. Proyectar en pantalla o compartir: `t.me/recetas_ucm_bot`
4. Los alumnos abren el link → click **Start** → escriben un plato → el bot responde

**Qué decir:**

> "Escribid un nombre de plato en inglés — 'chicken', 'pasta', 'beef stew'. El bot busca la receta, la simplifica, la adapta para niños, y os devuelve la lista de la compra. Todo automático."
>
> "Esto es un workflow de n8n corriendo en mi portátil, conectado a internet con ngrok, respondiendo a Telegram. En producción lo pondríais en un servidor y funcionaría 24/7."

### Después de la clase

1. Desactivar el workflow en n8n (toggle Active off)
2. Cerrar ngrok (Ctrl+C)
3. El bot deja de responder — no gasta nada

**Workflow:** `expanded_workflows/01_prompt_chaining_telegram.json`

---

## Qué decir al cerrar

> "Hemos ido de un workflow estático a algo que cualquiera puede usar desde su móvil:"
>
> "1. Prompt Chaining: tres LLMs en cadena, cada uno transforma el resultado del anterior"
> "2. HTTP Request: conectamos el workflow a internet para buscar recetas reales"
> "3. Agent con herramientas: el agente decide qué herramienta usar según la pregunta"
> "4. Compartir: Chat Trigger como URL pública, o Telegram para que cualquiera pueda usarlo"
>
> "La diferencia clave: en Prompt Chaining tú controlas cada paso. Con un Agent, tú defines las reglas y el agente decide. Y con buenas tool descriptions, el agente elige la herramienta correcta."

---

## Cheat Sheet — AI Agent (referencia rápida para la clase)

### Dónde va cada cosa

| Qué | Dónde se configura | Para qué |
|-----|-------------------|----------|
| Comportamiento general del agente | **System Message** (Agent → Options → System Message) | Reglas, personalidad, cuándo usar cada tool |
| Qué hace una tool concreta | **Tool Description** (dentro de cada sub-nodo tool) | El agente lee esto para decidir si/cuándo usarla |
| Qué parámetros necesita la tool | **Placeholder Definitions** (dentro del HTTP Request Tool) | El agente sabe qué valores pasar |
| Cómo se llama la tool | **Name** (primer campo de cada tool) | Debe coincidir con el nombre en el system prompt |

### Nombres que deben coincidir

| En el System Prompt dice... | El campo Name de la tool debe ser... |
|-----------------------------|--------------------------------------|
| "use Recipe Search (TheMealDB)" | `Recipe Search` |
| "use Google Search" | `Google Search` |

### Líneas sólidas vs punteadas

| Tipo | Qué conecta | Ejemplo |
|------|-------------|---------|
| **Sólida** → | Flujo de datos principal | Chat Trigger → Agent → Output |
| **Punteada** ┄ | Sub-nodo del Agent | Agent ┄ Chat Model, Agent ┄ Memory, Agent ┄ Tool |

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| **"Invalid URL" en Recipe Search** | **Error más común.** Verificar: 1) ✨ activado en el campo URL, 2) Description rellena (no vacía), 3) Placeholder definido. Si el banner "No parameters are set up to be filled by AI" aparece, falta el ✨ |
| **Recipe Search recibe "5 años" o texto del usuario** | El ✨ no está activado en la URL. Sin ✨, n8n pasa el chatInput crudo a la tool en vez de dejar que el agente construya la URL |
| El agent no recuerda la conversación anterior | Verificar que **Memory** (Window Buffer Memory) está conectada con línea punteada. Sin memoria, cada mensaje se trata como independiente |
| El chat no responde | Verificar que Chat Trigger tiene Response Mode = `Last Node` |
| El chat muestra JSON en vez de texto | El último nodo (Output) debe tener un campo llamado exactamente `output` |
| TheMealDB no devuelve resultados | Probar con términos en inglés (`chicken`, `pasta`, `lasagna`) |
| SerpAPI da error 401 | Verificar credencial en Settings → Credentials |
| El agent no usa las tools | Verificar que las tools están conectadas con **línea punteada** (no sólida) y que la Description no está vacía |
| El agent usa la tool incorrecta | Verificar que los nombres (`Name`) coinciden con el system prompt |
| El agent siempre usa Google en vez de TheMealDB | Revisar las tool descriptions — Recipe Search debe ir primero |

### Chat Trigger compartido

| Problema | Solución |
|----------|----------|
| La URL del Chat Trigger no funciona para otros | El workflow debe estar **activado** (Active on). La URL de test solo funciona durante la ejecución manual |
| "502 Bad Gateway" al abrir la URL | ngrok está corriendo pero n8n no. Verificar que n8n está arrancado |
| Los alumnos ven una página en blanco | Verificar que la URL termina en `/chat`. Sin `/chat`, el webhook existe pero no muestra la interfaz |

### ngrok

| Problema | Solución |
|----------|----------|
| `command not found: ngrok` | Instalar con `brew install ngrok` o descargar de ngrok.com/download |
| `ERR_NGROK_xxx` al arrancar | Verificar que el authtoken está configurado: `ngrok config add-authtoken TOKEN` |
| La URL cambia cada vez | Normal en el plan gratuito. Si necesitas URL fija, ngrok tiene plan de pago ($8/mes) o usar n8n Cloud |
| Los webhooks de n8n no usan la URL de ngrok | Arrancar n8n con `WEBHOOK_URL=https://xxx.ngrok-free.app n8n start` |

### Telegram

| Problema | Solución |
|----------|----------|
| El bot no responde | Verificar: 1) workflow activado, 2) ngrok corriendo, 3) `WEBHOOK_URL` configurado |
| "Unauthorized" al configurar credencial | El token de BotFather es incorrecto. Ir a @BotFather → `/mybots` → copiar token de nuevo |
| Telegram Trigger no se activa | Telegram necesita enviar webhooks a n8n. Si n8n no es accesible desde internet, el trigger no funciona |
| El bot responde dos veces | Puede haber dos workflows activos con el mismo Telegram Trigger. Desactivar el duplicado |
| Mensaje muy largo (> 4096 chars) | Telegram tiene límite de 4096 caracteres por mensaje. Si la respuesta es más larga, se trunca. Reducir la longitud en los prompts |
