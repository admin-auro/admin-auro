"""Procedural snowy owl under an aurora, in Auroscale brand light.

Outputs:
  assets/owl.webp   animated (README)
  assets/owl.png    still frame (profile picture)
Run: python owl.py   (needs pillow + numpy)
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 1024                 # working resolution
OUT = 640                # webp size
FRAMES = 48
MS = 70
rng = np.random.default_rng(11)
A = Path(__file__).parent / "assets"

yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
CX = S / 2

# brand colours (0-1)
BLUE = np.array([10, 126, 252]) / 255
VIOLET = np.array([108, 114, 240]) / 255
VIOLET2 = np.array([154, 92, 240]) / 255
TEAL = np.array([0, 224, 170]) / 255
BG = np.array([3, 4, 5]) / 255
NAVY = np.array([11, 26, 51]) / 255

# ---------------------------------------------------------------- geometry
HEAD = (CX, 420, 258, 205)        # cx, cy, rx, ry
BODY = (CX, 930, 372, 450)
FACE = (CX, 445, 200, 165)        # facial disc
EYES = [(CX - 96, 425), (CX + 96, 425)]
ER = 50                            # iris radius
WINGS = [(CX - 268, 900, 150, 360, 0.16), (CX + 268, 900, 150, 360, -0.16)]  # cx, cy, rx, ry, rot


def ell(c, x=xx, y=yy):
    cx, cy, rx, ry = c[:4]
    if len(c) > 4:
        a = c[4]
        dx, dy = x - cx, y - cy
        x2 = dx * math.cos(a) + dy * math.sin(a)
        y2 = -dx * math.sin(a) + dy * math.cos(a)
        return (x2 / rx) ** 2 + (y2 / ry) ** 2
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2


def smin(a, b, k=7.0):
    return -np.log(np.exp(-k * a) + np.exp(-k * b)) / k


def field(x=xx, y=yy):
    """<1 inside the owl: head and body melted together, no neck."""
    return smin(ell(HEAD, x, y), ell(BODY, x, y), 3.2)


def height():
    return np.sqrt(np.clip(1 - field(), 0, 1))


def blur(a, r):
    """Float Gaussian blur via FFT (no 8-bit banding)."""
    a = np.asarray(a, np.float32)
    f = np.fft.fftfreq(S).astype(np.float32)
    g = np.exp(-2 * (math.pi * r * f) ** 2)
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g[None, :] * g[:, None])).astype(np.float32)


def in_owl(x, y):
    return float(smin(ell(HEAD, x, y), ell(BODY, x, y), 3.2)) < 1


# ---------------------------------------------------------------- feathers
def feather_layers():
    """Returns (mask, detail, spots, wing) float arrays."""
    base = (field() < 1).astype(np.float32)
    m = Image.fromarray((base * 255).astype(np.uint8))
    md = ImageDraw.Draw(m)
    # soft feathered silhouette: short swept tufts along the edge
    edge = np.argwhere((np.abs(field() - 1) < 0.012))
    for k in rng.choice(len(edge), 2600):
        y, x = edge[k]
        nx, ny = x - CX, y - (HEAD[1] if y < 600 else BODY[1])
        a = math.atan2(ny, nx) + 0.35 * np.sign(nx) * (1 if y > 520 else 0.4)
        ln = rng.uniform(4, 13)
        md.line((x - 4 * math.cos(a), y - 4 * math.sin(a), x + ln * math.cos(a), y + ln * math.sin(a)),
                fill=255, width=int(rng.uniform(2, 4)))
    mask = np.asarray(m.filter(ImageFilter.GaussianBlur(1.4))).astype(np.float32) / 255

    # micro feather texture: long soft barbs, low contrast
    d = Image.new("L", (S, S), 128)
    dd = ImageDraw.Draw(d)
    fx, fy = FACE[0], FACE[1] + 25
    pts = 0
    while pts < 30000:
        x, y = rng.uniform(0, S), rng.uniform(150, S)
        if mask[int(y), int(x)] < 0.5:
            continue
        pts += 1
        if ell(FACE, x, y) < 1:
            ang = math.atan2(y - fy, x - fx)
            ln, amp = rng.uniform(8, 16), 26
        elif y < 560:
            ang = math.pi / 2 + (x - CX) / 380 + rng.normal(0, 0.15)
            ln, amp = rng.uniform(12, 22), 30
        else:
            ang = math.pi / 2 + (x - CX) / 900 + rng.normal(0, 0.10)
            ln, amp = rng.uniform(18, 34), 32
        v = int(128 + rng.normal(0, 1) * amp)
        mx, my = x + ln * 0.5 * math.cos(ang), y + ln * 0.5 * math.sin(ang)
        bend = rng.normal(0, 0.18)
        ex, ey = mx + ln * 0.5 * math.cos(ang + bend), my + ln * 0.5 * math.sin(ang + bend)
        dd.line((x, y, mx, my, ex, ey), fill=max(0, min(255, v)), width=2)
    # overlapping feather tips (scallops) on chest and wings
    for row in range(14):
        y = 600 + row * 30
        off = (row % 2) * 22
        for x in np.arange(CX - 420 + off, CX + 420, 44):
            if not in_owl(x, y):
                continue
            jx, jy = x + rng.normal(0, 4), y + rng.normal(0, 3)
            dd.arc((jx - 24, jy - 16, jx + 24, jy + 16), 20, 160, fill=int(rng.uniform(80, 105)), width=2)
            dd.arc((jx - 24, jy - 14, jx + 24, jy + 18), 25, 155, fill=int(rng.uniform(160, 185)), width=1)
    detail = np.asarray(d.filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) / 255 - 0.5

    # wings: folded at the sides
    wing = np.zeros((S, S), np.float32)
    for w in WINGS:
        wing = np.maximum(wing, (ell(w) < 1).astype(np.float32))
    wing = blur(wing, 5) * mask

    # snowy-owl markings: sparse dots on the crown, bars on wings, chevrons low on the chest
    s = Image.new("L", (S, S), 0)
    sd = ImageDraw.Draw(s)
    for _ in range(2600):
        x, y = rng.uniform(0, S), rng.uniform(170, S)
        if mask[int(min(y, S - 1)), int(x)] < 0.9 or ell(FACE, x, y) < 1.3:
            continue
        w_here = max(float(ell(w, x, y) < 1) for w in WINGS)
        if y < HEAD[1] and rng.random() < 0.10:
            r = rng.uniform(1.6, 3.6)
            sd.ellipse((x - r * 1.5, y - r, x + r * 1.5, y + r), fill=int(rng.uniform(110, 200)))
        elif w_here and rng.random() < 0.20:
            w = rng.uniform(10, 24)
            sd.line((x - w, y + 2, x, y - 2, x + w, y + 3), fill=int(rng.uniform(150, 235)), width=int(rng.uniform(4, 8)))
        elif y > 700 and rng.random() < 0.035:
            w = rng.uniform(8, 16)
            sd.line((x - w, y - 2, x, y + 3, x + w, y - 2), fill=int(rng.uniform(110, 190)), width=int(rng.uniform(3, 5)))
    spots = np.asarray(s.filter(ImageFilter.GaussianBlur(1.8))).astype(np.float32) / 255
    return mask, detail, spots, wing


def shade_owl():
    mask, detail, spots, wing = feather_layers()
    z = height()
    # wings stand slightly proud of the body, with a fold groove at their inner edge
    wz = np.zeros_like(z)
    groove = np.zeros_like(z)
    for w in WINGS:
        e = ell(w)
        wz = np.maximum(wz, np.sqrt(np.clip(1 - e, 0, 1)) * 0.12)
        groove = np.maximum(groove, np.exp(-((np.sqrt(e) - 1) / 0.05) ** 2) / (1 + np.exp(-(yy - 600) / 25)))
    zs = blur(z + wz, 5) * 230 + blur(detail, 0.9) * 7.0
    gy, gx = np.gradient(zs)
    n = np.dstack([-gx, -gy, np.ones_like(gx) * 1.0])
    n /= np.linalg.norm(n, axis=2, keepdims=True)

    L = np.array([-0.42, -0.58, 0.70]); L /= np.linalg.norm(L)
    lam = np.clip((n * L).sum(2), 0, 1) ** 0.9
    rim = np.clip(1 - n[..., 2], 0, 1) ** 2.0

    face = np.clip(1.15 - ell(FACE), 0, 1) ** 0.7
    alb = 0.90 + detail * 0.55 * (1 - 0.35 * face)
    ruff = np.exp(-((np.sqrt(ell(FACE)) - 1.03) / 0.05) ** 2) / (1 + np.exp((yy - 570) / 20))
    # heavy brow above each eye: the snowy owl's hooded stare
    brow = sum(np.exp(-(((xx - ex) / 70) ** 2 + ((yy - (ey - 62)) / 22) ** 2)) for ex, ey in EYES)
    alb = alb * (1 - 0.14 * ruff) * (1 - 0.85 * spots) * (1 - 0.06 * wing) * (1 - 0.35 * groove)
    alb = alb[..., None] * np.array([1.0, 0.99, 0.975])

    key = lam[..., None] * np.array([1.0, 1.0, 1.0]) * 1.18
    amb = np.array([0.16, 0.21, 0.36]) * (0.8 - 0.3 * n[..., 1:2])
    side = np.clip((xx - CX) / 330, -1, 1)[..., None]
    rimcol = np.where(side < 0, TEAL * 0.85 + BLUE * 0.35, VIOLET * 0.85 + VIOLET2 * 0.35)
    rim_l = rim[..., None] * rimcol * 1.1 * (0.45 + 0.55 * np.abs(side))
    fall = np.clip(1.35 - (yy - 560) / 560, 0.38, 1)[..., None]
    col = alb * (key + amb) * fall + rim_l
    col *= (1 - 0.22 * brow)[..., None]
    return np.clip(col, 0, 1), mask


def beak(img):
    d = ImageDraw.Draw(img)
    bx, by = CX, 478
    d.polygon([(bx, by - 30), (bx - 21, by - 6), (bx - 13, by + 26), (bx, by + 48), (bx + 13, by + 26), (bx + 21, by - 6)],
              fill=(30, 29, 33))
    d.polygon([(bx - 5, by - 22), (bx - 14, by), (bx - 8, by + 22), (bx - 1, by + 36)], fill=(86, 84, 94))
    d.ellipse((bx - 6, by - 20, bx - 1, by - 12), fill=(150, 150, 160))
    # bristle feathers over the beak base
    for k in range(55):
        a = rng.uniform(-2.6, -0.55)
        sx = bx + rng.normal(0, 14)
        sy = by - 10 + rng.normal(0, 10)
        ln = rng.uniform(12, 26)
        c = int(rng.uniform(170, 235))
        d.line((sx, sy, sx + ln * math.cos(a) * 0.5 * (1 if sx > bx else -1), sy - ln * math.sin(a) * 0.9),
               fill=(c, c, int(c * 1.02)), width=2)


# ---------------------------------------------------------------- eyes
def iris_texture(r):
    n = int(r * 2 + 8)
    y, x = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
    rr = np.sqrt(x ** 2 + y ** 2) / r
    th = np.arctan2(y, x)
    fib = sum(np.sin(th * k + p) * a for k, p, a in
              [(37, 0.3, .35), (61, 1.1, .25), (97, 2.2, .2), (143, .7, .15)])
    base = np.array([1.0, 0.76, 0.06]) * (1 - 0.25 * rr[..., None])               # amber-gold
    base = base + np.array([0.08, 0.05, -0.02]) * fib[..., None] * (rr[..., None] > .5)
    limbal = np.clip((rr - 0.82) / 0.18, 0, 1)[..., None]
    base = base * (1 - 0.75 * limbal)
    return np.clip(base, 0, 1), rr


IRIS, IRR = iris_texture(ER)


def draw_eyes(canvas, t, blink):
    """canvas float HxWx3; t loop phase 0..1; blink 0(open)..1(closed)."""
    out = canvas.copy()
    pup = 0.50 + 0.06 * math.sin(2 * math.pi * t)        # pupil breathing
    n = IRIS.shape[0]
    for ex, ey in EYES:
        x0, y0 = int(ex - n / 2), int(ey - n / 2)
        reg = out[y0:y0 + n, x0:x0 + n]
        # dark socket ring
        ring = np.clip(1 - (IRR - 1.0) / 0.16, 0, 1) * (IRR < 1.16)
        reg *= (1 - 0.88 * ring[..., None] * (IRR >= 0.98)[..., None])
        eye = IRIS.copy()
        pm = np.clip((pup - IRR) / 0.04, 0, 1)[..., None]
        eye = eye * (1 - pm) + np.array([0.01, 0.01, 0.015]) * pm
        # corneal reflections: aurora tint low, sky glint high
        yy_, xx_ = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
        glint = np.exp(-(((xx_ + ER * .32) / (ER * .2)) ** 2 + ((yy_ + ER * .38) / (ER * .13)) ** 2))
        dot = np.exp(-(((xx_ - ER * .28) / (ER * .07)) ** 2 + ((yy_ + ER * .1) / (ER * .07)) ** 2))
        arc = np.exp(-((np.sqrt(xx_ ** 2 + yy_ ** 2) / ER - .78) / .07) ** 2) * (yy_ > ER * .25)
        eye = eye + glint[..., None] * .85 + dot[..., None] * .9 + arc[..., None] * TEAL * .35
        inside = np.clip((1 - IRR) / 0.03, 0, 1)
        # eyelid: comes down from the top, feather coloured
        top = (ey - ER - 4) + (0.24 + 0.76 * blink) * (2 * ER + 8)
        lid = np.clip(((y0 + yy_ + n / 2) - top) / 2.5, 0, 1)        # 1 below lid edge = visible eye
        lid = lid * np.clip(((ey + ER * 0.86) - (y0 + yy_ + n / 2)) / 2.5, 0, 1)   # lower lid
        vis = (inside * lid)[..., None]
        reg[:] = reg * (1 - vis) + np.clip(eye, 0, 1) * vis
        lidmask = (inside * (1 - lid))[..., None]
        reg *= (1 - 0.18 * lidmask)          # lid = brow feathers, slightly shaded
        edge = np.exp(-(((y0 + yy_ + n / 2) - top) / 3.0) ** 2) * np.clip((1.06 - IRR) / 0.06, 0, 1)
        reg *= (1 - 0.92 * edge[..., None])
    return out


# ---------------------------------------------------------------- sky
STARS = rng.uniform(0, 1, (260, 3))
SNOW = rng.uniform(0, 1, (140, 4))


def sky(t):
    u = xx / S
    v = yy / S
    col = BG * (1 - v[..., None]) + NAVY * 0.9 * v[..., None]
    ph = 2 * math.pi * t
    # curtain base line, waving
    base = 0.50 + 0.07 * np.sin(u * 6.0 + ph) + 0.035 * np.sin(u * 13.0 - ph * 2 + 1.3)
    above = base - v
    curtain = np.where(above > 0, np.exp(-above / 0.20), np.exp(above / 0.018))
    rays = 0.74 + 0.26 * sum(a * np.sin(u * f + ph * sp + p) for f, sp, p, a in [(23, 1, .4, .35), (47, -2, 1.9, .25), (89, 3, .7, .18), (151, -1, 2.6, .12), (233, 2, 1.1, .10)])
    inten = curtain * np.clip(rays, 0, 1.2) * (0.6 + 0.4 * np.sin(u * 3.1 + ph))
    hue = np.clip(above / 0.32, 0, 1)[..., None]                  # teal at the hem → blue → violet up high
    c1 = TEAL * (1 - hue) + BLUE * hue
    c2 = BLUE * (1 - hue) + VIOLET2 * hue
    acol = c1 * (1 - hue) + c2 * hue
    col = col + acol * inten[..., None] * 1.25
    # second faint curtain higher up
    b2 = 0.26 + 0.05 * np.sin(u * 4.0 - ph + 2.0)
    a2 = b2 - v
    c2v = np.where(a2 > 0, np.exp(-a2 / 0.12), np.exp(a2 / 0.015)) * (0.5 + 0.5 * np.sin(u * 90 - ph * 2))
    col = col + VIOLET * c2v[..., None] * 0.35
    # stars
    img = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for sx, sy, sp in STARS:
        a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(ph * 2 + sp * 20))
        c = int(255 * a * 0.85)
        r = 1.0 + sp * 1.2
        d.ellipse((sx * S - r, sy * S * 0.7 - r, sx * S + r, sy * S * 0.7 + r), fill=(c, c, min(255, c + 20)))
    return np.asarray(img).astype(np.float32) / 255


def snow(img, t):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for sx, sy, sz, sp in SNOW:
        speed = 1 + int(sp * 2)                      # integer loops per cycle → seamless
        y = ((sy + t * speed) % 1.0) * (S + 40) - 20
        x = sx * S + 14 * math.sin(2 * math.pi * (t * speed + sp))
        r = 1.2 + sz * 3.2
        a = int(110 + 120 * sz)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 242, 255, a))
    lay = lay.filter(ImageFilter.GaussianBlur(1.1))
    return Image.alpha_composite(img.convert("RGBA"), lay)


# ---------------------------------------------------------------- compose
def main():
    print("shading owl…")
    owl, mask = shade_owl()
    owl_img = Image.fromarray((owl * 255).astype(np.uint8))
    beak(owl_img)
    owl = np.asarray(owl_img).astype(np.float32) / 255
    # soft contact shadow / glow behind the owl
    halo = blur(mask, 40)

    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        blink_t = (t - 0.62) / 0.10
        blink = math.sin(math.pi * blink_t) if 0 <= blink_t <= 1 else 0.0
        bg = sky(t)
        bg = bg * (1 - 0.55 * halo[..., None])
        body = draw_eyes(owl, t, blink)
        m = mask[..., None]
        frame = bg * (1 - m) + body * m
        # subtle cinematic vignette + grade
        vig = np.clip(1 - 0.55 * (((xx - CX) / S) ** 2 + ((yy - S * .45) / S) ** 2) * 2.2, 0, 1)
        frame = frame * vig[..., None]
        im = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8))
        im = snow(im, t).convert("RGB")
        frames.append(im.resize((OUT, OUT), Image.LANCZOS))
        print(f"frame {i + 1}/{FRAMES}", end="\r")
    A.mkdir(exist_ok=True)
    frames[0].resize((512, 512), Image.LANCZOS).save(A / "owl.png")
    frames[0].save(A / "owl.webp", save_all=True, append_images=frames[1:], duration=MS, loop=0,
                   quality=82, method=6)
    print("\nwrote assets/owl.webp, assets/owl.png")


if __name__ == "__main__":
    main()
