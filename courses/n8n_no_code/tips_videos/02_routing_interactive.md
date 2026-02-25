# Clase: Routing — Vídeo

**Workflow base:** `02_routing.json` (ya importado)
**Pre-requisito:** Credenciales configuradas (ver vídeo `00_configurar_credenciales`)

Tres cambios sobre el workflow base:
1. Chat Trigger (input interactivo)
2. Text Classifier reemplaza Router LLM + Store Route + Switch (3 nodos → 1)
3. Categoría fallback "other" para casos no reconocidos

---

## Paso 0: Mostrar el workflow base

1. Abrir `02_routing.json`
2. Zoom out para ver la estructura: Input → Router → Store → Switch → 3 especialistas
3. Ejecutar → mostrar cómo el Router clasifica y el Switch envía por la rama correcta

**Qué decir:**

> "El patrón de Routing clasifica el input y lo envía por diferentes caminos. Aquí un LLM lee un ticket de soporte y devuelve una etiqueta: 'refund', 'order_status', o 'support'. Esa etiqueta pasa por el Switch, que decide qué especialista responde."
>
> "Fijaos en un detalle clave: el Router tiene que devolver SOLO la etiqueta, en minúsculas, sin puntuación. Si devuelve 'Refund' con mayúscula, el Switch falla. Por eso el Store Route hace `.trim().toLowerCase()` como protección."
>
> "Funciona, pero son tres nodos solo para clasificar: el LLM, el Store, y el Switch. Hay una forma más directa."

---

## Paso 1: Chat Trigger

1. Duplicar el workflow (click derecho → Duplicate)
2. Eliminar **Manual Trigger**
3. Añadir **Chat Trigger** (buscar "When chat message received")
4. Conectar Chat Trigger → Input — Support Ticket
5. Abrir **Input — Support Ticket**, cambiar los campos:

| Campo | Modo | Valor |
|-------|------|-------|
| `ticket_subject` | Expression | 📋 `{{ $json.chatInput.split('\n')[0] ?? 'Customer inquiry' }}` |
| `ticket_body` | Expression | 📋 `{{ $json.chatInput }}` |

6. Click en **Chat** → pegar un ticket → ejecutar

**Qué decir:**

> "Mismo concepto que en los otros workflows: Chat Trigger para que el usuario pueda escribir directamente."

**Test:**

📋
```
Quiero un reembolso, me cobraron dos veces por el pedido #999
```
→ Debe clasificar como `refund` y responder con el especialista de reembolsos

---

## Paso 2: Text Classifier (reemplaza Router + Store + Switch)

**Qué decir:**

> "Ahora tenemos tres nodos para clasificar: el LLM que lee el ticket, el Store que guarda la etiqueta, y el Switch que compara. n8n tiene un nodo que hace todo esto: Text Classifier."

1. Eliminar **Router — Choose Route**, **Store Route**, y **Switch — Route**
2. Añadir **Text Classifier** (buscar "Text Classifier")
3. Conectar Input — Support Ticket → Text Classifier
4. Conectar el **Chat Model** al Text Classifier (línea punteada)
5. Configurar:

| Campo | Valor |
|-------|-------|
| **Input Text** | 📋 `{{ $json.ticket_subject }}\n{{ $json.ticket_body }}` (Expression) |

6. En **Categories**, añadir (click en "Add Category" tres veces):

| Category Name | Description |
|---------------|-------------|
| `refund` | 📋 `Customer wants money back, was charged incorrectly, duplicate charge, billing issue` |
| `order_status` | 📋 `Customer asking about delivery, shipping, tracking, where is my order` |
| `support` | 📋 `General help, login issues, account problems, technical support` |

7. Conectar las salidas del Text Classifier a los especialistas:
   - Output "refund" → Refund Specialist
   - Output "order_status" → Order Status Specialist
   - Output "support" → Support Specialist

**Qué decir:**

> "Fijaos: tres nodos menos. Text Classifier define las categorías con descripciones, y cada categoría tiene su propia salida — como un Switch integrado. No necesito preocuparme de mayúsculas, trim, ni match exacto."
>
> "Internamente es lo mismo: un LLM con un prompt generado automáticamente. Pero la configuración es más clara y menos propensa a errores."

8. Ejecutar con los mismos tickets → verificar que clasifica igual

### Diagrama

```
┌──────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Chat   │────▶│ Input — Support │────▶│ Text Classifier  │
│  Trigger │     │ Ticket          │     │                  │
└──────────┘     └─────────────────┘     └──────────────────┘
                                                │ │ │
                                     refund ────┘ │ └──── support
                                                  │
                                          order_status
                                              │ │ │
                                              ▼ ▼ ▼
                                        (especialistas)
                                              │ │ │
                                              ▼ ▼ ▼
                                            Output
```

---

## Paso 3: Añadir categoría fallback ("other")

**Qué decir:**

> "¿Qué pasa si alguien escribe 'Cuánto cuesta la suscripción premium'? No es refund, ni order_status, ni support. Sin fallback, el ticket desaparece. Siempre hay que tener un catch-all."

1. En Text Classifier, click **Add Category**:

| Category Name | Description |
|---------------|-------------|
| `other` | 📋 `Anything that doesn't fit the other categories: product questions, pricing, complaints, feedback` |

2. Añadir **Basic LLM Chain** → renombrar a `Fallback Response`
3. Conectar Text Classifier output "other" → Fallback Response
4. Conectar el **Chat Model** al Fallback Response (línea punteada)
5. Configurar:

**System Message:**

📋
```
You are a helpful customer support agent.
The customer's request doesn't fit our standard categories.

Rules:
- Acknowledge their message
- If it's a product/pricing question, say you'll connect them with sales
- If it's feedback, thank them
- If unclear, ask a clarifying question
- Keep it under 100 words

Output ONLY the response.
```

**User Message (Expression):**

📋
```
Subject: {{ $json.ticket_subject }}
Body:
{{ $json.ticket_body }}

Write the reply:
```

6. Conectar Fallback Response → Output

### Probar

**Test — Fuera de categorías:**

📋
```
¿Cuánto cuesta la suscripción premium?
```
→ Debe ir por "other" y ofrecer conectar con ventas

**Test — Ambiguo:**

📋
```
Tengo un problema
```
→ Puede ir a "support" o "other" — en ambos casos hay una respuesta útil

**Test — Los de siempre:**

📋
```
Me cobraron dos veces por el pedido #12345
```
→ Sigue yendo a "refund"

📋
```
¿Dónde está mi pedido? Lo pedí hace una semana
```
→ Sigue yendo a "order_status"

**Qué decir:**

> "Cuatro categorías, cuatro caminos, y ningún ticket se pierde. La categoría 'other' es esencial en producción. Si algo no encaja, mejor dar una respuesta genérica que no responder nada."

**Workflow expandido:** `expanded_workflows/02_routing_interactive.json`

---

## Qué decir al cerrar

> "Hemos simplificado el routing de 6 nodos (LLM + Store + Switch + 3 salidas) a 1 nodo (Text Classifier con 4 salidas). Y añadimos un fallback para que ningún ticket se pierda."
>
> "La clave: Text Classifier es perfecto cuando tienes categorías fijas y bien definidas. Si necesitas más control sobre el prompt de clasificación, siempre puedes volver al Router LLM + Switch del workflow base."

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Todo va a "other" | Las descripciones de las otras categorías son muy restrictivas — ampliar con más ejemplos |
| Text Classifier clasifica mal | Ser más específico en las descripciones — incluir qué SÍ y qué NO entra |
| Los outputs no conectan bien | Cada categoría tiene su propio output. Arrastrar desde el output específico, no del nodo en general |
| El chat muestra JSON en vez de texto | El último nodo debe tener un campo llamado `output` |
