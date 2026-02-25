# Tips Video: 02 Routing

## Concepto clave
Un LLM clasifica → Switch node envía por el camino correcto → Especialista responde.

## Flujo del workflow
```
Manual Trigger → Input (ticket) → Router (classify) → Store Route → Switch → [3 especialistas] → Output
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Support Ticket

| Field | Value |
|-------|-------|
| `ticket_subject` | `Refund request — charged twice` |
| `ticket_body` | `Hi team,`<br>`I was charged twice for order #A-10492.`<br>`Please refund the extra charge. I can provide a screenshot if needed.`<br>`Thanks,`<br>`Jamie` |

**ticket_body (para copiar):**
```
Hi team,
I was charged twice for order #A-10492.
Please refund the extra charge. I can provide a screenshot if needed.
Thanks,
Jamie
```

### Router — Choose Route

**System Message:**
```
You route customer support tickets.

Choose exactly ONE route label, lowercase, no punctuation:
- refund
- order_status
- support

Return ONLY the label.
```

**User Message:**
```
Subject: {{ $json.ticket_subject }}
Body:
{{ $json.ticket_body }}

Route label:
```

### Store Route

| Field | Expression |
|-------|------------|
| `route` | `{{ $json.text.trim().toLowerCase() }}` |

### Switch — Route

| Output | Condition |
|--------|-----------|
| `refund` | `{{ $json.route }}` equals `refund` |
| `order_status` | `{{ $json.route }}` equals `order_status` |
| `support` | `{{ $json.route }}` equals `support` |
| **Fallback** | Any unmatched value → goes to Support Specialist |

Enable **Fallback Output** in Options.

### Refund Specialist — Draft Reply

**System Message:**
```
You are a customer support specialist for refunds.
Write a short, professional reply.

Rules:
- Acknowledge the issue
- Ask for any missing info (only if needed)
- Explain next steps and expected timeline
- Keep it under 120 words

Output ONLY the reply.
```

**User Message:**
```
Subject: {{ $node['Input — Support Ticket'].json.ticket_subject }}
Body:
{{ $node['Input — Support Ticket'].json.ticket_body }}

Write the reply:
```

### Order Status Specialist — Draft Reply

**System Message:**
```
You are a customer support specialist for order status.
Write a short, professional reply.

Rules:
- Confirm you are checking the order
- Ask for order number if missing
- Provide what you can and what you still need
- Keep it under 120 words

Output ONLY the reply.
```

### Support Specialist — Draft Reply

**System Message:**
```
You are a general customer support specialist.
Write a short, professional reply.

Rules:
- Clarify the problem
- Ask 1–2 targeted questions (only if needed)
- Offer a next step
- Keep it under 120 words

Output ONLY the reply.
```

### Output nodes

| Field | Expression |
|-------|------------|
| `reply` | `{{ $json.text }}` |
| `route` | `refund` / `order_status` / `support` |

---

## 🧪 Tickets de prueba

**Para probar ruta `refund`:**
```
Subject: Refund request — charged twice
Body: I was charged twice for order #A-10492. Please refund.
```

**Para probar ruta `order_status`:**
```
Subject: Where is my order?
Body: I ordered 5 days ago and haven't received shipping info. Order #B-2234.
```

**Para probar ruta `support`:**
```
Subject: How do I change my password?
Body: I can't find the option to change my password in settings.
```

---

## 🎬 Paso a paso para el video

### 1. Input — Support Ticket
- **Mostrar:** ticket_subject y ticket_body
- **Explicar:** Simula un ticket real de soporte
- **Tip:** "Cambiar estos valores para probar diferentes rutas"

### 2. Router — Choose Route
- **Mostrar:** System message
- **Destacar:** "lowercase, no punctuation" — CRÍTICO para el Switch
- **Explicar:** Solo 3 opciones: refund, order_status, support
- **Tip:** "Si el LLM devuelve 'Refund' con mayúscula, el Switch falla"

### 3. Store Route
- **Mostrar:** `.trim().toLowerCase()` en la expresión
- **Explicar:** `.trim()` limpia espacios, `.toLowerCase()` normaliza mayúsculas

### 4. Switch — Route
- **Mostrar:** Las 3 condiciones (equals "refund", etc.) + Fallback Output
- **Explicar:** Case-sensitive — por eso usamos `.toLowerCase()`
- **Destacar:** Fallback envía labels inesperados a Support como catch-all

### 5. Especialistas
- **Mostrar:** Cada uno tiene system message diferente
- **Explicar:** Acceden al input original con `$node['Input — Support Ticket']`
- **Destacar:** Diferentes reglas para cada tipo de respuesta

---

## ✅ Puntos clave para el video
- [ ] El Router solo CLASIFICA, no responde
- [ ] Switch node necesita valores EXACTOS
- [ ] "lowercase, no punctuation" es el truco clave
- [ ] Especialistas acceden a nodos anteriores por nombre

## 🎥 Demo sugerida
1. Ejecutar con ticket de refund → mostrar ruta
2. Cambiar ticket a "Where is my order?" → ejecutar → mostrar ruta diferente
3. Mostrar cómo el Switch decide
4. Mostrar la respuesta del especialista

## ⚠️ Errores comunes
- LLM devuelve "REFUND" en mayúsculas → `.toLowerCase()` lo resuelve
- Olvidar .trim() → espacios rompen la comparación
- No activar Fallback Output → labels inesperados desaparecen silenciosamente
- No especificar "Return ONLY the label"

---

## 🔀 Switch Node: Tips avanzados

### Estructura if-elif-elif-else

Añadir múltiples reglas en orden. El Switch evalúa de arriba a abajo y sale por la primera que cumple:

```
Rule 0: $json.route equals "refund"     → Output: refund
Rule 1: $json.route equals "order"      → Output: order
Rule 2: $json.route equals "complaint"  → Output: complaint
Fallback (activar en settings)          → Output: other (el else)
```

### Condiciones con OR

**Problema:** No hay botón nativo de OR entre condiciones.

**Solución 1 - Múltiples reglas + Merge:**
```
Rule 0: $json.route equals "refund"   → Output 0
Rule 1: $json.route equals "REFUND"   → Output 1
Rule 2: $json.route equals "return"   → Output 2
```
Luego conectar Output 0, 1, 2 al mismo nodo Merge.

**Solución 2 - Expresión con includes():**
```
Value:    {{ ["refund", "REFUND", "return"].includes($json.route) }}
Operator: is equal to
Compare:  {{ true }}  (en Expression mode)
```

**Solución 3 - Regex case-insensitive:**
```
Value:    {{ /^refund$/i.test($json.route) }}
Operator: is equal to
Compare:  {{ true }}
```

### ⚠️ Error de tipos con booleanos

Si ves: `Wrong type: 'true' is a string but was expecting a boolean`

**Solución:** Convertir a string y comparar:
```
Value:    {{ String($json.route == "refund" || $json.route == "REFUND") }}
Operator: is equal to
Compare:  true  (en Fixed mode, como string)
```

### Condiciones AND (nativas)

Dentro de una misma regla, click "Add Condition" — se evalúan como AND:
```
Rule 0:
  Condition 1: $json.category equals "refund"
  AND
  Condition 2: $json.priority equals "high"
```
