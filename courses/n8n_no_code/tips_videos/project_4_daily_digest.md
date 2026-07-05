# Guion — Project 4: Daily Digest (workflow `18_daily_digest.json`)

## Concepto
Todos los proyectos anteriores **te esperaban a ti** (un chat, una foto, un formulario). Este **se ejecuta solo**, en un horario, sin nadie delante.
Cada mañana, un **Schedule Trigger** despierta el workflow, trae los titulares tech del día, un agente los **lee** (y puede profundizar en uno), escribe un **briefing** corto y lo **guarda**. Te levantas con un resumen que nunca pediste — el "agente que trabaja mientras duermes".
**La capacidad nueva:** un **trigger programado** → agentes **proactivos**. Y es el puente perfecto al deploy: un chat lo pruebas en tu portátil, pero algo *programado* solo se dispara si n8n está **vivo 24/7**.

## Flujo del workflow
```
Every morning ──▶ Get Top Stories ──▶ Briefing Writer ──▶ Save Briefing
(Schedule)        (HTTP: Hacker News)  (Agente)             (Data Table)
                                          ┊ sub-nodos
                                  ┌───────┴────────┐
                             Chat Model       Story Details
                                            (HTTP tool, bajo demanda)
```
**Requisitos:** OpenRouter (`gpt-4o-mini`) + **n8n 1.113+**. Sin más credenciales — la API de Hacker News es gratis y sin key.

---

## 🗺️ Los nodos de un vistazo (léelo primero)

Al importar, **ya está todo conectado**. Esto es lo que hay:

| Nodo | Qué es |
|------|--------|
| **Every morning** | El disparador: se ejecuta solo, cada día a las 8:00 |
| **Get Top Stories** | Trae los titulares del día (HTTP a Hacker News, JSON) |
| **Briefing Writer** | El agente: lee la lista y escribe el briefing |
| **OpenRouter Chat Model** | El cerebro del agente |
| **Story Details** | Tool: abre UN artículo para profundizar (el agente decide) |
| **Save Briefing** | Guarda el briefing + fecha en la tabla `briefings` |

**Solo 2 cosas que hacer:** **(1)** crear la tabla `briefings`, **(2)** poner tu modelo en OpenRouter Chat Model. Lo demás ya viene cableado.

---

## 🔧 Preparación ANTES de grabar (checklist)

1. **Importa** el workflow (Import from URL): `https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/18_daily_digest.json`
2. **Crea la tabla `briefings`** (Overview → Data tables → Create Data Table):
   - **⚡ Rápido:** Import CSV con `briefings_template.csv` (repo, `_static/data/`) → crea las columnas solas.
   - **✋ A mano:** From scratch → 2 columnas **String**: `date` · `briefing`.
   - El nodo **Save Briefing** ya apunta a ella **por nombre** → nada que seleccionar.
3. **Modelo** en OpenRouter Chat Model: `openai/gpt-4o-mini`.
4. **No esperes a las 8:00:** para probar, se pulsa **Execute workflow** y se dispara al momento.

## 🔗 URLs para tener a mano

| Para qué | URL |
|----------|-----|
| n8n docs — Schedule Trigger | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/ |
| n8n docs — HTTP Request | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/ |
| Hacker News Search API | https://hn.algolia.com/api |

---

# 🎬 GUION DE GRABACIÓN (de arriba abajo)

## 0 · (Opcional) Cold open — el gancho (20s)
> Grábalo al final. En pantalla: el workflow ejecutándose solo y un briefing recién guardado en la tabla.
- **Di:** *"Este agente no espera a que yo le hable. Cada mañana se ejecuta solo, lee las noticias del día y me deja un resumen escrito. Un agente que trabaja mientras duermo. Vamos a montarlo."*

## 1 · La idea: un agente proactivo (1.5 min)
- **Di:** *"Hasta ahora todos los agentes eran **reactivos**: esperaban a que TÚ les hablaras. Hoy le damos la vuelta: un agente **proactivo**, que arranca solo, en un horario, y te entrega el resultado. Monitorización, informes diarios, avisos… un montón de la automatización real es así, y no hay ninguna ventana de chat."*
- **Di (el puente al deploy):** *"Y ojo: esto solo funciona si n8n está encendido. Un chat lo pruebas en tu portátil; algo programado tiene que vivir en un servidor 24/7. Por eso el siguiente proyecto es **desplegar** — este es el primero que DE VERDAD necesitas poner en producción."*

## 2 · El Schedule Trigger (45s)
- **[Click en `Every morning`]**
- **Di:** *"La estrella: el **Schedule Trigger**. En vez de esperar un mensaje, se dispara con un reloj. Aquí: **Trigger Interval = Days**, **Trigger at Hour = 8**. Cada día a las 8 de la mañana, se ejecuta solo. Podría ser cada hora, cada lunes, lo que quieras."*

## 3 · Traer las noticias (45s)
- **[Click en `Get Top Stories`]**
- **Di:** *"Un **HTTP Request** normal a la API gratuita de Hacker News. Nos devuelve, en un JSON, los titulares de portada: título, enlace, puntos, comentarios. Sin credenciales, sin API key. Así metemos datos frescos del mundo dentro del workflow."*

## 4 · El agente que resume (2 min)
- **[Click en `Briefing Writer`]**
- **Di (la entrada):** *"Al agente le pasamos la lista de noticias como texto — fijaos en el Prompt: `{{ JSON.stringify($json.hits) }}`, o sea, el JSON de titulares que trajo el paso anterior."*
- **[Options → System Message]** — recórrelo:
  1. **Elige** las 3-4 noticias más relevantes (prefiere IA, startups, software).
  2. **Una línea por noticia:** título en cristiano + "por qué importa".
  3. **Puede** usar la tool **Story Details** UNA vez, en la más interesante, para profundizar. *Con moderación.*
  4. Cierra con **"Today's theme:"**.
- **[Click en `Story Details`]**
- **Di (la tool):** *"Esta herramienta abre UNA noticia por su `objectID` para leer su discusión. Fíjate en la URL: lleva un `$fromAI('story_id')` — el agente decide QUÉ noticia abrir y rellena el id. Es agente de verdad: no resume a lo bruto, edita y decide si merece la pena profundizar."*

## 5 · Guardar el briefing (30s)
- **[Click en `Save Briefing`]**
- **Di:** *"Al final, un nodo **Data Table** (Insert) guarda una fila en `briefings` con la **fecha** y el **texto**. Reutilizamos las Data Tables de antes. Día a día se va formando un archivo de briefings, sin ninguna credencial."*

---

## 6 · DEMO — que se ejecute solo (2-3 min)

**No esperes a las 8:00.** Para la demo, lo disparas tú.

### Ejecútalo ahora
- Pulsa **Execute workflow** (arriba en el canvas).
> **Di:** *"Normalmente esto pasaría solo a las 8. Yo lo fuerzo para enseñarlo."*
- **Qué esperar:** al final aparece el briefing, y en la tabla `briefings` una fila nueva.

### Enseña que el agente PIENSA
- Abre **Briefing Writer → Logs**.
> **Di:** *"Aquí está lo bueno: veis la lista de noticias que recibió, y —a veces— una llamada a **Story Details** con un `objectID`. Ha DECIDIDO abrir esa noticia. En un día flojo se salta la tool; en un día de noticia gorda, entra. Esa decisión es el agente haciendo su trabajo."*

### Enseña la tabla
- Abre **Data tables → `briefings`**.
> **Di:** *"Ahí está el briefing guardado, con su fecha. Cada mañana añade una fila — un archivo de tu semana."*

### El puente al deploy
- Pulsa **Publish** (arriba a la derecha).
> **Di:** *"Y ahora lo importante: le doy a Publish. A partir de aquí se dispararía cada mañana… **si n8n está encendido**. En mi portátil, solo mientras lo tengo abierto. Para que funcione DE VERDAD todos los días, hay que desplegarlo. Y eso es justo el siguiente proyecto."*

---

## 7 · Variaciones (para el vídeo o los deberes)

- **Tu tema, tu fuente:** cambia la URL del HTTP (o mete un nodo **RSS Read** de un blog) y adapta el prompt → briefing de LO TUYO, no de tech.
- **Entrégalo, no solo lo guardes:** en vez de (o además de) la tabla, mándalo por **Telegram** (token de bot gratis) o **Email (SMTP)**.
- **Solo avísame si importa:** que el agente devuelva `important: true/false` y un **IF** que solo entregue en días de noticia gorda. Un monitor, no una pesadez diaria.
- **Resumen semanal:** un segundo workflow con Schedule semanal que lee la tabla `briefings` de los últimos 7 días y escribe un "week in review".

## Cierre (20s)
- **Di:** *"Mismo motor de siempre —un agente con una herramienta que guarda en una Data Table—, pero cambiando UNA cosa, el trigger, tienes un tipo de app completamente distinto: uno que trabaja solo. Y el siguiente paso natural es ponerlo en producción para que corra de verdad."*
