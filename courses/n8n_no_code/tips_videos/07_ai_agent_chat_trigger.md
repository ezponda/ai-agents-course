# Tips Video: 07 AI Agent Chat Trigger

## Concepto clave
Chat Trigger = entrada tipo CHAT (no Manual Trigger). Conversación real con memoria + búsqueda de salarios.

## Flujo del workflow
```
Chat Trigger → AI Agent ← [SerpAPI, Calculator, Think, Memory, Chat Model] → Output
```

---

## 📋 COPY-PASTE: Fields y Prompts

### When chat message received (Chat Trigger)

| Setting | Value |
|---------|-------|
| Public | `true` |
| Mode | `Webhook` |
| Response Mode | `Last Node` |

### AI Agent — Salary Chat

**System Message:**
```
You are a salary research assistant inside an n8n AI Agent workflow.
Be concise.
If the user asks about salaries, job markets, or company info, search Google first.
If the user asks for arithmetic, use the Calculator tool.
Use Think to plan multi-step research.
If the user asks you to remember something, store it in memory and confirm briefly.
If you don't know, say so.
```

**Prompt (User Message):**
```
{{ $json.chatInput }}
```

### Simple Memory (10 messages)

| Setting | Value |
|---------|-------|
| Session ID Type | `Custom Key` |
| Session Key | `{{ $json.sessionId }}` |
| Context Window Length | `10` |

### Output — Chat Response

| Field | Expression |
|-------|------------|
| `output` | `{{ $json.output }}` |

---

## 🧪 Mensajes de prueba (en el chat)

**Búsqueda de salario:**
```
What is the average software engineer salary in Berlin?
```

**Cálculo de neto:**
```
Calculate the monthly net if annual gross is €55,000 with 30% tax
```

**Comparación:**
```
Compare data analyst vs data scientist salaries in London
```

**Memoria - guardar:**
```
Remember that I'm interested in Berlin for my job search.
```

**Memoria - recuperar:**
```
What city am I interested in?
```

---

## 🎬 Paso a paso para el video

### 1. Chat Trigger vs Manual Trigger
- **Mostrar:** El botón "Chat" en la UI de n8n
- **Explicar:** Abre ventana de chat, no usa pinned data
- **Destacar:** Más parecido a producción real

### 2. Cómo usar el Chat Trigger
- **Demo:** Click en "Chat" → se abre panel de chat
- **Mostrar:** Escribir mensaje → enviar → ver respuesta
- **Explicar:** Cada mensaje es una ejecución del workflow

### 3. Tools disponibles
- **Mostrar:** SerpAPI para buscar datos de salarios
- **Mostrar:** Calculator para cálculos de impuestos/neto
- **Mostrar:** Think para planificar antes de buscar
- **Destacar:** SerpAPI necesita API key configurada

### 4. Memory en contexto de chat
- **Mostrar:** sessionKey viene del Chat Trigger automáticamente
- **Explicar:** Misma sesión de chat = misma memoria
- **Demo:** Cerrar chat y abrir nuevo = nueva sesión

### 5. System message
- **Mostrar:** Reglas para salarios, cálculos, y memoria
- **Explicar:** Guía explícita para cada tipo de pregunta
- **Destacar:** "If you don't know, say so" — evita alucinaciones

### 6. Output — Chat Response
- **Mostrar:** Campo se llama `output` (para que Chat Trigger lo muestre)
- **Explicar:** Chat Trigger espera campo `output` para mostrar respuesta

---

## ✅ Puntos clave para el video
- [ ] Chat Trigger = entrada conversacional
- [ ] Memoria persiste DENTRO de la sesión
- [ ] Nueva ventana de chat = nueva sesión
- [ ] Output debe llamarse `output`
- [ ] SerpAPI necesita API key configurada

## 🎥 Demo sugerida
1. Abrir Chat en n8n
2. `What is the average software engineer salary in Berlin?` → ver que usa SerpAPI
3. `Calculate monthly net with 30% tax` → ver que usa Calculator
4. `Remember I'm interested in Berlin` → confirma
5. `What city am I interested in?` → responde "Berlin"
6. Cerrar chat, abrir nuevo → `What city am I interested in?` → no sabe

## ⚠️ Errores comunes
- Esperar que memoria persista entre sesiones de chat
- Output no se muestra → verificar que el campo se llama `output`
- Confundir Chat Trigger con Webhook Trigger
- No configurar credenciales de SerpAPI → búsquedas fallan

## 📧 Para producción
- Chat Trigger puede exponerse públicamente (toggle "Public")
- URL del chat se puede compartir
- Útil para chatbots internos de investigación de salarios
