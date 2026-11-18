"""LetMeBank card renderer v2: two styles, mix them across days.
Usage: python3 render2.py cards.json OUT_DIR
Card fields:
  slug   short-kebab-name (file: letmebank-<slug>.png)
  style  "light" (1080x1350, cream, tall) or "split" (1600x900, green panel + dark)
  tag    e.g. CHECKLIST, BANKING TIP, MYTH VS FACT, WORD OF THE WEEK, STATE GUIDE, KNOW THE DIFFERENCE
  head   headline, under 45 characters
  mark   optional: part of head to highlight (light style underline / split style white)
  stat   optional: short number or word shown big (use only when it means something)
  items  optional: 2 to 4 short lines (under 60 chars each), shown as a numbered list
  sub    optional: one line under the list or headline (under 90 chars); wrap words in **..** for bold
  source optional: e.g. "Source: CFPB" or "LetMeBank Texas research"
Needs fonts in /tmp/fonts (see routine set-up) and Chrome at /usr/bin/google-chrome.
"""
import json, os, re, sys
from html import escape
from playwright.sync_api import sync_playwright

cards = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
F = "/tmp/fonts"
INK, G, DG, CREAM = "#191c1e", "#4ecb8d", "#1f8a57", "#f6f1e7"
faces = f"@font-face{{font-family:FT;font-weight:800;src:url(file://{F}/fontsource-figtree-5.3.0/files/figtree-latin-800-normal.woff2)}}"
faces += "".join(f"@font-face{{font-family:RB;font-weight:{w};src:url(file://{F}/fontsource-rubik-5.3.0/files/rubik-latin-{w}-normal.woff2)}}" for w in (400, 500))

def rich(t, bold_color):
    t = escape(t)
    return re.sub(r"\*\*(.+?)\*\*", rf'<b style="color:{bold_color}">\1</b>', t)

def head_html(c, mark_style):
    h = escape(c["head"]); m = c.get("mark")
    if m and escape(m) in h:
        h = h.replace(escape(m), f'<span style="{mark_style}">{escape(m)}</span>', 1)
    return h

def items_html(items, dark, fs, pd):
    line = "#2c3134" if dark else "#e4ddd0"
    rows = "".join(f"""<div style="display:flex;gap:30px;align-items:flex-start;padding:{pd}px 0;border-top:3px solid {line}">
<div style="flex:none;width:76px;height:76px;border-radius:50%;background:{G};color:{INK};font-family:FT;font-weight:800;font-size:44px;display:flex;align-items:center;justify-content:center">{i}</div>
<div style="font-size:{fs}px;line-height:1.25;font-weight:500;padding-top:6px">{escape(t)}</div></div>""" for i, t in enumerate(items, 1))
    return rows + f'<div style="border-top:3px solid {line}"></div>'

def light(c):
    n = len(c.get("items", []))
    fs, pd = {0: (50, 40), 2: (54, 48), 3: (50, 40), 4: (44, 30)}.get(n, (44, 30))
    stat = f'<div style="font-family:FT;font-weight:800;font-size:220px;line-height:.95;color:{DG};margin:10px 0 20px">{escape(c["stat"])}</div>' if c.get("stat") else ""
    body = items_html(c["items"], False, fs, pd) if n else ""
    sub = f'<div style="padding-top:34px;font-size:{40 if n else 50}px;color:#4a4f53;line-height:1.35">{rich(c["sub"], INK)}</div>' if c.get("sub") else ""
    return f"""<div style="width:1080px;height:1350px;box-sizing:border-box;padding:84px 80px 64px;background:{CREAM};color:{INK};font-family:RB;display:flex;flex-direction:column">
<div style="font-family:FT;font-weight:800;font-size:30px;letter-spacing:4px;color:{DG}">{escape(c['tag'])}</div>
{stat}<div style="font-family:FT;font-weight:800;font-size:{92 if len(c['head'])<=34 else 80}px;line-height:1.04;margin:22px 0 46px">{head_html(c, f"background:linear-gradient(transparent 58%,{G} 58%)")}</div>
<div style="{'' if n else 'flex:0'}">{body}</div>{sub}
<div style="margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end">
<div style="font-family:FT;font-weight:800;font-size:54px">LetMe<span style="color:{DG}">Bank</span></div>
<div style="font-size:26px;color:#6b7075">{escape(c.get('source',''))}</div></div></div>""", 1080, 1350

def split(c):
    n = len(c.get("items", []))
    fs, pd = {2: (48, 40), 3: (42, 30), 4: (36, 22)}.get(n, (42, 30))
    hs = 74 if len(c["head"]) <= 34 else 64
    stat = f'<div style="font-family:FT;font-weight:800;font-size:200px;line-height:.9;margin-top:24px">{escape(c["stat"])}</div>' if c.get("stat") else ""
    right = items_html(c["items"], True, fs, pd) if n else ""
    sub = f'<div style="padding-top:30px;font-size:{34 if n else 52}px;line-height:1.35;color:#C9CED3">{rich(c["sub"], "#fff")}</div>' if c.get("sub") else ""
    src = f'<div style="padding-top:14px;font-size:24px;color:#8a9096">{escape(c["source"])}</div>' if c.get("source") else ""
    return f"""<div style="width:1600px;height:900px;box-sizing:border-box;background:{INK};color:#fff;font-family:RB;display:flex">
<div style="width:620px;flex:none;background:{G};color:{INK};padding:80px 64px;box-sizing:border-box;display:flex;flex-direction:column">
<div style="font-family:FT;font-weight:800;font-size:28px;letter-spacing:4px">{escape(c['tag'])}</div>{stat}
<div style="font-family:FT;font-weight:800;font-size:{hs}px;line-height:1.04;margin-top:28px">{head_html(c, 'color:#fff')}</div>
<div style="margin-top:auto;font-family:FT;font-weight:800;font-size:46px">LetMe<span style="color:#fff">Bank</span></div></div>
<div style="flex:1;padding:70px 80px;display:flex;flex-direction:column;justify-content:center">{right}{sub}{src}</div></div>""", 1600, 900

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
    for c in cards:
        html, w, h = (split if c.get("style") == "split" else light)(c)
        pg = b.new_page(viewport={"width": w, "height": h})
        open("/tmp/card2.html", "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{faces}body{{margin:0}}</style></head><body>{html}</body></html>')
        pg.goto("file:///tmp/card2.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(out, f"letmebank-{c['slug']}.png")); pg.close()
    b.close()
