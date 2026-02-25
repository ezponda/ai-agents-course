# Clase: Human-in-the-Loop — Vídeo

**Workflow base:** `04_human_in_the_loop.json` (ya importado)
**Pre-requisito:** Credenciales configuradas (ver vídeo `00_configurar_credenciales`)

Tres cambios sobre el workflow base:
1. Approve/Reject con query params (dos caminos según decisión)
2. Timeout (si nadie responde, escalar automáticamente)
3. Emails: notificar al aprobador con links de approve/reject + enviar al cliente si aprobado

---

## Paso 0: Mostrar el workflow base

1. Abrir `04_human_in_the_loop.json`
2. Zoom out para ver la estructura: Input → Draft LLM → Store Draft → Wait → Output
3. Ejecutar → mostrar que se pausa en el Wait

**Qué decir:**

> "Human-in-the-Loop es el patrón más importante para producción. La AI genera un borrador, pero un humano tiene que aprobar antes de que se envíe."
>
> "El nodo clave es Wait. Pausa la ejecución hasta que recibe una señal externa. Aquí usa modo webhook: genera una URL única, y cuando alguien la abre, el workflow continúa."

### Demostrar el Wait

1. Ejecutar el workflow → se pausa en Wait (círculo naranja)
2. Click en el nodo **Wait**
3. En el panel derecho, copiar la **Test URL**
4. Abrir la URL en el navegador → el workflow continúa y termina
5. Volver a n8n y ver que llegó al Output

**Qué decir:**

> "Funciona, pero hay dos problemas. Primero: solo hay una opción (aprobar). ¿Y si el aprobador quiere rechazar? Segundo: no hay timeout. Si nadie abre el link, el workflow se queda pausado para siempre."

---

## Paso 1: Approve/Reject con query params

**Qué decir:**

> "Vamos a dar dos opciones al aprobador: aprobar o rechazar. El truco es usar la misma URL del Wait pero con un parámetro diferente."

1. Duplicar el workflow (click derecho → Duplicate)
2. Después del **Wait**, eliminar el Output actual
3. Añadir un nodo **If** (renombrar a `Check Decision`)
4. Conectar Wait → Check Decision
5. Configurar la condición:

| Value 1 (Expression) | Operation | Value 2 |
|----------------------|-----------|---------|
| 📋 `{{ $json.query.decision }}` | Equals | 📋 `approve` |

### Rama True → Aprobado

6. Añadir **Edit Fields** → renombrar a `Output — Approved`
7. Conectar Check Decision (True) → Output — Approved
8. Configurar:

| Campo | Tipo | Valor |
|-------|------|-------|
| `final_response` | String | 📋 `{{ $node['Store Draft + Status'].json.draft_response }}` (Expression) |
| `send_to` | String | 📋 `{{ $node['Store Draft + Status'].json.customer_email }}` (Expression) |
| `subject` | String | 📋 `Re: {{ $node['Store Draft + Status'].json.ticket_subject }}` (Expression) |
| `status` | String | 📋 `approved` |

### Rama False → Rechazado

9. Añadir **Edit Fields** → renombrar a `Output — Rejected`
10. Conectar Check Decision (False) → Output — Rejected
11. Configurar:

| Campo | Tipo | Valor |
|-------|------|-------|
| `status` | String | 📋 `rejected` |
| `ticket_subject` | String | 📋 `{{ $node['Store Draft + Status'].json.ticket_subject }}` (Expression) |
| `reason` | String | 📋 `Response rejected by reviewer — ticket returned to queue` |

### Probar

12. Ejecutar → copiar la Test URL del Wait
13. Pegar en el navegador añadiendo el parámetro:

**Para aprobar:**
```
TEST_URL?decision=approve
```

**Para rechazar:**
```
TEST_URL?decision=reject
```

14. Ver qué rama se activa

**Qué decir:**

> "El Wait recibe todo lo que venga en la URL como query parameters. Si el link tiene `?decision=approve`, el If detecta 'approve' y va por la rama de aprobación. Si tiene `?decision=reject`, va por la otra."
>
> "En producción, estos dos links se enviarían por Slack o email al aprobador. Uno verde para aprobar, otro rojo para rechazar."

---

## Paso 2: Timeout

**Qué decir:**

> "¿Qué pasa si nadie responde? El workflow se queda pausado para siempre. Necesitamos un timeout."

1. Abrir el nodo **Wait — Human Approval**
2. Activar **Limit Wait Time**
3. Configurar:

| Campo | Valor |
|-------|-------|
| **Limit Type** | After Time Interval |
| **Amount** | 📋 `1` |
| **Unit** | 📋 `Minutes` (para testing; en producción: `Hours`) |

4. Ahora el If necesita manejar tres casos. Cuando hay timeout, `$json.query` no existe

5. Modificar **Check Decision**: cambiar la condición a:

| Value 1 (Expression) | Operation | Value 2 |
|----------------------|-----------|---------|
| 📋 `{{ $json.query?.decision }}` | Equals | 📋 `approve` |

> El `?.` (optional chaining) evita un error si `query` no existe (timeout).

6. Añadir otro **If** en la rama False → renombrar a `Check Rejected`
7. Conectar Check Decision (False) → Check Rejected
8. Configurar:

| Value 1 (Expression) | Operation | Value 2 |
|----------------------|-----------|---------|
| 📋 `{{ $json.query?.decision }}` | Equals | 📋 `reject` |

9. Mover **Output — Rejected** a Check Rejected (True)

### Rama timeout

10. Añadir **Edit Fields** → renombrar a `Output — Timeout`
11. Conectar Check Rejected (False) → Output — Timeout
12. Configurar:

| Campo | Tipo | Valor |
|-------|------|-------|
| `status` | String | 📋 `escalated_timeout` |
| `ticket_subject` | String | 📋 `{{ $node['Store Draft + Status'].json.ticket_subject }}` (Expression) |
| `reason` | String | 📋 `No response within time limit — escalated automatically` |

### Probar el timeout

13. Ejecutar → NO abrir ningún link
14. Esperar 1 minuto → ver que el workflow continúa solo y va por la rama timeout

**Qué decir:**

> "Si nadie responde en el tiempo límite, el workflow continúa sin datos de webhook. `$json.query` no existe, así que ambos If fallan y vamos a la rama de timeout."
>
> "En producción, aquí enviaríais una alerta a Slack: 'Nadie aprobó este ticket en 2 horas, escalando a manager'. O podríais auto-enviar el draft si confiáis en la calidad."

---

## Paso 3: Emails — notificar al aprobador + enviar al cliente

**Qué decir:**

> "Hasta ahora el aprobador tiene que copiar la URL del nodo Wait manualmente. En producción, eso no funciona. Vamos a enviarle un email con los links de aprobar y rechazar. Y si aprueba, enviar el email al cliente automáticamente."

### 3a: Notificar al aprobador (antes del Wait)

1. Añadir **Send Email** entre **Store Draft + Status** y **Wait**
2. Renombrar a `Notify Approver`
3. Conectar Store Draft + Status → Notify Approver (rama paralela — el Wait sigue conectado también)
4. Configurar:

| Campo | Valor |
|-------|-------|
| **From Email** | 📋 `workflow@yourcompany.com` |
| **To Email** | 📋 `reviewer@yourcompany.com` |
| **Subject** | 📋 `Review needed: {{ $json.ticket_subject }}` (Expression) |
| **Email Format** | HTML |

5. En **HTML Body** (Expression):

📋
```html
<h3>Support ticket needs your review</h3>
<p><b>Subject:</b> {{ $json.ticket_subject }}</p>
<p><b>Customer:</b> {{ $json.customer_email }}</p>
<p><b>Draft response:</b></p>
<blockquote style="border-left:3px solid #ccc;padding-left:12px;color:#555">
{{ $json.draft_response }}
</blockquote>
<hr>
<p style="font-size:16px">
  <a href="http://localhost:5678/webhook-test-waiting/{{ $execution.id }}?decision=approve">APPROVE</a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="http://localhost:5678/webhook-test-waiting/{{ $execution.id }}?decision=reject">REJECT</a>
</p>
```

**Qué decir:**

> "El truco está en la URL. Sabemos que el Wait genera un webhook en `webhook-test-waiting/{execution_id}`. Como `$execution.id` está disponible en cualquier nodo, podemos construir la URL antes de que el Wait se ejecute."
>
> "El aprobador recibe un email con el borrador y dos links. No tiene que abrir n8n. Solo hace click."

> **Nota:** `webhook-test-waiting` es la ruta en modo test (ejecución manual). En producción (workflow activado), la ruta es `webhook-waiting`.

> **Nota:** Send Email requiere credenciales SMTP. Si no las tenéis configuradas, el nodo fallará — pero el Wait seguirá funcionando porque es una rama paralela. Podéis copiar la URL manualmente como antes. Alternativas: Gmail node, Outlook node, Slack, o Telegram.

### 3b: Enviar al cliente (después del approve)

6. Añadir **Send Email** después de **Output — Approved**
7. Renombrar a `Send Email`
8. Conectar Output — Approved → Send Email
9. Configurar:

| Campo | Valor |
|-------|-------|
| **From Email** | 📋 `support@yourcompany.com` |
| **To Email** | 📋 `{{ $json.send_to }}` (Expression) |
| **Subject** | 📋 `{{ $json.subject }}` (Expression) |
| **Text** | 📋 `{{ $json.final_response }}` (Expression) |

**Qué decir:**

> "Ahora el ciclo completo: la AI genera el draft, el aprobador recibe un email con los links, hace click en aprobar, y el email se envía al cliente automáticamente. El humano no tiene que abrir n8n, ni copiar, ni pegar. Solo un click."

### Diagrama final

```
                                                                        ┌─────────────────┐
                                                                        │ Notify Approver  │
                                                                        │ (email con links)│
                                                                        └─────────────────┘
                                                                              ▲
┌──────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────────┐     ┌─────────────────┐
│ Manual       │────▶│ Input —     │────▶│ Draft LLM   │────▶│ Store Draft + │──┬─▶│ Wait            │
│ Trigger      │     │ Ticket      │     │             │     │ Status        │  │  │ (timeout: 1min) │
└──────────────┘     └─────────────┘     └─────────────┘     └───────────────┘  │  └─────────────────┘
                                                                                │          │
                                                                    (paralelo)─┘   ┌──────┴──────┐
                                                                                   ▼             ▼
                                                                             ┌──────────┐  ┌──────────────┐
                                                                             │ Approved?│  │ (not approve)│
                                                                             │ (If)     │  └──────────────┘
                                                                             └──────────┘         │
                                                                                │           ┌─────┴─────┐
                                                                          approve│          ▼           ▼
                                                                                ▼      Rejected?    Timeout
                                                                          ┌──────────┐  (If)      (fallback)
                                                                          │ Output   │
                                                                          │ Approved │
                                                                          └──────────┘
                                                                                │
                                                                                ▼
                                                                          ┌──────────┐
                                                                          │ Send     │
                                                                          │ Email    │
                                                                          └──────────┘
```

**Workflow expandido:** `expanded_workflows/04_human_in_the_loop_interactive.json`

---

## Qué decir al cerrar

> "Human-in-the-Loop en tres niveles:"
>
> "1. Básico: Wait node, un link de aprobación"
> "2. Producción: approve/reject con query params, timeout para no olvidar tickets"
> "3. Completo: el aprobador recibe un email con los links, y si aprueba, el email se envía al cliente automáticamente"
>
> "Este patrón genera confianza. Los stakeholders saben que nada sale sin supervisión humana. Y cuando confíen en la calidad de los drafts, podéis acortar el timeout o incluso auto-aprobar casos simples."

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| El Wait no se resume al abrir la URL | Verificar que el workflow está en estado "waiting" (círculo naranja). Si terminó, ejecutar de nuevo |
| `query.decision` está vacío | Verificar que la URL incluye `?decision=approve` o `?decision=reject` |
| El timeout no funciona | Activar "Limit Wait Time" en la configuración del Wait |
| Send Email falla | Necesita credenciales SMTP configuradas. Alternativa: Gmail node o Outlook node |
| El If siempre va por False | Usar `$json.query?.decision` (con `?.`) para evitar error cuando query no existe (timeout) |
