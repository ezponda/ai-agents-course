# Tips Video: 03 Parallelization

## Concepto clave
3 análisis independientes en PARALELO → Merge → Respuesta final mejorada.

## Flujo del workflow
```
Manual Trigger → Input (email)
                    ├→ Branch A (Extract Facts) → Store
                    ├→ Branch B (Sentiment)     → Store  → Merge A+B → Merge (A+B)+C → Finalize → Output
                    └→ Branch C (Draft Reply)   → Store
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Customer Email

| Field           | Value                                          |
| --------------- | ---------------------------------------------- |
| `email_subject` | `Can't access my account after password reset` |
| `email_body`    | (ver abajo)                                    |

**email_body (para copiar):**
```
Hello,
I reset my password twice but I still can't log in. It says 'invalid token'.
I'm trying to access my invoices before end of day.
Can you help?
— Sam
```

### Branch A — Extract Facts

**System Message:**
```
Extract key facts from the email.
Return STRICT JSON with keys:
customer_name, issue, deadline, requested_action, missing_info (array).
Return JSON only.
```

**User Message:**
```
Subject: {{ $json.email_subject }}
Body:
{{ $json.email_body }}

JSON:
```

### Store Facts

| Field   | Type   | Expression                     |
| ------- | ------ | ------------------------------ |
| `facts` | Object | `{{ JSON.parse($json.text) }}` |

`JSON.parse()` convierte el string JSON del LLM en un objeto real.

### Branch B — Sentiment & Urgency

**System Message:**
```
Classify sentiment and urgency.
Return STRICT JSON with keys:
sentiment (positive|neutral|negative), urgency (low|medium|high), risk_flags (array).
Return JSON only.
```

**User Message:**
```
Subject: {{ $json.email_subject }}
Body:
{{ $json.email_body }}

JSON:
```

### Store Sentiment

| Field       | Type   | Expression                     |
| ----------- | ------ | ------------------------------ |
| `sentiment` | Object | `{{ JSON.parse($json.text) }}` |

### Branch C — Draft Reply

**System Message:**
```
Draft a helpful customer support email reply.
Rules:
- Friendly and concise
- Ask for missing info only if needed
- Offer 1–2 concrete next steps
- Under 140 words

Output ONLY the reply text.
```

**User Message:**
```
Subject: {{ $json.email_subject }}
Body:
{{ $json.email_body }}

Reply:
```

### Store Draft Reply

| Field | Expression |
|-------|------------|
| `draft_reply` | `{{ $json.text }}` |

### Merge A+B / Merge (A+B)+C

| Setting | Value |
|---------|-------|
| Mode | `Combine` |
| Combine By | `Combine By Position` |

### Finalize — One Improved Reply

**System Message:**
```
You are a senior support agent.
You will receive:
- Parsed customer facts (name, issue, deadline, requested action)
- Parsed sentiment analysis (sentiment, urgency, risk flags)
- A draft reply

Task:
1) Improve the draft to match urgency and include any critical missing info questions.
2) Keep it under 160 words.
3) Output ONLY the final reply text.
```

**User Message:**
```
Customer: {{ $json.facts.customer_name }}
Issue: {{ $json.facts.issue }}
Deadline: {{ $json.facts.deadline }}
Requested action: {{ $json.facts.requested_action }}

Sentiment: {{ $json.sentiment.sentiment }}
Urgency: {{ $json.sentiment.urgency }}
Risk flags: {{ $json.sentiment.risk_flags.join(', ') }}

Draft reply:
{{ $json.draft_reply }}

Final reply:
```

### Output — Final Reply

| Field | Expression |
|-------|------------|
| `final_reply` | `{{ $json.text }}` |

---

## 🎬 Paso a paso para el video

### 1. Input — Customer Email
- **Mostrar:** email_subject y email_body
- **Explicar:** Email urgente con problema técnico
- **Tip:** "Deadline 'end of day' = urgencia alta"

### 2. Las 3 ramas paralelas
- **Mostrar:** En el canvas, las 3 conexiones salen del mismo nodo
- **Explicar:** n8n las ejecuta SIMULTÁNEAMENTE
- **Destacar:** Ahorra tiempo vs hacerlo secuencial

### 3. Branch A — Extract Facts
- **Mostrar:** System message pide JSON con keys específicos
- **Explicar:** customer_name, issue, deadline, etc.
- **Destacar:** "STRICT JSON" + `JSON.parse()` en Store Facts convierte string → objeto real
- **Tip:** "Ahora puedes acceder a `$json.facts.customer_name` directamente"

### 4. Branch B — Sentiment & Urgency
- **Mostrar:** Clasificación (positive/neutral/negative, low/medium/high)
- **Explicar:** Detecta riesgo y urgencia
- **Tip:** "risk_flags puede indicar cliente enfadado"

### 5. Branch C — Draft Reply
- **Mostrar:** Escribe respuesta sin ver los otros análisis
- **Explicar:** Borrador inicial, se mejorará después

### 6. Merge A+B y Merge (A+B)+C
- **Mostrar:** Modo "Combine by Position"
- **Explicar:** Une los 3 outputs en UN objeto JSON
- **Tip:** "Ahora tenemos facts + sentiment + draft juntos"

### 7. Finalize — One Improved Reply
- **Mostrar:** Recibe los 3 campos combinados
- **Explicar:** "Senior support agent" mejora el draft
- **Destacar:** Usa urgency para ajustar tono

---

## ✅ Puntos clave para el video
- [ ] Paralelo = más rápido que secuencial
- [ ] Cada branch hace UNA cosa bien
- [ ] Merge combina resultados
- [ ] Finalize sintetiza todo

## 🎥 Demo sugerida
1. Ejecutar workflow
2. Mostrar que las 3 ramas tienen output
3. Mostrar el Merge con los 3 campos juntos
4. Comparar draft original vs final mejorado

## ⚠️ Errores comunes
- Merge en modo incorrecto → no combina bien
- Olvidar que branches deben ser INDEPENDIENTES
- JSON mal formado en branches A/B
