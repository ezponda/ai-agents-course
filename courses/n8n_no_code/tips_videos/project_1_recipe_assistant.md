# Guion — Project 1: Recipe Assistant (workflow `10_recipe_assistant.json`)

## Concepto clave
Un workflow completo que combina todo lo visto en el curso: agent con tools, memoria, formulario de revisión humana, branching condicional, y un segundo agent que busca precios reales en Google.

## Flujo del workflow
```
Chat Trigger → Recipe Search Agent → Review Recipe (Form) → Want Prices? (IF)
                    ┊                                           │
         ┌──────────┼──────────┐                   Yes ─────────┼──▶ Shopping List Agent → Output — With Prices
         ┊          ┊     ┊    ┊                                │         ┊
    Chat Model  Memory  HTTP  SerpAPI              No ──────────┼──▶ Output — Recipe Only
                      (MealDB) (fallback)                            ┊
                                                              Chat Model + Price Search (SerpAPI)
```

**Credenciales necesarias:** OpenRouter + SerpAPI

---

## 🔧 Preparación ANTES de grabar

1. **Cuota SerpAPI:** entra en tu dashboard de serpapi.com y comprueba las búsquedas que te quedan este mes — cada demo con lista de compras gasta 1-2.
2. **Ejecución completa de prueba** (receta → formulario → lista con precios): calienta el flujo y confirma que las credenciales funcionan antes de grabar.
3. **TheMealDB en 10 segundos:** `curl "https://www.themealdb.com/api/json/v1/1/search.php?s=chicken"` — te evita descubrir en directo que la API está caída.
4. **Durabilidad — modelos:** no te recrees en `gpt-4o-mini` a cámara; di "un modelo rápido y barato — el que tengáis configurado". Los nombres de modelos caducan antes que el vídeo.
5. **Durabilidad — UI:** nombra funciones, no posiciones ("el botón **Chat** del editor", no "abajo a la derecha"); n8n mueve botones entre versiones. Verifica también los nombres de nodo en TU versión (la memoria hoy se llama **Simple Memory**; antes *Window Buffer Memory*).

---

## 🎬 Guion paso a paso (comentando el workflow importado)

### 0. Cold open (opcional, 40s)

**Empezar con el resultado final de una ejecución anterior en pantalla: la receta + la lista de la compra con precios.**

> "Esto es un asistente de recetas montado en n8n sin una línea de código: busca recetas reales en internet, me deja revisarlas en un formulario y, si quiero, me genera la lista de la compra con precios reales sacados de Google. Vamos a verlo por dentro, nodo a nodo."

---

### 1. Introducción — Qué vamos a ver (30s)

> "Este es el Project 1 del curso. Combina casi todo lo que habéis visto: un agent con herramientas, memoria, un formulario para que el humano revise, y un segundo agent que busca precios reales por internet. Vamos a recorrer el workflow nodo a nodo."

**Abrir el workflow importado y hacer zoom out para que se vea entero.**

---

### 2. Chat Trigger — El punto de entrada (30s)

**Click en "When chat message received".**

> "A diferencia de los workflows anteriores que usaban Manual Trigger, aquí usamos Chat Trigger. Esto habilita el botón **Chat** del editor, que abre una ventanita donde podemos escribir como si fuera ChatGPT. Cada mensaje que enviamos genera una ejecución."

**Dato interesante:** "Como tiene `responseMode: lastNode`, el chat espera a que el ÚLTIMO nodo del flujo devuelva la respuesta. Si elegimos generar la lista de compras, el chat no responde hasta que TODO el flujo termina."

---

### 3. Recipe Search Agent — El cerebro del workflow (2 min)

**Click en "Recipe Search Agent". Mostrar las 4 conexiones de abajo: Chat Model, Memory, Recipe Search, Google Search.**

> "Este agent tiene cuatro cosas conectadas por debajo. Vamos a verlas una a una."

#### 3a. System Message

**Click en Options → System Message.**

> "El system message le dice al agent tres cosas importantes:"

1. **Traducción automática:** "Convierte la petición a inglés antes de buscar. Si el alumno escribe 'quiero pollo', el agent busca 'chicken'. TheMealDB solo entiende inglés."

2. **Estrategia de fallback:** "Usa primero Recipe Search (TheMealDB), que devuelve datos estructurados. Solo usa Google Search si TheMealDB no encuentra nada — o sea, si `meals` es `null`."

3. **Formato de respuesta:** "Le damos un formato exacto: nombre, categoría, ingredientes con cantidades, instrucciones. Esto es importante porque luego el segundo agent necesita leer esos ingredientes para la lista de compras."

#### 3b. Memory

**Click en Simple Memory.**

> "Simple Memory — el Window Buffer de toda la vida — con 10 mensajes. Gracias a esto podemos tener una conversación: 'busca pollo', luego 'ahora dame una receta de pasta', y el agent recuerda el contexto."

**Dato interesante:** "El Session ID usa `$json.sessionId`, que viene del Chat Trigger. Cada ventana de chat tiene su propia conversación."

#### 3c. HTTP Request Tool — Recipe Search

**Click en Recipe Search. Mostrar la configuración.**

> "Esta es la primera vez que usamos el HTTP Request Tool. Permite que el agent llame a cualquier API de internet."

**Señalar estos campos:**

- **URL:** `https://www.themealdb.com/api/json/v1/1/search.php` — "La URL es fija, sin parámetros."
- **Query Parameters:** "Aquí está la magia. El parámetro `s` tiene un valor con `$fromAI()`. Esto le dice al agent: 'tú decides qué valor poner aquí'. Si el usuario pide chicken, el agent rellena `s=chicken` y la URL final es `search.php?s=chicken`."
- **Tool Description:** "Importante: la descripción le dice al agent CUÁNDO usar esta herramienta y QUÉ esperar. Fíjaos que dice 'If the response contains meals:null, no recipes were found'. Esto le ayuda a decidir si probar Google."
- **Optimize Response:** "Reduce el JSON de respuesta para gastar menos tokens."

**Dato interesante:** "TheMealDB es gratis y no necesita API key. El `1` en la URL es la key de prueba que ellos proporcionan."

#### 3d. Google Search (SerpAPI) — Fallback

**Click en Google Search.**

> "SerpAPI es el plan B. Si TheMealDB no tiene la receta (por ejemplo, un plato muy específico), el agent busca en Google. Esto ya lo vimos en el capítulo de AI Agents."

---

### 4. Review Recipe — El formulario humano (1.5 min)

**Click en "Review Recipe".**

> "Después de que el agent encuentra la receta, el workflow se PAUSA aquí. Este es un Wait node configurado como formulario. Es el mismo patrón de Human-in-the-Loop que vimos antes, pero con un formulario web."

**Señalar los campos del formulario:**

- **Recipe (HTML):** "Muestra la receta en formato legible. Usa `$json.output` que es la respuesta del agent."
- **Generate shopping list? (Dropdown):** "Aquí el humano decide: quiero lista de compras con precios, o solo la receta."

> "Para probarlo: cuando ejecutéis el workflow, el chat no va a responder inmediatamente. Tenéis que ir al nodo Review Recipe en el panel de ejecución, copiar la Test URL, y abrirla en el navegador. Ahí veréis el formulario."

**Dato interesante:** "Este patrón es súper útil en producción: el AI draft, el humano revisa. Nunca dejéis que un agent envíe algo directamente sin revisión humana."

---

### 5. Want Prices? — Branching condicional (30s)

**Click en "Want Prices?".**

> "Un IF simple. Si el usuario eligió 'Yes, with price estimates', va por arriba hacia el Shopping List Agent. Si eligió 'No', va directamente al Output — Recipe Only."

**Señalar la expresión:** `$json["Generate shopping list?"]`

> "Fíjaos que el nombre del campo del formulario se usa tal cual como clave del JSON. Los espacios y el interrogante son parte del nombre."

---

### 6. Shopping List Agent — Precios reales (1.5 min)

**Click en "Shopping List Agent".**

> "Aquí es donde se pone interesante. Esto NO es un Basic LLM Chain como los que hemos visto antes. Es un SEGUNDO agent, con su propia herramienta: SerpAPI para buscar precios en Google."

#### 6a. Por qué un agent y no un LLM Chain

> "Un LLM Chain simplemente genera texto. Si le pides precios, se los inventa — 'realistic estimates based on 2024 averages'. Un agent puede BUSCAR esos precios en Google, así que son datos reales."

#### 6b. System Message

**Click en Options → System Message.**

> "El prompt le dice al agent algo clave: que agrupe los ingredientes en UNA sola búsqueda. En vez de buscar 'price chicken', 'price tomatoes', 'price onions' — una búsqueda por ingrediente, que gastaría mucha API — busca 'grocery store prices chicken breast tomatoes onions' todo junto. Máximo 2 búsquedas."

**Señalar:** "Los ingredientes que no encuentra los marca con `≈` para que el usuario sepa cuáles son estimados y cuáles son reales."

#### 6c. Prompt — Referencia a otro nodo

**Señalar la expresión del prompt:** `$('Recipe Search Agent').first().json.output`

> "Esto es importante: después del Wait node, `$json` contiene los datos del formulario, NO la receta. Para acceder a la receta tenemos que referenciar el nodo del agent anterior por nombre. Esta expresión dice: 've al Recipe Search Agent, coge su primer output, y dame el campo output'."

#### 6d. Price Search (SerpAPI)

**Click en Price Search.**

> "Misma herramienta SerpAPI que ya tenéis configurada. El agent la usa para buscar precios actuales de supermercado."

---

### 7. Output nodes (30s)

**Click en "Output — With Prices".**

> "Si se generó lista de compras, este nodo combina la receta original con la lista. Usa la misma expresión `$('Recipe Search Agent')` para la receta, y `$json.output` para la lista del Shopping List Agent."

**Click en "Output — Recipe Only".**

> "Si el usuario dijo que no quería lista de compras, simplemente pasa la receta tal cual."

---

### 8. DEMO en vivo (3 min)

> "Vamos a probarlo. Click en el botón **Chat** del editor."

**Escribir en el chat:**

```
I want a chicken recipe
```

**Mientras trabaja (mirad el canvas, no el chat):**
> "Ojo: el chat se va a quedar 'pensando' y no va a decir nada todavía — está configurado para responder solo cuando TODO el flujo termina. El progreso lo vemos aquí en el canvas: el agent está llamando a TheMealDB con 'chicken'."

**Cuando la ejecución se pausa en Review Recipe:**
> "El workflow se ha parado en el formulario. Fijaos: la receta NO está en el chat — la vamos a ver dentro del formulario."

**Ir al nodo Review Recipe → copiar la Test URL → abrirla en el navegador.** (En versiones recientes n8n abre el formulario automáticamente al llegar al nodo — si lo hace, mejor.)

> "Aquí está la receta, dentro del formulario. Voy a elegir 'Yes, with price estimates' y pulsar Continue."

**Volver a n8n y esperar el resultado final.**

> "Ahora el Shopping List Agent está buscando precios en Google... Y aquí tenemos la lista de compras con precios reales."

**Volver al chat: ahora sí aparece la respuesta completa (receta + lista con precios) — la primera y única respuesta del chat en toda la ejecución.**

---

### 9. Demo — Follow-up con memoria (1 min)

**Escribir en el chat (sin cerrar la sesión):**

```
Now find me a pasta recipe
```

> "Gracias a la memoria, el agent recuerda que estamos buscando recetas. No hace falta repetir contexto."

---

### 10. Demo — Fallback a Google (opcional, 1 min)

**Escribir en el chat:**

```
How do I make Spanish fabada asturiana?
```

> "Fabada asturiana probablemente no está en TheMealDB, que tiene unas 300 recetas en inglés. Vamos a ver si el agent activa el fallback a Google..."

**Expandir execution details para ver qué tools se usaron.**

> "Veis: primero intentó TheMealDB, recibió `meals: null`, y luego buscó en Google. Eso es la estrategia de fallback funcionando."

---

### 11. Cierre — Qué combina este proyecto (30s)

> "Recapitulemos lo que habéis visto:"

- **HTTP Request Tool** — el agent llama a una API real (TheMealDB)
- **`$fromAI()`** — el agent rellena los parámetros dinámicamente
- **Fallback strategy** — primero TheMealDB, luego Google
- **Memoria** — conversación multi-turno
- **Wait + Form** — humano revisa antes de continuar
- **IF branching** — camino diferente según la elección del usuario
- **Segundo agent con búsqueda** — precios reales, no inventados
- **`$('Node').first().json.output`** — referenciar nodos anteriores después de un Wait

> "Es el workflow más completo del curso. Combina casi todos los patrones que habéis aprendido en un solo proyecto funcional."

---

## 🎬 PARTE 2 — Variaciones (para alargar el vídeo)

Cinco variaciones autocontenidas, ordenadas de menos a más montaje. Elige las que quieras — con la **2 + 3 + 4** añades ~12 min de vídeo con chicha. Si grabas variaciones, colócalas **antes del cierre** (sección 11) y guarda el cierre para el final.

> ⚠️ **Al terminar de grabar:** las variaciones ensucian el workflow. Revierte o reimporta el JSON limpio del curso, que es el que descargan los alumnos.

---

### Variación 1 — ¿Qué pasa sin memoria? (2 min, sin config)

**Qué enseña:** qué hace la memoria de verdad, mostrándolo por ausencia.

**Pasos:**
1. **Desconecta** el nodo Simple Memory del agent (borra la línea de puntos; no borres el nodo).
2. En el chat: `I want a chicken recipe` → responde normal.
3. En el mismo chat: `What recipe did you just give me?`

> "Sin memoria, cada mensaje es una conversación nueva. El agent no tiene ni idea de qué le acabo de preguntar — no es que 'se le olvide': es que nunca lo supo."

4. **Reconecta** la memoria y repite la segunda pregunta → ahora sí.

> "Esto es todo lo que hace la memoria: reinyectar los últimos mensajes en cada llamada. Sin ella no hay conversación, hay preguntas sueltas."

**Revertir:** ya está revertido al reconectar.

---

### Variación 2 — Agent vs Basic LLM Chain: los precios inventados (4 min)

**Qué enseña:** POR QUÉ el Shopping List es un agent y no un chain — viéndolo fallar. Es la demostración práctica de la sección 6a.

**Pasos:**
1. Añade un nodo **Basic LLM Chain** → renómbralo `Shopping List (Chain)`.
2. Conéctale el **OpenRouter Chat Model** existente (línea de puntos).
3. Configúralo:
   - **Source for Prompt:** `Define below`
   - **Prompt** (Expression) — copia y pega:
     ```
     {{ $('Recipe Search Agent').first().json.output }}
     ```
   - Añade un **System Message** (Add prompt → System) — copia y pega:
     ```
     You are a shopping assistant. From the recipe provided, create a complete shopping list with estimated US grocery prices.

     Rules:
     - Include exact quantities from the recipe
     - Group items by store section (Produce, Meat / Fish, Dairy, Pantry)
     - End with an estimated total
     - Output ONLY the shopping list
     ```
4. **Recablea temporalmente:** desconecta la salida **true** de `Want Prices?` del Shopping List Agent y conéctala a `Shopping List (Chain)`.
5. Demo: `I want a chicken recipe` → formulario → `Yes, with price estimates`.
6. Abre el output del chain en el panel:

> "Fijaos: lista perfecta, precios de aspecto razonable... e inventados TODOS. Un chain no puede buscar — no tiene herramientas. Genera texto plausible, que es justo lo peligroso. El agent de verdad, con SerpAPI, va a Google y trae precios reales."

7. Señala de paso el campo de salida: "Y otro detalle: el chain deja su respuesta en `text`, no en `output` — si dejáramos esto conectado, el nodo Output se rompería. Chain → `text`, Agent → `output`. Os lo dije en Core Concepts y aquí muerde de verdad."

**Revertir:** reconecta la salida true del IF al **Shopping List Agent** (el chain puede quedarse desconectado en el canvas o borrarse).

**Bonus:** esta variación no gasta SerpAPI.

---

### Variación 3 — Nueva herramienta: Random Recipe (4 min)

**Qué enseña:** añadir una herramienta a un agent existente y ver cómo DECIDE usarla (es el Challenge 1 del notebook — díselo a los alumnos).

**Pasos:**
1. En el **Recipe Search Agent** → **+ Tool** → **HTTP Request Tool** → renómbrala `Random Recipe`.
2. Configúrala:

| Campo | Valor |
|-------|-------|
| **Method** | `GET` |
| **URL** | `https://www.themealdb.com/api/json/v1/1/random.php` |
| **Send Query Parameters** | OFF (no necesita parámetros — esa es la gracia) |
| **Optimize Response** | ON |

3. **Description** — copia y pega:
   ```
   Returns one random recipe from TheMealDB. Takes no input. Use this only when the user asks to be surprised or wants a random recipe.
   ```
4. En el **System Message** del agent, añade esta línea como punto 4 de la sección "Searching for recipes" — copia y pega:
   ```
   4. If the user asks to be surprised or wants a random pick, use Random Recipe (it takes no input)
   ```
5. Demo: `Surprise me!`

> "No he tocado ni una línea de lógica — le he dado una herramienta nueva con una buena descripción y una regla en el prompt. El agent solo elige Random Recipe cuando la petición es 'sorpréndeme'. Miradlo en los logs: para 'I want chicken' sigue usando la búsqueda normal."

6. Segunda demo de contraste: `I want a chicken recipe` → en los logs, verifica que usa Recipe Search y NO Random Recipe.

**Revertir:** opcional — esta variación puede quedarse (coincide con el Challenge 1); si la dejas, deja también la línea 4 del prompt.

---

### Variación 4 — Cambiar un nodo por otro: IF → Switch, con tercera opción (5-6 min)

**Qué enseña:** el Switch como generalización del IF (capítulo de Routing), y cuándo basta un chain (sin herramientas, no gasta SerpAPI).

**Pasos:**
1. En el formulario **Review Recipe**, añade una tercera opción al dropdown `Generate shopping list?` — copia y pega:
   ```
   Just the list, no prices
   ```
2. Añade un nodo **Switch** → renómbralo `Route Choice`. Tres reglas, todas sobre la misma expresión — copia y pega en **Left Value** de cada regla:
   ```
   {{ $json["Generate shopping list?"] }}
   ```

| Regla | Operación | Right Value (copia y pega) | Renombra la salida |
|-------|-----------|---------------------------|--------------------|
| 1 | equals | `Yes, with price estimates` | `prices` |
| 2 | equals | `Just the list, no prices` | `list` |
| 3 | equals | `No, just the recipe` | `recipe` |

3. Añade un **Basic LLM Chain** → renómbralo `Shopping List — No Prices`. Conéctale el **OpenRouter Chat Model** (línea de puntos). Configuración:
   - **Source for Prompt:** `Define below`
   - **Prompt** (Expression) — copia y pega:
     ```
     {{ $('Recipe Search Agent').first().json.output }}
     ```
   - **System Message** — copia y pega:
     ```
     You are a shopping assistant. From the recipe provided, extract a complete shopping list.

     Rules:
     - Include exact quantities from the recipe
     - Group items by store section (Produce, Meat / Fish, Dairy, Pantry)
     - Skip items most kitchens already have (salt, pepper, cooking oil)
     - No prices
     - Output ONLY the shopping list
     ```
4. Añade un **Edit Fields** → renómbralo `Output — List Only`, con un campo String:
   - `output` (Expression) — copia y pega:
     ```
     {{ $('Recipe Search Agent').first().json.output + '\n\n---\n\n' + $json.text }}
     ```
5. **Recablea:** `Review Recipe` → `Route Choice`; salida `prices` → Shopping List Agent; salida `list` → `Shopping List — No Prices` → `Output — List Only`; salida `recipe` → Output — Recipe Only. (El IF `Want Prices?` queda desconectado — no lo borres hasta el final del vídeo.)
6. Demo: receta → formulario → elige `Just the list, no prices`.

> "Tres decisiones ya no caben en un IF — para eso está el Switch: mismas expresiones, N salidas. Y fijaos en la rama nueva: para extraer la lista SIN precios no hace falta buscar nada, así que basta un Basic LLM Chain — más barato y más rápido que un agent. Herramientas solo cuando hacen falta."

7. Señala el `$json.text` del Output — List Only: "el chain responde en `text`, por eso este Output es distinto de los otros dos."

**Revertir:** vuelve a conectar `Review Recipe` → `Want Prices?` y quita la tercera opción del formulario (o reimporta el JSON limpio).

---

### Variación 5 — El prompt manda: formato y idioma (3 min, solo prompt)

**Qué enseña:** cambiar el comportamiento sin tocar ni un nodo — solo el system message.

**Pasos:**
1. Abre el **System Message** del Recipe Search Agent y sustitúyelo ENTERO por este — copia y pega:
   ```
   You are a friendly recipe assistant that helps users find recipes.

   Searching for recipes:
   1. Convert the user's request to a simple English search term for the tool (e.g. "quiero pollo" → search for "chicken", "pasta con tomate" → search for "tomato pasta")
   2. Use Recipe Search (TheMealDB) first — it returns structured, reliable data
   3. Only use Google Search if TheMealDB returns no results (meals is null)

   Presenting recipes — use this format:
   RECIPE: [name]
   Category: [category] | Cuisine: [cuisine]
   Difficulty: [easy/medium/hard] | Time: [estimated total minutes]

   INGREDIENTS:
   - [quantity] [ingredient]
   - [quantity] [ingredient]
   ...

   INSTRUCTIONS:
   1. [step]
   2. [step]
   ...

   Rules:
   - Never invent recipes — only present what you find from tools
   - Include ALL ingredients with exact quantities from the source
   - If no results, suggest alternative search terms
   - Always reply in the same language the user wrote in (translate the recipe if needed)
   ```
   (Son dos cambios sobre el original: la línea `Difficulty/Time` en el formato, y la última regla de idioma.)
2. Demo en español: `Quiero una receta con pollo`

> "Mismo workflow, mismos nodos. He añadido dos líneas al prompt: ahora estima dificultad y tiempo, y responde en el idioma del usuario — busca en inglés por dentro, pero me contesta en español. El 80% de estos sistemas es el prompt."

**Ojo:** `Difficulty` y `Time` los estima el modelo (TheMealDB no los trae) — dilo en voz alta, conecta con la lección de 'datos reales vs generados'.

**Revertir:** restaura el system message original (está en el notebook y en el JSON del curso).

---

## 🧪 Textos de prueba (copy-paste para el chat)

**Pollo (demo principal):**
```
I want a chicken recipe
```

**Pasta (follow-up para demostrar memoria):**
```
Now find me a pasta recipe
```

**Plato específico:**
```
How do I make beef stroganoff?
```

**Postre:**
```
Find me a chocolate dessert
```

**Fallback a Google (plato que no está en TheMealDB):**
```
How do I make Spanish fabada asturiana?
```

**En español (para demostrar traducción automática):**
```
Quiero hacer algo con pescado
```

**Aleatorio/vago (el agent elige):**
```
Surprise me with something Italian
```

---

## ⚠️ Cosas a tener en cuenta durante la grabación

1. **El formulario tarda:** Después de que el agent responde, hay que ir al nodo Review Recipe, copiar la Test URL y abrirla en el navegador. Esto puede parecer lento en el vídeo — avisa a los alumnos de que es normal. (En versiones recientes n8n abre el formulario solo al llegar al nodo.)

2. **SerpAPI tiene límite:** el free tier tiene un tope mensual de búsquedas (100/mes al escribir esto — compruébalo en tu dashboard). Cada ejecución del Shopping List Agent usa 1-2 búsquedas. Si haces muchas demos seguidas, puedes llegar al límite.

3. **TheMealDB es limitada:** ~300 recetas en inglés. Si buscas algo muy específico o en otro idioma, probablemente caerá al fallback de Google.

4. **Los precios del Shopping List Agent:** Son reales pero aproximados — vienen de resultados de Google, no de una API de supermercado. El agent marca con `≈` los que estima por su cuenta.

5. **Dos credenciales SerpAPI:** El workflow usa SerpAPI en DOS sitios (Google Search como fallback del Recipe Agent, y Price Search para el Shopping List Agent). Ambos usan la misma credencial, pero cuentan como búsquedas separadas.
