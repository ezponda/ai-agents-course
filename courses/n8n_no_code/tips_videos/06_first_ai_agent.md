# Tips Video: First AI Agent (Chapter 6)

Tres workflows que van de menos a más. Cada uno añade una capacidad nueva.

| Workflow | Qué añade |
|----------|-----------|
| **05 — Calculator + Memory** | Primer agent, un tool, memoria |
| **06 — SerpAPI + Calculator + Think** | Múltiples tools, el agent elige |
| **07 — Chat Trigger + Memory** | Chat real en vez de Manual Trigger |

---

## Workflow 1: Calculator + Memory

**Abrir el workflow importado. Zoom out.**

> "Este es el primer agent del curso. Hasta ahora habíamos usado Basic LLM Chain — un prompt, una respuesta. El agent es diferente: tiene un LOOP. Piensa, usa herramientas, observa el resultado, y repite hasta que tiene la respuesta."

### Nodo por nodo

**Click en Input — Agent Prompt.**

> "Dos campos: `chatInput` con la pregunta, y `sessionId` para la memoria. El sessionId es como un número de conversación — mismo ID, misma memoria."

**Click en AI Agent — Calculator + Memory. Mostrar las tres conexiones de abajo: Chat Model, Memory, Calculator.**

> "Fíjaos en las líneas de puntos. Las líneas sólidas son flujo de datos: 'este nodo pasa datos al siguiente'. Las de puntos son CAPACIDADES: 'este agent PUEDE usar esta herramienta'. No significa que la vaya a usar siempre — él decide."

**Click en Options → System Message.**

> "La regla más importante: 'For ANY arithmetic, ALWAYS use the Calculator tool'. Sin esto, el LLM intenta hacer las cuentas de cabeza y se equivoca. Con esta regla, siempre usa la calculadora."

**Click en Output — Answer.**

> "Un detalle importante: el agent devuelve su respuesta en un campo llamado `output`, NO `text`. El Basic LLM Chain usa `text`, el Agent usa `output`. Es un error muy común."

### Demo

**Ejecutar el workflow.**

```
A junior data analyst in Madrid earns €24,000/year. What's the monthly net salary after 15% tax?
```

> "Vamos a ver el resultado... Click en el Agent, expandimos execution details, y ahí vemos que llamó al Calculator con `24000 * (1 - 0.15) / 12`. No se lo inventó — usó la herramienta."

**Para demostrar memoria, cambiar el chatInput y ejecutar otra vez:**

```
My name is Alberto. Remember it.
```

**Ejecutar una tercera vez:**

```
What is my name?
```

> "Responde 'Alberto' porque el sessionId es el mismo: 'demo'. Si cambio el sessionId a otra cosa, pierde la memoria."

---

## Workflow 2: SerpAPI + Calculator + Think

**Abrir el workflow. Señalar que tiene la misma estructura pero más tools.**

> "Mismo patrón: Manual Trigger → Input → Agent → Output. La diferencia es que ahora el agent tiene TRES herramientas. Y él decide cuál usar y en qué orden."

### Qué cambia respecto al anterior

**Click en el Agent. Mostrar los tres tools: SerpAPI, Calculator, Think.**

> "Tres herramientas nuevas respecto al anterior:"

**1. SerpAPI:**
> "Busca en Google. A diferencia de Wikipedia (que vimos brevemente), SerpAPI da resultados actualizados. Necesita API key — gratis en serpapi.com, 100 búsquedas al mes."

**2. Think:**
> "Esta es curiosa. No hace nada externo — es un bloc de notas interno donde el agent escribe su plan ANTES de actuar. Parece inútil, pero mejora mucho los resultados en tareas de varios pasos. Sin Think, el agent a veces salta directamente a buscar sin pensar qué necesita."

**3. Calculator:** "Igual que antes."

**Click en Options → System Message.**

> "Fíjaos en las reglas: cada tool tiene su indicación. 'Para salarios, usa Google Search. Para cálculos, usa Calculator. Usa Think brevemente para planificar.' Si no ponéis estas reglas, el agent puede elegir mal — por ejemplo, inventarse un salario en vez de buscarlo."

### Demo

**Ejecutar el workflow.**

```
Search for the average data scientist salary in Spain. Then calculate the monthly net salary after 24% income tax.
```

> "Esto requiere TRES pasos: pensar, buscar, calcular. Vamos a ver qué hizo..."

**Expandir execution details del Agent.**

> "Primero Think: 'Necesito buscar el salario y luego calcular el neto.' Luego SerpAPI: busca en Google y encuentra ~35.000€. Luego Calculator: `35000 * (1 - 0.24) / 12 = 2216.67`. Tres herramientas en secuencia, todo decidido por el agent."

---

## Workflow 3: Chat Trigger + Memory

**Abrir el workflow. Señalar que es más corto — no tiene Manual Trigger ni Input.**

> "Este es el mismo agent de antes, pero ahora con una entrada REAL. En vez de Manual Trigger con datos fijos, usamos Chat Trigger — una ventanita de chat como ChatGPT."

### Qué cambia

**Click en When chat message received.**

> "El Chat Trigger genera automáticamente `chatInput` (lo que escribe el usuario) y `sessionId` (un ID único por sesión de chat). Ya no hace falta el nodo Input."

**Click en Output — Chat Response.**

> "Atención: el campo se llama `output`, NO `answer`. El Chat Trigger busca específicamente un campo llamado `output` en el último nodo. Si lo llamáis `answer` o `response`, el chat muestra JSON crudo en vez del texto."

### Demo

**Click en el botón Chat abajo a la derecha (NO en Execute Workflow).**

```
What is the average software engineer salary in Berlin?
```

> "El agent busca en Google y responde. Ahora, sin cerrar el chat, le pregunto otra cosa:"

```
Calculate the monthly net if that's €55,000 with 30% tax
```

> "No he dicho de qué estamos hablando — pero gracias a la memoria, sabe que hablamos del salario de Berlin. Usa Calculator y responde."

```
Remember that I'm interested in Berlin
```

> "Confirma. Ahora le pregunto:"

```
What city am I interested in?
```

> "Responde Berlin. La memoria funciona dentro de la sesión."

**Cerrar el chat. Abrir otro chat nuevo.**

```
What city am I interested in?
```

> "No lo sabe. Nueva ventana de chat = nuevo sessionId = memoria vacía. Esto es importante: la memoria es por sesión, no global."

---

## Resumen — Progresión de los tres workflows

> "Recapitulemos lo que habéis visto:"

1. **Workflow 05:** Un agent con UNA herramienta (Calculator) y memoria. Lo básico.
2. **Workflow 06:** El mismo agent con TRES herramientas. Él decide cuál usar y en qué orden.
3. **Workflow 07:** Chat Trigger — una interfaz de chat real, con memoria entre mensajes.

> "Los tres conceptos clave: el agent DECIDE qué herramientas usar, la memoria PERSISTE por sesión, y el output se llama `output` (no `text`)."

---

## Textos de prueba (copy-paste)

**Workflow 05 — Calculator:**
```
A junior data analyst in Madrid earns €24,000/year. What's the monthly net salary after 15% tax?
```

**Workflow 05 — Memoria (ejecutar los dos seguidos):**
```
My name is Alberto. Remember it.
```
```
What is my name?
```

**Workflow 06 — Multi-tool:**
```
Search for the average data scientist salary in Spain. Then calculate the monthly net salary after 24% income tax.
```

**Workflow 07 — Chat (escribir uno a uno en el chat):**
```
What is the average software engineer salary in Berlin?
```
```
Calculate the monthly net if that's €55,000 with 30% tax
```
```
Remember that I'm interested in Berlin
```
```
What city am I interested in?
```

---

## Errores comunes

- **`$json.text` en vez de `$json.output`** — el Agent usa `output`, el Basic LLM Chain usa `text`
- **Chat muestra JSON crudo** — el último nodo debe tener un campo llamado `output`, no `answer`
- **La memoria no funciona** — comprobar que el sessionId es el mismo entre ejecuciones
- **SerpAPI falla** — hay que configurar la credencial en Settings → Credentials (gratis en serpapi.com)
- **El agent no usa Calculator** — añadir "ALWAYS use Calculator" en el system message
