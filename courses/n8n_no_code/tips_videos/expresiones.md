# Tips: Expresiones en n8n

## Acceder a nodos anteriores

```
{{ $json.field }}                         → nodo inmediatamente anterior
{{ $node['Node Name'].json.field }}       → nodo específico (sintaxis clásica)
{{ $('Node Name').item.json.field }}      → nodo específico (sintaxis nueva)
```

## Autocompletado en Expression Editor

- Hacer clic en campo → pestaña "Expression"
- Al escribir `$` aparecen sugerencias
- Al escribir `$('` aparecen los nombres de nodos
- Panel izquierdo: navegador de "Input" y "Nodes" → clic para insertar

## Drag & Drop

- Abrir Output Panel de un nodo anterior
- Arrastrar campo directamente al campo de expresión
- n8n genera la expresión automáticamente

## Errores comunes

- Campo en modo "Fixed" en vez de "Expression"
- Nombre del nodo mal escrito (case-sensitive)
- Datos pinneados obsoletos
