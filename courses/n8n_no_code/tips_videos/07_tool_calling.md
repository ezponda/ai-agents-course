# Guion — Capítulo 07: Tool Calling (workflow `09_tool_calling_trip_briefing.json`)

## Concepto
En el Cap. 06 el agente ya usaba herramientas (Calculator, Wikipedia). Aquí abrimos la caja: **cómo** funciona el tool calling, **cómo diseñar** herramientas que el agente use bien, y **cómo mantenerlo seguro**.
La idea grande: **el modelo no ejecuta herramientas — las pide.** Tú le das un menú (nombre + descripción), él decide cuál llamar y con qué datos, y n8n la ejecuta. Todo el arte está en **la descripción**.
Y una regla que vale oro: **si una herramienta cambia algo en el mundo real, necesita aprobación humana antes de ejecutarse.**

## Flujo del workflow (el demo final)
```
Run: Trip Briefing ──▶ Input — Trip Request ──▶ Trip Briefing Agent ──▶ Wait — Approval ──▶ Output — Approved
(Manual)              (destino)                 (elige herramienta)     (⏸️ humano)         (brief aprobado)
                                                     ┊ sub-nodos (read-only)
                                        ┌────────────┼─────────────┐
                                   get_weather    Wikipedia    Google Search
                                   (HTTP+$fromAI) (hechos)     (info de hoy)
```
**Requisitos:** OpenRouter + **SerpAPI** (key gratis) + n8n. Wikipedia y wttr.in no piden credencial.

---

## 🗺️ Los nodos de un vistazo (léelo primero)

| Nodo | Qué es |
|------|--------|
| **Run: Trip Briefing** | Disparador manual (le das a Execute) |
| **Input — Trip Request** | El destino y qué quieres ("brief de Lisboa este finde") |
| **Trip Briefing Agent** | El agente: **elige** herramienta y escribe el brief |
| **OpenRouter Chat Model** | El cerebro del agente |
| **get_weather** | Tool HTTP: tiempo real vía `wttr.in`, la ciudad la rellena `$fromAI` |
| **Wikipedia** | Tool: hechos estables (historia, monumentos) |
| **Google Search** | Tool (SerpAPI): info de HOY (eventos, precios) |
| **Wait — Approval** | ⏸️ Pausa hasta que un humano aprueba |
| **Output — Approved** | El brief final, marcado `approved` |

**Las 3 tools son de solo lectura** → el agente investiga libre; lo que se "envía" queda detrás del Wait.

---

## 🔧 Preparación ANTES de grabar (checklist)

1. **Importa** el workflow (Import from URL):

```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/09_tool_calling_trip_briefing.json
```

2. **Credenciales:** OpenRouter (modelo barato actual) + **SerpAPI** (key gratis en serpapi.com, va en el nodo Google Search).
3. **Modelo** en OpenRouter Chat Model: `openai/gpt-4o-mini` (o el que uses).
4. **Prueba de humo:** **Execute Workflow** → abre `Trip Briefing Agent → Logs` (¿qué tools llamó?) → el run se para en `Wait — Approval` → abre el nodo, copia la **URL**, ábrela para aprobar.
5. Ten a mano la pestaña de **Logs** del agente: es LA pantalla del capítulo.

## 🔗 URLs para tener a mano

| Para qué | URL |
|----------|-----|
| Doc del capítulo | https://ezponda.github.io/ai-agents-course/07_tool_calling.html |
| HTTP Request Tool (docs) | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/ |
| Anthropic — Advanced Tool Use | https://www.anthropic.com/engineering/advanced-tool-use |
| Código de las tools de n8n | https://github.com/n8n-io/n8n/tree/master/packages/%40n8n/nodes-langchain/nodes/tools |

---

# 🎬 GUION DE GRABACIÓN (de arriba abajo)

## 0 · (Opcional) Cold open — el gancho (20s)
> Grábalo al final. En pantalla: el agente eligiendo `get_weather` en los Logs y el run parándose en el Wait.
- **Di:** *"Le pido a un agente un brief de viaje. Sin que yo le diga cómo, decide llamar a la API del tiempo, buscar en Wikipedia y en Google… y al final me pide permiso antes de 'enviarlo'. Eso es tool calling bien hecho. Vamos a verlo por dentro."*

## 1 · Cómo funciona el tool calling (1.5 min)
- **Di:** *"Cuando conectas herramientas a un agente, le das un **menú**. Ojo a esto: el modelo **no ejecuta** la herramienta. La **pide**, y n8n la ejecuta y le devuelve el resultado."*
- **Di (el bucle):** *"Es el mismo bucle ReAct del capítulo anterior: **Razona → Llama a la herramienta → Observa el resultado → Repite o Responde**. El agente da vueltas hasta que tiene lo que necesita."*
- **Di:** *"¿Con qué decide? Tres cosas: el **nombre** y la **descripción** de cada tool, la **pregunta** del usuario y el **System Message**. Si algo está flojo, elige mal o se lo inventa."*

## 2 · Cómo elige la herramienta (1 min)
- **Di:** *"Tú NO escribes 'si el usuario pregunta X, usa la tool Y'. Eso es lo viejo. Aquí n8n manda todas las descripciones al modelo y ÉL decide."*
- **Di (la clave):** *"Por eso **la descripción es la señal principal**. Las built-in (Wikipedia, Calculator) la traen escrita por dentro; en las tuyas (HTTP, Workflow) la escribes tú. El System Message es solo para **reglas extra** — 'prueba Wikipedia primero', 'no envíes sin preguntar' — no para describir tools."*

## 3 · Read-only vs Write — la regla de oro (1.5 min)
- **Di:** *"La distinción más importante del diseño de herramientas: **de lectura** vs **de escritura**."*
  - **Read-only** (Wikipedia, Calculator, tiempo, buscar): solo **leen**. Si el agente se equivoca, como mucho traes un dato irrelevante. **Se permiten libres.**
  - **Write** (enviar email, crear ticket, borrar, publicar): **cambian el mundo**. Si se equivoca, mandas un email vergonzoso o borras algo.
- **Di (regla de oro):** *"**Si una herramienta cambia algo real, necesita aprobación humana antes de ejecutarse.** Y da al agente solo las tools que necesita: privilegio mínimo. Un asistente de investigación no necesita 'enviar email'."*

## 4 · Escribir buenas descripciones (1.5 min)
- **Di:** *"Anthropic es tajante: 'da descripciones extremadamente detalladas, es de lejos el factor más importante'. Escríbela como se la explicarías a alguien que entra nuevo: qué hace, cuándo usarla, cuándo **NO**, y qué entra y sale."*
- **[Enséñalo en pantalla]** — el patrón:

```
Use this tool when [situación].
Do NOT use when [contra-situación].
Input: [qué necesita]
Output: [qué devuelve]
```

- **Di (el test del límite):** *"Si no puedes decir en una frase POR QUÉ el agente elegiría la tool A en vez de la B, sus descripciones se solapan y va a adivinar. Afínalas hasta que la frontera sea obvia."*
- **Di:** *"Y si elige mal: **mejora la descripción**, no metas lógica enrevesada en el System Message."*

## 5 · HTTP Request Tool + `$fromAI()` (2.5 min)
- **Di:** *"Las built-in cubren lo común. Pero ¿y tu API interna, o el tiempo? El **HTTP Request Tool** deja al agente llamar a CUALQUIER URL — y él decide cuándo y **con qué valores**."*
- **[Abre `get_weather`]** — enseña la URL:

```
https://wttr.in/{{ $fromAI('city', 'The destination city name in English, e.g. Lisbon or Paris', 'string') }}
```

- **Di (`$fromAI`):** *"Esta función le dice al modelo: 'aquí tienes que poner tú un valor'. Tres argumentos: **key** (el nombre que ve), **description** (qué poner) y **type**. Si el usuario dice '¿qué tiempo hace en Lisboa?', el agente rellena `city` con `Lisbon`."*
- **Di (el botón ✨):** *"La forma fácil de meterlo: pasa el ratón por el campo, sale la **estrellita ✨**, clic, y n8n te genera el `$fromAI`. Solo editas la descripción."*

### Mini-demo: ¿cuánto importa la descripción del parámetro? (opcional, potente)
> Enséñalo en los **Logs** del agente con "¿qué tiempo hace en Lisboa?".
- **1 · Descrito (recomendado)** — el modelo rellena limpio, `Lisbon`:

```
https://wttr.in/{{ $fromAI('city', 'The destination city in English, e.g. Lisbon or Paris', 'string') }}
```

- **2 · Placeholder pelado** — sin descripción, y lo arreglas en el System Message:

```
https://wttr.in/{{ $fromAI('query') }}
```
```
When you call get_weather, pass ONLY the destination city name in English — no extra words, just the city (e.g. "Lisbon").
```
> Funciona, pero es frágil: a veces manda "weather in Lisbon" y la URL se rompe.

- **3 · Fijo (sin `$fromAI`)** — hardcodeas la ciudad:

```
https://wttr.in/Lisbon
```
> Ahora el agente **no puede** cambiar de ciudad: siempre Lisboa. Deja de ser agéntico.

- **Di:** *"Describir el parámetro (estado 1) mueve el trabajo de tu prompt a la herramienta, donde el modelo lo gestiona fiable. Igual que una buena descripción de tool."*

## 6 · Guardrails (1 min)
- **Di:** *"Aun con buenas descripciones, un agente se puede desmadrar. Lo esencial:"*
  - **Max Iterations** 5-10 (Agente → Settings, el engranaje): corta bucles infinitos.
  - **Reglas en el System Message:** "llama a Wikipedia como mucho 2 veces", "si una tool falla, explica el error y para".
  - **Puerta de aprobación:** para tools de escritura, un **Wait** antes de la acción para que un humano revise.

---

## 7 · DEMO — el Trip Briefing Agent (3-4 min)

**La misión:** das un destino → el agente trae el **tiempo** (API en vivo), busca **monumentos** en Wikipedia y **eventos de esta semana** en Google → y un **humano aprueba** antes de "enviar".

### Enséñale el cerebro
- **[Abre `Trip Briefing Agent` → Options → System Message]** — recórrelo: define las 3 tools y **cuándo usar cada una** (estable→Wikipedia, de hoy→Google, tiempo→get_weather) y pide un brief de 4-6 bullets.
- **Di:** *"Fíjate: aquí no hay 'if'. Solo describo cada herramienta y su frontera, y el agente decide."*

### Ejecuta y mira cómo PIENSA
- Pulsa **Execute Workflow**.
- **[Abre `Trip Briefing Agent` → Logs]**
- **Di:** *"Esta es la pantalla clave. Veis qué tools llamó y con qué input: `get_weather` con `city: Lisbon`, Wikipedia para los monumentos, Google para lo de esta semana. Esa elección es el agente trabajando."*

### Fuérzale a elegir distinto (enseña el poder de la descripción)

| Le pides | Qué debería hacer |
|----------|-------------------|
| `What's the weather in Lisbon this weekend?` | solo `get_weather` |
| `Tell me about the history of the Belém Tower` | Wikipedia (hecho estable) |
| `What concerts are on in Lisbon this weekend?` | Google Search (info de hoy) |
| `Trip brief for Lisbon this weekend` | las tres |

### La puerta de aprobación
- **Di:** *"El run se ha **parado** en `Wait — Approval`. Todo lo anterior era lectura; nada se ha 'enviado'."*
- **[Abre `Wait — Approval`]** → copia la **URL** → ábrela → el run continúa a `Output — Approved`.
- **Di (el patrón):** *"El patrón siempre es el mismo: **la IA prepara → el humano aprueba → el sistema envía**. Aquí paramos en aprobar; en producción, después del Wait conectas el envío real (email, chat)."*

---

## 🐞 Si algo va mal (debug en directo)

| Síntoma | Mira | Arréglalo |
|---------|------|-----------|
| No usa ninguna tool | ¿La descripción es clara? | Añade "Use this tool when…" |
| Usa la tool equivocada | ¿Se solapan las descripciones? | Añade "Do NOT use when…" |
| Llama en bucle | ¿Le sirve el resultado? | Revisa el output, mejora la query |
| Ignora el resultado | ¿System Message muy restrictivo? | Afloja la instrucción |
| La tool da error | ¿Credenciales puestas? | Settings → Credentials (SerpAPI) |

> Siempre igual: **clic en el agente → mira los Steps/Logs → qué tools llamó, con qué input, y si usó el resultado.**

---

# 🎬 PARTE 2 — Variaciones (para alargar el vídeo)

> Cada variación es una receta corta: **qué nodo tocar → abrirlo → qué cambiar.**

## Variación 1 — Otra API con `$fromAI` (4 min)

**Qué logras:** el agente llama a una API tuya, no solo al tiempo.

- **1.** Copia `get_weather` (Ctrl+C → Ctrl+V) → renómbralo (p.ej. `Recipe Search`).
- **2.** Cambia la **URL** por tu endpoint y mete un `$fromAI` en el término de búsqueda:

```
https://www.themealdb.com/api/json/v1/1/search.php?s={{ $fromAI('query', 'A simple English food term like chicken or pasta', 'string') }}
```

- **3.** Reescribe la **Description** (cuándo usarla, qué devuelve, y "if meals:null, no recipes").
- **4.** **Di:** *"Misma mecánica: el agente decide cuándo llamar y rellena el hueco."*

## Variación 2 — Human review por tool (HITL nativo) (4 min) 🛡️

**Qué logras:** en vez de aprobar TODO el brief, apruebas solo la llamada peligrosa.

- **1.** Añade una tool de **escritura** (p.ej. enviar email/Telegram).
- **2.** En el conector de esa tool, activa el **Human review** (n8n reciente) → Slack/Telegram/Gmail.
- **3.** Al llamarla, el run **pausa** y te pregunta aprobar/denegar **esa** acción.
- **4.** **Di:** *"Review por tool cuando solo ALGO es peligroso; el Wait del final cuando quieres aprobar el resultado entero."*

## Variación 3 — Enviar de verdad tras aprobar (3 min)

**Qué logras:** cerrar el ciclo "prepara → aprueba → envía".

- **1.** Detrás de `Output — Approved`, añade **Send Email (SMTP)** o **Telegram**.
- **2.** Cuerpo del mensaje: `{{ $json.trip_brief }}`.
- **3.** **Di:** *"Ahora el humano aprueba y el sistema envía. El patrón completo de producción."*

## Variación 4 — MCP: tools de fuera (opcional, avanzado)

**Qué logras:** usar herramientas alojadas fuera de n8n (Notion, Slack, tu servidor).

- **1.** Añade **MCP Client Tool** como sub-nodo del agente.
- **2.** Configura el **SSE Endpoint** del servidor MCP (+ auth si hace falta).
- **3.** Elige qué tools exponer (All / Selected).
- **4.** **Di:** *"MCP es potente pero añade complejidad. Para el curso, las built-in bastan; MCP cuando necesitas algo que no está en n8n."*

---

## Cierre (30s)
- **Di:** *"Tool calling es esto: el modelo pide, n8n ejecuta, y la **descripción** manda. Las de lectura, libres; las de escritura, detrás de una aprobación humana. Con eso ya construyes agentes que hacen cosas de verdad… sin que te den un susto."*

## ⚠️ Avisos de grabación
1. **SerpAPI necesita key** (gratis) o Google Search falla — ponla antes de grabar.
2. **La pantalla clave es `Trip Briefing Agent → Logs`:** ahí se ve la elección de tool y el input de `$fromAI`.
3. **El run se PARA en el Wait:** para continuar, abre el nodo y abre su URL (no esperes nada automático).
4. **Modelo:** `gpt-4o-mini` va bien; si compartes, pon **Max Iterations** 5-8.
5. **Coste:** cada vuelta del bucle es una llamada al LLM; con las 3 tools puede dar 2-4 vueltas por brief.
6. **wttr.in y Wikipedia** no piden credencial — si el tiempo falla, suele ser la ciudad mal formada (revisa el `$fromAI`).
