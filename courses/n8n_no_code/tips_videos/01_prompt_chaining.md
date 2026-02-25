# Tips Video: 01 Prompt Chaining

## Concepto clave
Dividir una tarea compleja en pasos pequeños → más fiable que un solo prompt largo.

## Flujo del workflow
```
Manual Trigger → Input (Recipe) → Step 1 (Simplify) → Store → Step 2 (Adapt for Kids) → Store → Step 3 (Shopping List) → Output
```

---

## 📋 COPY-PASTE: Fields y Prompts

### Input — Recipe

Dos campos String:

**`recipe_name`:**

📋
```
Classic Beef Lasagna
```

**`recipe`:**

📋
```
Ingredients:
- 500g ground beef
- 1 onion, finely diced
- 3 cloves garlic, minced
- 800g canned crushed tomatoes
- 2 tbsp tomato paste
- 1 tsp dried oregano
- 1 tsp dried basil
- Salt and pepper to taste
- 250g lasagna sheets
- 500g ricotta cheese
- 1 egg
- 300g shredded mozzarella
- 50g grated parmesan
- Fresh basil for garnish

Instructions:
1. Brown the ground beef in a large skillet over medium-high heat. Drain excess fat.
2. Sauté the onion and garlic until translucent. Add crushed tomatoes, tomato paste, oregano, basil, salt, and pepper. Simmer for 20 minutes.
3. Mix ricotta, egg, and half the parmesan in a bowl.
4. Preheat oven to 375°F (190°C).
5. Layer in a 9x13 baking dish: sauce, lasagna sheets, ricotta mixture, mozzarella. Repeat 3 times.
6. Top with remaining sauce and mozzarella.
7. Cover with foil and bake 25 minutes. Remove foil, bake 15 more minutes until golden.
8. Let rest 10 minutes before serving. Garnish with fresh basil.
```

### Step 1 — Simplify Recipe

**System Message:**

📋
```
You are a cooking instructor for beginners.
Simplify the recipe into clear, easy-to-follow steps.

Rules:
- Use simple language (no cooking jargon)
- Explain any technique briefly (e.g., "sauté" → "cook in a pan, stirring often")
- Keep all original ingredients
- Number every step clearly
- Output ONLY the simplified recipe
```

**User Message (Expression):**

📋
```
Recipe: {{ $json.recipe_name }}

{{ $json.recipe }}

Simplify this recipe for a beginner cook.
```

### Store Simplified Recipe

Campo String — Name: `simplified_recipe`, Value (Expression):

📋
```
{{ $json.text }}
```

### Step 2 — Adapt for Kids

**System Message:**

📋
```
You are a family cooking expert.
Adapt the simplified recipe so it is fun and safe for kids aged 5–10 to help make.

Rules:
- Suggest milder alternatives for strong flavors (e.g., less garlic, skip pepper)
- Add fun names for steps (e.g., "Squish the cheese mix!")
- Flag any step that needs adult help (hot oven, sharp knives)
- Adjust portions for a family with kids
- Output ONLY the kid-friendly recipe
```

**User Message (Expression):**

📋
```
Simplified recipe:
{{ $json.simplified_recipe }}

Adapt this for kids.
```

### Store Kid-Friendly Recipe

Campo String — Name: `kid_friendly_recipe`, Value (Expression):

📋
```
{{ $json.text }}
```

### Step 3 — Shopping List

**System Message:**

📋
```
You are a helpful shopping assistant.
Create a shopping list from the recipe.

Rules:
- Group items by store section (Produce, Dairy, Meat, Pantry)
- Include quantities
- Skip items most kitchens already have (salt, pepper, olive oil)
- Add a "Check at home first" section for common pantry items
- Output ONLY the shopping list
```

**User Message (Expression):**

📋
```
Recipe:
{{ $json.kid_friendly_recipe }}

Create a shopping list.
```

### Output — Shopping List

Campo String — Name: `shopping_list`, Value (Expression):

📋
```
{{ $json.text }}
```

---

## 🎬 Paso a paso para el video

### 1. Input — Recipe
- **Mostrar:** Los 2 campos (recipe_name, recipe)
- **Explicar:** Separar inputs hace el workflow reutilizable
- **Tip:** "En producción esto vendría de un formulario, webhook, o incluso de un HTTP Request a una web de recetas"

### 2. Step 1 — Simplify Recipe
- **Mostrar:** System message con rol "cooking instructor for beginners"
- **Explicar:** El prompt pide SOLO la receta simplificada, nada más
- **Destacar:** Traducción de jerga culinaria ("sauté" → "cook in a pan, stirring often")

### 3. Store Simplified Recipe
- **Explicar:** Por qué renombramos `text` → `simplified_recipe`
- **Mostrar:** Output panel con el resultado
- **Tip:** "Útil para debugging y claridad visual"

### 4. Step 2 — Adapt for Kids
- **Mostrar:** System message con rol "family cooking expert"
- **Explicar:** Transformación clara: sabores suaves, nombres divertidos, notas de seguridad
- **Destacar:** Rol diferente = perspectiva diferente, output visiblemente distinto

### 5. Step 3 — Shopping List
- **Mostrar:** System message con rol "shopping assistant"
- **Explicar:** Output en formato completamente diferente (lista agrupada por sección de tienda)
- **Destacar:** Cada paso produce algo visiblemente distinto

---

## ✅ Puntos clave para el video
- [ ] Cada LLM Chain tiene un ROL diferente
- [ ] Output de uno → Input del siguiente
- [ ] "Output ONLY..." evita texto extra
- [ ] Los Store nodes son opcionales pero ayudan a debuggear
- [ ] Cada paso produce un formato de output visiblemente distinto

## 🎥 Demo sugerida
1. Ejecutar workflow completo
2. Mostrar output de cada paso en Output Panel
3. Comparar: receta original → simplificada → para niños → lista de compra
4. Destacar lo diferente que es cada output

## ⚠️ Errores comunes
- Prompt demasiado largo en un solo paso
- No especificar formato de output
- Olvidar que cada paso debe ser independiente

## 💡 Tip extra: leer outputs largos en n8n
- n8n no formatea el texto del LLM (no renderiza markdown)
- En el Output Panel, usar **Table** view y hacer clic en el valor del campo `text` → se abre en un panel expandido más legible
- Pin data (📌) tras la primera ejecución exitosa para no repetir llamadas API mientras se edita
