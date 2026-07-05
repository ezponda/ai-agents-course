# Tips Video: 10 Recipe Assistant (Project 1)

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

## 🎬 Guion paso a paso (comentando el workflow importado)

### 1. Introducción — Qué vamos a ver (30s)

> "Este es el Project 1 del curso. Combina casi todo lo que habéis visto: un agent con herramientas, memoria, un formulario para que el humano revise, y un segundo agent que busca precios reales por internet. Vamos a recorrer el workflow nodo a nodo."

**Abrir el workflow importado y hacer zoom out para que se vea entero.**

---

### 2. Chat Trigger — El punto de entrada (30s)

**Click en "When chat message received".**

> "A diferencia de los workflows anteriores que usaban Manual Trigger, aquí usamos Chat Trigger. Esto abre una ventanita de chat abajo a la derecha donde podemos escribir como si fuera ChatGPT. Cada mensaje que enviamos genera una ejecución."

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

> "Window Buffer Memory con 10 mensajes. Gracias a esto podemos tener una conversación: 'busca pollo', luego 'ahora dame una receta de pasta', y el agent recuerda el contexto."

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

> "El prompt le dice al agent algo clave: que agrupe los ingredientes en UNA sola búsqueda. En vez de buscar 'price chicken', 'price tomatoes', 'price onions' — una búsqueda por ingrediente, que gastaría mucha API — busca 'grocery store prices chicken breast tomatoes onions 2025' todo junto. Máximo 2 búsquedas."

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

> "Vamos a probarlo. Click en Chat abajo a la derecha."

**Escribir en el chat:**

```
I want a chicken recipe
```

**Mientras espera:**
> "Veis que el agent está trabajando... Está llamando a TheMealDB con 'chicken'. Ahora está procesando la respuesta y formateándola."

**Cuando el chat responde con la receta:**
> "Perfecto, ha encontrado una receta. Pero fíjaos que el chat NO ha terminado — el workflow está esperando en el formulario."

**Ir al nodo Review Recipe → copiar Test URL → abrir en navegador.**

> "Aquí tenemos la receta. Voy a elegir 'Yes, with price estimates' y pulsar Continue."

**Volver a n8n y esperar el resultado final.**

> "Ahora el Shopping List Agent está buscando precios en Google... Y aquí tenemos la lista de compras con precios reales."

**Mostrar el output final en el chat o en el último nodo.**

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

1. **El formulario tarda:** Después de que el agent responde, hay que ir al nodo Review Recipe, copiar la Test URL y abrirla en el navegador. Esto puede parecer lento en el vídeo — avisa a los alumnos de que es normal.

2. **SerpAPI tiene límite:** 100 búsquedas/mes en el free tier. Cada ejecución del Shopping List Agent usa 1-2 búsquedas. Si haces muchas demos seguidas, puedes llegar al límite.

3. **TheMealDB es limitada:** ~300 recetas en inglés. Si buscas algo muy específico o en otro idioma, probablemente caerá al fallback de Google.

4. **Los precios del Shopping List Agent:** Son reales pero aproximados — vienen de resultados de Google, no de una API de supermercado. El agent marca con `≈` los que estima por su cuenta.

5. **Dos credenciales SerpAPI:** El workflow usa SerpAPI en DOS sitios (Google Search como fallback del Recipe Agent, y Price Search para el Shopping List Agent). Ambos usan la misma credencial, pero cuentan como búsquedas separadas.
