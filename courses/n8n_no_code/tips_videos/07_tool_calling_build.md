# Build from Scratch: Tool Calling — Trip Briefing Agent (progresivo)

## Objetivo del video

> "Hasta ahora nuestros agentes usaban tools que vienen de fábrica: Calculator, Wikipedia, SerpAPI. Hoy damos el salto: vamos a darle al agente una herramienta que llama a **cualquier API de internet**, y sobre todo vamos a aprender lo más importante del tool calling — **cómo el agente decide qué herramienta usar**. Y la respuesta os va a sorprender: **decide leyendo la descripción que tú escribes.**"

**Qué vamos a construir:** un *Trip Briefing Agent* — un asistente que, dado un destino, prepara un mini-informe de viaje: el **tiempo** (API en vivo), un par de **sitios que ver** (Wikipedia) y **qué pasa ahora mismo** allí (Google), y deja el informe listo para enviar **tras aprobación humana**.

Construimos UN workflow y lo ampliamos en 4 anillos. Cada anillo es un workflow que ya funciona:

| Anillo | Qué añadimos | Concepto nuevo |
|--------|--------------|----------------|
| **1** | Agent + `get_weather` (HTTP Request Tool) | Llamar a cualquier API · `$fromAI()` · el botón ✨ |
| **2** | + Wikipedia + Google Search | El agente **elige** la tool · descripción vs system message |
| **3** | (variación en vivo) romper y arreglar una descripción | **La descripción ES la interfaz** |
| **4** | Wait — Approval | Tools de **lectura vs escritura** · gate de aprobación |

### Para quién y qué aprenderán

- **Para quién:** alumnos que ya saben qué es el nodo **AI Agent** (LLM + tools + memoria) y han usado tools nativas (Calculator, Wikipedia). No hace falta programar.
- **Qué aprenderán:**
  1. Cómo el agente **elige** una herramienta (la descripción).
  2. Conectar **cualquier API** con el HTTP Request Tool.
  3. `$fromAI()`: que el modelo rellene los parámetros.
  4. Tools de **lectura vs escritura** y el gate de aprobación.

### ¿De qué va el workflow?

Un **conserje de viajes**: le dices un destino y prepara un mini-informe (el **tiempo**, un par de **sitios que ver**, **qué pasa ahora mismo**) y lo deja listo **tras aprobación humana**. Es la excusa perfecta para ver, con un caso real, cómo un agente reparte el trabajo entre varias herramientas.

> **Énfasis docente:** hoy NO repetimos qué es un agente (ya lo saben). El foco es uno: **la descripción manda**. Vuelve a esa idea en cada anillo.

**Credenciales necesarias:** OpenRouter API key · SerpAPI key (gratis, [serpapi.com](https://serpapi.com)) a partir del anillo 2. `get_weather` (wttr.in) y Wikipedia **no necesitan clave**.

> **Import via URL** (n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/09_tool_calling_trip_briefing.json
> ```

---

## Concepto clave: ¿cómo elige el agente una herramienta?

> "Cuando conectas tools a un AI Agent, n8n le manda al modelo una *lista* de herramientas: el **nombre**, la **descripción** y los **parámetros** de cada una. El modelo lee esa lista, lee la pregunta del usuario, y **decide**. Tú NO escribes 'si pregunta por el tiempo, usa get_weather'. Eso lo deduce el modelo. ¿De dónde? Sobre todo de **la descripción**."

| Lo que ve el modelo | De dónde sale |
|---------------------|---------------|
| Nombre de la tool | el nombre del nodo |
| **Descripción** (lo más importante) | tools personalizadas (HTTP, Code): la escribes tú · tools nativas (Wikipedia): viene fija |
| Parámetros que rellenar | `$fromAI()` en la tool |
| Reglas extra | el **System Message** del agente |

> "Quedaos con esto: para el modelo, **la descripción ES la herramienta**. El código que hay detrás le da igual."

---

## Anillo 1: Agent con `get_weather` (HTTP Request Tool)

> "Empezamos con UNA sola tool, pero una potente: una que llama a una API de tiempo de verdad."

### Paso 1: Crear workflow

1. **Workflows** → **Add Workflow**
2. Renombrar a "Trip Briefing Agent"

### Paso 2: Manual Trigger + Input

1. Añadir **Manual Trigger** → renombrar a `Run: Trip Briefing`
2. Añadir **Edit Fields** → renombrar a `Input — Trip Request`
3. Un campo String:

| Name | Value |
|------|-------|
| `request` | (copiar abajo) |

Valor de `request`:
```
I'm visiting Lisbon this weekend. Give me a short trip brief: the weather, a couple of must-see sights, and anything happening right now.
```

### Paso 3: Añadir el AI Agent

1. Añadir **AI Agent** → renombrar a `Trip Briefing Agent`
2. **Source for Prompt**: `Define below`. **Prompt** (modo Expression):

```
{{ $json.request }}
```

3. **Options** → **System Message** (de momento solo el rol; las reglas de tools las afinamos en el anillo 2):

```
You are a Trip Briefing assistant. The user names a destination and you prepare a short, practical trip brief.
```

> "Recordad de capítulos anteriores: el AI Agent siempre es ahora un **Tools Agent** y **necesita al menos una tool conectada**. Vamos a darle la primera."

### Paso 4: Chat Model (sub-nodo)

1. Click **+ Chat Model** → **OpenRouter Chat Model**
2. Credencial + modelo (p. ej. `openai/gpt-4o-mini` o un modelo actual barato)

### Paso 5: Añadir `get_weather` — el HTTP Request Tool

1. Click en el **+** del conector **Tool** del agente
2. Buscar **HTTP Request** → se añade como **HTTP Request Tool**
3. Renombrar el nodo a `get_weather`
4. Configurar:

| Campo | Valor |
|-------|-------|
| **Description** | (copiar abajo) |
| **Method** | `GET` |
| **URL** | `https://wttr.in/` … + `$fromAI` (ver abajo) |
| **Send Query Parameters** | ON → `format` = `j1` |
| **Optimize Response** | ON |

**Description** (esto es lo que lee el modelo):
```
Get the current weather for a city. Input: the destination city name in English (for example "Lisbon"). Returns temperature, conditions, humidity and wind. Use this when the user asks about the weather or what to pack. Do NOT use it for opening hours, events, prices or general facts.
```

### Paso 6: El botón ✨ y `$fromAI()`

> "Aquí está la magia. La URL necesita la ciudad… pero yo no sé qué ciudad pedirá el usuario. Que la rellene el modelo."

1. En el campo **URL**, escribe `https://wttr.in/`
2. Pasa el ratón por el final del campo → aparece el icono **✨** → clic
3. n8n inserta una expresión `$fromAI(...)`. Ajusta la `key` y la descripción para que quede:

```
https://wttr.in/{{ $fromAI('city', 'The destination city name in English, e.g. Lisbon or Paris', 'string') }}
```

> "`$fromAI('city', ...)` es un hueco que el modelo rellena. Mira la URL de abajo: aún no resuelve nada. Pero cuando el agente ejecute, leerá la pregunta, verá que el usuario habla de Lisboa, y pondrá `city = Lisbon`. El resultado: `https://wttr.in/Lisbon`."

### Paso 7: Output

1. Añadir **Edit Fields** → renombrar a `Output — Approved` (lo reusaremos en el anillo 4)
2. Un campo String `trip_brief` con este valor (Expression):

```
{{ $('Trip Briefing Agent').item.json.output }}
```

3. Conectar: `Run: Trip Briefing → Input → Trip Briefing Agent → Output`

### Demo (anillo 1)

1. **Execute Workflow**
2. Abrir el nodo **Trip Briefing Agent** → pestaña **Logs**
3. Ver la llamada a `get_weather`: con qué `city` la llamó y qué devolvió wttr.in

> "Fijaos en el log: el agente decidió llamar a get_weather, rellenó `city: Lisbon` él solito, y wttr.in devolvió el tiempo. Una tool, una API real, el modelo rellenando los parámetros. Eso es tool calling."

---

## Anillo 2: + Wikipedia + Google Search (el agente elige)

> "Una tool es fácil: si la necesita, la usa. Lo interesante es con VARIAS: ¿cuál elige y por qué?"

### Paso 1: Añadir Wikipedia

1. **+** en el conector **Tool** → **Wikipedia** (sin credenciales)

### Paso 2: Añadir Google Search (SerpAPI)

1. **+** en el conector **Tool** → **SerpAPI** → renombrar a `Google Search`
2. Credencial de SerpAPI (gratis, 100 búsquedas/mes)

### Paso 3: Actualizar el System Message

Reemplazar por:
```
You are a Trip Briefing assistant. The user names a destination (and sometimes dates) and you prepare a short, practical trip brief.

You have three tools:
- get_weather: live weather for a city. Use it whenever the user wants the weather or what to pack.
- Wikipedia: established background facts (history, main sights, geography) that rarely change. Use it for general "tell me about" knowledge.
- Google Search: current, time-sensitive info (events this week, opening hours, ticket prices, recent news). Use it when the answer depends on what is happening NOW.

Rules:
- Choose the RIGHT tool: stable facts -> Wikipedia; current/this-week info -> Google Search; weather -> get_weather.
- Do NOT invent opening hours, prices or dates. If it is time-sensitive, search.
- Final answer: a short brief of 4-6 bullets (weather, 2-3 things to see, 1 current tip).
```

> "Mirad bien: Wikipedia y Google Search se parecen — las dos 'buscan información'. ¿Cómo sabe el agente cuál usar? Por la diferencia que le marco: **hechos que no cambian → Wikipedia; cosas de AHORA → Google.** Wikipedia y Google son tools nativas: su descripción viene fija, no la puedo editar. Así que las dirijo con el **System Message**. Esa es una pista clave: cuando no puedes tocar la descripción de una tool, la guías desde el system message."

### Demo (anillo 2)

1. **Execute Workflow** (misma pregunta de Lisboa)
2. Abrir el agente → **Logs** → ver la **secuencia de tool calls**

> "Mirad la secuencia: get_weather para el tiempo, Wikipedia para la Torre de Belén y el Castillo de San Jorge, y Google Search para los eventos del finde. Tres herramientas, cada una para lo suyo, decidido por el agente."

---

## Anillo 3 (VARIACIÓN EN VIVO): la descripción ES la interfaz

> "Os dije que el agente elige por la descripción. Vamos a demostrarlo rompiéndola."

### Paso 1: Romper la descripción de `get_weather`

1. Abrir el nodo `get_weather`
2. Cambiar el campo **Description** por algo vago:
```
Checks the weather.
```
3. **Execute Workflow** con una pregunta ambigua, p. ej.:
```
I'm going to Porto on Saturday — is it a good day to walk around?
```

> "Con una descripción pobre el modelo duda: a veces no llama a la tool y se inventa el tiempo, a veces la llama mal. El nombre `get_weather` no basta — el modelo solo la conoce por su descripción."

### Paso 2: Arreglarla

1. Restaurar la **Description** buena:
```
Get the current weather for a city. Input: the destination city name in English (for example "Lisbon"). Returns temperature, conditions, humidity and wind. Use this when the user asks about the weather or what to pack. Do NOT use it for opening hours, events, prices or general facts.
```
2. **Execute Workflow** con la misma pregunta → ahora la llama bien

> "Solo he cambiado **un campo de texto** y el comportamiento cambia por completo. Por eso Anthropic dice que la descripción es, con diferencia, el factor número uno. Escríbela como si se la explicaras a alguien que entra nuevo en tu equipo: **qué hace, cuándo usarla, cuándo NO, qué entra y qué sale.** Tres o cuatro frases."

### (Opcional) Variación: prioridad vía system message

> "¿Y si quiero forzar que SIEMPRE consulte el tiempo aunque no lo pidan? No toco la descripción: añado una regla al system message."

Añadir al System Message: `Always include current weather in the brief, even if the user does not ask for it.` → ejecutar y comparar.

---

## Anillo 4: lectura vs escritura + aprobación

> "Todas nuestras tools son de SOLO LECTURA: buscan y leen, no cambian nada. Si el agente se equivoca, como mucho trae un dato malo. Pero el día que una tool **envíe un email** o **borre algo**, un error sale caro. Regla de oro: **si una tool cambia algo en el mundo real, necesita aprobación humana antes de ejecutarse.**"

### Paso 1: Añadir el gate de aprobación

1. Entre el Agent y el Output, añadir un nodo **Wait** → renombrar `Wait — Approval`
2. Configurar:

| Setting | Value |
|---------|-------|
| Resume | `On Webhook Call` |
| Webhook Suffix (Options) | `{{ $execution.id }}` |

3. Reconectar: `Trip Briefing Agent → Wait — Approval → Output — Approved`

### Paso 2: Completar el Output

En `Output — Approved`, añadir el campo de estado:

| Name | Value |
|------|-------|
| `trip_brief` | `{{ $('Trip Briefing Agent').item.json.output }}` |
| `status` | `approved` |

(activar **Keep Only Set**)

### Demo (anillo 4)

1. **Execute Workflow** → el workflow se **pausa** en `Wait — Approval`
2. Clic en el nodo **Wait — Approval** → copiar la **Test URL** → abrirla en el navegador
3. El workflow continúa → `Output — Approved` con `status: approved`

> "El agente investiga libremente porque sus tools son de lectura. Pero el informe no 'se manda' hasta que un humano abre el enlace y aprueba. En producción, después del Wait conectarías un nodo que envíe de verdad. El patrón es siempre: **la IA prepara → el humano aprueba → el sistema ejecuta.**"

---

## Resumen final

> "Recapitulemos el Trip Briefing Agent:"

| Anillo | Qué aprendimos |
|--------|----------------|
| **1** | Una tool HTTP llama a **cualquier API**; `$fromAI()` deja que el modelo rellene los parámetros |
| **2** | Con varias tools, el agente **elige**; la descripción (o el system message) decide |
| **3** | **La descripción ES la interfaz**: cámbiala y cambia el comportamiento |
| **4** | **Lectura vs escritura**: las acciones que cambian el mundo van detrás de un gate de aprobación |

**Tres ideas para llevarse:**
1. El modelo elige la tool **leyendo su descripción** (qué hace + cuándo usarla + cuándo NO).
2. `$fromAI()` = el modelo rellena los argumentos de la tool en tiempo de ejecución.
3. **Read-only se usa libre; write necesita aprobación.**

---

## Errores comunes

| Error | Solución |
|-------|----------|
| El agente no llama a `get_weather` | Descripción vaga → poner "Use this when… / Do NOT use…" |
| El agente elige Wikipedia cuando debía buscar en Google (o al revés) | Marcar la diferencia en el system message: hechos estables vs info de ahora |
| `$fromAI` no rellena la ciudad | Comprobar que la URL está en modo **Expression** y que la `key` tiene sentido (`city`) |
| wttr.in devuelve un texto enorme / falla | Dejar `Optimize Response` ON; si da guerra, ponerlo OFF y simplificar |
| Ciudad con espacios ("New York") falla en la URL | wttr.in acepta `New+York`; o codificar el espacio (`%20`) |
| El workflow no continúa tras el Wait | Hay que abrir la **Test URL** del nodo Wait para reanudarlo |
| Output muestra JSON crudo en un Chat Trigger | El último nodo debe tener un campo `output` (aquí usamos Manual Trigger, no aplica) |
| El agente se queda en bucle de tools | Bajar **Max Iterations** (Agent → Options) a 5-8 |
