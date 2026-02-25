# Analisis y Variaciones: RAG Document Chat

## Objetivo del video

> "En este video vamos a coger un RAG Document Chat completo — uno que acepta PDFs, los indexa, busca por significado, y responde solo con lo que encuentra — y lo vamos a abrir pieza a pieza. Despues vamos a hacer variaciones: cambiar el documento, debilitar las guardrails para ver que pasa, y añadir herramientas extra. La idea es que entendais que RAG es un PATRON reutilizable: cambia los datos y tienes otro bot."

**Que vamos a hacer:**

| Parte | Contenido |
|-------|-----------|
| **1** | Importar el workflow RAG Document Chat y analizar nodo a nodo |
| **2** | Variacion A: Subir otro PDF (otro tema, mismo pipeline) |
| **3** | Variacion B: Debilitar las guardrails — ver que pasa |
| **4** | Variacion C: Añadir Calculator y Think — RAG + herramientas |

**Credenciales necesarias:**
- **OpenRouter API key** (para el chat model)
- **Google Gemini API key** (para embeddings) — gratis desde [ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key)

**PDF de ejemplo:** DataLearn Employee Handbook (5 paginas):
```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/data/datalearn_employee_handbook.pdf
```

---

## Parte 1: Analisis nodo a nodo

> "Vamos a importar un workflow de RAG que tiene dos partes: una para subir documentos y otra para chatear. Lo analizamos nodo a nodo."

### Importar el workflow

1. **Workflows** → **Import from URL**
2. Pegar:
```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/14_rag_faq_bot.json
```
3. Configurar credenciales: OpenRouter y Google Gemini

### Vista general

> "Este workflow tiene DOS partes que comparten el mismo canvas. La de la izquierda indexa los datos. La de la derecha responde preguntas."

```
PARTE A — INDEXING                              PARTE B — CHAT
(Form Trigger — el usuario sube un PDF)         (Boton de Chat para ejecutar)

┌──────────────┐  ┌────────────┐                ┌──────────────┐  ┌────────────┐  ┌────────┐
│ Upload       │─▶│ Vector     │                │ Chat Trigger │─▶│ AI Agent   │─▶│ Output │
│ Document     │  │ Store —    │                │              │  │ — Document │  │        │
│ (Form)       │  │ Insert     │                │              │  │ Assistant  │  │        │
└──────────────┘  └────────────┘                └──────────────┘  └────────────┘  └────────┘
                       ┊                                               ┊
                 ┌─────┼─────┐                           ┌─────────────┼─────────┐
                 ┊     ┊     ┊                           ┊             ┊         ┊
            ┌────────┐ ┌──────┐                    ┌────────┐    ┌────────┐ ┌────────────┐
            │Gemini  │ │Data  │                    │Chat   │    │Memory │ │Vector Store│
            │Embed.  │ │Loader│                    │Model  │    │       │ │— Search    │
            └────────┘ │Binary│                    └────────┘    └────────┘ └────────────┘
                       └──────┘                                                 ┊
                          ┊                                                ┌────────┐
                     ┌─────────┐                                           │Gemini  │
                     │Text     │                                           │Embed.  │
                     │Splitter │                                           └────────┘
                     └─────────┘
```

> "Son dos pipelines independientes. La izquierda se ejecuta cuando alguien envia el formulario. La derecha se ejecuta con el boton de Chat."

---

### Pipeline de Indexing (izquierda)

#### Nodo 1: Form Trigger (`Upload Document (Form)`)

> "Este nodo crea una pagina web con un formulario para subir archivos. Cuando el usuario sube un PDF y pulsa enviar, el workflow se ejecuta automaticamente."

| Setting | Valor | Por que |
|---------|-------|---------|
| **Form Title** | `Upload Document` | Titulo que ve el usuario |
| **Field Type** | `File` | Acepta archivos binarios (PDF, TXT, etc.) |
| **Accept File Types** | `.pdf,.txt,.md` | Limita los tipos de archivo aceptados |
| **Respond With** | `Text` | Muestra un mensaje de confirmacion |

> "A diferencia del Manual Trigger, donde los datos estan hardcodeados dentro del workflow, aqui el usuario proporciona el documento desde fuera. El archivo llega como datos BINARIOS — no como texto en un campo JSON."

**Form Trigger vs Manual Trigger:**

| | Manual Trigger | Form Trigger |
|--|---------------|-------------|
| Datos | Hardcodeados en el workflow | El usuario los proporciona |
| Ejecucion | Boton Execute Workflow | El usuario envia el formulario |
| Tipo de datos | JSON (texto en campos) | Binary (archivos) + JSON |
| Uso | Testing, desarrollo | Produccion, interfaces reales |

#### Nodo 2: Vector Store — Insert (`In-Memory Vector Store`)

> "Aqui es donde se guarda todo. El vector store recibe el PDF, lo corta en trozos, convierte cada trozo en un vector, y lo almacena para busquedas posteriores."

| Setting | Valor | Por que |
|---------|-------|---------|
| **Mode** | `Insert Documents` | Estamos INSERTANDO datos, no buscando |
| **Memory Key** | `doc_store` | Nombre del almacen — debe coincidir con el de busqueda |
| **Clear Store** | Activado | Borra todo antes de insertar — cada PDF nuevo reemplaza al anterior |

> "El Memory Key es la pieza que CONECTA la parte de indexing con la de chat. Si escribis `doc_store` en el insert pero otro nombre en la busqueda, el agent busca en un almacen vacio."

#### Sub-nodos del Vector Store (Insert)

**Embeddings Google Gemini:**

| Setting | Valor |
|---------|-------|
| Modelo | `text-embedding-004` |
| Credencial | Google Gemini API key (gratis) |

> "Los embeddings convierten texto en vectores — numeros que representan el SIGNIFICADO. 'Vacaciones' y 'dias libres' tienen vectores similares aunque sean palabras diferentes."

**Default Data Loader (modo Binary):**

> "IMPORTANTE: el Data Loader debe estar en modo **Binary**, no JSON. El Form Trigger envia el PDF como datos binarios. En modo Binary, el Data Loader sabe leer PDFs automaticamente — extrae el texto y lo pasa al splitter."

**Recursive Character Text Splitter:**

| Setting | Valor | Por que |
|---------|-------|---------|
| **Chunk Size** | `400` | Trozos de ~400 caracteres — adecuado para secciones del handbook |
| **Chunk Overlap** | `100` | Cada trozo repite 100 chars del anterior — no perder contexto entre trozos |

> "El chunking es CRITICO. Si los trozos son demasiado grandes, la busqueda devuelve texto irrelevante. Si son demasiado pequeños, puede cortar una respuesta por la mitad."

---

### Pipeline de Chat (derecha)

#### Nodo 3: Chat Trigger (`When chat message received`)

> "Abre la ventanita de chat. El usuario escribe una pregunta y el workflow la procesa."

| Setting | Valor |
|---------|-------|
| Response Mode | `When Last Node Finishes` |

#### Nodo 4: AI Agent (`AI Agent — Document Assistant`)

> "El cerebro del bot. Recibe la pregunta, decide si buscar en el documento, y genera la respuesta."

| Setting | Valor |
|---------|-------|
| Source for Prompt | `Define below` |
| Prompt (Expression) | `{{ $json.chatInput }}` |
| System Message | (ver abajo) |

#### System Message — analisis linea a linea

```
You are a helpful document assistant.

Rules:
- ALWAYS search the document knowledge base before answering.
- Answer ONLY based on the information found in the uploaded document.
- If the document does not contain the answer, say: "I don't have that information in the uploaded document."
- Keep answers concise and friendly.
- Do not make up information.
```

| Regla | Que controla | Sin ella... |
|-------|-------------|-------------|
| `ALWAYS search the document` | Obliga a consultar el vector store | El LLM responde de memoria sin buscar |
| `Answer ONLY based on the uploaded document` | Prohibe inventar informacion | Mezcla datos del documento con conocimiento general |
| `"I don't have that information..."` | Respuesta por defecto si no encuentra | Inventa una respuesta plausible pero falsa |
| `Keep answers concise` | Respuestas cortas | Parrafos innecesarios |
| `Do not make up information` | Guardrail redundante contra alucinaciones | Refuerzo extra, por si acaso |

> "Hay REDUNDANCIA a proposito: 'ONLY based on the document' y 'Do not make up information' dicen casi lo mismo. En guardrails de produccion, la redundancia es buena."

#### Sub-nodos del Agent

**Vector Store — Search (`In-Memory Vector Store`):**

| Setting | Valor | Por que |
|---------|-------|---------|
| **Mode** | `Retrieve Documents (as Tool for AI Agent)` | El agent DECIDE cuando buscar |
| **Memory Key** | `doc_store` | DEBE ser identico al del insert |
| **Tool Description** | `Knowledge base containing the uploaded document...` | Le dice al agent CUANDO usar esta herramienta |

> "El modelo de embeddings debe ser EXACTAMENTE el mismo en ambos lados — insert y search. Si usas uno diferente para buscar, los vectores no coinciden y no encuentra nada."

#### Nodo 5: Output (`Output — Chat Response`)

| Setting | Valor |
|---------|-------|
| Campo | `output` |
| Expresion | `{{ $json.output }}` |

> "El ultimo nodo DEBE tener un campo `output`. Si lo llamas de otra forma, el chat muestra JSON crudo."

---

### Demo rapida

1. Abrir la **Test URL** del Form Trigger y subir el Employee Handbook PDF
2. Abrir el **Chat** (boton abajo a la derecha)
3. Escribir: `What is the remote work policy?`
   - En los **Logs**: el agent llama al Vector Store, recibe el trozo relevante, genera la respuesta
4. Escribir: `What is the best pizza in Madrid?`
   - El agent busca, no encuentra nada relevante, y dice que no tiene esa informacion
5. Escribir: `How many vacation days do I get?` → luego `And personal days?`
   - La memoria mantiene el contexto entre turnos

> "Siempre abrid los Logs del AI Agent despues de cada respuesta. Ahi veis si busco en el vector store, que trozo encontro, y como lo uso."

---

## Parte 2: Variaciones

> "Ahora vamos a modificar el workflow para ver lo flexible que es RAG. Cada variacion toca UNA cosa."

---

### Variacion A: Subir otro PDF (otro tema)

> "RAG es agnostico al contenido. El pipeline es siempre el mismo — solo cambian los datos. Vamos a subir un documento completamente diferente."

**Pasos:**
1. Buscar cualquier PDF que tengais a mano — un apunte de clase, un manual de instrucciones, la politica de privacidad de alguna web, un CV
2. Abrir la URL del Form Trigger y subir ese PDF
3. Actualizar el **System Message** del AI Agent para que tenga sentido con el nuevo documento

**Ejemplo con un CV:**

System message:
```
You are a helpful assistant that answers questions about a candidate's CV.

Rules:
- ALWAYS search the document knowledge base before answering.
- Answer ONLY based on the information found in the CV.
- If the CV does not contain the answer, say: "That information is not in the CV."
- Keep answers concise.
- Do not make up information.
```

Probar:
```
What programming languages does this person know?
```
```
How many years of experience do they have?
```

> "Mismo workflow, mismos nodos, misma estructura — pero ahora es un analizador de CVs. Lo UNICO que hemos cambiado es el PDF que subimos y el system message. El pipeline de RAG (chunking, embeddings, vector store, busqueda) es identico."

**Concepto:** RAG es un patron reutilizable. Cambia los datos y el system message, y tienes un bot completamente diferente.

---

### Variacion B: Debilitar las guardrails

> "El system message tiene reglas estrictas. ¿Que pasa si las quitamos? Vamos a verlo."

**Paso 1 — Quitar la regla principal:**

Reemplazar el system message por:

```
You are a helpful document assistant.
Search the document when needed.
Keep answers concise.
```

> "Hemos quitado 'ONLY based on the document', 'do not make up information', y la respuesta por defecto. Veamos que pasa."

**Probar (con el Employee Handbook cargado):**

```
What is the remote work policy?
```

> "Esta probablemente siga funcionando — la informacion esta en el documento."

```
What is the best pizza in Madrid?
```

> "AQUI esta la diferencia. Antes decia 'I don't have that information.' Ahora probablemente responde con recomendaciones — porque no tiene la regla que se lo prohibe."

```
What is the salary range for junior developers at DataLearn?
```

> "Esto es PELIGROSO. Puede inventarse una respuesta plausible: 'Junior developers at DataLearn earn between 28,000 and 35,000 EUR.' Suena real, pero NO esta en el handbook. El usuario se lo cree porque viene de un bot que consulta documentos internos."

**Volver al system message original:**

> "¿Veis la diferencia? Sin guardrails fuertes, un RAG bot se convierte en un LLM normal que a veces consulta los datos. Las guardrails son lo que hace que RAG sea FIABLE."

**Concepto:** Las guardrails del system message son tan importantes como el vector store. Sin ellas, RAG pierde su ventaja principal: responder SOLO con datos verificados.

---

### Variacion C: Añadir Calculator y Think

> "El RAG bot actual solo tiene una herramienta: el vector store. Pero un AI Agent puede tener VARIAS herramientas. Vamos a darle Calculator y Think para que pueda hacer calculos con los datos del documento."

**Pasos:**
1. Click en el AI Agent → **+ Tool** → **Calculator**
2. Click en el AI Agent → **+ Tool** → **Think**
3. Actualizar el system message:

```
You are a helpful document assistant.

Rules:
- ALWAYS search the document knowledge base before answering.
- Answer ONLY based on the information found in the uploaded document.
- If the document does not contain the answer, say: "I don't have that information in the uploaded document."
- For calculations (budgets, allowances, comparisons), use the Calculator tool.
- Use Think to plan multi-step questions before searching.
- Keep answers concise and friendly.
- Do not make up information.
```

**Probar:**

```
If I work 22 office days this month, what is my total meal allowance?
```

> "Ahora el agent busca en el documento (11 EUR por dia de oficina), y luego usa Calculator para hacer la cuenta: 22 x 11 = 242 EUR. Antes no podia calcular."

```
Compare the home office budget for the first year vs the second year.
```

> "Con Think, el agent primero planifica: 'Necesito buscar el one-time setup, el monthly allowance, calcular el total del primer ano y del segundo.' Sin Think, podria olvidarse de algun paso."

**Concepto:** RAG + herramientas = un agent que sabe cosas (vector store) Y puede hacer cosas (calculator, think). Las herramientas se combinan.

---

## Resumen

> "Recapitulemos:"

| Que hicimos | Que aprendimos |
|-------------|----------------|
| **Analisis nodo a nodo** | El Form Trigger permite subir PDFs. El Data Loader en modo Binary los lee. El indexing y el chat se conectan por el Memory Key. Los embeddings DEBEN ser iguales en ambos lados. |
| **Variacion A (Otro PDF)** | RAG es un patron reutilizable. Cambia el documento y el system message = otro bot. El pipeline no cambia. |
| **Variacion B (Sin guardrails)** | Sin reglas estrictas, el LLM inventa respuestas. Las guardrails son lo que hace RAG fiable. |
| **Variacion C (+ Calculator + Think)** | RAG + herramientas extra = un agent mas capaz. Puede buscar datos Y operar con ellos. |

**Tres ideas clave:**
1. **Memory Key** conecta insert y search — si no coinciden, el bot no encuentra nada
2. Las **guardrails del system message** son tan importantes como el vector store — sin ellas, RAG no es fiable
3. RAG es **modular**: cambia los datos, las reglas, o las herramientas sin tocar la estructura del pipeline
