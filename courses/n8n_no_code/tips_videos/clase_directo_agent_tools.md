# Clase en directo — El nodo AI Agent: de *workflow* a *agente* (y cómo se describen las tools)

> **Formato:** clase en streaming · **Duración objetivo:** ~60 min (ampliable a ~75 con la Capa 3 y más Q&A)
> **Base:** capítulo *Reflection Pattern* + workflow `05_reflection_pattern.json`
> **Repaso de:** vídeos ya grabados de *First AI Agent* (Ejemplo 3) y los patrones deterministas (01 chaining, 02 routing).
> **Idea central (repetir 3 veces):** *un workflow normal te obliga a **cablear** cada decisión; el nodo AI Agent le da al modelo un **objetivo** y deja que **él** elija el camino.*

---

## 0. Antes de empezar (checklist de 2 min)

- [ ] n8n abierto con el workflow **`05 — Reflection Pattern (2 Approaches)`** importado.
- [ ] Credencial de **OpenRouter** configurada y funcionando.
- [ ] Workflows en **modo Test** (no *Activated*) → control de coste mientras enseñas.
- [ ] Ten a mano este guion en la 2ª pantalla (versión HTML).
- [ ] Bloques de **copy-paste** del final abiertos (descripciones y código de las 2 tools).

> **Modelo:** el workflow viene con `openai/gpt-4o-mini`. Para 2026 usa un modelo **actual y barato** (p. ej. *Claude Haiku 4.5* o un *GPT-5 mini*); verifica el ID exacto en OpenRouter el día de la clase. El concepto no depende del modelo.

---

## 🎬 GUION POR BLOQUES

### BLOQUE 1 — Marco: ¿workflow o agente? · `~8 min` · *(repaso + encuadre)*

**🗣️ Decir (el gancho):**
> "En los vídeos anteriores construisteis workflows donde **vosotros** decidíais cada paso: encadenar prompts, un Switch que enruta, un If que corta un bucle. Hoy entramos de lleno en el nodo que cambia las reglas: el **AI Agent**. Y la pregunta de toda la clase es: *¿qué decisión dejo de cablear yo y se la doy al modelo?*"

**🗣️ Las dos definiciones (de Anthropic, *Building Effective Agents*):**
- **Workflow** = *"sistemas donde los LLMs y las herramientas se orquestan mediante rutas de código predefinidas"*. → **Tú escribes el guion.**
- **Agente** = *"sistemas donde el LLM dirige dinámicamente sus propios procesos y el uso de herramientas, manteniendo el control de cómo logra la tarea"*. → **Tú das un objetivo.**

**🗣️ La frase que se queda:**
> **"Un agente = LLM + bucle + tools."** El workflow le da al modelo un *guion*; el agente le da una *meta* y le deja elegir el control de flujo.

**🗣️ Las 3 decisiones que dejas de cablear** (esto une todo lo que ya vieron):

| Decisión cableada | Workflow determinista (ya grabado) | La pieza concreta |
|---|---|---|
| **Secuencia** (en qué orden) | 01 Prompt Chaining | pasos fijos Step 1→2→3 |
| **Rama** (qué camino) | 02 Routing | el nodo `Switch` |
| **Bucle** (cuándo parar) | 05 Reflection V1 | el nodo `If Done?` |

> "El nodo AI Agent **colapsa las tres en una**: secuencia las tools, elige cuál y repite el bucle hasta acabar — solo. Hoy atacamos **el bucle** a fondo, y de paso veréis lo otro."

**🗣️ La regla de decisión (apúntala en pantalla):**
> **"¿Puedes dibujar el diagrama de flujo de la tarea antes de ejecutar el LLM? Si sí → workflow. Si no → agente."**
> Mantra de Anthropic: *"busca la solución más simple posible y solo añade complejidad cuando haga falta."*

**🖱️ Hacer — repaso exprés del nodo** (ya lo vieron en vídeo, NO re-analizar):
- Abre el **Reflection Agent (V2)** y señala los **sub-nodos por línea punteada**: **Chat Model** (el cerebro), **Memory** (opcional), **Tools** (las manos), **System Message** (las reglas).
- ⚠️ **Dato n8n que data el material antiguo:** desde **n8n v1.82** el desplegable de "tipo de agente" **desapareció**: ahora todos los AI Agent son **"Tools Agent"** y **requieren al menos una tool conectada**. Si en algún sitio ven "Conversational/ReAct/Plan-and-Execute", está obsoleto.

---

### BLOQUE 2 — El bucle a mano: Reflection V1 (determinista) · `~12 min`

**🗣️ El reto (enséñalo en pantalla):** escribir la descripción de un producto con **restricciones duras**, que un LLM casi nunca clava a la primera:

| Restricción | Requisito |
|---|---|
| Frases | Exactamente **3** |
| Palabras | **25–30** en total |
| Keyword | Contiene **"sound"** exactamente **2 veces** |
| Prohibido | **NO** contiene "music" ni "audio" |

> "Probadlo en ChatGPT de un tiro: falla casi siempre alguna. Por eso existe la **reflexión**: *generar → criticar → refinar → repetir.*"

**🖱️ Hacer:**
1. Ejecuta **`Run: V1 Loop`**.
2. Abre el panel y **muestra que los nodos se ejecutan varias veces** (Generate/Refine → Validate → Parse → If Done? → loop).
3. Señala la pieza clave, el **`If Done?`**: la condición de salida la pusiste **tú** → `all_pass OR iteration >= 5`.

**🗣️ Los dos puntos didácticos:**
1. **"En V1, el que decide cuándo parar soy yo."** El bucle es mío, el guardrail (máx. 5) es mío.
2. **Ojo a cómo valida V1:** usa **otro LLM** como validador… y *los LLMs cuentan mal*. (Jerarquía de verificación de Anthropic: el "LLM-as-judge" es **el método menos fiable**.) Esto nos lleva directo a V2.

> ⚠️ **Riesgo en directo:** como V1 valida con un LLM, puede no converger y agotar las 5 iteraciones. Es perfecto para tu argumento ("por eso V2 es mejor"), pero **no te juegues la clase** a que V1 dé un resultado bonito — apóyate en V2 para el "wow".

---

### BLOQUE 3 — El bucle delegado: V2, el agente decide · `~12 min`

**🗣️ Decir:**
> "Misma tarea, mismo reto. Pero en vez de cablear yo el bucle, le doy al agente **un objetivo y una herramienta** y que se las apañe."

**🖱️ Hacer:**
1. Ejecuta **`Run: V2 Agent`**.
2. Clica el nodo **Reflection Agent (V2)** → pestaña de **tool calls**: se ve cómo **escribe → llama al Validator → lee los issues → reescribe → vuelve a validar** hasta `all_pass`.
3. Compara con V1 lado a lado.

**🗣️ Los tres remates:**
1. **"El agente decide cuándo ha terminado"** (cuando ya no llama a más tools). Es el **agent loop**: *reunir contexto → actuar → **verificar** → repetir.*
2. **El Validator es código JavaScript, no un LLM.** Y aquí va la joya de Anthropic (jerarquía de verificación, de mejor a peor):
   - 🥇 **Reglas/tests** (linters, validadores, código) → *"la mejor forma de feedback"*.
   - 🥈 Feedback visual (capturas).
   - 🥉 **LLM-as-judge** → *"generalmente no es un método muy robusto"*.
   > "Por eso V2 con un validador de **código** es más fiable que V1 con un validador **LLM**: el código cuenta exacto, el LLM estima."
3. **La gran idea:** *"Los agentes no son magia: automatizan el mismo bucle que montaste a mano en V1."*

**🗣️ Tabla para cerrar el contraste (pantalla):**

| Versión | Tú diseñas… | n8n gestiona… | La IA gestiona… |
|---|---|---|---|
| **V1: Loop** | la estructura del bucle y la salida | iterar, contar | generar texto |
| **V2: Agente** | el objetivo y las tools | **todo** | **el bucle entero** |

---

### BLOQUE 4 — 🌟 NÚCLEO NUEVO: tool calling y **descripciones** · `~20 min`

> Esto es lo que **no** está en ningún vídeo. Es el corazón de la clase de hoy.

**🗣️ La pregunta:** "Vale, el agente 'llama al Validator'… pero **¿cómo sabe cuándo y cómo usarlo?**"
**🗣️ La respuesta:** "Lee su **descripción**. Para el modelo, *la descripción ES la herramienta*. El código por dentro le da igual."

> Cita de los docs de Anthropic: *"Provide extremely detailed descriptions. This is by far the most important factor in tool performance."* (Las descripciones son, con diferencia, el factor #1.)

#### 🔬 Capa 1 — "La descripción es la interfaz" (romper y arreglar) · *imprescindible*

**🖱️ Hacer:**
1. Abre el tool **Validator** y muestra su descripción actual (buena):
   > *"Validates a product description against constraints. Input: the description text only (no extra text). Returns JSON with: sentences, words, sound_count, has_forbidden, all_pass, and issues (list of specific problems to fix)."*
2. **Rómpela** en vivo → cámbiala por: `Checks the text.`
3. Ejecuta V2. Observa: el agente **duda qué enviar / cuándo llamarla**, o se pone a contar él mismo (violando la regla), o el bucle se degrada.
4. **Restáurala** → vuelve a funcionar limpio.

**🗣️ Las frases que se quedan:**
- **"El nombre `Validator` no basta. El modelo solo conoce la tool por su descripción."**
- El framing de Anthropic: *"Piensa cómo le describirías la herramienta a un fichaje nuevo en tu equipo"* / *"como escribir un buen docstring para un junior."*
- **ACI = HCI:** *"Dedica a la interfaz agente-ordenador (ACI) tanto esfuerzo como a una interfaz humano-ordenador (HCI)."*
- Heurística: **3–4 frases por descripción**, y di **cuándo SÍ y cuándo NO** usarla.

**🗣️ Ejemplo de pizarra (buena vs mala, de los docs de Anthropic):**
- ❌ **Mala:** `"Gets the stock price for a ticker."`
- ✅ **Buena:** `"Retrieves the current stock price for a given ticker symbol. The ticker must be a valid symbol on a major US exchange (NYSE/NASDAQ). Returns the latest trade price in USD. Use it when the user asks for the current/most recent price of a stock. It will not return any other company information."`

**🗣️ System message vs descripción (confusión típica):**
> "Fijaos: el **system message** del agente dice las **reglas** ('no cuentes palabras tú, usa el Validator'). La **descripción del tool** dice **qué hace y cómo llamarlo**. No son lo mismo: reglas ≠ manual de la herramienta."

#### 🔬 Capa 2 — Multi-tool: cómo **elige** (partir el Validator en dos) · *el núcleo*

**🖱️ Hacer:**
1. Sustituye el Validator por **dos tools enfocados** (código en el anexo):
   - **`LengthChecker`** → frases y nº de palabras.
   - **`KeywordChecker`** → cuenta "sound" y detecta "music"/"audio".
2. Con descripciones **claras y distintas**, ejecuta → el agente **elige la correcta** para cada necesidad (a veces llama a las dos).
3. **El "aha":** haz que las dos descripciones se **solapen** (ambas dicen "checks the description") → el agente llama mal o redundante → **afínalas** → arreglado.

**🗣️ Las frases que se quedan:**
- **"Con varias tools, la descripción es lo que las desambigua."**
- **Test del límite (úsalo de remate):** *"Si para describir una tool necesitas decir 'a diferencia de la otra…', el límite no está claro. Si no puedes decir en una frase por qué el agente elegiría la tool A en vez de la B, no está lista."*
- **Menos tools, mejores:** *"Más herramientas no dan mejores resultados."* (OpenAI: *"menos de 20 funciones disponibles al inicio del turno"*; cada servidor MCP puede costar decenas de miles de tokens solo en definiciones.) → tools pocas y nítidas, no envoltorios finos de una API.

#### 🔬 Capa 3 — "¿Y con qué argumento la llama?" · `$fromAI()` · *opcional / puente*

**🗣️ Decir:**
> "Tool calling = elegir la tool **+ rellenar sus argumentos**. ¿Quién decide *qué texto* mandar al Validator? El modelo. En n8n eso se hace con **`$fromAI()`**: un hueco que el modelo rellena."
- `$fromAI(key, description, type, defaultValue)` → el `description` *"actúa como pista para que el modelo ponga el dato correcto"*. Solo disponible en tools conectados al **AI Agent** (no en el Code tool).
- **Puente a la próxima clase:** el **HTTP Request Tool** + `$fromAI()` = el agente llama a **cualquier API**. (Y más adelante: **AI Agent Tool** para multi-agente y **MCP Client Tool**.)

---

### BLOQUE 5 — Cuándo **NO** usar un agente + cierre · `~5 min`

**🗣️ Decir (honestidad = credibilidad):**
- Anthropic: *"Los workflows ofrecen previsibilidad y consistencia para tareas bien definidas; los agentes son mejores cuando hace falta flexibilidad y decisión dirigida por el modelo a escala."*
- **Caso real (cuéntalo):** en la comunidad de n8n alguien montó la **misma** tarea de clasificación de facturas de las dos formas — *"el agente perdió"*: enrutaba la misma factura distinto en ejecuciones distintas, era más difícil de depurar y *"te dirá tan tranquilo que está 90% seguro de algo que ha fallado."* → **Clasificar es determinista: no metas un agente donde un Switch sobra.**
- Regla práctica de n8n: **"construye el workflow primero; añade IA solo donde haya ambigüedad."**

**🗣️ Cierre + teaser:**
> "Hoy: el agente como **bucle automatizado** y por qué las **descripciones** mandan. La próxima: darle **superpoderes** — HTTP tool con `$fromAI()`, multi-agente con AI Agent Tool, y MCP."

### Q&A · `tiempo restante`

---

## 📋 ANEXO A — Copy-paste para el directo

### A1. Descripción "mala" (para romper en la Capa 1)
```
Checks the text.
```

### A2. Descripción "buena" (para restaurar)
```
Validates a product description against the constraints. Input: ONLY the description text (no extra words like "Here is my draft:"). Returns JSON with sentences (count), words (count), sound_count, has_forbidden, all_pass (true/false) and issues (list of specific problems to fix). Use this after writing or revising a draft, before returning the final answer.
```

### A3. Tool `LengthChecker` (Capa 2)
**Description:**
```
Counts the number of sentences and words in a product description. Input: ONLY the description text. Returns JSON: { sentences, words, length_ok }. Use this to check the length/structure constraints (exactly 3 sentences, 25–30 words). Do NOT use it for keyword checks.
```
**JavaScript:**
```javascript
const item = $input.first().json;
let text = '';
for (const k of ['query','input','chatInput','action_input']) { if (item[k]) { text = String(item[k]).trim(); break; } }
if (!text) { for (const v of Object.values(item)) { if (typeof v === 'string' && v.trim()) { text = v.trim(); break; } } }

const sentences = text.split(/[.!?]+/).filter(s => s.trim()).length;
const words = text.split(/\s+/).filter(w => w).length;
const length_ok = sentences === 3 && words >= 25 && words <= 30;

return [{ json: { input_received: text.slice(0,200), sentences, words, length_ok } }];
```

### A4. Tool `KeywordChecker` (Capa 2)
**Description:**
```
Checks keyword rules in a product description. Input: ONLY the description text. Returns JSON: { sound_count, has_forbidden, keywords_ok }. Use this to verify the word "sound" appears exactly twice and that "music"/"audio" are absent. Do NOT use it to count sentences or total words.
```
**JavaScript:**
```javascript
const item = $input.first().json;
let text = '';
for (const k of ['query','input','chatInput','action_input']) { if (item[k]) { text = String(item[k]).trim(); break; } }
if (!text) { for (const v of Object.values(item)) { if (typeof v === 'string' && v.trim()) { text = v.trim(); break; } } }

const sound_count = (text.toLowerCase().match(/\bsound\b/g) || []).length;
const has_forbidden = /\b(music|audio)\b/i.test(text);
const keywords_ok = sound_count === 2 && !has_forbidden;

return [{ json: { input_received: text.slice(0,200), sound_count, has_forbidden, keywords_ok } }];
```

### A5. Descripciones "solapadas" (para la demo de fallo de la Capa 2)
```
LengthChecker  → "Checks the product description."
KeywordChecker → "Checks the product description."
```
> Con esto el agente no sabe cuál llamar. Luego restauras A3/A4 y arreglado.

---

## 🧾 ANEXO B — Frases citables (tenlas a mano)

- *"Provide extremely detailed descriptions. This is by far the most important factor in tool performance."* — Anthropic
- *"Think of how you would describe your tool to a new hire on your team."* — Anthropic
- *"Plan to invest as much effort in agent-computer interfaces (ACI) as in human-computer interfaces (HCI)."* — Anthropic
- *"The best form of feedback is providing clearly defined rules… LLM-as-judge is generally not a very robust method."* — Anthropic (Agent SDK)
- *"If you can't say in one sentence why an agent would pick tool A over tool B, the boundary isn't clear enough to ship."*
- *"Find the simplest solution possible, and only increase complexity when needed."* — Anthropic
- Analogía: workflow = **receta**; agente = **chef** que gestiona la comida entera de principio a fin. (LSE Business Review)
- Andrew Ng: escribir sin agente = *"redactar de un tirón sin poder borrar"*; con agente = *"esquema → investigar → borrador → reflexionar → revisar."*

---

## 🐞 ANEXO C — Troubleshooting en vivo

| Síntoma | Causa probable | Arreglo rápido |
|---|---|---|
| El agente no llama a la tool | descripción vaga / no dice *cuándo* usarla | descripción específica + regla en el system message |
| El recuento de palabras sale mal | el agente envía "Here is my draft:" además del texto | la descripción debe decir "ONLY the description text"; mira `input_received` |
| V1 no converge | el validador LLM cuenta mal | normal; es el argumento para V2 (validador de código) |
| El agente llama dos tools redundantes | descripciones que se solapan | afina límites: una frase clara de "para qué SÍ / para qué NO" |
| El bucle no para | sin guardrail | V1: `iteration >= 5`; V2: **Max Iterations** (default 10) |
| Output muestra JSON crudo | el campo de salida no se llama `output` | renombra el campo a `output` |

---

## 🔧 ANEXO D — Cambios recomendados al material (post-investigación)

> No bloquean la clase, pero conviene aplicarlos al capítulo/workflow.

1. **Modelo:** cambiar `openai/gpt-4o-mini` por un modelo actual (Claude Haiku 4.5 / GPT-5 mini); mantener model-agnóstico.
2. **Coherencia V2:** el agente tiene `maxIterations: 10` pero el system message dice "at most 5 times" → alinéalos (deja 5 o sube el texto a 10).
3. **Añadir al capítulo la sección de *tool descriptions*** (es el hueco real): el bloque 4 de esta clase puede convertirse en contenido del capítulo.
4. **Jerarquía de verificación:** añadir la nota de Anthropic (reglas > visual > LLM-judge) para reforzar por qué el Validator de código es lo correcto.
5. **Nota n8n actual:** mencionar que el AI Agent es siempre **"Tools Agent"** (v1.82+) y requiere ≥1 tool.
6. **Teaser:** enlazar a MCP Client Tool / AI Agent Tool como continuación.

---

## 🔗 Fuentes (primarias)

- Anthropic — *Building Effective Agents*: https://www.anthropic.com/engineering/building-effective-agents
- Anthropic — *Writing effective tools for AI agents*: https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic — *Building agents with the Claude Agent SDK*: https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- Anthropic — *Effective context engineering for AI agents*: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- n8n — AI Agent (Tools Agent): https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/
- n8n — `$fromAI()`: https://docs.n8n.io/advanced-ai/examples/using-the-fromai-function/
- Self-Refine (arXiv 2303.17651) · Reflexion (arXiv 2303.11366) · ReAct (arXiv 2210.03629)
- DeepLearning.AI — Agentic Design Patterns: Reflection
