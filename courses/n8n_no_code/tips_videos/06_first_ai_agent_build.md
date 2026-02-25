# Build from Scratch: First AI Agent (progresivo)

Construimos UN workflow y lo vamos ampliando en 3 fases:

| Fase | Qué construimos | Qué concepto nuevo |
|------|-----------------|---------------------|
| **1** | Agent + Calculator + Memory | Qué es un Agent, tools, memoria |
| **2** | + SerpAPI + Think | Múltiples tools, el agent elige |
| **3** | Chat Trigger | Interfaz de chat real, `output` vs `answer` |

**Credenciales necesarias:** OpenRouter API key. SerpAPI key (gratis, [serpapi.com](https://serpapi.com)) a partir de fase 2.

---

## Fase 1: Agent con Calculator + Memory

### Concepto clave: Agent vs Basic LLM Chain

> "Hasta ahora, Basic LLM Chain = un prompt, una respuesta. El Agent es diferente: tiene un LOOP. Piensa, decide si necesita una herramienta, la usa, observa el resultado, y repite hasta tener la respuesta."

| | Basic LLM Chain | AI Agent |
|--|-----------------|----------|
| Ejecucion | 1 prompt → 1 respuesta | Loop: Think → Act → Observe → Repeat |
| Tools | No | Si (Calculator, SerpAPI...) |
| Decision | Tu controlas todo | El agent decide |
| Campo de salida | `text` | `output` |

### Paso 1: Crear workflow

1. **Workflows** → **Add Workflow**
2. Renombrar a "AI Agent Calculator Practice"

### Paso 2: Manual Trigger + Input

1. Añadir **Manual Trigger**
2. Añadir **Edit Fields** → renombrar a `Input — Agent Prompt`
3. Dos campos String:

| Name | Value |
|------|-------|
| `chatInput` | (copiar abajo) |
| `sessionId` | `demo` |

Valor de `chatInput`:
```
A junior data analyst in Madrid earns €24,000/year. What's the monthly net salary after 15% tax?
```

> "El `sessionId` es como un numero de conversacion. Mismo ID = misma memoria. Si cambias el ID, empieza de cero."

### Paso 3: Añadir el nodo AI Agent

1. Añadir **AI Agent** → renombrar a `AI Agent — Calculator + Memory`
2. Configurar:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.chatInput }}`
3. Ir a **Options** → activar **System Message**:

```
You are a salary and career advisor.

Rules:
- For ANY arithmetic (tax, net salary, comparisons), ALWAYS use the Calculator tool.
- Keep the final answer short (max 5 lines).
- Format salary figures with currency symbols.
```

> "La regla mas importante: 'ALWAYS use the Calculator tool'. Sin esto, el LLM intenta hacer las cuentas de cabeza y se equivoca. Con esta regla, siempre usa la calculadora."

### Paso 4: Conectar sub-nodos (lineas de puntos)

> "Fijate en las lineas de puntos debajo del Agent. Las lineas solidas son flujo de datos: 'pasa datos al siguiente'. Las de PUNTOS son CAPACIDADES: 'este agent PUEDE usar esto'. No significa que lo use siempre — el decide."

**Chat Model:**
1. Click **+ Chat Model** en la parte inferior del Agent
2. Seleccionar **OpenRouter Chat Model**
3. Elegir credencial y modelo: `openai/gpt-4o-mini`

**Memory:**
1. Click **+ Memory** → **Window Buffer Memory**
2. Configurar:

| Setting | Value |
|---------|-------|
| Session ID Type | `Custom Key` |
| Session Key (Expression) | `{{ $json.sessionId }}` |
| Context Window Length | `10` |

> "Context Window = 10 significa que recuerda los ultimos 10 mensajes. Mas mensajes = mas tokens = mas coste."

**Calculator:**
1. Click **+ Tool** → **Calculator**
2. No necesita configuracion

> "Esto es un TOOL — una herramienta que el agent puede llamar. El Calculator hace operaciones matematicas. Sin credenciales, sin configuracion."

### Paso 5: Output

1. Añadir **Edit Fields** → renombrar a `Output — Answer`
2. Un campo:

| Name | Value (Expression) |
|------|---------------------|
| `answer` | `{{ $json.output }}` |

> "IMPORTANTE: el Agent devuelve `output`, NO `text`. El Basic LLM Chain usa `text`, el Agent usa `output`. Error muy comun."

### Paso 6: Conectar todo

```
Manual Trigger → Input — Agent Prompt → AI Agent → Output — Answer
```

### Demo

1. **Ejecutar el workflow** (Execute Workflow)
2. Click en el AI Agent → expandir execution details → ver que llamo al Calculator con `24000 * (1 - 0.15) / 12`

> "No se lo invento. Uso la herramienta."

3. Cambiar `chatInput` a:
```
My name is Alberto. Remember it.
```
4. Ejecutar. Cambiar `chatInput` a:
```
What is my name?
```
5. Ejecutar → responde "Alberto" (mismo `sessionId`)

> "Si cambio el sessionId a otra cosa, pierde la memoria. La memoria va por sesion."

---

## Fase 2: Añadir SerpAPI + Think

> "Ahora vamos a añadir dos tools mas. El agent tendra TRES herramientas y el decide cual usar y en que orden."

### Qué cambiamos

Solo añadimos dos tools mas al mismo Agent y actualizamos el system message. La estructura es la misma.

### Paso 1: Añadir SerpAPI

1. Click en el AI Agent → **+ Tool** → **SerpAPI**
2. Configurar credencial de SerpAPI (gratis en [serpapi.com](https://serpapi.com), 100 busquedas/mes)

> "SerpAPI busca en Google. A diferencia de Wikipedia, da resultados actualizados. Es gratis hasta 100 busquedas al mes."

### Paso 2: Añadir Think

1. Click en el AI Agent → **+ Tool** → **Think**
2. No necesita configuracion

> "Esta herramienta es curiosa. No hace nada externo — es un bloc de notas interno donde el agent escribe su plan ANTES de actuar. Parece inutil, pero mejora mucho los resultados en tareas de varios pasos. Sin Think, el agent a veces salta directamente a buscar sin pensar que necesita."

### Paso 3: Actualizar System Message

Reemplazar el system message anterior por:

```
You are a salary research assistant.

Rules:
- To find salary data, job market info, or company details: use the Google Search tool.
- For arithmetic (tax calculations, salary comparisons): ALWAYS use Calculator.
- Use Think briefly (1-2 sentences) to plan before calling tools.
- Output: short bullets with sources, then the final computed number.
```

> "Cada tool tiene su indicacion en el system message. Sin estas reglas, el agent puede elegir mal — por ejemplo, inventarse un salario en vez de buscarlo."

### Paso 4: Actualizar el chatInput

Cambiar el valor de `chatInput` en el nodo Input:

```
Search for the average data scientist salary in Spain. Then calculate the monthly net salary after 24% income tax.
```

### Demo

1. **Ejecutar el workflow**
2. Click en el AI Agent → expandir execution details
3. Ver la secuencia de tool calls:

> "Primero Think: 'Necesito buscar el salario y luego calcular el neto.' Luego SerpAPI: busca en Google y encuentra ~35.000 euros. Luego Calculator: `35000 * (1 - 0.24) / 12 = 2216.67`. Tres herramientas en secuencia, todo decidido por el agent."

---

## Fase 3: Chat Trigger + Memory

> "Ahora vamos a convertir esto en un chat REAL. En vez de Manual Trigger con datos fijos, usamos Chat Trigger — una ventanita de chat como ChatGPT."

### Qué cambiamos

1. Sustituir **Manual Trigger** + **Input** por **Chat Trigger**
2. Cambiar el nombre del campo de salida de `answer` a `output`

### Paso 1: Borrar Manual Trigger e Input

1. Borrar el nodo **Manual Trigger**
2. Borrar el nodo **Input — Agent Prompt**

### Paso 2: Añadir Chat Trigger

1. Añadir **Chat Trigger** (buscar "When chat message received")
2. Configurar:

| Setting | Value |
|---------|-------|
| Mode | `Webhook` (default) |
| Response Mode (en Options) | `When Last Node Finishes` |

> "El Chat Trigger genera automaticamente `chatInput` (lo que escribe el usuario) y `sessionId` (un ID unico por sesion de chat). Ya no hace falta el nodo Input."

### Paso 3: Conectar Chat Trigger al Agent

```
When chat message received → AI Agent → Output
```

### Paso 4: Actualizar el System Message

```
You are a salary research assistant inside an n8n AI Agent workflow.
Be concise.
If the user asks about salaries, job markets, or company info, search Google first.
If the user asks for arithmetic, use the Calculator tool.
Use Think to plan multi-step research.
If the user asks you to remember something, store it in memory and confirm briefly.
If you don't know, say so.
```

### Paso 5: Cambiar el Output (CRITICO)

En el nodo **Output**, cambiar el nombre del campo de `answer` a **`output`**:

| Name | Value (Expression) |
|------|---------------------|
| **`output`** | `{{ $json.output }}` |

> "ATENCION: El Chat Trigger busca especificamente un campo llamado `output` en el ultimo nodo. Si lo llamas `answer` o `response`, el chat muestra JSON crudo en vez del texto bonito."

| Campo en el ultimo nodo | El chat muestra |
|--------------------------|-----------------|
| `output: "Hello!"` | Hello! |
| `answer: "Hello!"` | `{"answer": "Hello!"}` (JSON crudo) |

### Paso 6: Renombrar nodos

- Agent → `AI Agent — Salary Chat`
- Output → `Output — Chat Response`

### Demo

> "IMPORTANTE: ahora NO click en Execute Workflow. Click en el boton de Chat abajo a la derecha."

1. Abrir el chat y escribir:
```
What is the average software engineer salary in Berlin?
```

2. Sin cerrar el chat, escribir:
```
Calculate the monthly net if that's €55,000 with 30% tax
```

> "No he dicho de que estamos hablando, pero gracias a la memoria, sabe que hablamos del salario de Berlin."

3. Escribir:
```
Remember that I'm interested in Berlin
```

4. Escribir:
```
What city am I interested in?
```

> "Responde Berlin. La memoria funciona dentro de la sesion."

5. **Cerrar el chat. Abrir otro chat nuevo.**

```
What city am I interested in?
```

> "No lo sabe. Nueva ventana de chat = nuevo sessionId = memoria vacia. La memoria es POR SESION, no global."

---

## Resumen final

> "Recapitulemos lo que habeis construido:"

| Fase | Que aprendimos |
|------|----------------|
| **1** | Un Agent con UN tool (Calculator) + memoria. El agent DECIDE si usar herramientas. |
| **2** | TRES tools — el agent elige cual usar y en que orden. Think ayuda a planificar. |
| **3** | Chat Trigger = interfaz de chat real. Memoria entre mensajes de la misma sesion. |

**Tres conceptos clave:**
1. El agent **DECIDE** que herramientas usar (loop: Think → Act → Observe)
2. La memoria **PERSISTE** por `sessionId` (mismo ID = misma conversacion)
3. El output se llama **`output`** (no `text`) — y en Chat Trigger el ultimo nodo DEBE usar `output`

---

## Errores comunes

| Error | Solucion |
|-------|----------|
| `$json.text` en vez de `$json.output` | Agent usa `output`, Basic LLM Chain usa `text` |
| Chat muestra JSON crudo | El ultimo nodo debe tener campo `output`, no `answer` |
| Memoria no funciona | Comprobar que `sessionId` es el mismo |
| SerpAPI falla | Configurar credencial en Settings → Credentials |
| Agent no usa Calculator | Poner "ALWAYS use Calculator" en system message |
| Agent se queda en bucle | Poner Max Iterations a 5-10 en Agent → Settings |
