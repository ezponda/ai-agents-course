# Clase: Configurar Credenciales (APIs)

**Pre-requisito:** n8n instalado y funcionando (ver vídeo de instalación)

Este es uno de los primeros vídeos del curso. Explica qué son las API keys, por qué las necesitamos, y cómo configurar las dos principales: OpenRouter (modelo de IA) y SerpAPI (búsqueda en Google).

---

## Paso 0: ¿Qué es una API key?

**Qué decir:**

> "Una API key es como una contraseña que identifica tu cuenta cuando un programa se conecta a un servicio externo. n8n necesita estas keys para hablar con los modelos de IA y con servicios como Google Search."
>
> "Vamos a configurar dos: OpenRouter para los modelos de IA, y SerpAPI para búsquedas en Google. Son las que usaremos en todo el curso."

---

## Paso 1: OpenRouter (modelos de IA)

### Crear cuenta y obtener API key

1. Ir a [openrouter.ai](https://openrouter.ai/)
2. Click en **Sign Up** (se puede usar cuenta de Google)
3. Ir a **Keys** (menú lateral) → **Create Key**
4. Nombre: `n8n-course` (o lo que quieras)
5. Click **Create** → **copiar la key**

**Qué decir:**

> "OpenRouter es un servicio que te da acceso a cientos de modelos de IA con una sola API key. Hay modelos gratuitos como DeepSeek V3, y modelos de pago como GPT-4o o Claude. Para este curso, los modelos gratuitos funcionan perfectamente."

### Configurar en n8n

1. Abrir n8n → cualquier workflow
2. Añadir un nodo **OpenRouter Chat Model** (o abrir uno existente)
3. En **Credential** → **Create New Credential**
4. Pegar la API key → **Save**
5. En **Model**, escribir: `deepseek/deepseek-chat-v3-0324:free`
6. Probar: conectar a un Basic LLM Chain → ejecutar

**Qué decir:**

> "Una vez guardada la credencial, n8n la recuerda para todos los workflows. No hace falta repetir este paso."
>
> "Estamos usando DeepSeek V3 free. Es gratuito, no necesita tarjeta de crédito, y funciona muy bien para aprender."

---

## Paso 2: SerpAPI (búsqueda en Google)

### Crear cuenta y obtener API key

1. Ir a [serpapi.com](https://serpapi.com/)
2. Click en **Register** → crear cuenta
3. Ir a **Dashboard** → copiar la **API Key** (aparece directamente)

**Qué decir:**

> "SerpAPI permite que nuestros workflows busquen en Google. La cuenta gratuita da 100 búsquedas al mes, más que suficiente para el curso."
>
> "No todos los workflows necesitan SerpAPI — solo los que buscan información en internet. Si un workflow no la usa, no hace falta tenerla."

### Configurar en n8n

1. Abrir n8n → cualquier workflow
2. Añadir un nodo **SerpAPI** (buscar "SerpAPI")
3. En **Credential** → **Create New Credential**
4. Pegar la API key → **Save**

**Qué decir:**

> "Igual que con OpenRouter: una vez guardada, está disponible en todos los workflows."

---

## Paso 3: Verificar que todo funciona

### Test rápido de OpenRouter

1. Crear workflow nuevo
2. Manual Trigger → Basic LLM Chain → conectar OpenRouter Chat Model
3. Prompt: `Say hello in three languages`
4. Ejecutar → debe devolver una respuesta

### Test rápido de SerpAPI

1. En el mismo workflow (o uno nuevo)
2. Manual Trigger → AI Agent → conectar OpenRouter Chat Model + SerpAPI tool
3. System message: `You are a helpful assistant. Use Google Search when needed.`
4. Prompt: `What is the weather like in Madrid today?`
5. Ejecutar → debe buscar en Google y responder

**Qué decir:**

> "Si ambos funcionan, estáis listos para el resto del curso. Si algo falla, lo más probable es que la API key esté mal copiada — id a Credentials y verificad que no hay espacios extra."

---

## Dónde se guardan las credenciales

**Qué decir:**

> "Las credenciales se guardan en n8n, no en los workflows. Si exportáis un workflow y se lo pasáis a alguien, las keys NO se incluyen — cada persona configura las suyas."
>
> "Podéis ver y editar todas vuestras credenciales en **Settings → Credentials**."

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| OpenRouter: "Invalid API key" | Verificar que la key está copiada completa (empieza por `sk-or-`) |
| OpenRouter: "Rate limit exceeded" | Estás usando un modelo gratuito con mucho tráfico — esperar unos minutos |
| SerpAPI: "Error 401" | API key incorrecta — copiar de nuevo desde el dashboard |
| SerpAPI: "Account limit reached" | Has superado las 100 búsquedas gratuitas del mes |
| "No credentials found" | Abrir el nodo → Credential → seleccionar la credencial guardada |

### Si usas Docker

| Problema | Solución |
|----------|----------|
| "Connection refused" o timeout al llamar a OpenRouter/SerpAPI | Problema de DNS dentro del contenedor. Reiniciar Docker Desktop. En Linux, usar `--network host` |
| Las credenciales desaparecen al reiniciar | Asegúrate de usar `-v n8n_data:/home/node/.n8n` en el `docker run`. Sin el volumen, todo se pierde |
| "ENOTFOUND" o "getaddrinfo failed" | El contenedor no tiene acceso a internet. Verificar que Docker Desktop tiene permisos de red en el firewall |
