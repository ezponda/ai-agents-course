# Tips Video: 08 Prompt Engineering Comparison

## Concepto clave
4 versiones del mismo prompt, cada una mejor que la anterior. Ver la diferencia en vivo.

## Flujo del workflow
```
Manual Trigger → Input (message) → [V1, V2, V3, V4 en paralelo]
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Test Message

| Field | Value |
|-------|-------|
| `message` | `I was charged twice for my order last week` |

### V1 — Basic

**System Message:**
```
Classify this customer message:
```

**User Message:**
```
{{ $json.message }}
```

### V2 — Role + Structure

**System Message:**
```
You are a customer support classifier for an e-commerce company.

Categorize messages into exactly ONE category:
- BILLING (payments, charges, refunds, invoices)
- TECHNICAL (login issues, bugs, how-to questions)
- FEEDBACK (compliments, complaints, suggestions)
- GENERAL (everything else)

Respond with ONLY the category name. No explanations.
```

**User Message:**
```
{{ $json.message }}
```

### V3 — Few-Shot

**System Message:**
```
You are a customer support classifier for an e-commerce company.

Categorize messages into exactly ONE category:
- BILLING (payments, charges, refunds, invoices)
- TECHNICAL (login issues, bugs, how-to questions)
- FEEDBACK (compliments, complaints, suggestions)
- GENERAL (everything else)

Examples:

Message: "I was charged $50 but my order was only $30"
Category: BILLING

Message: "The app crashes when I try to checkout"
Category: TECHNICAL

Message: "I love your new website design!"
Category: FEEDBACK

Message: "What are your store hours?"
Category: GENERAL

Message: "I need a refund and the website won't load"
Category: BILLING

Respond with ONLY the category name.
```

**User Message:**
```
{{ $json.message }}
```

### V4 — Production

**System Message:**
```
You are a customer support classifier for an e-commerce company.

Categorize messages into exactly ONE category:
- BILLING (payments, charges, refunds, invoices)
- TECHNICAL (login issues, bugs, how-to questions)
- FEEDBACK (compliments, complaints, suggestions)
- GENERAL (everything else)

Examples:

Message: "I was charged $50 but my order was only $30"
Category: BILLING

Message: "The app crashes when I try to checkout"
Category: TECHNICAL

Message: "I love your new website design!"
Category: FEEDBACK

Message: "What are your store hours?"
Category: GENERAL

Message: "I need a refund and the website won't load"
Category: BILLING

Edge cases:
- If multiple issues, classify by PRIMARY concern (usually first)
- If empty, gibberish, or unrelated: GENERAL [INVALID]
- If uncertain between categories: pick most likely + [LOW CONFIDENCE]

Respond with ONLY the category name (and optional flag).
```

**User Message:**
```
{{ $json.message }}
```

---

## 🧪 Mensajes de prueba

**Caso claro - BILLING:**
```
I was charged twice for my order
```

**Caso claro - TECHNICAL:**
```
How do I reset my password?
```

**Caso claro - FEEDBACK:**
```
Your product is amazing!
```

**Múltiples issues:**
```
I need a refund and the website won't load
```

**Gibberish:**
```
asdfghjkl
```

**Ambiguo:**
```
Maybe billing? Or technical?
```

---

## 🎬 Paso a paso para el video

### 1. Mostrar el workflow
- **Explicar:** 4 LLM Chains en paralelo, mismo input
- **Mostrar:** Cada uno tiene prompt diferente

### 2. V1 — Basic
- **Problema:** No sabe qué categorías, no sabe formato
- **Output típico:** Párrafos de explicación

### 3. V2 — + Role & Structure
- **Mejora:** Rol definido, categorías claras, formato especificado
- **Output típico:** `BILLING`

### 4. V3 — + Few-Shot Examples
- **Mejora:** Ejemplos muestran exactamente qué esperamos
- **Output típico:** Consistente incluso con casos ambiguos

### 5. V4 — + Edge Cases (Production)
- **Mejora:** Maneja input inesperado sin romper
- **Output típico:** `BILLING` o `GENERAL [INVALID]`

---

## ✅ Puntos clave para el video
- [ ] Rol + Categorías = básico
- [ ] Few-shot = consistencia
- [ ] Edge cases = producción
- [ ] Cada técnica añade fiabilidad

## 🎥 Demo sugerida
Ejecutar 3 veces con diferentes inputs:
1. `I was charged twice` → todas funcionan
2. `asdfghjkl` → solo V4 maneja bien
3. `I need a refund but the site won't load` → ver priorización

## ⚠️ Errores comunes
- Empezar directamente con V4 (complejo)
- No testear edge cases antes de producción
- Few-shot con ejemplos que no cubren variedad

## 📚 Conexión con Appendix A
Este workflow ES el ejercicio práctico del Appendix A (Prompt Engineering Basics)
