# Tips Video: 05 Reflection Pattern (V1 Loop + V2 Agent)

## Concepto clave
Generar → Validar → Refinar en bucle hasta cumplir todas las restricciones. Dos formas: loop manual (V1) o agente con tool (V2).

## Flujo V1: Loop
```
Manual Trigger → Input (product, constraints) → Generate/Refine → Store Draft → Validate → Parse Validation → If Done? → Output
                                                       ↑                                          │ (false)
                                                       └──────────── Prepare Refine ←─────────────┘
```

## Flujo V2: Agent
```
Manual Trigger → Input (product, constraints) → Reflection Agent ← [Validator Tool, Chat Model] → Output
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Product (V1 y V2)

| Field | Value |
|-------|-------|
| `product` | `Wireless Bluetooth Headphones` |
| `constraints` | (ver abajo) |

**constraints:**

📋
```
- Exactly 3 sentences
- 25–30 words total
- Contains the word "sound" exactly twice
- Does NOT contain the words "music" or "audio"
```

V1 tiene además:

| Field | Value |
|-------|-------|
| `iteration` | `0` |
| `draft` | (vacío) |

---

### V1: Generate/Refine

**System Message:**

📋
```
You are a product copywriter.

Write a product description that meets ALL the constraints exactly.
Count words carefully. Output ONLY the description.
```

**User Message (Expression):**

📋
```
Product: {{ $('Input — Product (V1)').first().json.product }}

Constraints:
{{ $json.constraints }}

{{ $json.draft ? 'Previous draft:\n' + $json.draft + '\n\nImprove the draft to fix the issues.' : 'Write the product description:' }}
```

### V1: Store Draft

| Field         | Expression                                                                                                       |
| ------------- | ---------------------------------------------------------------------------------------------------------------- |
| `draft`       | `{{ $json.text }}`                                                                                               |
| `constraints` | `{{ $('Input — Product (V1)').first().json.constraints }}`                                                       |
| `iteration`   | `{{ $if($('Parse Validation (V1)').isExecuted, $('Parse <br>Validation (V1)').first().json.iteration, 0) + 1 }}` |

### V1: Validate

**System Message:**

📋
```
You are a strict validator.

Check the draft against EACH constraint:
1. Count sentences (must be exactly 3)
2. Count words (must be 25–30)
3. Count occurrences of "sound" (must be exactly 2)
4. Check for forbidden words "music" or "audio" (must have 0)

Return a JSON object:
{
  "sentences": <number>,
  "words": <number>,
  "sound_count": <number>,
  "has_forbidden": <true/false>,
  "all_pass": <true/false>,
  "issues": ["list of issues if any"]
}

Return ONLY the JSON.
```

### V1: Parse Validation

| Field | Expression |
|-------|------------|
| `draft` | `{{ $('Store Draft (V1)').first().json.draft }}` |
| `constraints` | `{{ $('Store Draft (V1)').first().json.constraints }}` |
| `iteration` | `{{ $('Store Draft (V1)').first().json.iteration }}` |
| `validation_json` | `{{ $json.text }}` |
| `all_pass` | `{{ /\"all_pass\"\s*:\s*true/.test($json.text) }}` |
| `done` | `{{ /\"all_pass\"\s*:\s*true/.test($json.text) \|\| $('Store Draft (V1)').first().json.iteration >= 5 }}` |

### V1: If Done?

| Condition | Value |
|-----------|-------|
| `done` equals | `true` |
| True → | Output (V1) |
| False → | Prepare Refine (V1) → loop back to Generate/Refine |

### V1: Output

| Field | Expression |
|-------|------------|
| `final_description` | `{{ $json.draft }}` |
| `iterations` | `{{ $json.iteration }}` |
| `approach` | `{{ $json.all_pass ? 'V1: Loop with Exit Condition' : 'V1: Loop (max iterations reached)' }}` |

---

### V2: Reflection Agent

**System Message:**

📋
```
You are a product copywriter who writes precise descriptions.

Process:
1. Write a draft description
2. Use the Validator tool to check it (send ONLY the description text)
3. Read the issues list in the Validator response to see what failed
4. Revise the draft to fix those specific issues
5. Validate again — repeat until all_pass is true
6. Return ONLY the final description

Rules:
- Do NOT count words yourself — rely on the Validator tool
- Send ONLY the description to the Validator (no extra text like "Here is my draft:")
- Call the Validator at most 5 times
- When all_pass is true, return ONLY the final description
```

**User Message (Expression):**

📋
```
Product: {{ $json.product }}

Constraints:
{{ $json.constraints }}

Write a product description that meets ALL constraints. After writing, use the Validator tool to check it. Keep refining until all constraints pass.
```

**Agent Options:**

| Setting | Value |
|---------|-------|
| Max Iterations | `10` |

### V2: Validator Tool (Code Tool — JavaScript)

| Setting | Value |
|---------|-------|
| Name | `Validator` |
| Description | `Validates a product description against constraints. Input: the description text only (no extra text). Returns JSON with: sentences, words, sound_count, has_forbidden, all_pass, and issues.` |
| Language | `JavaScript` |

**Return format:** `return JSON.stringify({...})` (los tools del Agent devuelven string, no `[{json: ...}]`)

### V2: Output

| Field | Expression |
|-------|------------|
| `final_description` | `{{ $json.output }}` |
| `approach` | `V2: AI Agent with Validator Tool` |

---

## 🎬 Paso a paso para el video

### Intro (30s)
- **Explicar:** "Reflection = generar, criticar, refinar. El LLM no acierta siempre a la primera, así que lo hacemos iterar."
- **Mostrar:** El challenge: describir unos auriculares con restricciones difíciles (3 frases, 25-30 palabras, "sound" 2 veces, sin "music"/"audio")
- **Destacar:** "Vamos a ver dos formas de hacerlo."

### PARTE 1 — V1: Loop manual (~3min)

#### 1. Input — Product
- **Mostrar:** Los 4 campos (product, constraints, iteration=0, draft vacío)
- **Explicar:** iteration y draft se inicializan a 0 y vacío — se actualizan en cada vuelta

#### 2. Generate/Refine
- **Mostrar:** System message con "product copywriter"
- **Destacar:** El user message es dinámico: si hay draft previo pide "Improve", si no pide "Write"
- **Tip:** "La expresión con `$json.draft ?` decide si es la primera vez o si estamos refinando"

#### 3. Store Draft
- **Mostrar:** Guarda draft + constraints + iteration
- **Destacar:** La expresión de iteration: `$if($('Parse Validation (V1)').isExecuted, ..., 0) + 1`
- **Explicar:** "Usamos `$if/.isExecuted` porque en la primera ejecución Parse Validation todavía no ha corrido"

#### 4. Validate
- **Mostrar:** Otro LLM que actúa como validador estricto
- **Explicar:** Devuelve JSON con conteos exactos y `all_pass: true/false`
- **Tip:** "Es otro prompt, no el mismo — un LLM valida al otro"

#### 5. Parse Validation + If Done?
- **Mostrar:** Parse Validation extrae all_pass con regex y calcula `done`
- **Explicar:** `done = all_pass OR iteration >= 5` — sale si está bien O tras 5 intentos
- **Mostrar:** If Done? evalúa `done`: true → Output, false → Prepare Refine → vuelve a Generate

#### 6. Ejecutar y ver el loop — INSPECCIÓN
- **Ejecutar** el workflow
- **Mostrar:** Cómo los nodos se iluminan varias veces (el loop visual)
- **Click en Generate/Refine** → mostrar el selector "1 of N" abajo del Output Panel
- **Navegar** con ◀ ▶: "Fijaos cómo el draft cambia en cada iteración"
- **Click en Validate** → navegar iteraciones: "Aquí veis los conteos — sentences, words, sound_count — y cómo `all_pass` pasa de false a true"
- **Input tab** de Generate/Refine en iteración 2+: "Fijaos que ahora recibe el draft anterior y dice 'Improve'"
- **Destacar:** El número de iterations en Output (V1)

### PARTE 2 — V2: Agent (~2min)

#### 7. Input — Product
- **Mostrar:** Solo product y constraints (sin iteration ni draft — el agente lo maneja)
- **Explicar:** "Mucho más simple — el agente decide cuándo parar"

#### 8. Reflection Agent
- **Mostrar:** System message con los 6 pasos del proceso
- **Destacar:** Regla clave: "Do NOT count words yourself — rely on the Validator tool"
- **Explicar:** "Si no le dices esto, el LLM intenta contar solo y se equivoca"
- **Mostrar:** Max Iterations = 10 en opciones del Agent


#### 9. Validator Tool (Code Tool)
- **Mostrar:** Tipo Code Tool, lenguaje JavaScript
- **Explicar:** "En vez de otro LLM validando, usamos código: es determinista, no se equivoca al contar"
- **Destacar:** `return JSON.stringify({...})` — los tools del agente devuelven string
- **Tip:** "El campo `input_received` es para debugging — puedes ver qué recibió el tool"

#### 10. Ejecutar y ver la diferencia — INSPECCIÓN
- **Ejecutar** el workflow
- **Click en Reflection Agent** → Output Panel
- **Expandir Step 1** → mostrar Tool Call: Validator
  - "Aquí veis qué texto envió al Validator (Input) y qué recibió de vuelta (Output)"
  - Mostrar `input_received` en el Output: "Esto es para debugging — confirma que no envió texto extra"
  - Mostrar `issues`: "Estas son las cosas que tiene que arreglar"
- **Expandir Step 2** → mostrar segunda llamada
  - "Fijaos que el draft cambió — arregló los issues del paso anterior"
  - Si `all_pass: true`: "Ya está, el agente para aquí"
- **Click en el sub-nodo Validator Tool** → selector "1 of N"
  - "También podéis inspeccionar el tool directamente — cada ejecución es una llamada"
  - **Input tab**: "Esto es exactamente lo que recibió el código JavaScript"
- **Comparar:** "Mismo resultado que V1, pero con menos nodos y la inspección está centralizada en el Agent"

### Cierre (30s)
- **Comparar:** V1 = control total (tú decides la lógica del loop), V2 = simplicity (el agente decide)
- **Destacar:** V1 usa dos LLMs (generator + validator LLM), V2 usa un LLM + código
- **Tip:** "En producción, V2 suele ser más práctico; V1 te da más control para debugging"

---

## 🔍 Cómo inspeccionar las ejecuciones en n8n

Sección para explicar en el video: dónde mirar para ver qué ha pasado en cada paso.

### Conceptos generales (aplica a V1 y V2)

1. **Click en cualquier nodo** → se abre el **Output Panel** a la derecha
2. Arriba del panel hay **dos pestañas**: **Input** y **Output**
   - **Input**: lo que el nodo *recibió* del nodo anterior (los datos de entrada)
   - **Output**: lo que el nodo *produjo* (el resultado)
3. Dentro de cada pestaña hay **tres vistas**: **Table**, **JSON**, **Schema**
   - **Table**: vista limpia, una fila por campo. Haz clic en un valor largo para expandirlo
   - **JSON**: datos crudos — útil para copiar o ver la estructura exacta
   - **Schema**: muestra los tipos de datos (string, number, boolean)

### V1: Inspeccionar el loop (nodos que ejecutan varias veces)

Cuando un nodo se ejecuta múltiples veces (por el loop), n8n muestra **un selector de ejecuciones** en la parte inferior del Output Panel:

```
◀  1 of 3  ▶
```

**Paso a paso para inspeccionar V1:**

1. **Ejecutar el workflow** (click en "Test Workflow")
2. **Click en Generate/Refine (V1)** → Output Panel
   - Abajo aparece "1 of N" — N es el número de vueltas del loop
   - Navegar con ◀ ▶ para ver el draft de cada iteración
   - **Output tab → JSON**: ver el campo `text` con el draft generado
   - **Input tab**: ver qué recibió — en la iteración 1, `draft` está vacío; en iteraciones siguientes contiene el draft anterior
3. **Click en Store Draft (V1)** → Output
   - Ver `iteration: 1`, `draft: "..."` en la primera vuelta
   - Navegar a iteración 2, 3... ver cómo `iteration` sube y `draft` cambia
4. **Click en Validate (V1)** → Output
   - **Output tab → JSON**: ver el JSON de validación que devolvió el LLM
   - Aquí ves `sentences`, `words`, `sound_count`, `all_pass`
   - Navegar entre iteraciones para ver cómo los issues se van resolviendo
5. **Click en Parse Validation (V1)** → Output
   - Ver `all_pass: false/true` y `done: false/true`
   - En la última iteración, `done: true` (o `all_pass: true` o `iteration >= 5`)
6. **Click en Output (V1)** → Output
   - Solo tiene 1 ejecución (solo se ejecuta una vez, al salir del loop)
   - Ver `final_description`, `iterations`, `approach`

**Tip para el video:** "Fíjate en el selector '1 of 3' abajo — esto te permite rebobinar y ver qué pasó en cada vuelta del loop. Es como un historial de iteraciones."

### V2: Inspeccionar el agente y sus tool calls

El nodo Agent tiene un output especial que muestra **todo el proceso interno** del agente.

**Paso a paso para inspeccionar V2:**

1. **Ejecutar el workflow** (click en "Test Workflow")
2. **Click en Reflection Agent (V2)** → Output Panel
3. En el Output Panel, verás **el resultado final** (`output: "..."`)
4. Pero lo interesante está en la pestaña **"Output" → vista expandida**:
   - El Agent muestra un **log de pasos** con iconos desplegables
   - Cada paso tiene un **▶ triángulo** para expandir

**Qué ver en cada paso del agente:**

```
▶ Step 1: Agent thinks...            ← el razonamiento del agente
  ▶ Tool Call: Validator             ← qué tool llamó
    Input: "Experience premium..."   ← el texto que envió al tool
    Output: {"sentences": 3, ...}    ← lo que devolvió el tool
▶ Step 2: Agent thinks...            ← el agente lee el feedback
  ▶ Tool Call: Validator             ← segunda llamada
    Input: "Discover exceptional..."
    Output: {"all_pass": true, ...}
▶ Final Answer: "Discover..."        ← la respuesta final
```

5. **Expandir cada Tool Call** para ver:
   - **Input**: el texto exacto que el agente envió al Validator (debería ser SOLO la descripción, sin "Here is my draft:")
   - **Output**: el JSON con los conteos y los issues
   - El campo `input_received` muestra los primeros 200 chars que el tool recibió — útil para verificar que no hay texto extra
6. **Click en Validator Tool** (el sub-nodo)
   - También tiene el selector "1 of N" como en V1
   - Cada ejecución corresponde a una llamada del agente
   - **Input tab**: ver exactamente qué campo (`query`, `input`, etc.) recibió el code tool
   - **Output tab**: ver el JSON string que devolvió

**Tip para el video:** "En el Agent, expande cada paso para ver la 'conversación interna': el agente piensa, llama al tool, lee el resultado, y decide si necesita otro intento. Es como ver el cerebro del agente trabajando."

### Resumen visual (para mostrar en pantalla)

```
┌──────────────────────────────────────────────────────┐
│  V1: INSPECCIONAR LOOP                               │
│                                                      │
│  Click en nodo → Output Panel                        │
│  ┌────────────────────────────────────┐              │
│  │  [Input]  [Output]                 │  ← pestañas  │
│  │  [Table] [JSON] [Schema]           │  ← vistas    │
│  │                                    │              │
│  │  { "draft": "Experience...",       │              │
│  │    "iteration": 2,                 │              │
│  │    "all_pass": false }             │              │
│  │                                    │              │
│  │  ◀  2 of 3  ▶                     │  ← iterac.   │
│  └────────────────────────────────────┘              │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  V2: INSPECCIONAR AGENT                              │
│                                                      │
│  Click en Agent → Output Panel                       │
│  ┌────────────────────────────────────┐              │
│  │  ▶ Step 1                          │              │
│  │    ▶ Tool Call: Validator          │  ← expandir  │
│  │      Input:  "Experience..."       │  ← qué envió │
│  │      Output: {sentences: 3, ...}   │  ← qué volvió│
│  │  ▶ Step 2                          │              │
│  │    ▶ Tool Call: Validator          │              │
│  │      Input:  "Discover..."         │              │
│  │      Output: {all_pass: true}      │              │
│  │  ✅ Final Answer                   │              │
│  └────────────────────────────────────┘              │
└──────────────────────────────────────────────────────┘
```

---

## ✅ Puntos clave para el video
- [ ] Reflection = Generar → Validar → Refinar (loop)
- [ ] V1: loop manual con If Done? (all_pass OR max iterations)
- [ ] V2: Agent + Validator Tool (agente decide cuándo parar)
- [ ] `$if/.isExecuted` para nodos que no han corrido aún
- [ ] Validator Tool devuelve string (`JSON.stringify`), no `[{json}]`
- [ ] "Do NOT count words yourself" — regla crítica del system prompt
- [ ] Dos LLMs (V1) vs LLM + Código determinista (V2)
- [ ] **Inspección V1:** selector "1 of N" en cada nodo para ver cada iteración
- [ ] **Inspección V2:** expandir Steps del Agent para ver tool calls (Input/Output)
- [ ] Pestañas Input/Output + vistas Table/JSON/Schema

## 🎥 Demo sugerida
1. Ejecutar V1 → mostrar loop iterando (nodos se iluminan varias veces)
2. Click en Generate/Refine → navegar "1 of N" → ver draft mejorando
3. Click en Validate → navegar iteraciones → ver conteos e issues
4. Cambiar a Input tab en iteración 2 → ver que ahora recibe el draft previo
5. Ejecutar V2 → click en Agent → expandir Steps → ver Tool Calls
6. Expandir un Tool Call → mostrar Input (texto enviado) y Output (JSON con issues)
7. Click en sub-nodo Validator Tool → selector "1 of N" → ver cada llamada
8. Comparar número de iteraciones V1 vs V2

## ⚠️ Errores comunes
- `return [{json: {...}}]` en el Validator Tool → "Wrong output type returned" (debe ser `return JSON.stringify(...)`)
- Python Code Tool → timeout (usar JavaScript, corre nativo en Node.js)
- `$('Parse Validation (V1)').first().json.iteration` sin `$if/.isExecuted` → "Node hasn't been executed" en la primera iteración
- No decirle al agente "rely on the Validator tool" → intenta contar palabras él solo y se equivoca
- Enviar texto extra al Validator ("Here is my draft: ...") → el conteo de palabras falla
