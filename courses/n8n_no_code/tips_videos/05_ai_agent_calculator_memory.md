# Tips Video: 05 AI Agent Basics (Calculator + Memory)

## Concepto clave
Agent = LLM que DECIDE cuándo usar herramientas. Diferente de Basic LLM Chain.

## Flujo del workflow
```
Manual Trigger → Input (chatInput, sessionId) → AI Agent ← [Calculator, Memory, Chat Model] → Output
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Agent Prompt

| Field | Expression |
|-------|------------|
| `chatInput` | `{{ $json.chatInput \|\| "A junior data analyst in Madrid earns €24,000/year. What's the monthly net salary after 15% tax?" }}` |
| `sessionId` | `{{ $json.sessionId \|\| "demo" }}` |

### AI Agent — Calculator + Memory

**System Message:**
```
You are a salary and career advisor.

Rules:
- For ANY arithmetic (tax, net salary, comparisons), ALWAYS use the Calculator tool.
- Keep the final answer short (max 5 lines).
- Format salary figures with currency symbols.
```

**Prompt (User Message):**
```
{{ $json.chatInput }}
```

### Simple Memory

| Setting | Value |
|---------|-------|
| Session ID Type | `Custom Key` |
| Session Key | `{{ $json.sessionId }}` |
| Context Window Length | `10` |

### Output — Answer

| Field | Expression |
|-------|------------|
| `answer` | `{{ $json.output }}` |

---

## 🧪 Prompts de prueba

**Cálculo de salario neto:**
```
A junior data analyst in Madrid earns €24,000/year. What's the monthly net salary after 15% tax?
```

**Memoria - guardar:**
```
My name is Alberto. Remember it.
```

**Memoria - recuperar:**
```
What is my name?
```

**Otro ejemplo de salario:**
```
A junior developer earns €28,000/year gross. After 19% income tax, what's the monthly take-home pay?
```

---

## 🎬 Paso a paso para el video

### 1. Diferencia Agent vs Basic LLM Chain
- **Explicar:** Basic LLM Chain = un prompt, una respuesta
- **Explicar:** Agent = loop (Think → Act → Observe → Repeat)
- **Destacar:** Agent DECIDE si usar herramientas

### 2. Input — Agent Prompt
- **Mostrar:** chatInput con valor default (salario junior data analyst)
- **Mostrar:** sessionId para memoria
- **Tip:** "Cambiar sessionId = nueva conversación"

### 3. AI Agent node
- **Mostrar:** Las conexiones DOTTED (no solid)
- **Explicar:** Dotted = "capacidades", no flujo de datos
- **Mostrar:** System message con "ALWAYS use Calculator" y "salary and career advisor"

### 4. Calculator tool
- **Mostrar:** No necesita configuración
- **Explicar:** El agent lo llama cuando necesita math (tax, net salary)
- **Demo:** Ver en output cómo el agent llamó al tool

### 5. Simple Memory
- **Mostrar:** sessionKey = `{{ $json.sessionId }}`
- **Mostrar:** contextWindowLength = 10
- **Explicar:** Recuerda últimos 10 mensajes de esa sesión

### 6. Output — Answer
- **Mostrar:** Usa `$json.output` (no `$json.text`)
- **Destacar:** Agent devuelve `output`, Basic LLM Chain devuelve `text`

---

## ✅ Puntos clave para el video
- [ ] Agent LOOP: Think → Act → Observe
- [ ] "ALWAYS use Calculator" evita que calcule mal
- [ ] Memory necesita sessionId consistente
- [ ] Dotted lines = capacidades, no datos

## 🎥 Demo sugerida
1. `A junior data analyst in Madrid earns €24,000/year. Monthly net after 15% tax?` → ver que usa Calculator
2. `My name is Alberto.` → ejecutar
3. `What is my name?` (mismo sessionId) → responde "Alberto"
4. Cambiar sessionId → `What is my name?` → no sabe

## ⚠️ Errores comunes
- Esperar `$json.text` en vez de `$json.output`
- Cambiar sessionId sin querer → pierde memoria
- No decir "ALWAYS use Calculator" → agent calcula mal

## 🔍 Cómo ver que usó el tool
En Output Panel del Agent → expandir → ver "Tool Calls"
