# Tips Video: 06 AI Agent Multi-Tool (SerpAPI + Calculator + Think)

## Concepto clave
Un agent con MÚLTIPLES tools. El agent decide CUÁL usar y CUÁNDO.

## Flujo del workflow
```
Manual Trigger → Input → AI Agent ← [SerpAPI, Calculator, Think, Memory, Chat Model] → Output
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Agent Prompt

| Field | Expression |
|-------|------------|
| `chatInput` | `{{ $json.chatInput \|\| "Search for the average data scientist salary in Spain. Then calculate the monthly net salary after 24% income tax." }}` |
| `sessionId` | `{{ $json.sessionId \|\| "demo" }}` |

### AI Agent — Salary Research

**System Message:**
```
You are a salary research assistant.

Rules:
- To find salary data, job market info, or company details: use the Google Search tool.
- For arithmetic (tax calculations, salary comparisons): ALWAYS use Calculator.
- Use Think briefly (1-2 sentences) to plan before calling tools.
- Output: short bullets with sources, then the final computed number.
```

**Prompt (User Message):**
```
{{ $json.chatInput }}
```

### Simple Memory

| Setting | Value |
|---------|-------|
| Session ID Type | `Custom Key` |
| Session Key | `{{ $json.sessionId }}` |
| Context Window Length | `10` |

### Output — Answer

| Field | Expression |
|-------|------------|
| `answer` | `{{ $json.output }}` |

---

## 🧪 Prompts de prueba

**Salario data scientist (default):**
```
Search for the average data scientist salary in Spain. Then calculate the monthly net salary after 24% income tax.
```

**Software engineer en Berlin:**
```
What is the average software engineer salary in Berlin? Calculate the monthly net after 30% tax.
```

**Comparación de salarios:**
```
Compare junior vs senior data analyst salaries in London.
```

**Salario con beneficios:**
```
Search for the average product manager salary in Barcelona. Calculate monthly net after 22% tax.
```

---

## 🎬 Paso a paso para el video

### 1. Por qué múltiples tools
- **Explicar:** Tareas complejas necesitan diferentes capacidades
- **Ejemplo:** "Busca el salario promedio de data scientist en España y calcula el neto mensual"
- **Destacar:** Un tool no puede hacerlo todo

### 2. System message
- **Mostrar:** Reglas específicas para CADA tool
- **Explicar:** Sin estas reglas, el agent puede elegir mal

### 3. SerpAPI tool
- **Mostrar:** NECESITA API key (gratis en serpapi.com)
- **Explicar:** Busca en Google, devuelve resultados actualizados
- **Tip:** "Útil para datos de salarios, mercado laboral, empresas"
- **Destacar:** A diferencia de Wikipedia, da datos en tiempo real

### 4. Think tool
- **Mostrar:** Es un "tool interno" — no hace llamadas externas
- **Explicar:** Ayuda al agent a planificar antes de actuar
- **Destacar:** "1-2 sentences" evita que piense demasiado

### 5. Calculator tool
- **Explicar:** Mismo que en workflow 05
- **Destacar:** "ALWAYS use Calculator" sigue siendo importante

### 6. Ver la secuencia de tools
- **Demo:** Ejecutar pregunta de salario
- **Mostrar:** En Output Panel, la secuencia: Think → SerpAPI → Calculator
- **Explicar:** El agent decidió el orden

---

## ✅ Puntos clave para el video
- [ ] Agent orquesta múltiples tools
- [ ] System message dice CUÁNDO usar cada uno
- [ ] Think tool = planificación interna
- [ ] SerpAPI NECESITA API key (gratis en serpapi.com)

## 🎥 Demo sugerida
1. Ejecutar prompt de salario data scientist en España
2. Ver secuencia: Think → SerpAPI → Calculator
3. Mostrar cómo el agent "razona" paso a paso

## ⚠️ Errores comunes
- No dar guidance de CUÁNDO usar cada tool
- No configurar credenciales de SerpAPI → tool falla
- Esperar que el agent adivine qué tool usar
- Think tool sin límite → agent divaga
