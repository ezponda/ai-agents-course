#!/usr/bin/env python3
"""Convierte un guion .md a HTML con sidebar de navegación (TOC) y scrollspy.

Uso:
    python3 md_to_html.py project_1_recipe_assistant.md [otro.md ...]

Genera <mismo_nombre>.html junto al .md, con la estética de los guiones HTML
del repo (tema oscuro, aside sticky, botón "copiar" en cada bloque de código).
Si editas el .md, vuelve a ejecutar el script para regenerar el HTML.

Requiere: pip install markdown  (extensiones estándar: tables, fenced_code, toc)
"""
import html
import re
import sys
from pathlib import Path

import markdown

TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root{{
    --bg:#0f1117; --panel:#171a23; --panel2:#1e2230; --ink:#e8eaf0; --muted:#9aa3b2;
    --line:#2a2f3e; --accent:#36a3ff; --say:#4aa3ff; --do:#36c98b; --warn:#ffb84d;
    --quote:#c08bff; --code:#0b0d13; --radius:14px;
  }}
  *{{box-sizing:border-box}}
  html{{scroll-behavior:smooth}}
  body{{margin:0;background:var(--bg);color:var(--ink);
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}}
  .wrap{{display:grid;grid-template-columns:280px 1fr;min-height:100vh}}

  aside{{position:sticky;top:0;height:100vh;overflow:auto;background:var(--panel);
    border-right:1px solid var(--line);padding:20px 16px}}
  aside h1{{font-size:14px;margin:0 0 16px;line-height:1.4}}
  .nav a{{display:block;color:var(--muted);text-decoration:none;padding:7px 11px;
    border-radius:10px;font-size:13px;margin-bottom:2px;border:1px solid transparent;line-height:1.35}}
  .nav a.h3{{padding-left:24px;font-size:12.5px}}
  .nav a:hover{{background:var(--panel2);color:var(--ink)}}
  .nav a.active{{background:var(--panel2);color:var(--ink);border-color:var(--line)}}

  main{{padding:36px 48px;max-width:980px}}
  main h1{{font-size:26px;margin:0 0 18px;line-height:1.3}}
  main h2{{font-size:21px;margin:44px 0 14px;padding-top:22px;border-top:1px solid var(--line)}}
  main h3{{font-size:17px;margin:30px 0 10px;color:var(--accent)}}
  main h4{{font-size:15px;margin:22px 0 8px;color:var(--tip,#caa45a)}}
  main a{{color:var(--accent)}}
  main blockquote{{margin:12px 0;padding:10px 16px;border-left:3px solid var(--say);
    background:var(--panel);border-radius:0 10px 10px 0;color:#cfe3ff}}
  main blockquote p{{margin:0}}
  main strong{{color:#d6f5e7}}
  main code{{background:var(--code);border:1px solid var(--line);border-radius:6px;
    padding:1px 6px;font-size:.9em}}
  main pre{{position:relative;background:var(--code);border:1px solid var(--line);
    border-radius:10px;padding:14px 16px;overflow-x:auto}}
  main pre code{{background:none;border:0;padding:0;font-size:13.5px;line-height:1.55}}
  .copy{{position:absolute;top:8px;right:8px;background:var(--panel2);color:var(--muted);
    border:1px solid var(--line);border-radius:8px;padding:3px 10px;font-size:12px;cursor:pointer}}
  .copy:hover{{color:var(--ink)}}
  main table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:14.5px}}
  main th,main td{{border:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}}
  main th{{background:var(--panel2)}}
  main tr:nth-child(even) td{{background:var(--panel)}}
  main hr{{border:0;border-top:1px solid var(--line);margin:28px 0}}
  main ul,main ol{{padding-left:26px}}
  main li{{margin:5px 0}}

  @media(max-width:860px){{.wrap{{grid-template-columns:1fr}}aside{{position:static;height:auto}}main{{padding:24px 20px}}}}
  @media print{{aside{{display:none}}.wrap{{grid-template-columns:1fr}}.copy{{display:none}}}}
</style>
</head>
<body>
<div class="wrap">
<aside>
  <h1>{title}</h1>
  <nav class="nav">
{nav}
  </nav>
</aside>
<main>
{body}
</main>
</div>
<script>
// Botón "copiar" en cada bloque de código
document.querySelectorAll('main pre').forEach(pre => {{
  const btn = document.createElement('button');
  btn.className = 'copy'; btn.textContent = 'copiar';
  btn.addEventListener('click', () => {{
    navigator.clipboard.writeText(pre.querySelector('code').innerText.trimEnd());
    btn.textContent = '✓ copiado';
    setTimeout(() => btn.textContent = 'copiar', 1500);
  }});
  pre.appendChild(btn);
}});
// Scrollspy: resalta en el sidebar la sección visible
const links = [...document.querySelectorAll('.nav a')];
const byId = Object.fromEntries(links.map(a => [a.getAttribute('href').slice(1), a]));
const obs = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      links.forEach(a => a.classList.remove('active'));
      byId[e.target.id]?.classList.add('active');
    }}
  }});
}}, {{rootMargin: '0px 0px -75% 0px'}});
document.querySelectorAll('main h2[id], main h3[id]').forEach(h => obs.observe(h));
</script>
</body>
</html>
"""


def convert(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    body = md.convert(text)

    # Título: primer H1 del markdown (sin sintaxis de código)
    m = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = html.escape(re.sub(r"`([^`]*)`", r"\1", m.group(1))) if m else md_path.stem

    # Sidebar a partir de los tokens del TOC (h2 + h3)
    items = []
    for tok in md.toc_tokens:
        items.append(f'    <a href="#{tok["id"]}">{tok["name"]}</a>')
        for child in tok.get("children", []):
            items.append(f'    <a class="h3" href="#{child["id"]}">{child["name"]}</a>')
    nav = "\n".join(items)

    out = md_path.with_suffix(".html")
    out.write_text(TEMPLATE.format(title=title, nav=nav, body=body), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        print("→", convert(Path(arg)))
