# Build from Scratch: RAG FAQ Bot

## Objetivo del video

> "En este video vamos a construir un chatbot que responde preguntas usando SOLO una base de conocimiento — no inventa nada. Esto es RAG: Retrieval-Augmented Generation. En vez de que el LLM responda de memoria, primero BUSCA en tus documentos y responde con lo que encuentra. Vamos a construirlo paso a paso."

**Que vamos a construir:** un bot de FAQ para una empresa ficticia (DataLearn) que responde preguntas de clientes usando solo su base de datos de preguntas frecuentes. Si la respuesta no esta en el FAQ, dice que no lo sabe.

Un workflow con dos partes:

| Parte | Que construimos | Que concepto nuevo |
|-------|-----------------|---------------------|
| **A** | Indexing: Manual Trigger → FAQ Data → Vector Store (Insert) | Embeddings, chunking, vector store |
| **B** | Chat: Chat Trigger → AI Agent + Vector Store (as Tool) → Output | RAG como tool del agent, guardrails |

**Credenciales necesarias:**
- **OpenRouter API key** (para el chat model)
- **Google Gemini API key** (para embeddings) — gratis desde [ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key)

---

## Concepto clave: RAG en 30 segundos

> "Imaginad que teneis un empleado nuevo. Sabe muchas cosas generales, pero NO conoce las politicas de vuestra empresa. Que haceis? Le dais un manual. RAG hace exactamente eso: le da al LLM un manual que puede consultar antes de responder."

```
SIN RAG                                CON RAG
──────                                 ───────

User: "Cual es vuestra politica        User: "Cual es vuestra politica
       de reembolso?"                          de reembolso?"
         │                                        │
         ▼                                        ▼
    ┌─────────┐                           ┌─────────────────┐
    │   LLM   │                           │ Buscar en FAQ   │
    └─────────┘                           │ → "Reembolso    │
         │                                │   total en 30   │
         ▼                                │   dias..."      │
  "No tengo acceso a                      └─────────────────┘
   vuestras politicas."                           │
                                                  ▼
                                          ┌─────────────────┐
                                          │ LLM + contexto  │
                                          └─────────────────┘
                                                  │
                                                  ▼
                                          "Reembolso total
                                           en 30 dias..."
```

> "Hay tres pasos para que RAG funcione: primero INDEXAR los documentos (cortarlos en trozos y convertirlos en vectores), luego cuando el usuario pregunta, BUSCAR los trozos mas relevantes, y finalmente enviarlos al LLM para que responda."

---

## Parte A: Indexing — Cargar el FAQ en el Vector Store

> "Primero vamos a preparar la base de conocimiento. Es como meter todos los documentos en un archivador inteligente que entiende significados, no solo palabras."

### Paso 1: Crear workflow

1. **Workflows** → **Add Workflow**
2. Renombrar a "RAG FAQ Bot"

### Paso 2: Manual Trigger + FAQ Data

1. Añadir **Manual Trigger** → renombrar a `Load FAQ (run first)`
2. Añadir **Edit Fields** → renombrar a `FAQ Data`
3. Un campo String llamado `text`:

```
DataLearn Company FAQ

Q: What are your business hours?
A: Monday to Friday, 9 AM to 6 PM CET. Closed on Spanish public holidays. Support chat is available 24/7 for Premium plan users.

Q: How do I reset my password?
A: Go to Settings > Security > Change Password. You will receive a confirmation email within 5 minutes. If you do not receive it, check your spam folder or contact support.

Q: What is your refund policy?
A: Full refund within 30 days of purchase, no questions asked. Between 30 and 90 days, we offer 50% credit toward future purchases. No refunds after 90 days.

Q: How do I contact support?
A: Email support@datalearn.com or use the chat widget on our website. Average response time is under 2 hours during business hours. Premium users get priority support with a 30-minute response guarantee.

Q: What payment methods do you accept?
A: Visa, Mastercard, American Express, PayPal, and SEPA bank transfers. All prices are in EUR. Annual plans receive a 20% discount compared to monthly billing.

Q: Do you offer student discounts?
A: Yes, students get 40% off all annual plans with a valid university email address (.edu or equivalent). The discount renews automatically each year while the student email remains active.

Q: How do I cancel my subscription?
A: Go to Settings > Billing > Cancel Subscription. Your access continues until the end of the current billing period. There are no cancellation fees. You can reactivate anytime.

Q: What is your uptime guarantee?
A: 99.9% uptime for all paid plans. If uptime falls below this threshold in any calendar month, affected users automatically receive a prorated account credit.

Q: Can I export my data?
A: Yes, go to Settings > Data > Export. You can download all your data in CSV or JSON format. Data exports are available for 7 days after generation. We support GDPR data portability requests.

Q: Do you offer team plans?
A: Yes, team plans start at 5 users with centralized billing and admin controls. Teams of 10+ get volume pricing. Contact sales@datalearn.com for custom enterprise plans.
```

> "En un caso real, esto vendria de un PDF, una base de datos, o Google Drive. Aqui lo hardcodeamos para simplificar."

### Paso 3: Vector Store (Insert)

1. Añadir **In-Memory Vector Store** → renombrar a `Vector Store — Insert FAQ`
2. Configurar:

| Setting | Value |
|---------|-------|
| Mode | `Insert Documents` |
| Memory Key | `faq_store` |
| Clear Store | Activado |

> "El Memory Key es como el nombre de la estanteria. Luego cuando el agent busque, usara este mismo nombre para saber DONDE buscar. Clear Store borra todo antes de insertar — asi evitamos duplicados si ejecutamos varias veces."

### Paso 4: Añadir sub-nodos al Vector Store

> "Fijate en los conectores de puntos debajo del Vector Store. Para insertar documentos necesitamos tres cosas: un modelo de embeddings, un loader que lea los datos, y un splitter que los corte en trozos."

**Embeddings Google Gemini:**
1. Click en el conector **Embedding** del Vector Store
2. Seleccionar **Embeddings Google Gemini**
3. Configurar credencial de Google Gemini (gratis en [ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key))
4. Modelo: `text-embedding-004`

> "Los embeddings convierten texto en numeros — vectores — que representan el SIGNIFICADO. 'Reembolso' y 'devolucion' tienen vectores similares aunque sean palabras diferentes. Usamos Gemini porque es gratis."

**Default Data Loader:**
1. Click en el conector **Document** del Vector Store
2. Seleccionar **Default Data Loader**
3. Dejar la configuracion por defecto

> "El Data Loader lee los datos que llegan del nodo anterior. En nuestro caso, lee el campo `text` del FAQ Data."

**Recursive Character Text Splitter:**
1. Dentro del Default Data Loader, click en el conector **Text Splitter**
2. Seleccionar **Recursive Character Text Splitter**
3. Configurar:

| Setting | Value |
|---------|-------|
| Chunk Size | `400` |
| Chunk Overlap | `100` |

> "Esto es el chunking — cortar el texto en trozos manejables. Chunk Size 400 significa trozos de ~400 caracteres. Overlap 100 significa que cada trozo repite 100 caracteres del anterior. El overlap es importante: sin el, podrias cortar una frase por la mitad y perder contexto."

> "¿Por que 400 y no 1000? Nuestro FAQ tiene respuestas cortas. Chunks mas pequenos = busqueda mas precisa. Si tuvierais documentos largos con parrafos densos, usariais chunks mas grandes (500-1000)."

> "¿Por que Recursive y no otro splitter? Porque intenta cortar por parrafos, luego por frases, luego por palabras. Es el mas inteligente — respeta la estructura natural del texto."

### Paso 5: Conectar la parte de indexing

```
Load FAQ (run first) → FAQ Data → Vector Store — Insert FAQ
```

### Demo: Ejecutar el indexing

1. **Execute Workflow** (click en el boton de arriba)
2. Click en el nodo **Vector Store — Insert FAQ** para ver el resultado
3. Deberia mostrar los items insertados

> "Ya tenemos el FAQ en el vector store. Ahora cada pregunta esta convertida en vectores. Cuando el usuario pregunte 'politica de reembolso', el vector store encontrara el trozo sobre reembolsos aunque use palabras diferentes."

---

## Parte B: Chat — AI Agent con Vector Store como Tool

> "Ahora la parte interesante: un AI Agent que BUSCA en el FAQ antes de responder. El Vector Store se convierte en una herramienta — como la Calculator o SerpAPI, pero para buscar en documentos."

### Paso 6: Chat Trigger

1. Añadir **Chat Trigger** (buscar "When chat message received")
2. Ir a **Options** → Response Mode: `When Last Node Finishes`

> "El Chat Trigger crea la ventanita de chat. Response Mode 'When Last Node Finishes' significa que el chat espera a que el ultimo nodo termine antes de mostrar la respuesta."

### Paso 7: AI Agent

1. Añadir **AI Agent** → renombrar a `AI Agent — FAQ Assistant`
2. Configurar:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.chatInput }}`
3. Ir a **Options** → activar **System Message**:

```
You are a helpful FAQ assistant for DataLearn.

Rules:
- ALWAYS search the FAQ knowledge base before answering.
- Answer ONLY based on the information found in the FAQ.
- If the FAQ does not contain the answer, say: "I don't have that information in our FAQ. Please contact support@datalearn.com."
- Keep answers concise and friendly.
- Do not make up information.
```

> "El system message es CRITICO para RAG. Fijate en las reglas: 'ALWAYS search' obliga al agent a consultar el FAQ antes de responder. 'Answer ONLY based on the FAQ' le prohibe inventarse cosas. Sin estas reglas, el LLM puede ignorar el FAQ y responder con su conocimiento general — que puede ser incorrecto o inventado."

> "La regla de 'I don't have that information' es el guardrail principal. Si alguien pregunta '¿Cual es el sentido de la vida?' — eso NO esta en el FAQ, asi que debe decir que no lo sabe. Sin esta regla, el LLM responderia con filosofia."

### Paso 8: Sub-nodos del AI Agent

**Chat Model:**
1. Click **+ Chat Model** → **OpenRouter Chat Model**
2. Elegir credencial y modelo: `openai/gpt-4o-mini`

**Memory:**
1. Click **+ Memory** → **Window Buffer Memory**
2. Configurar:

| Setting | Value |
|---------|-------|
| Session ID Type | `Custom Key` |
| Session Key (Expression) | `{{ $json.sessionId }}` |
| Context Window Length | `10` |

> "La memoria permite conversaciones de varios turnos. El usuario puede preguntar '¿Cual es la politica de reembolso?' y luego '¿Y para equipos?' sin repetir contexto."

**Vector Store (como Tool):**
1. Click **+ Tool** → **In-Memory Vector Store** → renombrar a `Vector Store — Search FAQ`
2. Configurar:

| Setting | Value |
|---------|-------|
| Mode | `Retrieve Documents (as Tool for AI Agent)` |
| Memory Key | `faq_store` |
| Tool Description | `FAQ knowledge base about DataLearn company policies, pricing, support, and features. Use this to answer any customer question.` |

> "IMPORTANTE: el Mode debe ser 'as Tool for AI Agent'. Esto convierte el vector store en una herramienta que el agent decide cuando usar. El Memory Key DEBE ser el mismo que usamos en el insert: `faq_store`. Si no coincide, el agent busca en un store vacio."

> "El Tool Description le dice al agent CUANDO usar esta herramienta. Debe ser descriptivo: 'FAQ about policies, pricing, support...' Si pones algo vago como 'buscar cosas', el agent no sabra cuando usarlo."

3. Dentro del Vector Store — Search FAQ, click en el conector **Embedding** → **Embeddings Google Gemini**
4. Misma credencial y modelo: `text-embedding-004`

> "MUY IMPORTANTE: el modelo de embeddings debe ser EXACTAMENTE el mismo en ambos lados — insert y search. Si usas `text-embedding-004` para insertar y un modelo diferente para buscar, los vectores no coinciden y no encuentra nada. Es como buscar con un mapa de Madrid en Barcelona."

### Paso 9: Output

1. Añadir **Edit Fields** → renombrar a `Output — Chat Response`
2. Un campo:

| Name | Value (Expression) |
|------|---------------------|
| `output` | `{{ $json.output }}` |

> "El campo DEBE llamarse `output`. Si lo llamas `answer` o `response`, el chat mostrara JSON crudo en vez del texto bonito."

### Paso 10: Conectar la parte de chat

```
When chat message received → AI Agent — FAQ Assistant → Output — Chat Response
```

---

## Demo: Probarlo todo

> "Ahora vamos a probarlo. Primero cargamos los datos, luego chateamos."

### Paso 1: Cargar el FAQ

1. Click en **Execute Workflow** (el boton de arriba)
2. Esto ejecuta la parte izquierda: Manual Trigger → FAQ Data → Vector Store Insert
3. Verificar que el Vector Store muestra los items insertados

> "Solo hay que hacer esto UNA VEZ (o cada vez que cambie el FAQ). Mientras n8n este corriendo, los datos estan en memoria."

### Paso 2: Abrir el chat

> "IMPORTANTE: NO click en Execute Workflow otra vez. Click en el boton de **Chat** abajo a la derecha."

1. Escribir:
```
What is the refund policy?
```

> "El agent deberia buscar en el FAQ y responder: 'Full refund within 30 days...' Si abris los Logs del AI Agent, vereis que primero llamo al Vector Store tool, recibio el trozo relevante del FAQ, y luego genero la respuesta."

### Como ver que paso por dentro

1. Despues de que responda, **doble click** en el nodo **AI Agent**
2. Click en la pestaña **Logs** (arriba a la derecha, al lado de Output)
3. Vereis la secuencia:
   - **Tool call**: `Vector Store — Search FAQ` con la query del usuario
   - **Tool response**: el trozo del FAQ relevante
   - **LLM response**: la respuesta final basada en ese trozo

> "Esto es clave para debugging. Si el bot da una respuesta incorrecta, abrid los Logs y comprobad: ¿busco en el vector store? ¿Encontro el trozo correcto? ¿Lo interpreto bien?"

### Paso 3: Probar la guardrail

2. Escribir:
```
What is the meaning of life?
```

> "Esto NO esta en el FAQ. El bot deberia decir algo como 'I don't have that information in our FAQ. Please contact support@datalearn.com.' Si en vez de eso responde con filosofia, hay que reforzar el system message."

### Paso 4: Probar conversacion con memoria

3. Escribir:
```
Do you have student discounts?
```

4. Sin cerrar el chat, escribir:
```
And what about team plans?
```

> "No he dicho 'descuentos para equipos', solo 'team plans'. Pero gracias a la memoria, el agent entiende que seguimos hablando de precios y planes."

### Paso 5: Probar una pregunta sutil

5. Escribir:
```
Can I pay with Bitcoin?
```

> "El FAQ menciona Visa, Mastercard, PayPal, y SEPA — pero NO Bitcoin. El bot deberia decir que segun el FAQ, los metodos aceptados son esos, y que Bitcoin no esta incluido. Si inventa que 'si aceptamos Bitcoin', la guardrail no esta funcionando."

---

## Conceptos clave explicados

### Embeddings — Por que Gemini y gratis

> "Hay varios proveedores de embeddings: OpenAI, Google Gemini, Cohere, Ollama... Usamos Google Gemini `text-embedding-004` por dos razones: es gratis y tiene nodo nativo en n8n. OpenRouter, que usamos para el chat model, NO tiene nodo nativo de embeddings en n8n."

| Proveedor | Modelo | Coste | Nodo nativo en n8n |
|-----------|--------|-------|-------------------|
| Google Gemini | `text-embedding-004` | Gratis | Si |
| OpenAI | `text-embedding-3-small` | ~$0.02/1M tokens | Si |
| Ollama | Varios | Gratis (local) | Si |

### Vector Store — In-Memory vs Produccion

> "Usamos In-Memory Vector Store porque no necesita configuracion. Pero tiene un problema: los datos se PIERDEN cuando n8n se reinicia. Para produccion, usariais Supabase, Pinecone, o Qdrant — mismo workflow, solo cambias el nodo de vector store."

| Vector Store | Persistencia | Setup |
|-------------|-------------|-------|
| **In-Memory** | Se pierde al reiniciar | Ninguno |
| Supabase | Persistente | Free tier |
| Pinecone | Persistente | Free tier |
| Qdrant | Persistente | Self-hosted |

### Retrieve as Tool — Por que asi

> "Hay dos formas de conectar un vector store al agent: como 'retriever' (siempre busca) o como 'tool' (el agent decide cuando buscar). Usamos Tool porque es mas flexible — el agent puede decidir que NO necesita buscar si ya tiene la respuesta de una busqueda anterior."

---

## Resumen final

> "Recapitulemos lo que habeis construido:"

| Parte | Que hicimos |
|-------|------------|
| **A — Indexing** | Cargamos el FAQ → lo cortamos en chunks → lo convertimos en vectores → lo guardamos en el vector store |
| **B — Chat** | El usuario pregunta → el agent busca en el vector store → responde SOLO con lo que encuentra |

**Cinco conceptos clave:**
1. **Embeddings** convierten texto en vectores que representan significado
2. **Chunking** corta documentos en trozos buscables (400 chars, overlap 100)
3. **Memory Key** conecta el insert con la busqueda — DEBE ser identico en ambos lados
4. **Retrieve as Tool** deja que el agent DECIDA cuando buscar
5. **System message** con guardrails impide que el LLM invente respuestas

---

## Errores comunes

| Error | Solucion |
|-------|----------|
| El bot inventa respuestas | Reforzar system message: "ONLY based on the FAQ" |
| El bot no encuentra nada | Comprobar que el Memory Key es el mismo en Insert y Search |
| Error de embeddings | Comprobar que el modelo es el mismo en ambos lados (`text-embedding-004`) |
| Chat muestra JSON crudo | El ultimo nodo debe tener campo `output`, no `answer` |
| "No data found" al chatear | Ejecutar primero el workflow (Execute Workflow) para cargar el FAQ |
| Datos desaparecen | In-Memory se pierde al reiniciar n8n — ejecutar el indexing otra vez |
| Agent no busca en el vector store | Comprobar Tool Description — debe describir bien que contiene |
