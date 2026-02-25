# Build from Scratch: RAG Document Chat

## Objetivo del video

> "En este video vamos a construir un chatbot que responde preguntas usando SOLO un documento que tu le des — no inventa nada. Esto es RAG: Retrieval-Augmented Generation. En vez de que el LLM responda de memoria, primero BUSCA en tu documento y responde con lo que encuentra. Lo hacemos con un Form para subir PDFs, asi que podeis usar CUALQUIER documento."

**Que vamos a construir:** un bot que acepta un PDF mediante un formulario web, lo indexa, y luego permite chatear con su contenido. Si la respuesta no esta en el documento, dice que no lo sabe.

Un workflow con dos partes:

| Parte | Que construimos | Que concepto nuevo |
|-------|-----------------|---------------------|
| **A** | Indexing: Form Trigger (upload PDF) → Vector Store (Insert) | Form Trigger, binary data, embeddings, chunking |
| **B** | Chat: Chat Trigger → AI Agent + Vector Store (as Tool) → Output | RAG como tool del agent, guardrails |

**Credenciales necesarias:**
- **OpenRouter API key** (para el chat model)
- **Google Gemini API key** (para embeddings) — gratis desde [ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key)

**PDF de ejemplo:** DataLearn Employee Handbook (5 paginas). Descargarlo antes de empezar:
```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/data/datalearn_employee_handbook.pdf
```

---

## Concepto clave: RAG en 30 segundos

> "Imaginad que teneis un empleado nuevo. Sabe muchas cosas generales, pero NO conoce las politicas de vuestra empresa. Que haceis? Le dais el manual de empleados. RAG hace exactamente eso: le da al LLM un documento que puede consultar antes de responder."

```
SIN RAG                                CON RAG
──────                                 ───────

User: "Cuantos dias de                 User: "Cuantos dias de
       vacaciones tengo?"                      vacaciones tengo?"
         │                                        │
         ▼                                        ▼
    ┌─────────┐                           ┌─────────────────┐
    │   LLM   │                           │ Buscar en el    │
    └─────────┘                           │ handbook...     │
         │                                │ → "25 dias      │
         ▼                                │   laborables"   │
  "No tengo acceso a                      └─────────────────┘
   vuestras politicas."                           │
                                                  ▼
                                          ┌─────────────────┐
                                          │ LLM + contexto  │
                                          └─────────────────┘
                                                  │
                                                  ▼
                                          "Tienes 25 dias
                                           laborables al ano."
```

> "Hay tres pasos para que RAG funcione: primero INDEXAR el documento (cortarlo en trozos y convertirlos en vectores), luego cuando el usuario pregunta, BUSCAR los trozos mas relevantes, y finalmente enviarlos al LLM para que responda."

---

## Parte A: Indexing — Subir un PDF al Vector Store

> "Primero vamos a crear un formulario web donde el usuario sube un PDF. El workflow lee el PDF, lo corta en trozos, y lo guarda en un almacen inteligente que entiende significados."

### Paso 1: Crear workflow

1. **Workflows** → **Add Workflow**
2. Renombrar a "RAG Document Chat"

### Paso 2: Form Trigger (upload de archivo)

1. Añadir **Form Trigger** → renombrar a `Upload Document (Form)`
2. Configurar:

| Setting | Value |
|---------|-------|
| Form Title | `Upload Document` |
| Form Description | `Upload a PDF or text file to create a searchable knowledge base.` |

3. Añadir un campo de formulario:

| Field Label | Field Type | Accept File Types | Required |
|-------------|-----------|-------------------|----------|
| `Document` | `File` | `.pdf,.txt,.md` | Si |

4. En **Options**:
   - Respond With: `Text`
   - Form Submitted Text: `Document uploaded and indexed successfully! You can now open the Chat in n8n to ask questions.`

> "El Form Trigger crea una pagina web con un formulario. Cuando alguien sube un archivo y pulsa enviar, el workflow se ejecuta con ese archivo como input. El archivo llega como datos BINARIOS — no como texto en un campo."

> "Es diferente al Manual Trigger que hemos usado antes. Con Manual Trigger, tu defines los datos a mano dentro del workflow. Con Form Trigger, los datos los proporciona el usuario desde fuera."

### Paso 3: Vector Store (Insert)

1. Añadir **In-Memory Vector Store** → renombrar a `Vector Store — Insert`
2. Configurar:

| Setting | Value |
|---------|-------|
| Mode | `Insert Documents` |
| Memory Key | `doc_store` |
| Clear Store | Activado |

> "El Memory Key es como el nombre de la estanteria. Luego cuando el agent busque, usara este mismo nombre para saber DONDE buscar. Clear Store borra todo antes de insertar — asi cada vez que subas un PDF nuevo, reemplaza al anterior."

### Paso 4: Añadir sub-nodos al Vector Store

> "Fijate en los conectores de puntos debajo del Vector Store. Para insertar documentos necesitamos tres cosas: un modelo de embeddings, un loader que lea los datos binarios del PDF, y un splitter que los corte en trozos."

**Embeddings Google Gemini:**
1. Click en el conector **Embedding** del Vector Store
2. Seleccionar **Embeddings Google Gemini**
3. Configurar credencial de Google Gemini (gratis en [ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key))
4. Modelo: `text-embedding-004`

> "Los embeddings convierten texto en numeros — vectores — que representan el SIGNIFICADO. 'Vacaciones' y 'dias libres' tienen vectores similares aunque sean palabras diferentes. Usamos Gemini porque es gratis."

**Default Data Loader (modo Binary):**
1. Click en el conector **Document** del Vector Store
2. Seleccionar **Default Data Loader**
3. **IMPORTANTE:** Cambiar **Type of Data** a `Binary`

> "Aqui esta la clave: el Form Trigger envia el PDF como datos binarios, no como texto. El Data Loader en modo Binary sabe leer PDFs automaticamente — extrae el texto del PDF y lo pasa al siguiente paso. Si dejais el modo en JSON (el defecto), no encontrara el archivo."

**Recursive Character Text Splitter:**
1. Dentro del Default Data Loader, click en el conector **Text Splitter**
2. Seleccionar **Recursive Character Text Splitter**
3. Configurar:

| Setting | Value |
|---------|-------|
| Chunk Size | `400` |
| Chunk Overlap | `100` |

> "Esto es el chunking — cortar el texto en trozos manejables. Chunk Size 400 significa trozos de ~400 caracteres. Overlap 100 significa que cada trozo repite 100 caracteres del anterior. El overlap es importante: sin el, podrias cortar una frase por la mitad y perder contexto."

> "¿Por que 400 y no 1000? El handbook tiene secciones con respuestas concretas. Chunks mas pequenos = busqueda mas precisa. Si tuvierais documentos largos con parrafos densos, usariais chunks mas grandes (500-1000)."

### Paso 5: Conectar la parte de indexing

```
Upload Document (Form) → Vector Store — Insert
```

> "Solo dos nodos en la linea principal. Toda la magia esta en los sub-nodos de debajo."

---

## Parte B: Chat — AI Agent con Vector Store como Tool

> "Ahora la parte interesante: un AI Agent que BUSCA en el documento antes de responder. El Vector Store se convierte en una herramienta — como la Calculator o SerpAPI, pero para buscar en documentos."

### Paso 6: Chat Trigger

1. Añadir **Chat Trigger** (buscar "When chat message received")
2. Ir a **Options** → Response Mode: `When Last Node Finishes`

> "El Chat Trigger crea la ventanita de chat. Response Mode 'When Last Node Finishes' significa que el chat espera a que el ultimo nodo termine antes de mostrar la respuesta."

### Paso 7: AI Agent

1. Añadir **AI Agent** → renombrar a `AI Agent — Document Assistant`
2. Configurar:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.chatInput }}`
3. Ir a **Options** → activar **System Message**:

```
You are a helpful document assistant.

Rules:
- ALWAYS search the document knowledge base before answering.
- Answer ONLY based on the information found in the uploaded document.
- If the document does not contain the answer, say: "I don't have that information in the uploaded document."
- Keep answers concise and friendly.
- Do not make up information.
```

> "El system message es CRITICO para RAG. Fijate en las reglas: 'ALWAYS search' obliga al agent a consultar el vector store antes de responder. 'Answer ONLY based on the uploaded document' le prohibe inventarse cosas. Sin estas reglas, el LLM puede ignorar el documento y responder con su conocimiento general."

> "La regla de 'I don't have that information' es el guardrail principal. Si alguien pregunta '¿Cual es la mejor pizza de Madrid?' — eso NO esta en el handbook, asi que debe decir que no lo sabe."

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

> "La memoria permite conversaciones de varios turnos. El usuario puede preguntar '¿Cual es la politica de trabajo remoto?' y luego '¿Y cuantos dias?' sin repetir contexto."

**Vector Store (como Tool):**
1. Click **+ Tool** → **In-Memory Vector Store** → renombrar a `Vector Store — Search`
2. Configurar:

| Setting | Value |
|---------|-------|
| Mode | `Retrieve Documents (as Tool for AI Agent)` |
| Memory Key | `doc_store` |
| Tool Description | `Knowledge base containing the uploaded document. Use this to answer any question about the document content.` |

> "IMPORTANTE: el Mode debe ser 'as Tool for AI Agent'. Esto convierte el vector store en una herramienta que el agent decide cuando usar. El Memory Key DEBE ser el mismo que usamos en el insert: `doc_store`. Si no coincide, el agent busca en un store vacio."

> "El Tool Description le dice al agent CUANDO usar esta herramienta. Debe ser descriptivo. Si pones algo vago como 'buscar cosas', el agent no sabra cuando usarlo."

3. Dentro del Vector Store — Search, click en el conector **Embedding** → **Embeddings Google Gemini**
4. Misma credencial y modelo: `text-embedding-004`

> "MUY IMPORTANTE: el modelo de embeddings debe ser EXACTAMENTE el mismo en ambos lados — insert y search. Si usas `text-embedding-004` para insertar y un modelo diferente para buscar, los vectores no coinciden y no encuentra nada."

### Paso 9: Output

1. Añadir **Edit Fields** → renombrar a `Output — Chat Response`
2. Un campo:

| Name | Value (Expression) |
|------|---------------------|
| `output` | `{{ $json.output }}` |

> "El campo DEBE llamarse `output`. Si lo llamas `answer` o `response`, el chat mostrara JSON crudo en vez del texto bonito."

### Paso 10: Conectar la parte de chat

```
When chat message received → AI Agent — Document Assistant → Output — Chat Response
```

---

## Demo: Probarlo todo

> "Ahora vamos a probarlo. Primero subimos el PDF, luego chateamos."

### Paso 1: Subir el PDF

1. Click en el nodo **Upload Document (Form)** para ver la **Test URL**
2. Abrir esa URL en el navegador — aparece un formulario web
3. Subir el PDF del Employee Handbook
4. Click en **Submit** — deberia aparecer el mensaje de confirmacion

> "Fijate: no hemos hecho click en Execute Workflow. El Form Trigger se ejecuta automaticamente cuando alguien envia el formulario. El PDF se ha cortado en trozos, convertido en vectores, y guardado en el vector store."

### Paso 2: Abrir el chat

> "IMPORTANTE: ahora click en el boton de **Chat** abajo a la derecha."

1. Escribir:
```
What is the remote work policy?
```

> "El agent deberia buscar en el documento y responder: 'Up to 3 days per week, Tuesdays and Thursdays mandatory office days...' Si abris los Logs del AI Agent, vereis que primero llamo al Vector Store tool, recibio el trozo relevante, y luego genero la respuesta."

### Como ver que paso por dentro

1. Despues de que responda, **doble click** en el nodo **AI Agent**
2. Click en la pestaña **Logs** (arriba a la derecha, al lado de Output)
3. Vereis la secuencia:
   - **Tool call**: `Vector Store — Search` con la query del usuario
   - **Tool response**: el trozo del documento relevante
   - **LLM response**: la respuesta final basada en ese trozo

> "Esto es clave para debugging. Si el bot da una respuesta incorrecta, abrid los Logs y comprobad: ¿busco en el vector store? ¿Encontro el trozo correcto? ¿Lo interpreto bien?"

### Paso 3: Probar la guardrail

2. Escribir:
```
What is the best pizza in Madrid?
```

> "Esto NO esta en el handbook. El bot deberia decir algo como 'I don't have that information in the uploaded document.' Si en vez de eso responde con recomendaciones, hay que reforzar el system message."

### Paso 4: Probar conversacion con memoria

3. Escribir:
```
How many vacation days do I get?
```

4. Sin cerrar el chat, escribir:
```
And personal days?
```

> "No he dicho 'cuantos dias personales tengo segun el handbook', solo 'personal days'. Pero gracias a la memoria, el agent entiende que seguimos hablando de tiempo libre y busca en el documento."

### Paso 5: Probar una pregunta de calculo

5. Escribir:
```
What is the total meal allowance for a month with 22 office days?
```

> "El handbook dice 11 EUR por dia de oficina. El agent deberia buscar ese dato y calcular: 22 x 11 = 242 EUR. Si no lo calcula bien, no pasa nada — no tiene Calculator. Pero deberia al menos dar el dato de 11 EUR/dia."

---

## Conceptos clave explicados

### Form Trigger vs Manual Trigger

> "Hasta ahora usabamos Manual Trigger, donde los datos estan escritos dentro del workflow. Con Form Trigger, los datos los proporciona el usuario desde FUERA — sube un archivo, rellena un formulario. Es mucho mas realista."

| | Manual Trigger | Form Trigger |
|--|---------------|-------------|
| Datos | Hardcodeados en el workflow | El usuario los proporciona |
| Ejecucion | Boton Execute Workflow | El usuario envia el formulario |
| Tipo de datos | JSON (texto en campos) | Binary (archivos) + JSON |
| Uso | Testing, desarrollo | Produccion, interfaces reales |

### Binary vs JSON en el Data Loader

> "El Data Loader tiene dos modos: JSON lee un campo de texto del nodo anterior, Binary lee un archivo (PDF, TXT, etc.). Como el Form Trigger envia archivos como datos binarios, DEBEMOS usar el modo Binary."

### Embeddings — Por que Gemini y gratis

> "Hay varios proveedores de embeddings: OpenAI, Google Gemini, Cohere, Ollama... Usamos Google Gemini `text-embedding-004` por dos razones: es gratis y tiene nodo nativo en n8n."

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
| **A — Indexing** | El usuario sube un PDF via formulario → se corta en chunks → se convierte en vectores → se guarda en el vector store |
| **B — Chat** | El usuario pregunta → el agent busca en el vector store → responde SOLO con lo que encuentra |

**Seis conceptos clave:**
1. **Form Trigger** permite que el usuario suba archivos desde fuera del workflow
2. **Data Loader en modo Binary** lee PDFs y otros archivos automaticamente
3. **Embeddings** convierten texto en vectores que representan significado
4. **Chunking** corta documentos en trozos buscables (400 chars, overlap 100)
5. **Memory Key** conecta el insert con la busqueda — DEBE ser identico en ambos lados
6. **System message** con guardrails impide que el LLM invente respuestas

---

## Errores comunes

| Error | Solucion |
|-------|----------|
| El bot inventa respuestas | Reforzar system message: "ONLY based on the uploaded document" |
| El bot no encuentra nada | Comprobar que el Memory Key es el mismo en Insert y Search |
| Error de embeddings | Comprobar que el modelo es el mismo en ambos lados (`text-embedding-004`) |
| Chat muestra JSON crudo | El ultimo nodo debe tener campo `output`, no `answer` |
| "No data found" al chatear | Subir primero un PDF via el formulario |
| Datos desaparecen | In-Memory se pierde al reiniciar n8n — subir el PDF otra vez |
| Agent no busca en el vector store | Comprobar Tool Description — debe describir bien que contiene |
| El Data Loader no lee el PDF | Comprobar que Type of Data esta en `Binary`, no `JSON` |
| El formulario no aparece | Hay que activar el workflow (toggle ON) o usar la Test URL |
