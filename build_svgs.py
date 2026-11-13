"""Builds the animated SVGs for README.md in the Auroscale design language.

Palette, radii, glass pills, orbit lines, pipeline light and marquee follow the
company site. Display type is outlined to paths (wide heavy grotesque) so it
renders the same for every visitor; body copy uses the site's font stack.

Run: python build_svgs.py   (needs fonttools + pillow, and assets/owl.png from owl.py)
"""
import base64
import io
import math
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTCollection
from PIL import Image

A = Path(__file__).parent / "assets"
W = 1200

# ---- site tokens
BG, BG1, BG2, BG3 = "#030405", "#080b0e", "#0e1318", "#131a21"
LINE, LINE2 = "#1a2027", "#2a313b"
INK, BODY, MUTED = "#f5f7fa", "#a3a9b5", "#8a9099"
BLUE, BLUE_D, BLUE_L, BLUE9 = "#0a7efc", "#0666fc", "#4e9cf6", "#0b1a33"
VIOLET, VIOLET2, TEAL, AMBER, GREEN, GREEN9 = "#6c72f0", "#9a5cf0", "#00e0aa", "#f6a800", "#1ecc84", "#0b2a1d"
FONT = "'Bricolage Grotesque',ui-sans-serif,system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
EASE = "cubic-bezier(.2,.7,.2,1)"

# ---- outlined display type (wide heavy grotesque, like Archivo 800 @ 112%)
_TTC = TTCollection("/System/Library/Fonts/Avenir Next.ttc")
FONTS = {"heavy": _TTC.fonts[8], "demi": _TTC.fonts[2], "medium": _TTC.fonts[5]}


def text_path(s, size, x, y, weight="heavy", anchor="start", stretch=1.1, track=-0.035):
    f = FONTS[weight]
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    upm = f["head"].unitsPerEm
    sc = size / upm
    hmtx = f["hmtx"]
    adv = [hmtx[cmap.get(ord(c), "space")][0] * sc * stretch + track * size for c in s]
    width = sum(adv) - track * size
    x0 = x - (width if anchor == "end" else width / 2 if anchor == "middle" else 0)
    pen = SVGPathPen(gs)
    cx = x0
    for c, a in zip(s, adv):
        g = cmap.get(ord(c))
        if g:
            gs[g].draw(TransformPen(pen, (sc * stretch, 0, 0, -sc, cx, y)))
        cx += a
    return pen.getCommands(), width


def T(s, size, x, y, fill=INK, **kw):
    d, _ = text_path(s, size, x, y, **kw)
    return f'<path d="{d}" fill="{fill}"/>'


def width_of(s, size, **kw):
    return text_path(s, size, 0, 0, **kw)[1]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def body(s, size, x, y, fill=BODY, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def svg(h, inner, style="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
            f'<defs>{defs}</defs><style>{style}</style>{inner}</svg>\n')


# ---- icons (24px stroke, lucide-like)
ICONS = {
    "spark": "M12 3l1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2z",
    "bulb": "M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z",
    "wand": "M15 4V2M15 10V8M11 6h2M17 6h2M3 21l12-12M13 7l1 1",
    "send": "M22 2L11 13M22 2l-7 20-4-9-9-4z",
    "chart": "M3 3v18h18M7 15l4-4 3 3 6-7",
    "bot": "M5 8h14v11H5zM12 4v4M9 13h.01M15 13h.01M9 16.5h6M2 13h3M19 13h3",
    "grid": "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z",
    "cal": "M3 5h18v16H3zM3 10h18M8 3v4M16 3v4",
    "check": "M5 12.5l4.5 4.5L19 7",
    "arrow": "M5 12h14M13 6l6 6-6 6",
    "film": "M3 5h18v14H3zM7 5v14M17 5v14M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4",
    "moon": "M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z",
}


def icon(name, x, y, size=22, color=BLUE, sw=1.8):
    s = size / 24
    return (f'<path d="{ICONS[name]}" transform="translate({x},{y}) scale({s})" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>')


def ic_box(name, x, y, color=BLUE, tint=False):
    bg = BLUE9 if tint else BG2
    stroke = "none" if tint else LINE
    return (f'<rect x="{x}" y="{y}" width="46" height="46" rx="13" fill="{bg}" stroke="{stroke}"/>'
            + icon(name, x + 12, y + 12, 22, color))


def glass(x, y, label, ic=None, color=BLUE, h=38, size=14, anim=""):
    w = width_of(label, size, weight="medium", stretch=1.0, track=0) + 28 + (26 if ic else 0)
    out = f'<g {anim}><rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="12" fill="rgba(3,4,5,0.74)" stroke="rgba(245,247,250,0.14)"/>'
    tx = x + 14
    if ic:
        out += icon(ic, x + 13, y + (h - 16) / 2, 16, color)
        tx += 26
    out += body(label, size, tx, y + h / 2 + size * 0.36, INK, 500) + "</g>"
    return out, w


# ================================================================ hero
def hero():
    H = 600
    rnd = random.Random(4)
    palettes = [("#1d3b6e", "#0a7efc"), ("#2b1d52", "#9a5cf0"), ("#0b3a33", "#00e0aa"), ("#4a2a08", "#f6a800"),
                ("#1a2433", "#6c72f0"), ("#3a1430", "#e05c9a"), ("#10261e", "#1ecc84"), ("#22303f", "#4e9cf6")]
    labels = ["Reel 9:16", "Story", "Carousel 4:5", "Ad 1:1", "Post 4:5", "Short 9:16", "Banner 16:9", "Pin 2:3"]
    ratios = [1.25, 1.78, 1.0, 0.56, 1.33, 1.5]
    cols, cw, gap = 7, 158, 14
    x0 = (W - (cols * cw + (cols - 1) * gap)) / 2
    defs = ""
    tiles = ""
    for c in range(cols):
        x = x0 + c * (cw + gap)
        y = 0
        col = ""
        items = []
        while y < 1000:
            r = rnd.choice(ratios)
            h = cw * r
            p = rnd.randrange(len(palettes))
            items.append((y, h, p))
            y += h + gap
        total = y
        for rep in (0, 1):
            for k, (ty, th, p) in enumerate(items):
                gid = f"g{c}_{k}"
                if rep == 0:
                    a, b = palettes[p]
                    ang = rnd.choice([(0, 0, 1, 1), (1, 0, 0, 1), (0, 1, 1, 0)])
                    defs += (f'<linearGradient id="{gid}" x1="{ang[0]}" y1="{ang[1]}" x2="{ang[2]}" y2="{ang[3]}">'
                             f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
                yy = ty + rep * total
                col += f'<rect x="{x:.0f}" y="{yy:.0f}" width="{cw}" height="{th:.0f}" rx="18" fill="url(#{gid})"/>'
                # a soft "light" in each tile so they read as photos
                col += (f'<circle cx="{x + cw * (0.3 + 0.4 * ((k * 37 + c * 11) % 10) / 10):.0f}" cy="{yy + th * 0.35:.0f}" '
                        f'r="{cw * 0.32:.0f}" fill="#fff" opacity=".10"/>')
                col += f'<rect x="{x:.0f}" y="{yy + th * 0.62:.0f}" width="{cw}" height="{th * 0.38:.0f}" rx="18" fill="#030405" opacity=".28"/>'
                lab = labels[(k + c) % len(labels)]
                lw = len(lab) * 6.4 + 18
                col += (f'<rect x="{x + 10:.0f}" y="{yy + th - 34:.0f}" width="{lw:.0f}" height="24" rx="12" fill="rgba(3,4,5,0.72)" stroke="rgba(245,247,250,0.14)"/>'
                        + body(lab, 11.5, x + 19, yy + th - 18, "#c9ced6", 500))
        dur = [78, 90, 70, 84, 80, 96, 74][c]
        dirn = "up" if c % 2 == 0 else "down"
        tiles += f'<g class="{dirn}" style="animation-duration:{dur}s;--h:-{total:.0f}px">{col}</g>'

    pill, pw = glass(0, 0, "Building AI agents for brand marketing", None)
    pill_x = W / 2 - (pw + 16) / 2
    auro_d, auro_w = text_path("auro", 168, W / 2, 288, anchor="middle", stretch=1.12, track=-0.05)
    l1 = "Automate the boring. "
    l2 = "Ship the bold."
    w1, w2 = width_of(l1, 40), width_of(l2, 40)
    lx = W / 2 - (w1 + w2) / 2
    verbs = [("Plan", "bulb"), ("Create", "wand"), ("Publish", "send"), ("Optimize", "chart")]
    vw = [glass(0, 0, v, i)[1] for v, i in verbs]
    vx = W / 2 - (sum(vw) + 12 * 3) / 2
    vhtml = ""
    for k, ((v, i), w) in enumerate(zip(verbs, vw)):
        g, _ = glass(vx, 486, v, i, anim=f'class="rise" style="animation-delay:{1.3 + k * .12:.2f}s"')
        vhtml += g
        vx += w + 12

    style = f"""
    .up{{animation:up linear infinite}} .down{{animation:down linear infinite}}
    @keyframes up{{from{{transform:translateY(0)}}to{{transform:translateY(var(--h))}}}}
    @keyframes down{{from{{transform:translateY(var(--h))}}to{{transform:translateY(0)}}}}
    .orb{{animation:spin 90s linear infinite;transform-origin:600px 312px}}
    .orb path{{stroke-dasharray:1400;stroke-dashoffset:1400;animation:draw 2.6s cubic-bezier(.4,0,.2,1) .2s forwards}}
    @keyframes draw{{to{{stroke-dashoffset:0}}}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    .rise{{opacity:0;animation:rise .9s {EASE} forwards}}
    @keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
    .dot{{animation:blink 1.6s ease-in-out infinite}} @keyframes blink{{50%{{opacity:.3}}}}
    .shine{{animation:shine 6s ease-in-out 1.2s infinite}}
    @keyframes shine{{0%{{transform:translateX(-700px)}}60%,100%{{transform:translateX(700px)}}}}
    """
    defs += f"""
    {defs and ''}
    <radialGradient id="scrim" cx="50%" cy="52%" r="60%"><stop offset="0" stop-color="{BG}" stop-opacity=".97"/>
      <stop offset=".55" stop-color="{BG}" stop-opacity=".9"/><stop offset="1" stop-color="{BG}" stop-opacity=".45"/></radialGradient>
    <linearGradient id="fadeT" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
    <linearGradient id="fadeB" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
    <linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".5" stop-color="{BLUE_L}" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <clipPath id="auroClip"><path d="{auro_d}"/></clipPath>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    """
    inner = f"""
    <g clip-path="url(#card)">
      <rect width="{W}" height="{H}" fill="{BG}"/>
      <g opacity=".9">{tiles}</g>
      <rect width="{W}" height="{H}" fill="url(#scrim)"/>
      <rect width="{W}" height="110" fill="url(#fadeT)"/><rect y="{H - 110}" width="{W}" height="110" fill="url(#fadeB)"/>
      <g class="orb" opacity=".6" fill="none" stroke="{BLUE}" stroke-width="1.1" stroke-linecap="round">
        <path d="M600 12 A300 300 0 1 1 599 12"/>
        <path d="M120 312 A480 210 0 1 1 1080 312" opacity=".7"/>
      </g>
      <g class="rise" style="animation-delay:.2s">
        <rect x="{pill_x:.0f}" y="96" width="{pw + 16:.0f}" height="38" rx="12" fill="rgba(3,4,5,0.74)" stroke="rgba(245,247,250,0.14)"/>
        <circle class="dot" cx="{pill_x + 18:.0f}" cy="115" r="3.5" fill="{BLUE}"/>
        <circle cx="{pill_x + 18:.0f}" cy="115" r="8" fill="{BLUE}" opacity=".18"/>
        {body("Building AI agents for brand marketing", 14, pill_x + 32, 120, INK, 500)}
      </g>
      <g class="rise" style="animation-delay:.45s">
        <path d="{auro_d}" fill="{INK}"/>
        <g clip-path="url(#auroClip)"><rect class="shine" x="{W / 2 - 160:.0f}" y="150" width="320" height="160" fill="url(#sh)"/></g>
      </g>
      <g class="rise" style="animation-delay:.8s">{T(l1, 40, lx, 372)}{T(l2, 40, lx + w1, 372, BLUE)}</g>
      <g class="rise" style="animation-delay:1.05s">
        {body("AI agents that plan, create, publish and optimize creative for brand marketing.", 19, W / 2, 428, BODY, 400, "middle")}
      </g>
      {vhtml}
      <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
    </g>"""
    return svg(H, inner, style, defs)


# ================================================================ marquee
def marquee():
    H = 64
    items = ["Instagram", "Facebook", "LinkedIn", "TikTok", "YouTube", "X", "Pinterest", "Meta Ads", "Google Ads", "Claude", "MCP", "AWS"]
    x, out = 0, ""
    for it in items:
        w = len(it) * 8.6
        out += body(it, 16, x, 38, MUTED, 500) + f'<circle cx="{x + w + 24:.0f}" cy="32" r="2.5" fill="{BLUE}" opacity=".75"/>'
        x += w + 48
    total = x
    style = f".lane{{animation:mq 40s linear infinite}} @keyframes mq{{to{{transform:translateX(-{total:.0f}px)}}}}"
    defs = (f'<linearGradient id="fl" x1="0" x2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG1}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="fr" x1="1" x2="0"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG1}" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>')
    inner = (f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{BG1}"/>'
             f'<g class="lane"><g>{out}</g><g transform="translate({total:.0f})">{out}</g></g>'
             f'<rect width="120" height="{H}" fill="url(#fl)"/><rect x="{W - 120}" width="120" height="{H}" fill="url(#fr)"/>'
             f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{LINE}"/></g>')
    return svg(H, inner, style, defs)


# ================================================================ section heading
def heading(kick, title, blue_tail=""):
    H = 118
    tw = width_of(title, 46)
    inner = (body(kick, 15, 0, 30, BLUE_L, 500)
             + T(title, 46, 0, 88) + (T(blue_tail, 46, tw, 88, BLUE) if blue_tail else ""))
    return svg(H, inner)


# ================================================================ composer (about)
def composer():
    Wc, H = 990, 480
    briefs = ["Plan a month of launch content for 9 channels",
              "Turn one product photo into 40 on-brand ads",
              "Find what is working and shift budget overnight"]
    slot, total = 5.0, 15.0
    pc = lambda s: f"{s / total * 100:.2f}%"
    css, typed = "", ""
    for i, b in enumerate(briefs):
        css += (f"@keyframes b{i}{{0%{{clip-path:inset(0 100% 0 0)}}{pc(1.8)}{{clip-path:inset(0 0 0 0)}}"
                f"{pc(4.4)}{{clip-path:inset(0 0 0 0);opacity:1}}{pc(4.9)}{{opacity:0}}100%{{opacity:0;clip-path:inset(0 100% 0 0)}}}}"
                f".b{i}{{clip-path:inset(0 100% 0 0);animation:b{i} {total}s steps({len(b)}) {i * slot}s infinite}}")
        typed += f'<g class="b{i}">{body(b, 22, 36, 176, INK, 400)}</g>'
    steps = [("Researching audience and trends", 1.2), ("Drafting on-brand creatives", 2.2), ("Scheduling across channels", 3.2)]
    rows = ""
    for k, (s, d) in enumerate(steps):
        y = 330 + k * 44
        css += (f"@keyframes s{k}{{0%,{pc(d)}{{opacity:.25}}{pc(d + .3)},{pc(4.6)}{{opacity:1}}{pc(4.95)},100%{{opacity:.25}}}}"
                f".s{k}{{animation:s{k} 5s infinite}}"
                f"@keyframes k{k}{{0%,{pc(d + .2)}{{opacity:0}}{pc(d + .5)},{pc(4.6)}{{opacity:1}}{pc(4.95)},100%{{opacity:0}}}}"
                f".k{k}{{animation:k{k} 5s infinite}}")
        rows += (f'<g class="s{k}"><rect x="24" y="{y}" width="{Wc - 48}" height="36" rx="10" fill="{BG2}" stroke="{LINE}"/>'
                 + body(s, 14.5, 66, y + 23, INK, 400) + "</g>"
                 + f'<g class="k{k}"><circle cx="46" cy="{y + 18}" r="10" fill="{GREEN9}"/>{icon("check", 39, y + 11, 14, GREEN, 2.2)}'
                 + f'<rect x="{Wc - 106}" y="{y + 8}" width="58" height="20" rx="7" fill="{GREEN9}"/>'
                 + body("Done", 12, Wc - 77, y + 22, GREEN, 500, "middle") + "</g>")
    css = css.replace("5s infinite", f"{slot}s infinite")
    chips = ""
    cx = 24
    for lab, on in [("Brand kit", True), ("Auto-publish", True), ("Approvals", False)]:
        w = len(lab) * 7.6 + 46
        fill, stroke, col = (BLUE9, BLUE, INK) if on else ("none", LINE2, BODY)
        chips += (f'<rect x="{cx}" y="222" width="{w:.0f}" height="40" rx="12" fill="{fill}" stroke="{stroke}"/>'
                  + icon("check" if on else "spark", cx + 13, 234, 15, BLUE_L if on else MUTED, 2)
                  + body(lab, 13.5, cx + 34, 247, col, 500))
        cx += w + 8
    style = css + f""".caret{{animation:bl 1s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
      .btn{{animation:pulse 2.4s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.82}}}}
      .glow{{animation:gl 5s ease-in-out infinite}}@keyframes gl{{50%{{opacity:.9}}}}"""
    inner = f"""
    <rect x="1" y="1" width="{Wc - 2}" height="{H - 2}" rx="20" fill="{BG1}" stroke="{LINE2}"/>
    <rect class="glow" x="1" y="1" width="{Wc - 2}" height="{H - 2}" rx="20" fill="none" stroke="{BLUE_L}" opacity=".35"/>
    <rect x="24" y="24" width="212" height="48" rx="12" fill="{BG2}" stroke="{LINE}"/>
    <rect x="28" y="28" width="100" height="40" rx="9" fill="{BLUE_D}"/>
    {body("Agents", 14.5, 78, 53, "#fff", 500, "middle")}{body("Studio", 14.5, 182, 53, BODY, 500, "middle")}
    {body("night shift · always on", 13.5, Wc - 24, 53, MUTED, 400, "end")}
    {icon("spark", 36, 106, 18, BLUE)}{body("Brief", 13.5, 62, 120, MUTED, 500)}
    {typed}
    {chips}
    <g class="btn"><rect x="{Wc - 184}" y="218" width="160" height="48" rx="12" fill="{BLUE_D}"/>
      {body("Run agent", 15.5, Wc - 120, 248, "#fff", 500, "middle")}{icon("arrow", Wc - 66, 233, 17, "#fff", 2)}</g>
    <line x1="24" y1="298" x2="{Wc - 24}" y2="298" stroke="{LINE}"/>
    {rows}
    """
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wc}" height="{H}" viewBox="0 0 {Wc} {H}">'
            f'<style>{style}</style>{inner}</svg>\n')


# ================================================================ bento
def bento():
    H = 640
    g = 20
    wl, wr = (W - g) * 7 / 12, (W - g) * 5 / 12
    cards = [(0, 0, wl, 310), (wl + g, 0, wr, 310), (0, 330, wr, 310), (wr + g, 330, wl, 310)]
    out = ""

    def card(x, y, w, h, ic, col, title, desc, i):
        return (f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="24" fill="{BG1}" stroke="{LINE}"/>'
                + ic_box(ic, x + 26, y + 26, col, i == 0)
                + body(title, 21, x + 88, y + 46, INK, 500) + body(desc, 15, x + 88, y + 70, BODY))

    out += card(*cards[0], "bot", BLUE, "AI agents that do the work", "Plan, create, publish, optimize. On autopilot.", 0)
    out += card(*cards[1], "film", VIOLET2, "Creative at scale", "One brief in, a whole campaign out.", 1)
    out += card(*cards[2], "send", TEAL, "Publish everywhere", "Every channel, scheduled and live.", 2)
    out += card(*cards[3], "chart", GREEN, "Optimize while you sleep", "Agents read the numbers and act on them.", 3)

    # card 1: agent node flow with moving wires
    x, y, w, h = cards[0]
    nodes = [("Brief", BLUE), ("Plan", VIOLET), ("Create", VIOLET2), ("Ship", TEAL)]
    nw = (w - 52 - 3 * 34) / 4
    for k, (lab, c) in enumerate(nodes):
        nx = x + 26 + k * (nw + 34)
        out += (f'<rect x="{nx:.0f}" y="{y + 130}" width="{nw:.0f}" height="132" rx="16" fill="{BG2}" stroke="{LINE}"/>'
                f'<circle cx="{nx + 22:.0f}" cy="{y + 156}" r="4" fill="{c}"/><circle cx="{nx + 22:.0f}" cy="{y + 156}" r="9" fill="{c}" opacity=".2"/>'
                + body(lab, 15, nx + 38, y + 161, INK, 500))
        for j in range(3):
            ww = nw - 32 - (j * 17 + k * 9) % 34
            out += f'<rect class="bar" style="animation-delay:{k * .4 + j * .15:.2f}s" x="{nx + 16:.0f}" y="{y + 184 + j * 22}" width="{ww:.0f}" height="8" rx="4" fill="{LINE2}"/>'
        if k < 3:
            out += f'<line class="wire" x1="{nx + nw + 4:.0f}" y1="{y + 196}" x2="{nx + nw + 30:.0f}" y2="{y + 196}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="4 6"/>'

    # card 2: creative thumbnails popping in
    x, y, w, h = cards[1]
    pal = [("#1d3b6e", BLUE), ("#2b1d52", VIOLET2), ("#0b3a33", TEAL), ("#4a2a08", AMBER), ("#1a2433", VIOLET), ("#10261e", GREEN)]
    tw = (w - 52 - 2 * 10) / 3
    defs = ""
    for k, (a, b) in enumerate(pal):
        tx = x + 26 + (k % 3) * (tw + 10)
        ty = y + 116 + (k // 3) * 92
        defs += f'<linearGradient id="t{k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
        out += (f'<g class="pop" style="animation-delay:{k * .18:.2f}s;transform-origin:{tx + tw / 2:.0f}px {ty + 41:.0f}px">'
                f'<rect x="{tx:.0f}" y="{ty}" width="{tw:.0f}" height="82" rx="12" fill="url(#t{k})"/>'
                f'<circle cx="{tx + tw * .7:.0f}" cy="{ty + 26}" r="14" fill="#fff" opacity=".18"/></g>')

    # card 3: channels
    x, y, w, h = cards[2]
    chans = [("Instagram", "Reel · 9:16", "Live"), ("LinkedIn", "Carousel · 4:5", "Live"), ("TikTok", "Short · 9:16", "Queued")]
    for k, (n, f, s) in enumerate(chans):
        cy = y + 112 + k * 56
        live = s == "Live"
        out += (f'<g class="slide" style="animation-delay:{k * .25:.2f}s">'
                f'<rect x="{x + 26}" y="{cy}" width="{w - 52:.0f}" height="46" rx="10" fill="{BG2}" stroke="{LINE}"/>'
                + body(n, 14.5, x + 42, cy + 29, INK, 500) + body(f, 12.5, x + 140, cy + 29, MUTED)
                + f'<rect x="{x + w - 100:.0f}" y="{cy + 12}" width="60" height="22" rx="7" fill="{GREEN9 if live else BLUE9}"/>'
                + body(s, 12, x + w - 70, cy + 27, GREEN if live else BLUE_L, 500, "middle") + "</g>")

    # card 4: metrics + sparkline drawing
    x, y, w, h = cards[3]
    mets = [("ROAS", "4.2x", "+18%"), ("CPA", "$12.40", "-23%"), ("CTR", "2.9%", "+0.6")]
    for k, (lab, v, d) in enumerate(mets):
        mx = x + 26 + k * 132
        out += (f'<rect x="{mx}" y="{y + 108}" width="120" height="70" rx="12" fill="{BG2}" stroke="{LINE}"/>'
                + body(lab, 12, mx + 14, y + 130, MUTED) + body(v, 20, mx + 14, y + 158, INK, 600)
                + body(d, 12, mx + 106, y + 130, GREEN, 500, "end"))
    sx, sy, sw, sh = x + 440, y + 104, w - 466, 170
    pts_a = [(0, .78), (.12, .70), (.25, .74), (.38, .55), (.5, .58), (.62, .40), (.75, .44), (.88, .24), (1, .16)]
    pts_b = [(0, .88), (.12, .86), (.25, .80), (.38, .82), (.5, .70), (.62, .72), (.75, .60), (.88, .55), (1, .44)]
    pa = " ".join(f"{'M' if i == 0 else 'L'}{sx + px * sw:.0f} {sy + py * sh:.0f}" for i, (px, py) in enumerate(pts_a))
    pb = " ".join(f"{'M' if i == 0 else 'L'}{sx + px * sw:.0f} {sy + py * sh:.0f}" for i, (px, py) in enumerate(pts_b))
    for gy in range(4):
        out += f'<line x1="{sx}" y1="{sy + gy * sh / 3:.0f}" x2="{sx + sw}" y2="{sy + gy * sh / 3:.0f}" stroke="{LINE}"/>'
    defs += (f'<linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity=".35"/>'
             f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>')
    out += f'<path class="area" d="{pa} L{sx + sw} {sy + sh} L{sx} {sy + sh} Z" fill="url(#ga)"/>'
    out += f'<path class="draw" d="{pb}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    out += f'<path class="draw" d="{pa}" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    out += f'<circle class="ping" cx="{sx + sw}" cy="{sy + pts_a[-1][1] * sh:.0f}" r="5" fill="{BLUE}"/>'
    out += (body("ROAS", 12.5, x + 26, y + 214, BODY) + f'<rect x="{x + 26}" y="{y + 222}" width="14" height="3" rx="2" fill="{BLUE}"/>'
            + body("Spend efficiency", 12.5, x + 80, y + 214, BODY) + f'<rect x="{x + 80}" y="{y + 222}" width="14" height="3" rx="2" fill="{GREEN}"/>')
    out += body("Budget shifted to the top 3 creatives at 02:14", 14, x + 26, y + 272, MUTED)
    out += f'<circle class="dot" cx="{x + 400}" cy="{y + 267}" r="3.5" fill="{BLUE}"/>'

    # spotlight that drifts across the grid (like the card hover glow)
    defs += (f'<radialGradient id="spot"><stop offset="0" stop-color="{BLUE}" stop-opacity=".13"/>'
             f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="cards">' + "".join(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="24"/>' for cx, cy, cw, ch in cards) + "</clipPath>")
    out = f'<g clip-path="url(#cards)"><circle class="spot" cx="0" cy="0" r="420" fill="url(#spot)"/></g>' + out
    style = f"""
    .wire{{animation:flow 1s linear infinite}}@keyframes flow{{to{{stroke-dashoffset:-20}}}}
    .bar{{animation:bar 2.4s ease-in-out infinite}}@keyframes bar{{50%{{fill:#24426e}}}}
    .pop{{animation:pop 6s {EASE} infinite}}
    @keyframes pop{{0%{{opacity:0;transform:scale(.85) translateY(6px)}}12%,85%{{opacity:1;transform:none}}100%{{opacity:0}}}}
    .slide{{animation:sl 6s {EASE} infinite}}
    @keyframes sl{{0%{{opacity:0;transform:translateX(-10px)}}12%,85%{{opacity:1;transform:none}}100%{{opacity:0}}}}
    .draw{{stroke-dasharray:900;stroke-dashoffset:900;animation:dr 6s {EASE} infinite}}
    @keyframes dr{{0%{{stroke-dashoffset:900}}40%,90%{{stroke-dashoffset:0;opacity:1}}100%{{stroke-dashoffset:0;opacity:0}}}}
    .area{{animation:ar 6s ease infinite}}@keyframes ar{{0%,30%{{opacity:0}}50%,90%{{opacity:1}}100%{{opacity:0}}}}
    .ping{{animation:pg 1.6s ease-out infinite;transform-box:fill-box;transform-origin:center}}
    @keyframes pg{{0%{{transform:scale(1);opacity:1}}100%{{transform:scale(2.6);opacity:0}}}}
    .dot{{animation:blink 1.6s ease-in-out infinite}}@keyframes blink{{50%{{opacity:.3}}}}
    .spot{{animation:spot 14s ease-in-out infinite}}
    @keyframes spot{{0%,100%{{transform:translate(200px,160px)}}25%{{transform:translate(950px,140px)}}50%{{transform:translate(1000px,500px)}}75%{{transform:translate(220px,480px)}}}}
    """
    return svg(H, out, style, defs)


# ================================================================ pipeline
def pipeline():
    H = 300
    stages = [("Spark", ("An idea, a product,", "or a goal."), "bulb", "Brief agent"),
              ("Plan", ("Calendar, angles", "and channels."), "cal", "Strategy agent"),
              ("Create", ("Images, video and", "copy, on brand."), "wand", "Studio agent"),
              ("Publish", ("Scheduled, approved", "and live."), "send", "Publishing agent"),
              ("Optimize", ("Budget follows", "what works."), "chart", "Growth agent")]
    gap = 14
    sw = (W - 4 * gap) / 5
    out = (f'<line x1="24" y1="30" x2="{W - 24}" y2="30" stroke="{LINE2}"/>'
           f'<rect class="travel" x="0" y="28" width="90" height="5" rx="2.5" fill="url(#tr)" filter="url(#gl)"/>')
    for k, (t, d, ic, ag) in enumerate(stages):
        x = k * (sw + gap)
        out += (f'<g class="st" style="animation-delay:{k * 1.4:.1f}s">'
                f'<rect x="{x + .5:.1f}" y="60.5" width="{sw - 1:.1f}" height="228" rx="22" fill="{BG1}" stroke="{LINE}"/>'
                f'<rect class="hl" style="animation-delay:{k * 1.4:.1f}s" x="{x + .5:.1f}" y="60.5" width="{sw - 1:.1f}" height="228" rx="22" fill="none" stroke="{BLUE}"/>'
                f'<circle cx="{x + 33:.1f}" cy="93" r="15" fill="{BLUE9}"/>'
                + body(f"0{k + 1}", 13, x + 33, 97.5, BLUE_L, 600, "middle")
                + body(t, 17, x + 58, 99, INK, 500)
                + body(d[0], 14, x + 18, 140, BODY) + body(d[1], 14, x + 18, 161, BODY)
                + f'<rect x="{x + 18:.1f}" y="196" width="{sw - 36:.1f}" height="1" fill="{LINE}"/>'
                + icon(ic, x + 18, 214, 16, BLUE_L) + body(ag, 13, x + 42, 227, BLUE_L, 500)
                + f'<circle cx="{x + 24:.1f}" cy="262" r="3" fill="{GREEN}"/>' + body("running 24/7", 12.5, x + 34, 266, MUTED)
                + "</g>")
    defs = (f'<linearGradient id="tr" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>'
            f'<filter id="gl" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    style = f"""
    .travel{{animation:travel 7s linear infinite}}
    @keyframes travel{{from{{transform:translateX(24px);opacity:0}}8%{{opacity:1}}92%{{opacity:1}}to{{transform:translateX({W - 114}px);opacity:0}}}}
    .hl{{opacity:0;animation:hl 7s ease-in-out infinite}}
    @keyframes hl{{0%,4%{{opacity:0}}10%,18%{{opacity:1}}26%,100%{{opacity:0}}}}
    .st{{animation:lift 7s {EASE} infinite}}
    @keyframes lift{{0%,4%{{transform:none}}10%,18%{{transform:translateY(-4px)}}26%,100%{{transform:none}}}}
    """
    return svg(H, out, style, defs)


# ================================================================ stats
def stats():
    H = 150
    items = [("24/7", "agents on the night shift"), ("9", "channels on autopilot"), ("5", "stages, idea to impact"), ("1", "brief to get started")]
    cw = W / 4
    out = f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="{BG1}" stroke="{LINE}"/>'
    for k, (n, lab) in enumerate(items):
        x = k * cw
        if k:
            out += f'<line x1="{x}" y1="1" x2="{x}" y2="{H - 1}" stroke="{LINE}"/>'
        out += (f'<g class="r" style="animation-delay:{k * .15:.2f}s">' + T(n, 46, x + 32, 82, BLUE_L)
                + body(lab, 15.5, x + 32, 116, BODY) + "</g>")
    style = f".r{{opacity:0;animation:r .9s {EASE} forwards}}@keyframes r{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}"
    return svg(H, out, style)


# ================================================================ CTA banner with the owl
def banner():
    H = 380
    im = Image.open(A / "owl.png").convert("RGB").resize((420, 420), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86)
    b64 = base64.b64encode(buf.getvalue()).decode()
    l1, l2 = "Automate the boring.", "Ship the bold."
    defs = (f'<clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath>'
            f'<linearGradient id="sc" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity=".97"/>'
            f'<stop offset=".45" stop-color="{BG}" stop-opacity=".84"/><stop offset=".8" stop-color="{BG}" stop-opacity=".15"/>'
            f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="fg" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset=".55" stop-color="#000"/>'
            f'<stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>'
            f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#fg)"/></mask>'
            f'<radialGradient id="glow" cx="20%" cy="40%" r="50%"><stop offset="0" stop-color="{BLUE}" stop-opacity=".18"/>'
            f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>')
    pill_w = width_of("Night shift, always on", 13.5, weight="medium", stretch=1.0, track=0) + 30
    inner = f"""
    <g clip-path="url(#c)">
      <rect width="{W}" height="{H}" fill="{BG}"/>
      <g mask="url(#fade)"><image class="kb" href="data:image/jpeg;base64,{b64}" x="{W - 500}" y="-50" width="500" height="500"/></g>
      <rect width="{W}" height="{H}" fill="url(#sc)"/>
      <rect width="{W}" height="{H}" fill="url(#glow)"/>
      <g class="orb" fill="none" stroke="{BLUE}" stroke-width="1" opacity=".45"><path d="M{W - 290} 20 A190 190 0 1 1 {W - 291} 20"/></g>
      <rect x="64" y="70" width="{pill_w:.0f}" height="34" rx="17" fill="rgba(3,4,5,0.5)" stroke="{VIOLET}"/>
      {body("Night shift, always on", 13.5, 79, 92, INK, 500)}
      {T(l1, 52, 64, 178)}{T(l2, 52, 64, 238, BLUE)}
      {body("While the owl keeps watch, the agents keep shipping.", 18, 64, 284, BODY)}
      <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
    </g>"""
    style = (f".kb{{animation:kb 18s ease-in-out infinite alternate;transform-origin:{W - 290}px 190px}}"
             f"@keyframes kb{{to{{transform:scale(1.06) translateX(-8px)}}}}"
             f".orb{{animation:spin 60s linear infinite;transform-origin:{W - 290}px 210px}}@keyframes spin{{to{{transform:rotate(360deg)}}}}")
    return svg(H, inner, style, defs)


if __name__ == "__main__":
    A.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "marquee.svg": marquee(),
        "composer.svg": composer(),
        "bento.svg": bento(),
        "pipeline.svg": pipeline(),
        "stats.svg": stats(),
        "banner.svg": banner(),
        "h-about.svg": heading("01 · About", "Half human, ", "half automation."),
        "h-build.svg": heading("02 · What I build", "Agents that ", "do the work."),
        "h-flow.svg": heading("03 · How it flows", "From idea ", "to impact."),
        "h-stack.svg": heading("04 · Toolbox", "Built with"),
    }
    for name, content in files.items():
        (A / name).write_text(content)
    # remove assets from the previous design
    for old in ["header.svg", "terminal.svg", "focus.svg", "footer.svg", "title-about.svg", "title-focus.svg", "title-stack.svg"]:
        (A / old).unlink(missing_ok=True)
    print("ok:", ", ".join(files))
