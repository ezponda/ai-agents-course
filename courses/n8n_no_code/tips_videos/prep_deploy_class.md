# Prep: Clase Deploy to Production (~1.5h)

## Antes de clase (hacer en casa, ~30 min)

### Railway setup
- [ ] Crear cuenta en [railway.com](https://railway.com/) (login con GitHub)
- [ ] Ir a [railway.com/template/n8n](https://railway.com/template/n8n) → Deploy Now
- [ ] Esperar 2-3 min al deploy
- [ ] Abrir la URL que te da Railway (`xxx.up.railway.app`)
- [ ] Crear cuenta admin en tu instancia de n8n
- [ ] En Railway → tu servicio n8n → **Variables** → verificar/añadir:
  ```
  WEBHOOK_URL = https://xxx.up.railway.app/
  ```
  (con slash final, usar TU url real)
- [ ] Esperar al redeploy automatico (~1 min)

### Credenciales en Railway n8n
- [ ] Settings → Credentials → añadir **OpenRouter API key**
- [ ] Settings → Credentials → añadir **Google Gemini API key** (para embeddings del RAG)
- [ ] (Opcional) añadir **SerpAPI key** si quieres el agent completo

### Test rapido: workflow simple
- [ ] Import from URL el workflow del proyecto:
  ```
  https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/13_deploy_to_production.json
  ```
- [ ] Configurar credencial OpenRouter en el nodo
- [ ] Activar workflow (toggle ON arriba a la derecha)
- [ ] Click en Chat Trigger → copiar **Production URL**
- [ ] Abrir en el navegador → probar que funciona
- [ ] **Guardar esa URL** — la vas a enseñar en clase

### Test rapido: RAG FAQ Bot
- [ ] Import from URL:
  ```
  https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/14_rag_faq_bot.json
  ```
- [ ] Configurar credenciales (OpenRouter + Gemini)
- [ ] Activar el workflow (toggle ON)
- [ ] Abrir la **Form Trigger URL** (click en el nodo Upload Document) y subir el Employee Handbook PDF
- [ ] Probar en el chat: `What is the remote work policy?`
- [ ] Probar algo fuera del documento: `What is the best pizza in Madrid?`

---

## Plan de clase (~1.5h)

### Bloque 1: Concepto (10 min)
- Hasta ahora todo local — solo funciona en vuestro portatil
- Produccion = servidor 24/7, URL publica, cualquiera puede usarlo
- Tres opciones: Railway (~5$/mes), n8n Cloud (~20€/mes), VPS+Docker (avanzado)
- Hoy hacemos Railway

### Bloque 2: Deploy en vivo (25 min)
- Mostrar Railway ya desplegado (lo has preparado antes)
- Enseñar la variable `WEBHOOK_URL` — sin ella las URLs apuntan a localhost
- Importar el workflow simple (13_deploy_to_production.json)
- Configurar credencial, activar, copiar Production URL
- **Momento wow**: abrir la URL en el movil / compartir con un alumno

### Bloque 3: Deploy del RAG Document Chat (25 min)
- Importar el workflow 14_rag_faq_bot.json en Railway
- Activar el workflow — el Form Trigger necesita estar activo para funcionar
- Abrir la Form Trigger URL y subir el Employee Handbook PDF
- Probar en el chat
- Pasar la URL del formulario a los alumnos para que suban sus propios PDFs
- **Limitacion importante**: la memoria se borra si Railway redeploya. Para produccion real habria que usar un vector store persistente (Supabase, Qdrant, Pinecone)

### Bloque 4: Cosas a tener en cuenta (15 min)
- **Credenciales son por instancia** — hay que reconfigurarlas en el servidor
- **Activate ON** — sin esto el Chat Trigger no funciona en produccion
- **output field** — el ultimo nodo DEBE tener un campo `output`
- **Seguridad**: URL publica = abierta a cualquiera = cada mensaje cuesta tokens
- **Execution History**: sidebar izquierdo → Executions — tu herramienta de debugging

### Buffer (15 min)
- Preguntas
- Si sobra tiempo: mostrar n8n Cloud como alternativa (2 min de setup, mas caro)
- Debugging si algo falla

---

## Cosas que pueden fallar

| Problema | Solucion |
|----------|----------|
| Chat muestra JSON crudo | El ultimo nodo no tiene campo `output` |
| Production URL da 404 | Workflow no esta activado (toggle OFF) |
| Chat no responde | `WEBHOOK_URL` no esta configurada o no tiene slash final |
| RAG no encuentra respuestas | No has subido un PDF via el formulario (Form Trigger URL) |
| Railway redeploya y el RAG deja de funcionar | Normal — In-Memory se borra. Volver a subir el PDF via el formulario |
| Credencial no funciona | Las credenciales de tu n8n local NO se copian. Hay que crearlas de nuevo en Railway |

---

## URLs que vas a necesitar

- Railway template n8n: `https://railway.com/template/n8n`
- Workflow simple: `https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/13_deploy_to_production.json`
- Workflow RAG: `https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/14_rag_faq_bot.json`
- PDF Employee Handbook: `https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/data/datalearn_employee_handbook.pdf`
- Railway pricing: `https://railway.com/pricing`
