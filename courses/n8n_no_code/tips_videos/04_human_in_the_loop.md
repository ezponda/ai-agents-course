# Tips Video: 04 Human-in-the-Loop

En n8n, un **webhook** es una **URL (endpoint HTTP)** que n8n “expone” para que **otros sistemas le envíen datos** (por ejemplo, cuando ocurre un evento), y con eso **disparar un workflow** o pasarle información.

## Concepto clave
AI genera borrador → Workflow PAUSA → Humano aprueba → Se envía.

## Flujo del workflow
```
Manual Trigger → Input (ticket) → Draft Response → Store Draft → ⏸️ WAIT → Output (approved)
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Support Ticket

| Field            | Value                                      |
| ---------------- | ------------------------------------------ |
| `ticket_subject` | `Urgent: Need refund for duplicate charge` |
| `ticket_body`    | (ver abajo)                                |
| `customer_email` | `maria@example.com`                        |

**ticket_body (para copiar):**
```
Hi,
I was charged twice for order #12345. The second charge of $89.99 appeared yesterday. Please refund ASAP as this is causing overdraft fees.
Thanks,
Maria
```

### Step 1 — Draft Response

**System Message:**
```
You are a customer support agent.
Draft a professional email reply.

Rules:
- Acknowledge the issue with empathy
- Confirm specific details (order #, amount)
- Explain the refund process and timeline
- Apologize for the inconvenience
- Keep under 150 words

Output ONLY the email body (no subject line).
```

**User Message:**
```
Subject: {{ $json.ticket_subject }}
Body:
{{ $json.ticket_body }}
Customer: {{ $json.customer_email }}

Draft the reply:
```

### Store Draft + Status

| Field | Expression |
|-------|------------|
| `draft_response` | `{{ $json.text }}` |
| `customer_email` | `{{ $node['Input — Support Ticket'].json.customer_email }}` |
| `ticket_subject` | `{{ $node['Input — Support Ticket'].json.ticket_subject }}` |
| `status` | `pending_approval` |
| `drafted_at` | `{{ $now.format('yyyy-MM-dd HH:mm') }}` |

### Wait — Human Approval

| Setting | Value |
|---------|-------|
| Resume | `Webhook` |
| Webhook Suffix | `{{ $execution.id }}` |

### Output — Approved Response

| Field | Expression |
|-------|------------|
| `final_response` | `{{ $node['Store Draft + Status'].json.draft_response }}` |
| `send_to` | `{{ $node['Store Draft + Status'].json.customer_email }}` |
| `subject` | `Re: {{ $node['Store Draft + Status'].json.ticket_subject }}` |
| `status` | `approved_and_sent` |

---

## 🎬 Paso a paso para el video

### 1. Input — Support Ticket
- **Mostrar:** ticket_subject, ticket_body, customer_email
- **Explicar:** Ticket urgente de refund
- **Destacar:** Incluye email del cliente para el envío final

### 2. Step 1 — Draft Response
- **Mostrar:** System message con reglas de empathy
- **Explicar:** "Output ONLY the email body (no subject line)"
- **Tip:** "En producción, el subject se añade después"

### 3. Store Draft + Status
- **Mostrar:** Guarda draft_response, customer_email, ticket_subject, status, drafted_at
- **Explicar:** status = "pending_approval", drafted_at = timestamp
- **Destacar:** `$now.format()` registra cuándo se creó el borrador
- **Tip:** "El revisor sabe si el draft es reciente o lleva horas esperando"

### 4. Wait — Human Approval ⏸️
- **Mostrar:** El nodo Wait con "Resume: Webhook"
- **Explicar:** El workflow SE PAUSA aquí
- **Mostrar:** Cómo obtener la Test URL (click en nodo → copy URL)
- **Demo:** Abrir URL en navegador → workflow continúa

### 5. Output — Approved Response
- **Mostrar:** status cambia a "approved_and_sent"
- **Explicar:** Aquí conectarías Gmail/Slack en producción

---

## ✅ Puntos clave para el video
- [ ] NUNCA enviar respuestas AI sin revisión humana
- [ ] Wait node = punto de control
- [ ] En producción: enviar draft + link de aprobación a Slack
- [ ] El workflow "recuerda" dónde estaba

## 🎥 Demo sugerida
1. Ejecutar workflow → se pausa en Wait
2. Mostrar el draft generado en Store Draft
3. Copiar Test URL del Wait node
4. Abrir URL en navegador
5. Ver que workflow continúa y termina

## ⚠️ Errores comunes
- Olvidar que en Test mode hay que copiar la Test URL
- No guardar datos antes del Wait (se pierden)
- En producción: olvidar enviar el link de aprobación

## 📧 Para producción
```
Store Draft → Slack/Email (envía draft + approval link) → Wait → Gmail (envía al cliente)
```
