# Clase: Parallelization — Vídeo

**Workflow base:** `03_parallelization.json` (ya importado)
**Pre-requisito:** Credenciales configuradas (ver vídeo `00_configurar_credenciales`)

Tres cambios sobre el workflow base:
1. Chat Trigger (input interactivo)
2. Information Extractor (reemplaza Branch A)
3. Routing post-merge (urgencia alta → respuesta express)

---

## Paso 0: Mostrar el workflow base

1. Abrir `03_parallelization.json`
2. Zoom out para ver la estructura: Input → 3 branches → Merge → Finalize → Output
3. Ejecutar una vez → mostrar el output de cada branch

**Qué decir:**

> "Este workflow analiza un email de soporte desde tres ángulos en paralelo: extrae hechos, analiza sentimiento, y genera un borrador. Después los combina con Merge y un LLM final mejora la respuesta."
>
> "Ningún branch depende de otro — por eso pueden ir en paralelo. El Merge espera a los tres y combina sus resultados con 'Combine by Position'."
>
> "Como siempre, el email está hardcoded. Vamos a hacerlo interactivo."

---

## Paso 1: Chat Trigger

1. Duplicar el workflow (click derecho → Duplicate)
2. Eliminar **Manual Trigger**
3. Añadir **Chat Trigger** (buscar "When chat message received")
4. Conectar Chat Trigger → Input — Customer Email
5. Abrir **Input — Customer Email**, cambiar los campos:

| Campo           | Modo       | Valor                                                           |
| --------------- | ---------- | --------------------------------------------------------------- |
| `email_subject` | Expression | 📋 `{{ $json.chatInput.split('\n')[0] ?? 'Customer inquiry' }}` |
| `email_body`    | Expression | 📋 `{{ $json.chatInput }}`                                      |

6. Click en **Chat** → pegar un email → ejecutar

**Qué decir:**

> "Ahora puedo pegar cualquier email en el chat y el sistema lo analiza desde tres ángulos. Fijaos en la expresión del subject: coge la primera línea del texto. Si no hay salto de línea, usa un valor por defecto."

**Test:**

📋
```
Hola equipo,

Llevo tres días intentando acceder a mi cuenta sin éxito. El sistema dice "token inválido".

Necesito urgentemente descargar mis facturas antes del cierre fiscal del viernes.

¿Pueden ayudarme lo antes posible?

Gracias,
Carlos
```

---

## Paso 2: Information Extractor (reemplazar Branch A)

**Qué decir:**

> "Branch A usa un Basic LLM Chain que pide JSON con un prompt. Funciona, pero hay un nodo especializado para esto: Information Extractor. En vez de escribir un prompt, defines los campos que quieres extraer."

1. Eliminar **Branch A — Extract Facts**
2. Añadir **Information Extractor** (buscar "Information Extractor")
3. Conectar Input — Customer Email → Information Extractor → Store Facts
4. Conectar el **Chat Model** al Information Extractor (línea punteada)
5. Configurar:

| Campo | Valor |
|-------|-------|
| **Text** | 📋 `{{ $json.email_body }}` (Expression) |

6. En **Attributes to Extract**, añadir:

| Attribute Name     | Data Type   | Description                                 |
| ------------------ | ----------- | ------------------------------------------- |
| `customer_name`    | 📋 `String` | 📋 `The name of the customer if mentioned`  |
| `issue`            | 📋 `String` | 📋 `The main problem or question they have` |
| `deadline`         | 📋 `String` | 📋 `Any time-sensitive deadline mentioned`  |
| `requested_action` | 📋 `String` | 📋 `What they want us to do`                |

7. Abrir **Store Facts**, cambiar el valor de `facts`:

| Campo | Tipo | Valor |
|-------|------|-------|
| `facts` | Object | 📋 `{{ $json.output }}` (Expression) |

> Antes usábamos `JSON.parse($json.text)` porque el LLM devolvía un string JSON. Information Extractor ya devuelve un objeto — no hace falta parsear.

8. Ejecutar → verificar que extrae los mismos campos

**Qué decir:**

> "Mismo resultado, pero más mantenible. Si mañana quiero añadir un campo 'language' para detectar el idioma, solo añado una línea aquí. Con el prompt del LLM tendría que modificar texto y esperar que no rompa el JSON."
>
> "Regla general: si necesitas extraer campos estructurados de texto, Information Extractor. Si necesitas lógica más compleja o texto libre, Basic LLM Chain."

---

## Paso 3: Routing post-merge

**Qué decir:**

> "Después del merge tenemos facts + sentiment + draft en un solo objeto. Ahora podemos tomar decisiones: si Branch B detectó urgencia alta, usamos un prompt más empático."

1. Después de **Merge (A+B)+C**, añadir un nodo **If** (renombrar a `Check Urgency`)
2. Configurar la condición:

| Value 1 (Expression) | Operation | Value 2 |
|----------------------|-----------|---------|
| 📋 `{{ $json.sentiment.urgency }}` | Equals | 📋 `high` |

3. Conectar **Merge (A+B)+C** → **Check Urgency**
4. Desconectar Merge del Finalize original

### Rama True → Express Response

5. Duplicar **Finalize — One Improved Reply** → renombrar a `Finalize — Express`
6. Conectar **Check Urgency** (True) → **Finalize — Express**
7. Cambiar el **System Message**:

📋
```
You are a senior support agent handling an URGENT case.
You will receive:
- Parsed customer facts (name, issue, deadline, requested action)
- Parsed sentiment analysis (sentiment, urgency, risk flags — this is HIGH URGENCY)
- A draft reply

Task:
1) The customer is stressed or in a hurry. Show empathy first.
2) Acknowledge the urgency explicitly
3) Promise fast resolution or immediate escalation
4) If you need info, ask only the most critical question
5) Keep it under 140 words
6) Output ONLY the final reply text.
```

8. Conectar el **Chat Model** al Finalize — Express (línea punteada)

### Rama False → Standard Response

9. Conectar **Check Urgency** (False) → **Finalize — One Improved Reply** (el original)

### Ambas ramas → Output

10. Renombrar el Output a `Output` y cambiar el campo:

| Campo | Valor |
|-------|-------|
| `output` | 📋 `{{ $json.text }}` (Expression) |

11. Conectar **Finalize — Express** → Output
12. Conectar **Finalize — One Improved Reply** → Output

### Diagrama final

```
                                 ┌──────────────────────┐     ┌──────────────┐
                            ┌───▶│ Information Extractor│────▶│ Store Facts  │────┐
                            │    └──────────────────────┘     └──────────────┘    │
┌──────────┐  ┌───────────┐─┤                                                     ├──▶ Merge A+B ──┐
│   Chat   │─▶│  Input    │ │    ┌──────────────────────┐     ┌──────────────┐    │                 │
│  Trigger │  │  Email    │ ├───▶│ Branch B — Sentiment │────▶│Store Sentim. │────┘                 │
└──────────┘  └───────────┘ │    └──────────────────────┘     └──────────────┘                      │
                            │                                                                       ├──▶ Merge (A+B)+C ──▶ Check Urgency
                            │    ┌──────────────────────┐     ┌──────────────┐                      │          │
                            └───▶│ Branch C — Draft     │────▶│ Store Draft  │──────────────────────┘      high│    │normal
                                 └──────────────────────┘     └──────────────┘                                 ▼    ▼
                                                                                                          Express  Standard
                                                                                                              └──┬──┘
                                                                                                              Output
```

### Probar

**Test — Urgente:**

📋
```
URGENTE: Necesito cancelar mi pedido AHORA. Acabo de darme cuenta de que usé la tarjeta equivocada y esa cuenta no tiene fondos. Por favor, cancelen antes de que se procese el pago.
```
→ Debe ir por rama Express (más empático, promete acción rápida)

**Test — Normal:**

📋
```
Hola, me gustaría saber el estado de mi pedido #12345. No hay prisa, solo curiosidad.
```
→ Debe ir por rama Standard

**Qué decir:**

> "Misma información de entrada, diferente tratamiento. El Express reconoce la urgencia, muestra empatía, promete resolución rápida. El Standard es profesional pero sin esa prioridad."
>
> "Podríamos llevar esto más lejos: si es urgente Y sentiment negativo, escalar a un humano en vez de responder automáticamente. Es el mismo patrón: combinar resultados paralelos para tomar decisiones inteligentes."

**Workflow expandido:** `expanded_workflows/03_parallelization_interactive.json`

---

## Qué decir al cerrar

> "El patrón de Parallelization analiza algo desde varios ángulos a la vez. Hoy vimos tres mejoras:"
>
> "1. Chat Trigger para input interactivo"
> "2. Information Extractor para extracción estructurada — más mantenible que un prompt de JSON"
> "3. Routing post-merge — usar los resultados combinados para tomar decisiones"
>
> "Para producción, podéis reemplazar el Chat Trigger por un Webhook o Schedule Trigger. Eso está en el Appendix B: Going Live."

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| El Merge no combina bien | Verificar que cada branch produce exactamente 1 item. Usar "Combine by Position" |
| Falta un campo después del Merge | Es correcto — cada Store node usa "Keep Only Set". El Merge los combina |
| El JSON.parse falla en Store Facts | Si usas Information Extractor, no necesitas JSON.parse — usa `{{ $json.output }}` |
| El If siempre va por False | Verificar que Branch B devuelve `urgency: "high"` (string, no `HIGH`) |
| El chat muestra JSON en vez de texto | El último nodo debe tener un campo llamado `output` |
