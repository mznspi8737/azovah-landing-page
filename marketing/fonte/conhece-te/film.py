# AZOVAH · "Conhece-te a ti mesmo" — Reels cinematográfico 1080x1920 (procedural)
import math, random, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W, H, FPS = 1080, 1920, 30
FD = '/home/claude/film/fonts/'
OUT = '/home/claude/film/out'; os.makedirs(OUT, exist_ok=True)
def F(n, s): return ImageFont.truetype(FD + n, s)
def INTER(w, s): return ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-%s.otf' % w, s)
def eo(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def eio(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
rng = np.random.default_rng(5)

# ---------- texto com alpha + brilho ----------
def text_layer(lines, y0, alpha=1.0, rise=0.0, glow=True, color=(255, 246, 228), center=True):
    """lines: [(texto, fonte, cor opcional)]; devolve camada RGBA"""
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L); y = y0 + rise
    for item in lines:
        txt, f = item[0], item[1]; col = item[2] if len(item) > 2 else color; gap = item[3] if len(item) > 3 else 1.12
        w = d.textlength(txt, font=f); x = (W - w) / 2
        d.text((x, y), txt, font=f, fill=col + (255,)); y += f.size * gap
    if alpha < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * alpha)))
    if glow:
        g = L.filter(ImageFilter.GaussianBlur(14)); g.putalpha(g.getchannel('A').point(lambda v: int(v * .55)))
        base = Image.new('RGBA', (W, H)); base.alpha_composite(g); base.alpha_composite(L); return base
    return L

# ---------- fundos pré-calculados ----------
def nebula(c1, c2, c3, seed):
    r = np.random.default_rng(seed); w, h = 270, 480
    yy = np.linspace(0, 1, h)[:, None]; base = np.zeros((h, w, 3))
    for i in range(3): base[..., i] = c1[i] * (1 - yy) + c2[i] * yy
    img = Image.fromarray(base.clip(0, 255).astype('uint8')).convert('RGBA')
    blob = Image.new('RGBA', (w, h)); bd = ImageDraw.Draw(blob)
    for _ in range(22):
        x, y, rr = r.uniform(0, w), r.uniform(0, h), r.uniform(25, 90)
        col = c3 if r.random() < .5 else tuple(int(v * .8) for v in c2)
        bd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (int(r.uniform(20, 60)),))
    blob = blob.filter(ImageFilter.GaussianBlur(28)); img.alpha_composite(blob)
    st = Image.new('RGBA', (w * 4, h * 4)); sd = ImageDraw.Draw(st)
    big = img.resize((w * 4, h * 4), Image.BICUBIC)
    for _ in range(700):
        x, y = r.uniform(0, w * 4), r.uniform(0, h * 4); s = r.choice([.6, 1, 1, 1.6, 2.2])
        sd.ellipse([x - s, y - s, x + s, y + s], fill=(255, 245, 230, int(r.uniform(60, 220))))
    big.alpha_composite(st); return big.convert('RGB')  # 1080x1920
BG_NIGHT = nebula((10, 8, 30), (34, 14, 52), (200, 140, 60), 1)
BG_DEEP = nebula((6, 14, 32), (30, 10, 46), (90, 60, 190), 2)
BG_WINE = nebula((40, 6, 24), (14, 2, 12), (220, 120, 90), 3)
# fundo claro lilás (cena do cartão)
def lilac():
    w, h = 270, 480; yy = np.linspace(0, 1, h)[:, None]; a = np.zeros((h, w, 3))
    top, mid, bot = np.array([238, 226, 248]), np.array([196, 176, 232]), np.array([150, 118, 206])
    for i in range(3): a[..., i] = np.where(yy < .55, top[i] * (1 - yy / .55) + mid[i] * (yy / .55), mid[i] * (1 - (yy - .55) / .45) + bot[i] * ((yy - .55) / .45))
    im = Image.fromarray(a.astype('uint8')).convert('RGBA'); b = Image.new('RGBA', (w, h)); bd = ImageDraw.Draw(b)
    for x, y, rr, c in [(40, 90, 90, (255, 255, 255, 90)), (230, 300, 110, (255, 210, 235, 70)), (120, 420, 120, (120, 90, 200, 80))]: bd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)
    im.alpha_composite(b.filter(ImageFilter.GaussianBlur(30))); return im.resize((W, H), Image.BICUBIC).convert('RGB')
BG_LILAC = lilac()

def kenburns(bg, t, dur, z0=1.0, z1=1.12, dy=0):
    z = z0 + (z1 - z0) * eio(t / dur); w, h = int(W / z), int(H / z)
    x = (W - w) // 2; y = int((H - h) / 2 + dy * eio(t / dur)); y = max(0, min(H - h, y))
    return bg.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)

def vignette():
    v = Image.new('L', (W, H), 0); d = ImageDraw.Draw(v)
    for i in range(40):
        k = i / 40; d.ellipse([-W * .45 + k * W * .35, -H * .3 + k * H * .25, W * 1.45 - k * W * .35, H * 1.3 - k * H * .25], fill=int(255 * k))
    return v.filter(ImageFilter.GaussianBlur(60))
VIG = vignette()
def finish(im, dark=True):
    if dark: im = Image.composite(im, Image.new('RGB', (W, H), (0, 0, 0)), VIG)
    return im

# ---------- partículas douradas (bokeh) ----------
def sprite(r, col):
    s = int(r * 4); im = Image.new('RGBA', (s, s)); d = ImageDraw.Draw(im)
    d.ellipse([s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r], fill=col + (255,))
    return im.filter(ImageFilter.GaussianBlur(r * .6))
SPR = [sprite(r, (255, 214, 140)) for r in (2, 3, 5, 8, 14)]
PARTS = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), v=rng.uniform(20, 90), k=int(rng.integers(0, 5)), ph=rng.uniform(0, 6.28), a=rng.uniform(.25, .9)) for _ in range(90)]
def particles(im, t, amt=1.0, up=True):
    L = Image.new('RGBA', (W, H))
    for p in PARTS[:int(90 * amt)]:
        y = (p['y'] - (p['v'] * t if up else -p['v'] * t)) % (H + 100) - 50; x = p['x'] + 18 * math.sin(t * .7 + p['ph'])
        s = SPR[p['k']]; a = p['a'] * (.6 + .4 * math.sin(t * 2 + p['ph']))
        if a <= 0: continue
        s2 = s.copy(); s2.putalpha(s2.getchannel('A').point(lambda v, a=a: int(v * a)))
        L.alpha_composite(s2, (int(x - s.width / 2), int(y - s.height / 2)))
    return Image.alpha_composite(im.convert('RGBA'), L)

def glow_orb(im, cx, cy, R, col, a):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    for i in range(30, 0, -1):
        k = i / 30; d.ellipse([cx - R * k, cy - R * k, cx + R * k, cy + R * k], fill=col + (int(a * 255 * (1 - k) ** 1.6 / 3),))
    return Image.alpha_composite(im.convert('RGBA'), L.filter(ImageFilter.GaussianBlur(R * .08)))

def rays(im, cx, cy, t, a, col=(255, 220, 150)):
    L = Image.new('RGBA', (W // 2, H // 2)); d = ImageDraw.Draw(L)
    for i in range(18):
        ang = math.radians(i * 20 + t * 6); w = .05 + .03 * math.sin(i * 1.7)
        d.polygon([(cx / 2, cy / 2), (cx / 2 + 1500 * math.cos(ang - w), cy / 2 + 1500 * math.sin(ang - w)), (cx / 2 + 1500 * math.cos(ang + w), cy / 2 + 1500 * math.sin(ang + w))], fill=col + (int(a * (16 + 10 * math.sin(i))),))
    L = L.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    return Image.alpha_composite(im.convert('RGBA'), L)

def golden(draw_fn, t):
    """desenha linhas douradas finas com brilho"""
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L); draw_fn(d, t)
    g = L.filter(ImageFilter.GaussianBlur(9)); out = Image.new('RGBA', (W, H)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(L); return out

GOLD = (236, 196, 120)
def reveal(t, st, dur=.9): return eo((t - st) / dur)

# ======================= CENAS =======================
def c1(t):  # prosperidade / autoconhecimento
    im = kenburns(BG_NIGHT, t, 5.5, 1.0, 1.1); im = rays(im, W / 2, 780, t, eo(t / 1.5))
    im = glow_orb(im, W / 2, 780, 520 + 30 * math.sin(t * 1.5), (255, 196, 120), .9 * eo(t / 1.2))
    # livro de luz: duas páginas
    def book(d, t):
        a = int(255 * eo(t / 1.3)); cx, cy = W / 2, 860; op = eo(t / 2.2)
        for s in (-1, 1):
            d.polygon([(cx, cy), (cx + s * 230 * op, cy - 70 - 30 * op), (cx + s * 240 * op, cy + 90), (cx, cy + 130)], outline=GOLD + (a,), width=3)
            for k in range(5): yk = cy - 20 + k * 26; d.line([(cx + s * 30, yk + 10), (cx + s * (60 + 150 * op), yk - 22 * op + 10)], fill=GOLD + (int(a * .5),), width=2)
    im.alpha_composite(golden(book, t)); im = particles(im, t, eo(t / 1.5))
    im.alpha_composite(text_layer([('A verdadeira prosperidade', F('Corm600i.ttf', 64), (255, 214, 160))], 1150, reveal(t, .6), 30 * (1 - reveal(t, .6))))
    im.alpha_composite(text_layer([('começa pelo', F('Corm500.ttf', 112)), ('autoconhecimento.', F('Corm500.ttf', 112))], 1240, reveal(t, 1.5), 30 * (1 - reveal(t, 1.5))))
    return finish(im.convert('RGB'))

def flower(d, t, cx, cy, R, prog, rot):
    pts = [(0, 0)] + [(R * math.cos(math.radians(60 * i + rot)), R * math.sin(math.radians(60 * i + rot))) for i in range(6)]
    pts += [(2 * R * math.cos(math.radians(60 * i + rot)), 2 * R * math.sin(math.radians(60 * i + rot))) for i in range(6)]
    pts += [(R * math.sqrt(3) * math.cos(math.radians(60 * i + 30 + rot)), R * math.sqrt(3) * math.sin(math.radians(60 * i + 30 + rot))) for i in range(6)]
    n = len(pts); k = prog * n
    for i, (x, y) in enumerate(pts):
        f = max(0, min(1, k - i))
        if f <= 0: continue
        d.arc([cx + x - R, cy + y - R, cx + x + R, cy + y + R], 0, 360 * f, fill=GOLD + (int(220 * min(1, f + .2)),), width=3)
    if prog > .7:
        a = int(255 * eo((prog - .7) / .3)); d.ellipse([cx - 3 * R, cy - 3 * R, cx + 3 * R, cy + 3 * R], outline=GOLD + (a,), width=3)

def c2(t):  # conhece-te a ti mesmo
    im = kenburns(BG_DEEP, t, 5.5, 1.08, 1.0)
    im = glow_orb(im, W / 2, 800, 600, (150, 120, 255), .7)
    im.alpha_composite(golden(lambda d, t: flower(d, t, W / 2, 800, 120, eo(t / 3.4), t * 6), t)); im = particles(im, t + 7, .7)
    im.alpha_composite(text_layer([('Conhece-te', F('Corm500.ttf', 132)), ('a ti mesmo.', F('Corm600i.ttf', 120), (255, 214, 160))], 1270, reveal(t, 1.0), 30 * (1 - reveal(t, 1.0))))
    return finish(im.convert('RGB'))

def c3(t):  # números 1..9 em círculo
    im = kenburns(BG_NIGHT, t + 3, 5.5, 1.05, 1.15); im = glow_orb(im, W / 2, 820, 480, (255, 180, 110), .6)
    cx, cy, R = W / 2, 820, 330
    def draw(d, t):
        for i in range(9):
            a = math.radians(-90 + 40 * i + t * 8); x, y = cx + R * math.cos(a), cy + R * math.sin(a)
            p = eo((t - i * .18) / .6)
            if p <= 0: continue
            d.ellipse([x - 52, y - 52, x + 52, y + 52], outline=GOLD + (int(230 * p),), width=3)
            d.text((x, y + 2), str(i + 1), font=F('Corm700.ttf', 72), fill=(255, 236, 200, int(255 * p)), anchor='mm')
        q = eo((t - 1.8) / 1.6)
        if q > 0:
            order = [0, 3, 6, 0, 1, 4, 7, 1, 2, 5, 8, 2]
            for j in range(len(order) - 1):
                f = max(0, min(1, q * (len(order) - 1) - j))
                if f <= 0: continue
                a1, a2 = [math.radians(-90 + 40 * k + t * 8) for k in (order[j], order[j + 1])]
                x1, y1, x2, y2 = cx + (R - 52) * math.cos(a1), cy + (R - 52) * math.sin(a1), cx + (R - 52) * math.cos(a2), cy + (R - 52) * math.sin(a2)
                d.line([(x1, y1), (x1 + (x2 - x1) * f, y1 + (y2 - y1) * f)], fill=GOLD + (150,), width=2)
    im.alpha_composite(golden(draw, t)); im = particles(im, t + 14, .6)
    im.alpha_composite(text_layer([('Seu nome e sua data guardam', F('Corm600i.ttf', 66), (255, 214, 160)), ('a chave do', F('Corm500.ttf', 112)), ('seu propósito.', F('Corm500.ttf', 112))], 1270, reveal(t, .9), 30 * (1 - reveal(t, .9))))
    return finish(im.convert('RGB'))

TRI = [[5, 5, 3, 5, 5, 1], [1, 8, 8, 1, 6], [9, 7, 9, 7], [7, 7, 7], [5, 5], [1]]
def c4(t):  # triângulo como constelação
    im = kenburns(BG_WINE, t, 5.5, 1.0, 1.1, -60); im = glow_orb(im, W / 2, 760, 520, (255, 140, 120), .55)
    def draw(d, t):
        cs, gap = 120, 22
        for r, row in enumerate(TRI):
            for k, v in enumerate(row):
                p = eo((t - r * .35 - k * .07) / .5)
                if p <= 0: continue
                x = W / 2 - (len(row) * cs + (len(row) - 1) * gap) / 2 + k * (cs + gap) + cs / 2; y = 360 + r * 128
                seq = r == 3 and t > 3.0
                col = (255, 120, 140) if seq else GOLD
                d.ellipse([x - 46, y - 46, x + 46, y + 46], outline=col + (int(230 * p),), width=4 if seq else 3)
                d.text((x, y + 2), str(v), font=F('Corm700.ttf', 66), fill=(255, 240, 220, int(255 * p)), anchor='mm')
                if r and p > .5:
                    for dk in (0, 1):
                        px = W / 2 - (len(TRI[r - 1]) * cs + (len(TRI[r - 1]) - 1) * gap) / 2 + (k + dk) * (cs + gap) + cs / 2
                        d.line([(px, y - 128 + 46), (x, y - 46)], fill=GOLD + (70,), width=2)
    im.alpha_composite(golden(draw, t)); im = particles(im, t + 21, .6)
    im.alpha_composite(text_layer([('Sem alinhamento interno,', F('Corm600i.ttf', 70), (255, 214, 160)), ('nenhuma conquista', F('Corm500.ttf', 108)), ('se sustenta.', F('Corm500.ttf', 108))], 1250, reveal(t, .9), 30 * (1 - reveal(t, .9))))
    return finish(im.convert('RGB'))

def c5(t):  # Mapa Numerológico
    im = kenburns(BG_NIGHT, t + 6, 4.5, 1.15, 1.0); im = rays(im, W / 2, 900, t * 2, 1.0); im = glow_orb(im, W / 2, 900, 640, (255, 200, 130), .8)
    im = particles(im, t + 28, 1.0)
    a = reveal(t, .3, 1.2); L = text_layer([('O seu', F('Corm600i.ttf', 80), (255, 214, 160)), ('Mapa', F('Corm500.ttf', 190)), ('Numerológico', F('Corm500.ttf', 150))], 640, a, 20 * (1 - a))
    # brilho passando pelas letras
    sh = (t - 1.6) / 1.2
    if 0 < sh < 1:
        band = Image.new('L', (W, H)); bd = ImageDraw.Draw(band); x = -300 + sh * (W + 600)
        bd.polygon([(x, 0), (x + 120, 0), (x - 200, H), (x - 320, H)], fill=255); band = band.filter(ImageFilter.GaussianBlur(30))
        m = ImageChops.multiply(band, L.getchannel('A')); L = Image.composite(Image.new('RGBA', (W, H), (255, 255, 255, 255)), L, m)
    im.alpha_composite(L)
    b = reveal(t, 1.4); im.alpha_composite(text_layer([('A Z O V A H', F('Cinzel600.ttf', 46), GOLD)], 1240, b * .9, 0, glow=False))
    return finish(im.convert('RGB'))

ITENS = [('Destino e Missão', 'O caminho que você veio cumprir'), ('Bloqueios e como superá-los', 'Sequências e lições do seu nome'), ('Ciclos e dívidas cármicas', 'O que se repete e por quê'), ('Arcano atual e próximos anos', 'A energia que rege a sua fase'), ('Assinatura com arcanos favoráveis', 'Equilíbrio direto no seu nome')]
def c6(t):  # cartão checklist (claro)
    im = kenburns(BG_LILAC, t, 9, 1.0, 1.06).convert('RGBA')
    a = eo(t / .6); cw, ch = 860, 640; x0, y0 = (W - cw) / 2, 300 + 30 * (1 - a)
    card = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([x0, y0 + 18, x0 + cw, y0 + ch + 18], 44, fill=(80, 50, 140, int(60 * a)))
    card = card.filter(ImageFilter.GaussianBlur(24)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], 44, fill=(255, 255, 255, int(205 * a)), outline=(255, 255, 255, int(255 * a)), width=2)
    d.text((W / 2, y0 + 70), 'No seu mapa AZOVAH:', font=F('Corm600i.ttf', 60), fill=(80, 50, 120, int(255 * a)), anchor='mm')
    step = 1.6; cur = min(len(ITENS) - 1, int(max(0, t - .5) / step))
    for i, (tit, _) in enumerate(ITENS):
        p = eo((t - .5 - i * step) / .5)
        if p <= 0: continue
        y = y0 + 150 + i * 96
        d.ellipse([x0 + 50, y - 26, x0 + 102, y + 26], fill=(214, 168, 72, int(255 * p)))
        d.line([(x0 + 63, y + 1), (x0 + 74, y + 12), (x0 + 91, y - 10)], fill=(255, 255, 255, int(255 * p)), width=6)
        d.text((x0 + 130 + 20 * (1 - p), y), tit, font=INTER('SemiBold', 38), fill=(58, 36, 90, int(255 * p)), anchor='lm')
    im.alpha_composite(card)
    # texto grande abaixo, troca a cada item
    k = cur; lt = (t - .5 - k * step)
    if t > .5:
        fa = eo(lt / .5) * (1 - eo((lt - step + .35) / .35)) if k < len(ITENS) - 1 else eo(lt / .5)
        tit, sub = ITENS[k]
        words = tit.split(' '); l1, l2 = (' '.join(words[:2]), ' '.join(words[2:])) if len(words) > 3 else (tit, '')
        lines = [(sub, F('Corm600i.ttf', 58), (110, 70, 160))] + [(l1, F('Corm500.ttf', 104), (60, 30, 96))] + ([(l2, F('Corm500.ttf', 104), (60, 30, 96))] if l2 else [])
        im.alpha_composite(text_layer(lines, 1110, fa, 24 * (1 - fa), glow=False))
    return im.convert('RGB')

SHOT = Image.open('/home/claude/repo/azovah-landing-page/site/assets/shot_inicio_m.webp').convert('RGB')
def phone(h):
    w = int(h * 780 / 1688); sc = SHOT.resize((w, h), Image.LANCZOS); pad = 16
    ph = Image.new('RGBA', (w + 2 * pad, h + 2 * pad)); pd = ImageDraw.Draw(ph); pd.rounded_rectangle([0, 0, w + 2 * pad - 1, h + 2 * pad - 1], 60, fill=(14, 10, 14, 255))
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 46, fill=255); ph.paste(sc, (pad, pad), m); return ph
PHONE = phone(1000)
def c7(t):  # o sistema + chamada
    im = kenburns(BG_WINE, t + 4, 5.5, 1.1, 1.0); im = glow_orb(im, W / 2, 760, 560, (255, 150, 170), .7); im = particles(im, t + 35, .7)
    p = eo(t / .9); ph = PHONE.rotate(-4 + 4 * p, resample=Image.BICUBIC, expand=True)
    ph.putalpha(ph.getchannel('A').point(lambda v: int(v * p)))
    sh = Image.new('RGBA', ph.size, (0, 0, 0, 0)); sh.putalpha(ph.getchannel('A').point(lambda v: int(v * .5))); sh = sh.filter(ImageFilter.GaussianBlur(30))
    x, y = int((W - ph.width) / 2), int(150 + 80 * (1 - p) + 8 * math.sin(t * 1.4))
    im.alpha_composite(sh, (x, y + 30)); im.alpha_composite(ph, (x, y))
    # faixa inferior escura para o texto
    fd = Image.new('RGBA', (W, H)); fdd = ImageDraw.Draw(fd)
    for i in range(60): fdd.rectangle([0, 1150 + i * 13, W, 1163 + i * 13], fill=(12, 2, 10, int(min(235, i * 9))))
    im.alpha_composite(fd)
    a = reveal(t, .8); im.alpha_composite(text_layer([('Tudo calculado na hora,', F('Corm600i.ttf', 66), (255, 214, 160)), ('no seu celular.', F('Corm500.ttf', 104))], 1290, a, 24 * (1 - a)))
    b = eo((t - 1.8) / .6)
    if b > 0:
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L); bw, bh = 780, 128; bx, by = (W - bw) / 2, 1560 + 20 * (1 - b); s = 1 + .025 * math.sin(t * 5)
        d.rounded_rectangle([bx - (s - 1) * bw / 2, by, bx + bw * s - (s - 1) * bw / 2, by + bh], 64, fill=(255, 255, 255, int(255 * b)))
        d.text((W / 2, by + bh / 2), 'Calcule grátis · link na bio', font=INTER('ExtraBold', 46), fill=(130, 20, 70, int(255 * b)), anchor='mm')
        d.text((W / 2, by + bh + 58), 'Planos a partir de R$ 62/mês', font=INTER('SemiBold', 38), fill=(240, 200, 140, int(255 * b)), anchor='mm')
        im.alpha_composite(L)
    return finish(im.convert('RGB'))

LOGO = Image.open('/home/claude/repo/azovah-landing-page/site/assets/logo_branca.webp').convert('RGBA')
def c8(t, dur=4.5):  # vinheta só com a logo
    g = Image.new('RGB', (W, H)); gd = ImageDraw.Draw(g)
    for y in range(0, H, 4): k = y / H; gd.rectangle([0, y, W, y + 4], fill=(int(30 - 18 * k), int(4 - 3 * k), int(14 - 8 * k)))
    im = g.convert('RGBA'); a = eo((t - .3) / 1.3); br = .5 + .5 * math.sin((t - .3) * 1.6)
    im = glow_orb(im, W / 2, H / 2, 520, (255, 150, 190), a * (.55 + .2 * br))
    im = particles(im, t + 40, .5 * a)
    sc = .94 + .06 * eo((t - .3) / 3.5); w = int(780 * sc); h = int(w * LOGO.height / LOGO.width); lg = LOGO.resize((w, h), Image.LANCZOS)
    sh = (t - 1.9) / 1.1
    if 0 < sh < 1:
        band = Image.new('L', (w, h)); bd = ImageDraw.Draw(band); x = -200 + sh * (w + 400)
        bd.polygon([(x, 0), (x + 70, 0), (x - 60, h), (x - 130, h)], fill=170); band = band.filter(ImageFilter.GaussianBlur(10))
        lg = Image.composite(Image.new('RGBA', (w, h), (255, 236, 200, 255)), lg, ImageChops.multiply(band, lg.getchannel('A')))
    lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a))); im.alpha_composite(lg, (int(W / 2 - w / 2), int(H / 2 - h / 2 - 10 * (1 - a))))
    im = im.convert('RGB')
    if t > dur - .7: im = Image.blend(im, Image.new('RGB', (W, H)), min(1, (t - (dur - .7)) / .7))
    return im

SC = [('c1', c1, 5.5), ('c2', c2, 5.5), ('c3', c3, 5.5), ('c4', c4, 5.5), ('c5', c5, 4.5), ('c6', c6, 9.0), ('c7', c7, 5.5), ('c8', c8, 4.5)]
XF = .5
def render(i):
    name, fn, dur = SC[i]; n = int(round(dur * FPS)); nxt = SC[i + 1][1] if i + 1 < len(SC) else None
    tmp = f'{OUT}/{name}.tmp.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    nx0 = nxt(0) if nxt else None
    for f in range(n):
        t = f / FPS; im = fn(t)
        if nxt and t > dur - XF: im = Image.blend(im, nx0, eio((t - (dur - XF)) / XF))
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); pr.wait(); os.replace(tmp, f'{OUT}/{name}.mp4'); print(name, flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        ims = [fn(d * .75).resize((216, 384)) for _, fn, d in SC]
        m = Image.new('RGB', (216 * 4, 384 * 2)); [m.paste(x, ((i % 4) * 216, (i // 4) * 384)) for i, x in enumerate(ims)]; m.save(f'{OUT}/sheet.jpg', quality=85)
    else:
        for i in map(int, sys.argv[1:]): render(i)
