"""Crediful social card renderer (1600x900). Usage: python3 render2.py cards.json OUTDIR
Every card: {"style", "slug", "tag": "BREAKING" | "JUST IN" | other short tag, "src": "Source name, report, date"}
Styles and their extra fields:
  classic   navy, big stat          stat, head, sub
  light     white, blue rail        stat, head, sub
  split     blue stat panel         stat, statlabel (short line under the stat), head, sub
  bulletin  news-wire, headline big head, sub, date (e.g. "NOV. 20, 2026"), stat (optional chip)
  quote     a real quote            quote (exact words, under 90 chars), speaker
  change    before and after        head, fromlabel, from, tolabel, to, dir ("up" or "down")
Output: OUTDIR/crediful-<slug>.png. Needs fonts in /tmp/fonts and the repo at /tmp/repo.
"""
import json, os, sys, html
from playwright.sync_api import sync_playwright
cards = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
F = "/tmp/fonts"; B = "file:///tmp/repo/brand/"
NAVY, BLUE, RED, INK, PAPER, MUTED = "#0F2A44", "#43A6DD", "#DC2626", "#0F2A44", "#F5F7FA", "#5B6B7F"
faces = "".join(f"@font-face{{font-family:Inter;font-weight:{w};src:url(file://{F}/fontsource-inter-5.3.0/files/inter-latin-{w}-normal.woff2)}}" for w in (400, 600, 700))
faces += f"@font-face{{font-family:SG;font-weight:700;src:url(file://{F}/fontsource-space-grotesk-5.3.0/files/space-grotesk-latin-700-normal.woff2)}}"
E = html.escape
def tag(c, dark_bg):
    if c["tag"] == "BREAKING": bg, fg = RED, "#fff"
    elif dark_bg: bg, fg = BLUE, NAVY
    else: bg, fg = NAVY, "#fff"
    return f'<span style="background:{bg};color:{fg};font-family:SG;font-weight:700;font-size:34px;letter-spacing:3px;padding:9px 24px;border-radius:8px">{E(c["tag"])}</span>'
def shell(inner, bg): return f'<!doctype html><html><head><meta charset="utf-8"><style>{faces}body{{margin:0}}*{{box-sizing:border-box}}</style></head><body><div style="width:1600px;height:900px;overflow:hidden;position:relative;background:{bg};font-family:Inter,sans-serif">{inner}</div></body></html>'
def statsize(s, big=190, small=150): return big if len(s) <= 6 else small


def classic(c):
    tb, tf = (RED, "#FFFFFF") if c["tag"] == "BREAKING" else (BLUE, NAVY)
    return shell(f'''<div style="width:1600px;height:900px;padding:72px 90px 0;color:#fff;display:flex;flex-direction:column;gap:22px;border-bottom:20px solid {BLUE}">
<div><span style="background:{tb};color:{tf};font-family:SG;font-weight:700;font-size:40px;letter-spacing:3px;padding:10px 28px;border-radius:10px">{E(c['tag'])}</span></div>
<div style="font-family:SG;font-weight:700;font-size:{statsize(c['stat'])}px;line-height:1;color:{BLUE};margin-top:18px">{E(c['stat'])}</div>
<div style="font-family:SG;font-weight:700;font-size:70px;line-height:1.08;max-width:1300px">{E(c['head'])}</div>
<div style="font-size:36px;line-height:1.3;color:#CBD5E1;max-width:1300px">{E(c['sub'])}</div>
<div style="margin-top:auto;padding-bottom:46px;display:flex;align-items:flex-end;justify-content:space-between;gap:40px">
<img src="{B}crediful-wordmark-white.png" style="height:64px;width:auto"><div style="font-size:24px;color:#CBD5E1;text-align:right;max-width:900px">Source: {E(c['src'])}</div></div></div>''', NAVY)

def light(c):  # white card, navy type, blue rail on the left
    return shell(f'''<div style="position:absolute;left:0;top:0;bottom:0;width:28px;background:{BLUE}"></div>
<div style="padding:72px 100px 0 118px;height:100%;display:flex;flex-direction:column;gap:22px;color:{INK}">
<div>{tag(c, False)}</div>
<div style="font-family:SG;font-weight:700;font-size:{statsize(c['stat'])}px;line-height:1;color:{BLUE};margin-top:14px">{E(c['stat'])}</div>
<div style="font-family:SG;font-weight:700;font-size:68px;line-height:1.08;max-width:1300px">{E(c['head'])}</div>
<div style="font-size:34px;line-height:1.3;color:{MUTED};max-width:1250px">{E(c['sub'])}</div>
<div style="margin-top:auto;padding:28px 0 46px;border-top:2px solid #DDE3EA;display:flex;align-items:center;justify-content:space-between;gap:40px">
<img src="{B}crediful-wordmark-navy.png" style="height:58px"><div style="font-size:23px;color:{MUTED};text-align:right;max-width:900px">Source: {E(c['src'])}</div></div></div>''', "#FFFFFF")

def split(c):  # big stat on a blue panel, story on navy
    return shell(f'''<div style="display:flex;height:100%">
<div style="width:640px;background:{BLUE};display:flex;flex-direction:column;justify-content:center;padding:0 60px;color:{NAVY}">
<div style="font-family:SG;font-weight:700;font-size:{150 if len(c['stat'])<=6 else 112}px;line-height:1">{E(c['stat'])}</div>
<div style="font-size:28px;font-weight:600;margin-top:24px;line-height:1.3">{E(c.get('statlabel',''))}</div></div>
<div style="flex:1;background:{NAVY};color:#fff;padding:72px 80px 0;display:flex;flex-direction:column;gap:26px">
<div>{tag(c, True)}</div>
<div style="font-family:SG;font-weight:700;font-size:64px;line-height:1.08;margin-top:10px">{E(c['head'])}</div>
<div style="font-size:32px;line-height:1.35;color:#CBD5E1">{E(c['sub'])}</div>
<div style="margin-top:auto;padding-bottom:46px;display:flex;flex-direction:column;gap:18px">
<div style="font-size:21px;color:#94A3B8">Source: {E(c['src'])}</div>
<img src="{B}crediful-wordmark-white.png" style="height:52px;width:fit-content"></div></div></div>''', NAVY)

def bulletin(c):  # news-wire look: headline first, ruled lines, stat as a chip
    return shell(f'''<div style="padding:64px 90px 0;height:100%;display:flex;flex-direction:column;color:{INK}">
<div style="display:flex;align-items:center;gap:24px;padding-bottom:22px;border-bottom:6px solid {NAVY}">{tag(c, False)}
<div style="font-family:SG;font-weight:700;font-size:28px;letter-spacing:4px;color:{MUTED}">CREDIFUL MONEY NEWS</div>
<div style="margin-left:auto;font-size:24px;color:{MUTED}">{E(c.get('date',''))}</div></div>
<div style="font-family:SG;font-weight:700;font-size:92px;line-height:1.04;margin-top:46px;max-width:1420px">{E(c['head'])}</div>
<div style="display:flex;align-items:center;gap:36px;margin-top:40px">
{f'<div style="background:{BLUE};color:{NAVY};font-family:SG;font-weight:700;font-size:72px;line-height:1;padding:18px 30px;border-radius:14px;white-space:nowrap">{E(c["stat"])}</div>' if c.get('stat') else ''}
<div style="font-size:34px;line-height:1.3;color:#334155;max-width:900px">{E(c['sub'])}</div></div>
<div style="margin-top:auto;padding:26px 0 44px;border-top:2px solid #CBD5E1;display:flex;align-items:center;justify-content:space-between">
<img src="{B}crediful-wordmark-navy.png" style="height:54px"><div style="font-size:23px;color:{MUTED};text-align:right;max-width:950px">Source: {E(c['src'])}</div></div></div>''', PAPER)

def quote(c):  # for Fed speeches and official statements; needs quote + speaker
    return shell(f'''<div style="padding:70px 100px 0;height:100%;display:flex;flex-direction:column;color:#fff">
<div style="display:flex;justify-content:space-between;align-items:center">{tag(c, True)}<img src="{B}crediful-wordmark-white.png" style="height:50px"></div>
<div style="font-family:SG;font-weight:700;font-size:260px;line-height:.6;color:{BLUE};margin-top:70px;height:110px">&ldquo;</div>
<div style="font-family:SG;font-weight:700;font-size:80px;line-height:1.1;max-width:1350px">{E(c['quote'])}</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:40px"><div style="width:70px;height:6px;background:{BLUE}"></div>
<div style="font-size:34px;font-weight:600">{E(c['speaker'])}</div></div>
<div style="margin-top:auto;padding-bottom:46px;font-size:23px;color:#94A3B8">Source: {E(c['src'])}</div></div>''', NAVY)

def change(c):  # before and after number with an arrow; needs from, to, label
    up = c.get('dir','up') == 'up'
    return shell(f'''<div style="padding:72px 90px 0;height:100%;display:flex;flex-direction:column;color:#fff">
<div>{tag(c, True)}</div>
<div style="font-family:SG;font-weight:700;font-size:66px;line-height:1.08;margin-top:40px;max-width:1350px">{E(c['head'])}</div>
<div style="display:flex;align-items:center;gap:50px;margin-top:60px">
<div><div style="font-size:26px;color:#94A3B8;font-weight:600;letter-spacing:2px">{E(c['fromlabel'])}</div><div style="font-family:SG;font-weight:700;font-size:130px;line-height:1;color:#94A3B8">{E(c['from'])}</div></div>
<div style="font-family:SG;font-weight:700;font-size:120px;color:{RED if up else '#22C55E'}">{'&#8599;' if up else '&#8600;'}</div>
<div><div style="font-size:26px;color:{BLUE};font-weight:600;letter-spacing:2px">{E(c['tolabel'])}</div><div style="font-family:SG;font-weight:700;font-size:170px;line-height:1;color:{BLUE}">{E(c['to'])}</div></div></div>
<div style="margin-top:auto;padding-bottom:46px;display:flex;align-items:flex-end;justify-content:space-between;gap:40px">
<img src="{B}crediful-wordmark-white.png" style="height:60px"><div style="font-size:23px;color:#CBD5E1;text-align:right;max-width:900px">Source: {E(c['src'])}</div></div></div>''', NAVY)

STYLES = dict(classic=classic, light=light, split=split, bulletin=bulletin, quote=quote, change=change)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1600, "height": 900})
    for c in cards:
        open("/tmp/card.html", "w").write(STYLES[c["style"]](c)); pg.goto("file:///tmp/card.html")
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(out, f"crediful-{c['slug']}.png"))
    b.close()
