import json, os, sys
from playwright.sync_api import sync_playwright
cards = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
F = "/tmp/fonts"; LOGO = "file:///tmp/repo/letmebank/brand/letmebank-logo-light-2000.png"
BG, GREEN = "#191c1e", "#4ecb8d"
faces = f"@font-face{{font-family:FT;font-weight:800;src:url(file://{F}/fontsource-figtree-5.3.0/files/figtree-latin-800-normal.woff2)}}"
faces += "".join(f"@font-face{{font-family:RB;font-weight:{w};src:url(file://{F}/fontsource-rubik-5.3.0/files/rubik-latin-{w}-normal.woff2)}}" for w in (400, 500))
def page(c):
    ss = 180 if len(c["stat"]) <= 7 else 140
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{faces}body{{margin:0}}</style></head><body>
<div style="width:1600px;height:900px;box-sizing:border-box;padding:72px 90px 0;background:{BG};color:#fff;font-family:RB,sans-serif;display:flex;flex-direction:column;gap:22px;border-bottom:20px solid {GREEN}">
<div><span style="background:{GREEN};color:{BG};font-family:FT;font-weight:800;font-size:38px;letter-spacing:3px;padding:10px 28px;border-radius:10px">{c['tag']}</span></div>
<div style="font-family:FT;font-weight:800;font-size:{ss}px;line-height:1;color:{GREEN};margin-top:18px">{c['stat']}</div>
<div style="font-family:FT;font-weight:800;font-size:70px;line-height:1.08;max-width:1340px">{c['head']}</div>
<div style="font-size:36px;line-height:1.35;color:#C9CED3;max-width:1300px">{c['sub']}</div>
<div style="margin-top:auto;padding-bottom:46px;display:flex;align-items:flex-end;justify-content:space-between;gap:40px">
<img src="{LOGO}" style="height:60px;width:auto"><div style="font-size:26px;color:#C9CED3;text-align:right">{c.get('foot','letmebank.com')}</div></div></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1600, "height": 900})
    for c in cards:
        open("/tmp/card.html", "w").write(page(c)); pg.goto("file:///tmp/card.html")
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(out, f"letmebank-{c['slug']}.png"))
    b.close()
