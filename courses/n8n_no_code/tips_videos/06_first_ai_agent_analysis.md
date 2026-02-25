# Analisis y Variaciones: First AI Agent

## Objetivo del video

> "En este video vamos a coger un AI Agent completo — uno que tiene chat, busca en Google, hace calculos, y recuerda la conversacion — y lo vamos a abrir pieza a pieza para entender como funciona. Despues vamos a hacer variaciones: añadir herramientas nuevas, cambiar el system message para convertirlo en otro tipo de asistente, y quitar cosas para ver que pasa. La idea es que entendais que un AI Agent es modular: puedes cambiar las piezas sin romper nada."

**Que vamos a hacer:**

| Parte | Contenido |
|-------|-----------|
| **1** | Importar un workflow de AI Agent y analizar nodo a nodo |
| **2** | Variacion A: Añadir Wikipedia (tool gratis, sin credenciales) |
| **3** | Variacion B: Cambiar el system message (otro tema, otro comportamiento) |
| **4** | Variacion C: Quitar Think — ver la diferencia |

**Credenciales necesarias:** OpenRouter API key. SerpAPI key (gratis, [serpapi.com](https://serpapi.com)).

---

## Parte 1: Analisis nodo a nodo

> "Vamos a importar un workflow de AI Agent que tiene una interfaz de chat, tres herramientas (Google Search, Calculator, Think), y memoria. Lo analizamos nodo a nodo."

### Importar el workflow

1. **Workflows** → **Import from URL**
2. Pegar:
```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/07_ai_agent_chat_trigger_memory.json
```
3. Configurar credenciales: OpenRouter y SerpAPI

### Vista general

```
┌───────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  When chat message    │────▶│  AI Agent —            │────▶│  Output —              │
│  received             │     │  Salary Chat           │     │  Chat Response         │
└───────────────────────┘     └────────────────────────┘     └────────────────────────┘
                                          ┊ (sub-nodos)
                               ┌──────────┼──────────────────────────┐
                               ┊          ┊          ┊         ┊     ┊
                         ┌──────────┐ ┌────────┐ ┌──────┐ ┌───────┐ ┌───────┐
                         │Chat Model│ │ Memory │ │Calc. │ │SerpAPI│ │ Think │
                         └──────────┘ └────────┘ └──────┘ └───────┘ └───────┘
```

> "Son solo tres nodos en la linea principal. Toda la inteligencia esta en los sub-nodos de debajo."

---

### Nodo 1: Chat Trigger (`When chat message received`)

> "Este nodo es el punto de entrada. En vez de ejecutar con datos fijos, abre una ventana de chat — como ChatGPT — donde el usuario escribe en tiempo real."

#### Pestaña Parameters

| Setting | Valor | Que hace |
|---------|-------|----------|
| **Chat URL** | (auto-generada) | La URL donde se aloja el chat. n8n la crea automaticamente al activar el workflow. |
| **Make Chat Publicly Available** | `On` | Si esta ON, cualquiera con la URL puede chatear. Si esta OFF, solo funciona en testing. |
| **Mode** | `Webhook` | Como recibe los mensajes. `Webhook` = escucha peticiones HTTP. Tambien existe `Embedded Chat` para incrustar en una web. |
| **Authentication** | `None` | Sin autenticacion. En produccion puedes poner `Basic Auth` o `Header Auth` para proteger el acceso. |
| **Make Available in n8n Chat** | (toggle) | Si esta ON, el chat aparece en el panel de n8n para testing interno. |
| **Response Mode** (en Options) | `When Last Node Finishes` | El chat espera a que el ultimo nodo del workflow termine antes de responder. |

> "Los dos mas importantes para nosotros son **Mode** (dejamos Webhook) y **Response Mode** (dejamos When Last Node Finishes para que el agent tenga tiempo de pensar y responder). El resto son valores por defecto que no necesitamos tocar."

#### Pestaña Settings

| Setting | Valor | Que hace |
|---------|-------|----------|
| **Always Output Data** | `Off` | Si esta ON, el nodo genera datos aunque no reciba nada. Dejarlo OFF. |
| **Execute Once** | `Off` | Si esta ON, solo procesa el primer mensaje y para. Dejarlo OFF para un chat normal. |
| **Retry On Fail** | `Off` | Reintentar si falla. No suele hacer falta en un Chat Trigger. |
| **On Error** | `Stop Workflow` | Que hacer si hay error. `Stop Workflow` para el flujo — la opcion segura. |
| **Notes** | (vacio) | Notas personales para documentar el nodo. |

> "La pestaña Settings normalmente no la tocamos. Los valores por defecto estan bien. Lo unico que podria interesaros es `On Error` — si lo cambiaseis a `Continue`, el workflow seguiria aunque falle este nodo, pero eso casi nunca es lo que quereis."

---

**Que genera automaticamente:**

| Campo | Contenido |
|-------|-----------|
| `chatInput` | Lo que escribe el usuario |
| `sessionId` | ID unico por ventana de chat |

> "El Chat Trigger genera `chatInput` y `sessionId` automaticamente. No hace falta crear estos campos a mano — el nodo se encarga."

**Chat Trigger vs Manual Trigger:**

| | Manual Trigger | Chat Trigger |
|--|---------------|-------------|
| Se ejecuta con | Execute Workflow (boton de arriba) | Boton de Chat (abajo a la derecha) |
| Input | Datos fijos que tu escribes | Lo que el usuario escribe en tiempo real |
| `sessionId` | Tu lo defines | Se genera automaticamente |
| Uso | Testing, desarrollo | Interfaz de usuario final |

---

### Nodo 2: AI Agent (`AI Agent — Salary Chat`)

> "El cerebro del workflow. Recibe la pregunta, decide que herramientas usar, y genera la respuesta."

**Configuracion:**

| Setting | Valor |
|---------|-------|
| Source for Prompt | `Define below` |
| Prompt (Expression) | `{{ $json.chatInput }}` |
| System Message | (ver abajo) |

#### System Message — analisis linea a linea

```
You are a salary research assistant inside an n8n AI Agent workflow.
Be concise.
If the user asks about salaries, job markets, or company info, search Google first.
If the user asks for arithmetic, use the Calculator tool.
Use Think to plan multi-step research.
If the user asks you to remember something, store it in memory and confirm briefly.
If you don't know, say so.
```

> "Vamos a analizarlo linea a linea."

| Linea | Que hace | Sin ella... |
|-------|----------|-------------|
| `You are a salary research assistant` | Define el ROL — el agent sabe de que va | Responde de todo, sin foco |
| `Be concise` | Respuestas cortas | Parrafos largos que nadie lee |
| `search Google first` | Obliga a usar SerpAPI para datos reales | Inventa salarios de su training data |
| `use the Calculator tool` | Obliga a calcular con herramienta | Calcula de cabeza y se equivoca |
| `Use Think to plan` | Planifica antes de actuar | Salta directamente a buscar sin pensar |
| `store it in memory` | Responde a "recuerda X" | Ignora peticiones de memoria |
| `If you don't know, say so` | Guardrail contra alucinaciones | Inventa respuestas |

> "Cada linea del system message CONTROLA un comportamiento. Si quitais una linea, cambia lo que hace el agent. Luego lo vamos a demostrar."

#### Sub-nodos del Agent

**Chat Model — OpenRouter (`openai/gpt-4o-mini`):**

> "El modelo que razona. gpt-4o-mini es rapido y barato. Si quisierais mas calidad, podeis cambiar a `openai/gpt-4o` o `anthropic/claude-sonnet` desde el mismo dropdown — sin cambiar nada mas del workflow."

**Memory — Window Buffer Memory:**

| Setting | Valor | Significado |
|---------|-------|-------------|
| Session ID Type | `Custom Key` | Usa un ID que viene del input |
| Session Key | `{{ $json.sessionId }}` | El ID que genera el Chat Trigger |
| Context Window Length | `10` | Recuerda los ultimos 10 mensajes |

> "La memoria es POR SESION. Misma ventana de chat = mismo sessionId = misma memoria. Nueva ventana = nuevo sessionId = memoria vacia."

**Tools:**

| Tool | Que hace | Credenciales | Cuando lo usa el agent |
|------|----------|-------------|----------------------|
| **Calculator** | Operaciones matematicas | No | Calculos de impuestos, salarios netos |
| **SerpAPI** | Busca en Google | Si (gratis) | Datos de salarios, mercado laboral |
| **Think** | Bloc de notas interno | No | Planifica antes de usar otras tools |

> "Tres tools, cada una con su proposito. El agent ELIGE cual usar basandose en la pregunta y en las reglas del system message."

---

### Nodo 3: Output (`Output — Chat Response`)

| Setting | Valor |
|---------|-------|
| Campo | `output` |
| Expresion | `{{ $json.output }}` |

> "CRITICO: el campo se llama `output`. Si lo llamas `answer`, `response`, o cualquier otra cosa, el chat muestra JSON crudo en vez del texto."

| Campo en el ultimo nodo | El chat muestra |
|--------------------------|-----------------|
| `output: "Hello!"` | Hello! |
| `answer: "Hello!"` | `{"answer": "Hello!"}` |

> "Este es el error numero uno de los alumnos con Chat Trigger. Si vuestro chat muestra JSON, comprobad el nombre del campo."

---

### Demo rapida

1. Abrir el **Chat** (boton abajo a la derecha — NO Execute Workflow)
2. Escribir: `What is the average data analyst salary in Madrid?`
3. Abrir los **Logs** del AI Agent (doble click → pestaña Logs):
   - Think: "Voy a buscar el salario en Google..."
   - SerpAPI: busca y devuelve ~25.000-30.000 euros
   - Respuesta final con el dato

4. Escribir: `Calculate the monthly net after 20% tax`
   - El agent usa la memoria (sabe que hablamos de Madrid) + Calculator

> "Fijate que no le he dicho 'del salario de Madrid'. Sabe de que hablamos gracias a la memoria."

---

## Parte 2: Variaciones

> "Ahora viene lo divertido. Vamos a modificar el workflow para ver lo flexible que es un agent. Cada variacion toca UNA cosa para que veais el efecto."

---

### Variacion A: Añadir Wikipedia

> "Wikipedia es una herramienta gratis que no necesita credenciales. Perfecta para dar al agent conocimiento enciclopedico ademas de Google."

**Pasos:**
1. Click en el AI Agent → **+ Tool** → **Wikipedia**
2. No necesita configuracion

**Actualizar el system message** — añadir una linea:

```
You are a salary research assistant inside an n8n AI Agent workflow.
Be concise.
If the user asks about salaries, job markets, or company info, search Google first.
If the user asks for arithmetic, use the Calculator tool.
If the user asks about a company, industry, or concept, check Wikipedia for context.
Use Think to plan multi-step research.
If the user asks you to remember something, store it in memory and confirm briefly.
If you don't know, say so.
```

**Probar:**
```
What does Accenture do? And what's the average salary for a consultant there in Spain?
```

> "Ahora el agent puede hacer dos cosas: buscar en Wikipedia QUE es Accenture, y luego buscar en Google el salario. Antes solo podia buscar en Google, que a veces no explica bien que hace una empresa."

**Concepto:** cada tool que añades amplia las capacidades del agent. Pero siempre hay que decirle en el system message CUANDO usarla.

---

### Variacion B: Cambiar el tema (system message)

> "El system message ES la personalidad del agent. Cambiandolo, el MISMO workflow sirve para algo completamente diferente."

**Reemplazar todo el system message por:**

```
You are a travel planning assistant.
Be concise and friendly.
If the user asks about destinations, flights, or hotels, search Google first.
For budget calculations (currency conversions, daily costs, total trip cost), use Calculator.
Use Think to plan multi-step itineraries.
If you don't know, say so. Do not invent prices.
```

**Probar:**
```
I want to plan a 5-day trip to Lisbon from Madrid. What's a reasonable budget?
```

> "Mismo workflow, mismas herramientas, mismo modelo — pero ahora es un asistente de viajes. El agent busca precios en Google, calcula presupuestos con Calculator, y planifica con Think. Solo hemos cambiado el system message."

Luego probar volver al system message original:

> "¿Veis? El system message no es un detalle menor — es lo que DEFINE al agent. Las tools son las manos, el model es el cerebro, pero el system message es la mision."

---

### Variacion C: Quitar Think — ver la diferencia

> "Algunos pensareis: ¿para que sirve Think si no hace nada visible? Vamos a quitarlo y ver que pasa."

**Pasos:**
1. Seleccionar el nodo **Think** → borrar
2. Quitar la linea `Use Think to plan multi-step research.` del system message

**Probar con una tarea compleja:**
```
Compare the average data scientist salary in Spain vs Germany. Calculate the monthly net for each after 24% tax (Spain) and 35% tax (Germany). Which country pays more net?
```

> "Sin Think, el agent a veces se lanza directamente a buscar sin planificar. Puede buscar dos veces el mismo dato, o olvidarse de un paso. Con Think, primero escribe: 'Necesito buscar salario España, salario Alemania, calcular neto de ambos, y comparar.' Y luego ejecuta en orden."

**Volver a añadirlo:**
1. Click en el AI Agent → **+ Tool** → **Think**
2. Volver a poner la linea en el system message

**Probar la misma pregunta:**

> "Ahora en los Logs vereis que primero Think planifica los pasos, y luego ejecuta SerpAPI y Calculator en el orden correcto. La diferencia no siempre es dramatica en preguntas simples, pero en tareas de varios pasos es clara."

---

## Resumen

> "Recapitulemos:"

| Que hicimos | Que aprendimos |
|-------------|----------------|
| **Analisis nodo a nodo** | Chat Trigger genera `chatInput` y `sessionId`. El Agent tiene Prompt + System Message. El Output DEBE llamarse `output`. |
| **Variacion A (Wikipedia)** | Añadir una tool = ampliar capacidades. Siempre actualizar el system message. |
| **Variacion B (Tema nuevo)** | Cambiar el system message = cambiar la mision del agent. Mismas tools, diferente proposito. |
| **Variacion C (Sin Think)** | Think mejora la planificacion en tareas complejas. Sin el, el agent puede desordenarse. |

**Tres ideas clave:**
1. El **system message** es la pieza mas importante — define QUE hace el agent y CUANDO usa cada tool
2. Las **tools son modulares** — puedes añadir o quitar sin tocar el resto del workflow
3. Los **Logs** del AI Agent son tu herramienta de debugging — siempre miralos si algo falla

---

## Tools disponibles (sin credenciales)

> "Si quereis experimentar por vuestra cuenta, estas son tools que podeis añadir sin necesitar API keys:"

| Tool | Que hace | Idea de uso |
|------|----------|-------------|
| **Calculator** | Operaciones matematicas | Presupuestos, conversiones, impuestos |
| **Think** | Planificacion interna | Tareas de varios pasos |
| **Wikipedia** | Consulta enciclopedica | Informacion sobre empresas, paises, conceptos |
| **Code** | Ejecuta JavaScript | Formatear datos, logica personalizada |

> "SerpAPI necesita credencial pero es gratis (100 busquedas/mes). Wolfram Alpha tambien necesita credencial. El resto de tools de la lista son gratis y sin configuracion."
