"""Generates the animated SVGs used by README.md. Run: python3 build_svgs.py"""
from pathlib import Path

A = Path(__file__).parent / "assets"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

DEFS = """
  <linearGradient id="brand" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#00e5c7"/><stop offset=".5" stop-color="#8a6bff"/><stop offset="1" stop-color="#ff5fae"/>
  </linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
"""


def stars(n, w, h, seed=7):
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([0.8, 1.1, 1.5])
        d = rnd.uniform(0, 4)
        out.append(f'<circle class="star" cx="{x:.0f}" cy="{y:.0f}" r="{r}" style="animation-delay:{d:.2f}s"/>')
    return "\n    ".join(out)


# ---------------------------------------------------------------- header
def header():
    W, H = 1200, 340
    phrases = [
        "building autonomous AI agents",
        "automating growth & marketing",
        "shipping serverless on AWS",
        "turning ideas into products",
    ]
    slot, total = 4.0, 4.0 * len(phrases)
    fs, cw = 26, 26 * 0.6
    x0 = W / 2 - (max(len(p) for p in phrases) + 2) * cw / 2
    p = lambda s: f"{s / total * 100:.2f}%"
    css, groups = [], []
    for i, ph in enumerate(phrases):
        n = len(ph)
        css.append(f"""
    @keyframes t{i} {{ 0% {{clip-path:inset(0 100% 0 0)}} {p(1.6)} {{clip-path:inset(0 0 0 0)}}
      {p(3.3)} {{clip-path:inset(0 0 0 0)}} {p(3.8)} {{clip-path:inset(0 100% 0 0)}} 100% {{clip-path:inset(0 100% 0 0)}} }}
    @keyframes c{i} {{ 0% {{transform:translateX(0);opacity:1}} {p(1.6)} {{transform:translateX({n * cw:.1f}px)}}
      {p(3.3)} {{transform:translateX({n * cw:.1f}px)}} {p(3.8)} {{transform:translateX(0);opacity:1}} {p(3.95)} {{opacity:0}} 100% {{opacity:0}} }}
    .t{i} {{ clip-path:inset(0 100% 0 0); animation:t{i} {total}s steps({n}) {i * slot}s infinite }}
    .c{i} {{ opacity:0; animation:c{i} {total}s steps({n}) {i * slot}s infinite }}""")
        groups.append(f"""
    <text class="t{i}" x="{x0 + 2 * cw:.1f}" y="262" font-family="{MONO}" font-size="{fs}" fill="#dfe6ff">{ph}</text>
    <g class="c{i}"><rect class="blink" x="{x0 + 2 * cw + 2:.1f}" y="240" width="3" height="28" fill="#00e5c7"/></g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{DEFS}
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0d22"/><stop offset="1" stop-color="#1b0c33"/></linearGradient>
    <linearGradient id="title" y1="0" y2="0" gradientUnits="userSpaceOnUse" x1="300" x2="900">
      <stop offset="0" stop-color="#00e5c7"><animate attributeName="stop-color" values="#00e5c7;#8a6bff;#ff5fae;#00e5c7" dur="8s" repeatCount="indefinite"/></stop>
      <stop offset=".5" stop-color="#8a6bff"><animate attributeName="stop-color" values="#8a6bff;#ff5fae;#00e5c7;#8a6bff" dur="8s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#ff5fae"><animate attributeName="stop-color" values="#ff5fae;#00e5c7;#8a6bff;#ff5fae" dur="8s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <style>
    .star {{ fill:#fff; animation: tw 4s ease-in-out infinite; }}
    @keyframes tw {{ 0%,100% {{opacity:.15}} 50% {{opacity:.9}} }}
    .blob {{ animation: drift 14s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    .b2 {{ animation-duration: 18s; animation-direction: reverse; }}
    .b3 {{ animation-duration: 22s; }}
    @keyframes drift {{ 0%,100% {{transform:translate(0,0) scale(1)}} 33% {{transform:translate(120px,40px) scale(1.2)}} 66% {{transform:translate(-90px,-30px) scale(.9)}} }}
    .blink {{ animation: bl 1s steps(1) infinite; }}
    @keyframes bl {{ 50% {{opacity:0}} }}
    .rise {{ animation: rise 1.2s cubic-bezier(.2,.8,.2,1) both; }}
    @keyframes rise {{ from {{opacity:0; transform:translateY(18px)}} to {{opacity:1; transform:none}} }}
    .ring {{ animation: spin 30s linear infinite; transform-origin: 600px 170px; }}
    @keyframes spin {{ to {{ transform: rotate(360deg) }} }}
    {''.join(css)}
  </style>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <g filter="url(#blur)" opacity=".75">
      <circle class="blob" cx="250" cy="120" r="140" fill="#00e5c7" opacity=".55"/>
      <circle class="blob b2" cx="950" cy="230" r="160" fill="#ff5fae" opacity=".45"/>
      <circle class="blob b3" cx="620" cy="60" r="130" fill="#8a6bff" opacity=".6"/>
    </g>
    {stars(70, W, H)}
    <g class="ring" opacity=".25" fill="none" stroke="url(#brand)">
      <ellipse cx="600" cy="170" rx="470" ry="150" stroke-width="1.2" stroke-dasharray="4 10"/>
    </g>
    <g class="rise">
      <text x="600" y="168" text-anchor="middle" font-family="{SANS}" font-weight="800" font-size="118" letter-spacing="-4" fill="url(#title)" filter="url(#glow)">auro</text>
      <text x="600" y="206" text-anchor="middle" font-family="{MONO}" font-size="15" letter-spacing="6" fill="#9aa3c7">BUILDER · AUTOMATOR · SHIPPER</text>
    </g>
    <text x="{x0:.1f}" y="262" font-family="{MONO}" font-size="{fs}" fill="#ff5fae">&gt;</text>
    {''.join(groups)}
    <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="url(#brand)" stroke-opacity=".5" stroke-width="2"/>
  </g>
</svg>
"""


# ---------------------------------------------------------------- terminal
def terminal():
    W = 1200
    lines = [
        ("p", "whoami"),
        ("o", "auro — I build AI agents, automations & growth engines"),
        ("p", "cat focus.txt"),
        ("a", "▸ Autonomous AI agents that do real work — LLMs, MCP, tool use"),
        ("a", "▸ Growth engineering: ads, SEO & analytics on autopilot"),
        ("a", "▸ Cloud-native backends on AWS, serverless first"),
        ("a", "▸ Generative video & motion pipelines"),
        ("p", "echo $MOTTO"),
        ("m", '"Automate the boring. Ship the bold."'),
    ]
    top, lh = 92, 34
    H = top + lh * (len(lines) + 1) + 10
    cycle = 16
    body, css = [], []
    for i, (kind, txt) in enumerate(lines):
        y = top + i * lh
        start = 0.3 + i * 0.9
        pc = lambda s: f"{s / cycle * 100:.2f}%"
        css.append(f"@keyframes l{i} {{ 0%,{pc(start)} {{opacity:0;transform:translateX(-8px)}} "
                   f"{pc(start + .35)},{pc(cycle - 1.2)} {{opacity:1;transform:none}} {pc(cycle - .6)},100% {{opacity:0}} }}"
                   f" .l{i} {{ animation: l{i} {cycle}s ease-out infinite; }}")
        if kind == "p":
            content = (f'<tspan fill="#00e5c7">~</tspan><tspan fill="#8a6bff"> ❯ </tspan>'
                       f'<tspan fill="#eef1ff">{txt}</tspan>')
        else:
            col = {"o": "#c9d1f5", "a": "#9fe9dc", "m": "#ffb3d6"}[kind]
            content = f'<tspan fill="{col}">{txt}</tspan>'
        body.append(f'<text class="l{i}" x="44" y="{y}" font-family="{MONO}" font-size="19">{content}</text>')
    yc = top + len(lines) * lh
    pcs = lambda s: f"{s / cycle * 100:.2f}%"
    s_last = 0.3 + len(lines) * 0.9
    css.append(f"@keyframes lc {{ 0%,{pcs(s_last)} {{opacity:0}} {pcs(s_last + .3)},{pcs(cycle - 1.2)} {{opacity:1}} {pcs(cycle - .6)},100% {{opacity:0}} }}"
               f" .lc {{ animation: lc {cycle}s infinite; }}")
    body.append(f'<g class="lc"><text x="44" y="{yc}" font-family="{MONO}" font-size="19">'
                f'<tspan fill="#00e5c7">~</tspan><tspan fill="#8a6bff"> ❯ </tspan></text>'
                f'<rect class="blink" x="88" y="{yc - 17}" width="11" height="22" fill="#00e5c7"/></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{DEFS}</defs>
  <style>
    .blink {{ animation: bl 1s steps(1) infinite; }}
    @keyframes bl {{ 50% {{opacity:0}} }}
    .scan {{ animation: scan 6s linear infinite; }}
    @keyframes scan {{ from {{transform:translateY(-60px)}} to {{transform:translateY({H}px)}} }}
    {' '.join(css)}
  </style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="#0d1024" stroke="url(#brand)" stroke-opacity=".55" stroke-width="2"/>
  <path d="M1 17 a16 16 0 0 1 16 -16 H{W - 17} a16 16 0 0 1 16 16 V46 H1 Z" fill="#151936"/>
  <circle cx="30" cy="24" r="7" fill="#ff5f57"/><circle cx="54" cy="24" r="7" fill="#febc2e"/><circle cx="78" cy="24" r="7" fill="#28c840"/>
  <text x="{W / 2}" y="29" text-anchor="middle" font-family="{MONO}" font-size="14" fill="#7d86b0">auro@github: ~</text>
  <rect class="scan" x="2" y="0" width="{W - 4}" height="60" fill="url(#brand)" opacity=".035"/>
  {''.join(body)}
</svg>
"""


# ---------------------------------------------------------------- focus cards
def cards():
    W, H = 1200, 250
    items = [
        ("🤖", "AI Agents", "LLM agents with real tools", "#00e5c7"),
        ("📈", "Growth Engines", "Ads, SEO & funnels on autopilot", "#8a6bff"),
        ("☁️", "Cloud Native", "Serverless, scalable, on AWS", "#ff9d5c"),
        ("🎬", "Gen Media", "AI video & motion pipelines", "#ff5fae"),
    ]
    gap, cw = 24, (W - 3 * 24) / 4
    out = []
    for i, (ico, title, sub, col) in enumerate(items):
        x = i * (cw + gap)
        d = i * 0.25
        out.append(f"""
  <g class="card" style="animation-delay:{d}s">
    <rect x="{x + 1:.1f}" y="21" width="{cw - 2:.1f}" height="208" rx="18" fill="#0f1230"/>
    <rect x="{x + 1:.1f}" y="21" width="{cw - 2:.1f}" height="208" rx="18" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="120 600" class="trace" style="animation-delay:{i * .7}s"/>
    <rect x="{x + 1:.1f}" y="21" width="{cw - 2:.1f}" height="208" rx="18" fill="none" stroke="{col}" stroke-opacity=".22" stroke-width="1.5"/>
    <circle cx="{x + cw / 2:.1f}" cy="88" r="36" fill="{col}" opacity=".14" class="pulse" style="animation-delay:{i * .5}s"/>
    <text x="{x + cw / 2:.1f}" y="102" text-anchor="middle" font-size="40" class="bob" style="animation-delay:{i * .4}s">{ico}</text>
    <text x="{x + cw / 2:.1f}" y="164" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="22" fill="#eef1ff">{title}</text>
    <text x="{x + cw / 2:.1f}" y="194" text-anchor="middle" font-family="{SANS}" font-size="15" fill="#9aa3c7">{sub}</text>
  </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    .card {{ animation: up 1s cubic-bezier(.2,.8,.2,1) both; }}
    @keyframes up {{ from {{opacity:0; transform:translateY(20px)}} to {{opacity:1; transform:none}} }}
    .trace {{ animation: trace 5s linear infinite; }}
    @keyframes trace {{ to {{ stroke-dashoffset: -720 }} }}
    .pulse {{ animation: pulse 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes pulse {{ 0%,100% {{transform:scale(.85);opacity:.10}} 50% {{transform:scale(1.15);opacity:.25}} }}
    .bob {{ animation: bob 3s ease-in-out infinite; }}
    @keyframes bob {{ 0%,100% {{transform:translateY(0)}} 50% {{transform:translateY(-7px)}} }}
  </style>
  {''.join(out)}
</svg>
"""


# ---------------------------------------------------------------- section title & footer
def divider(label, name):
    W, H = 1200, 70
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{DEFS}</defs>
  <style>
    .sweep {{ animation: sw 4s ease-in-out infinite; }}
    @keyframes sw {{ 0% {{transform:translateX(-300px)}} 100% {{transform:translateX({W}px)}} }}
  </style>
  <text x="0" y="40" font-family="{SANS}" font-weight="800" font-size="30" fill="url(#brand)">{label}</text>
  <rect x="0" y="58" width="{W}" height="2" rx="1" fill="#2a2f55"/>
  <rect class="sweep" x="0" y="57" width="260" height="4" rx="2" fill="url(#brand)"/>
</svg>
"""


def footer():
    W, H = 1200, 150
    wave = lambda a, o: (f"M0 {o} " + " ".join(f"Q {150 + 300 * k} {o - a if k % 2 == 0 else o + a} {300 * (k + 1)} {o}" for k in range(8))
                         + f" V{H} H0 Z")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{DEFS}<clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>
  <style>
    .w1 {{ animation: mv 9s linear infinite; }} .w2 {{ animation: mv 6s linear infinite reverse; }}
    @keyframes mv {{ to {{ transform: translateX(-600px) }} }}
  </style>
  <g clip-path="url(#c)">
    <path class="w1" d="{wave(22, 70)}" fill="url(#brand)" opacity=".35"/>
    <path class="w2" d="{wave(16, 90)}" fill="url(#brand)" opacity=".6"/>
    <text x="{W / 2}" y="132" text-anchor="middle" font-family="{MONO}" font-size="16" fill="#ffffff" opacity=".9">thanks for dropping by · automate the boring, ship the bold ✦</text>
  </g>
</svg>
"""


if __name__ == "__main__":
    A.mkdir(exist_ok=True)
    esc = lambda s: s.replace(" & ", " &amp; ")  # only bare ampersands in copy text
    (A / "header.svg").write_text(esc(header()))
    (A / "terminal.svg").write_text(esc(terminal()))
    (A / "focus.svg").write_text(esc(cards()))
    (A / "footer.svg").write_text(footer())
    (A / "title-about.svg").write_text(divider("⚡ About me", "about"))
    (A / "title-focus.svg").write_text(divider("🚀 What I work on", "focus"))
    (A / "title-stack.svg").write_text(divider("🧰 Toolbox", "stack"))
    print("ok")
