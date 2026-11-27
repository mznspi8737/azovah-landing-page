# AZOVAH · "O nome que você assina" — Reels longo, narrativa de problema → segredo → sistema → novo rumo
import math, random, os, sys, subprocess
sys.path.insert(0, '/home/claude/film')
import film as Fm
from film import W, H, FPS, F, INTER, eo, eio, text_layer, numlayer, particles, glow_orb, rays, golden, kenburns, finish, BG_NIGHT, BG_DEEP, BG_WINE, GOLD, VIG
from PIL import Image, ImageDraw, ImageFilter, ImageChops
OUT = '/home/claude/vid2/out'; os.makedirs(OUT, exist_ok=True)
SH = '/home/claude/vid2/shots/'
PINK, RED, GREEN, CREAM = (255, 79, 139), (255, 70, 80), (61, 220, 151), (255, 244, 230)
def eb(t): t = max(0, min(1, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
R = random.Random(9)

# ---------- tipografia cinética ----------
def word_pop(im, txt, font, cy, t0, t, col=CREAM, hl=None, punch=True):
    """palavra/linha que entra com escala (1.35→1) e brilho"""
    p = (t - t0) / .35
    if p <= 0: return im
    a = eo(p); s = 1 + .35 * (1 - eb(p)) if punch else 1
    L = Image.new('RGBA', (W, 260)); d = ImageDraw.Draw(L); w = d.textlength(txt, font=font)
    d.text(((W - w) / 2, 130), txt, font=font, fill=(hl or col) + (255,), anchor='lm')
    if s != 1: L = L.resize((int(W * s), int(260 * s)), Image.BILINEAR); L = L.crop(((L.width - W) // 2, (L.height - 260) // 2, (L.width - W) // 2 + W, (L.height - 260) // 2 + 260))
    g = L.filter(ImageFilter.GaussianBlur(16))
    L2 = Image.new('RGBA', (W, 260)); L2.alpha_composite(g); L2.alpha_composite(L)
    L2.putalpha(L2.getchannel('A').point(lambda v: int(v * a)))
    im = im.convert('RGBA'); im.alpha_composite(L2, (0, int(cy - 130))); return im

def chip(im, txt, cx, cy, t0, t, bg=PINK, fg=(255, 255, 255), size=40):
    p = eb((t - t0) / .4)
    if p <= 0: return im
    f = INTER('ExtraBold', size); L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L); w = d.textlength(txt, font=f)
    s = min(1, p); pw, ph = (w + 56) * s, (size + 34) * s
    d.rounded_rectangle([cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2], ph / 2, fill=bg + (int(240 * min(1, p)),))
    if p > .6: d.text((cx, cy), txt, font=f, fill=fg + (255,), anchor='mm')
    g = L.filter(ImageFilter.GaussianBlur(18)); im = im.convert('RGBA'); im.alpha_composite(g); im.alpha_composite(L); return im

# ---------- efeitos ----------
GRAIN = [Image.effect_noise((W // 2, H // 2), 40).resize((W, H)).convert('L') for _ in range(4)]
def grain(im, t, k=.06):
    g = GRAIN[int(t * 24) % 4]; return Image.blend(im.convert('RGB'), Image.merge('RGB', (g, g, g)), k)
def glitch(im, amt, seed=0):
    if amt <= 0: return im
    r = random.Random(int(seed * 1000)); im = im.convert('RGB'); rr, gg, bb = im.split(); o = int(28 * amt)
    im = Image.merge('RGB', (ImageChops.offset(rr, o, 0), gg, ImageChops.offset(bb, -o, 0)))
    for _ in range(int(10 * amt)):
        y = r.randint(0, H - 80); h = r.randint(12, 90); dx = r.randint(-90, 90)
        band = im.crop((0, y, W, y + h)); im.paste(ImageChops.offset(band, dx, 0), (0, y))
    return im
def shake(im, t, amt):
    if amt <= 0: return im
    dx, dy = int(amt * 14 * math.sin(t * 91)), int(amt * 10 * math.cos(t * 77)); return ImageChops.offset(im, dx, dy)
def punch(im, k):  # zoom rápido
    if k <= 0: return im
    s = 1 + .07 * k; w, h = int(W / s), int(H / s); x, y = (W - w) // 2, (H - h) // 2
    return im.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)
def leak(im, t, col=(255, 120, 160), a=.35):
    L = Image.new('RGBA', (W // 4, H // 4)); d = ImageDraw.Draw(L)
    x = (W // 4) * (.5 + .45 * math.sin(t * .9)); y = (H // 4) * (.3 + .2 * math.cos(t * .6))
    d.ellipse([x - 160, y - 160, x + 160, y + 160], fill=col + (int(255 * a),))
    L = L.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR)
    return Image.alpha_composite(im.convert('RGBA'), L)
def dark(bg, t, dur, z0=1.0, z1=1.08):
    return kenburns(bg, t, dur, z0, z1)

# ---------- celular com tela rolando ----------
SHOTS = {k: Image.open(SH + k + '.png').convert('RGB') for k in ['nome', 'triangulo', 'alterar1', 'alterar2', 'inicio', 'antes', 'grafico', 'matriz']}
PW, PHH = 640, 1240
MASK = Image.new('L', (PW, PHH)); ImageDraw.Draw(MASK).rounded_rectangle([0, 0, PW - 1, PHH - 1], 56, fill=255)
def phone(shot, y0, zoom=1.0, zx=.5, zy=.5):
    S = SHOTS[shot]; sw = S.width; vh = int(sw * PHH / PW)
    y0 = int(max(0, min(S.height - vh, y0)))
    crop = S.crop((0, y0, sw, y0 + vh)).resize((PW, PHH), Image.BILINEAR)
    if zoom > 1:
        w, h = int(PW / zoom), int(PHH / zoom); x, y = int((PW - w) * zx), int((PHH - h) * zy); crop = crop.crop((x, y, x + w, y + h)).resize((PW, PHH), Image.BILINEAR)
    fr = Image.new('RGBA', (PW + 36, PHH + 36)); d = ImageDraw.Draw(fr)
    d.rounded_rectangle([0, 0, PW + 35, PHH + 35], 74, fill=(14, 10, 14, 255), outline=(255, 255, 255, 40), width=2)
    fr.paste(crop, (18, 18), MASK); d.rounded_rectangle([PW / 2 - 60, 30, PW / 2 + 60, 52], 11, fill=(14, 10, 14, 255))
    return fr
def place_phone(im, fr, t, cy=900, tilt=0.0, scale=1.0):
    if scale != 1: fr = fr.resize((int(fr.width * scale), int(fr.height * scale)), Image.BILINEAR)
    if tilt: fr = fr.rotate(tilt, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', fr.size, (0, 0, 0, 0)); sh.putalpha(fr.getchannel('A').point(lambda v: int(v * .55))); sh = sh.filter(ImageFilter.GaussianBlur(34))
    x, y = (W - fr.width) // 2, int(cy - fr.height / 2)
    im = im.convert('RGBA'); im.alpha_composite(sh, (x, y + 40)); im.alpha_composite(fr, (x, y)); return im
def tag(im, txt, x, y, t0, t, col=PINK, side='l'):
    """etiqueta com linha apontando (estilo HUD)"""
    p = eo((t - t0) / .35)
    if p <= 0: return im
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L); f = INTER('ExtraBold', 34); w = d.textlength(txt, font=f)
    bx = x - w - 70 if side == 'l' else x + 40
    d.line([(x, y), (x + (-30 if side == 'l' else 30), y)], fill=col + (int(255 * p),), width=4)
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col + (int(255 * p),))
    d.rounded_rectangle([bx, y - 32, bx + (w + 40) * p, y + 32], 16, fill=(12, 6, 12, int(220 * p)), outline=col + (int(255 * p),), width=3)
    if p > .7: d.text((bx + 20, y), txt, font=f, fill=CREAM + (255,), anchor='lm')
    im = im.convert('RGBA'); im.alpha_composite(L.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(L); return im

# ======================= CENAS =======================
def s1(t):  # você se esforça... círculos
    im = dark(BG_WINE, t, 5); im = leak(im, t, (255, 70, 110), .25)
    # seta circular girando (andar em círculos)
    def ring(d, t):
        cx, cy, r = W / 2, 760, 260; a0 = t * 120; ext = 300 * eo(t / 1.2)
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + ext, fill=PINK + (230,), width=8)
        ang = math.radians(a0 + ext); hx, hy = cx + r * math.cos(ang), cy + r * math.sin(ang)
        d.polygon([(hx + 26 * math.cos(ang + 1.9), hy + 26 * math.sin(ang + 1.9)), (hx + 34 * math.cos(ang + .2 + math.pi / 2), hy + 34 * math.sin(ang + .2 + math.pi / 2)), (hx + 26 * math.cos(ang - 1.2), hy + 26 * math.sin(ang - 1.2))], fill=PINK + (230,))
    im.alpha_composite(golden(ring, t))
    im = word_pop(im, 'VOCÊ SE ESFORÇA,', INTER('Black', 84), 1180, .3, t)
    im = word_pop(im, 'RECOMEÇA, TENTA DE NOVO…', INTER('Black', 64), 1300, 1.2, t, PINK)
    im.alpha_composite(text_layer([('e a vida parece andar em círculos?', F('Corm600i.ttf', 66), (255, 214, 190))], 1420, eo((t - 2.3) / .6)))
    return grain(finish(im.convert('RGB')), t)

PROB = [('MESMO EMPREGO.', 0.2), ('MESMO TIPO DE RELAÇÃO.', 1.3), ('MESMA CONTA', 2.4), ('NO VERMELHO.', 2.75)]
def s2(t):  # montagem de padrões
    im = dark(BG_WINE, t + 5, 5, 1.1, 1.0); im = numlayer(im, t * 3)
    flash = max(0, 1 - ((t - .2) % 1.1) / .25) if t > .2 and t < 3.4 else 0
    if flash > 0: im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H), (120, 10, 30)), .35 * flash)
    y = 620
    for i, (w, t0) in enumerate(PROB):
        im = word_pop(im, w, INTER('Black', 92 if i == 0 else (76 if i == 1 else 104)), y + i * 170 + (60 if i >= 2 else 0) - (40 if i == 3 else 0), t0, t, RED if i == 3 else CREAM)
    im = shake(im.convert('RGB'), t, flash)
    return grain(finish(im), t)

def s3(t):  # não é azar, é padrão: 777
    im = dark(BG_NIGHT, t, 5.5); im = glow_orb(im, W / 2, 720, 520, (255, 60, 90), .55 * eo(t / .8))
    def sev(d, t):
        for i in range(3):
            p = eo((t - .9 - i * .25) / .3)
            if p <= 0: continue
            x = W / 2 + (i - 1) * 250; r = 105
            d.ellipse([x - r, 720 - r, x + r, 720 + r], outline=RED + (int(255 * p),), width=6)
            d.text((x, 724), '7', font=F('Corm700.ttf', 190), fill=CREAM + (int(255 * p),), anchor='mm')
    im.alpha_composite(golden(sev, t))
    im = word_pop(im, 'NÃO É AZAR.', INTER('Black', 120), 1150, .2, t)
    im = word_pop(im, 'É UM PADRÃO.', INTER('Black', 120), 1300, 1.8, t, PINK)
    im.alpha_composite(text_layer([('e ele está escrito no seu nome.', F('Corm600i.ttf', 70), (255, 214, 190))], 1430, eo((t - 3.0) / .6)))
    g = 1 - eo((t - 1.8) / .3) if 1.8 < t < 2.2 else 0
    return grain(finish(glitch(im.convert('RGB'), g * .8, t)), t)

def s4(t):  # a maioria nunca se conheceu
    im = dark(BG_DEEP, t, 5.5); im = numlayer(im, t * 2)
    def rings(d, t):
        for k in range(6):
            r = (120 + k * 90 + t * 60) % 620; a = int(200 * (1 - r / 620))
            d.ellipse([W / 2 - r, 760 - r, W / 2 + r, 760 + r], outline=(170, 150, 255, a), width=3)
        d.text((W / 2, 770), '?', font=F('Corm700.ttf', 300), fill=CREAM + (int(230 * eo(t / 1)),), anchor='mm')
    im.alpha_composite(golden(rings, t)); im = particles(im, t, .6)
    im.alpha_composite(text_layer([('E a maioria das pessoas', F('Corm600i.ttf', 72), (210, 200, 255)), ('nunca se conheceu', F('Corm500.ttf', 118)), ('de verdade.', F('Corm500.ttf', 118))], 1150, eo((t - .6) / .8), 26 * (1 - eo((t - .6) / .8))))
    return grain(finish(im.convert('RGB')), t)

STAGE = [('M', 'A', 'R', 'I', 'A'), ('M', 'A', 'R', 'Y', 'A', 'H')]
def s5(t):  # artistas e nome artístico
    im = Image.new('RGB', (W, H), (8, 4, 10)).convert('RGBA'); im = numlayer(im, t * 2 + 30)
    # holofotes
    L = Image.new('RGBA', (W // 2, H // 2)); d = ImageDraw.Draw(L)
    for sx, ang in ((90, 25 + 8 * math.sin(t * 1.3)), (450, -25 + 8 * math.sin(t * 1.1 + 1))):
        a = math.radians(90 + ang); ex, ey = sx + 900 * math.cos(a), 900 * math.sin(a)
        d.polygon([(sx, 0), (ex - 160, ey), (ex + 160, ey)], fill=(255, 230, 190, 40))
    im.alpha_composite(L.filter(ImageFilter.GaussianBlur(18)).resize((W, H)))
    im = word_pop(im, 'ENQUANTO ISSO…', INTER('Black', 70), 330, .1, t, (255, 214, 190), punch=False)
    # letreiro: tiles que trocam letras
    sw = t > 3.0; letters = STAGE[1] if sw else STAGE[0]; n = len(letters); tw = 132; x0 = (W - (n * tw + (n - 1) * 14)) / 2
    Ld = Image.new('RGBA', (W, H)); dd = ImageDraw.Draw(Ld)
    for i, ch in enumerate(letters):
        p = eo((t - .6 - i * .1) / .3) if not sw else eo((t - 3.0 - i * .06) / .25)
        if p <= 0: continue
        x = x0 + i * (tw + 14); y = 640 + 30 * (1 - p)
        changed = sw and (i >= 3)
        dd.rounded_rectangle([x, y, x + tw, y + 170], 22, fill=(30, 14, 24, int(240 * p)), outline=(GOLD if not changed else PINK) + (int(255 * p),), width=4)
        dd.text((x + tw / 2, y + 88), ch, font=F('Cinzel600.ttf', 104), fill=CREAM + (int(255 * p),), anchor='mm')
        for k in range(5):  # luzinhas do letreiro
            lx = x + 14 + k * 26; on = (int(t * 6) + k + i) % 2
            dd.ellipse([lx - 5, y - 18 - 5, lx + 5, y - 18 + 5], fill=(255, 220, 150, 220 if on else 60))
    im.alpha_composite(Ld.filter(ImageFilter.GaussianBlur(12))); im.alpha_composite(Ld)
    im.alpha_composite(text_layer([('NOME ARTÍSTICO', F('Cinzel600.ttf', 44), GOLD)], 860, eo((t - .9) / .5), 0, glow=False))
    im = word_pop(im, 'NÃO É À TOA QUE TANTOS', INTER('Black', 66), 1080, 1.4, t)
    im = word_pop(im, 'ARTISTAS E FAMOSOS', INTER('Black', 84), 1180, 1.9, t, PINK)
    im = word_pop(im, 'ADOTAM UM NOVO NOME.', INTER('Black', 66), 1290, 2.5, t)
    im.alpha_composite(text_layer([('Uma letra. Um acento. Outra vibração.', F('Corm600i.ttf', 64), (255, 214, 190))], 1420, eo((t - 3.4) / .6)))
    im.alpha_composite(text_layer([('Exemplo ilustrativo', INTER('SemiBold', 26), (190, 170, 180))], 1840, .8, 0, glow=False))
    g = 1 - eo((t - 3.0) / .25) if 2.95 < t < 3.3 else 0
    return grain(finish(glitch(im.convert('RGB'), g, t)), t)

TAB = [('1', 'A I Q J Y'), ('2', 'B K R'), ('3', 'C G L S'), ('4', 'D M T'), ('5', 'E H N'), ('6', 'U V W X Ç'), ('7', 'O Z'), ('8', 'F P')]
def s6(t):  # cada letra vale um número
    im = dark(BG_NIGHT, t + 9, 5.5); im = glow_orb(im, W / 2, 820, 560, (255, 190, 110), .5)
    im = word_pop(im, 'PORQUE UM NOME', INTER('Black', 86), 330, .1, t)
    im = word_pop(im, 'É VIBRAÇÃO.', INTER('Black', 120), 450, .7, t, GOLD)
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    for i, (n, ls) in enumerate(TAB):
        p = eo((t - 1.3 - i * .12) / .3)
        if p <= 0: continue
        y = 620 + i * 112; x = 180 + 40 * (1 - p)
        d.rounded_rectangle([x, y, x + 720, y + 92], 24, fill=(255, 255, 255, int(22 * p)), outline=GOLD + (int(120 * p),), width=2)
        d.text((x + 56, y + 46), n, font=F('Corm700.ttf', 76), fill=GOLD + (int(255 * p),), anchor='mm')
        d.text((x + 130, y + 46), ls, font=INTER('Bold', 44), fill=CREAM + (int(255 * p),), anchor='lm')
    im.alpha_composite(L)
    im.alpha_composite(text_layer([('Cada letra carrega um número.', F('Corm600i.ttf', 66), (255, 214, 190))], 1560, eo((t - 2.6) / .6)))
    return grain(finish(im.convert('RGB')), t)

def s7(t):  # o sistema: análise de Helena
    im = dark(BG_DEEP, t, 6, 1.0, 1.05); im = leak(im, t, (150, 110, 255), .25); im = numlayer(im, t * 2 + 50)
    y = 0 if t < 1.6 else (1500 * eio((t - 1.6) / 1.2) if t < 3.2 else 1500 + 2600 * eio((t - 3.4) / 1.4))
    z = 1 + .35 * eo((t - .8) / .4) * (1 - eo((t - 1.5) / .3))
    fr = phone('nome', y, z, .5, .22)
    im = place_phone(im, fr, t, 960, -3 + 3 * eo(t / .8), .95)
    im = word_pop(im, 'NO AZOVAH, EM SEGUNDOS:', INTER('Black', 58), 150, .1, t, punch=False)
    im = tag(im, 'EXPRESSÃO 1', 260, 820, .9, t, PINK, 'r') if t < 1.6 else im
    im = tag(im, 'O MAPA COMPLETO', 830, 1500, 3.4, t, GOLD, 'l') if t > 3.4 else im
    im.alpha_composite(text_layer([('Exemplo com nome fictício', INTER('SemiBold', 26), (190, 170, 200))], 1850, .8, 0, glow=False))
    return grain(finish(punch(im.convert('RGB'), max(0, 1 - abs(t - 1.0) / .25))), t)

def s8(t):  # triângulo: 777 e dívidas
    im = dark(BG_WINE, t + 3, 6); im = numlayer(im, t * 2 + 60)
    y = 1400 * eio(t / 1.2); z = 1 + 1.1 * eo((t - 1.6) / .6)
    fr = phone('triangulo', y, z, .5, .78)
    im = place_phone(im, fr, t, 960, 0, .95)
    im = tag(im, 'SEQUÊNCIA NEGATIVA 777', 400, 1000, 2.3, t, RED, 'r')
    im = chip(im, 'DÍVIDAS CÁRMICAS 19 · 14', W / 2, 1650, 3.0, t, RED)
    im = chip(im, 'ARCANO 51 · REI DE ESPADAS', W / 2, 1760, 3.5, t, (120, 80, 140))
    im = word_pop(im, 'O PADRÃO APARECE NA HORA.', INTER('Black', 56), 150, .1, t, punch=False)
    sk = max(0, 1 - abs(t - 2.3) / .25)
    return grain(finish(shake(punch(im.convert('RGB'), sk), t, sk)), t)

def s9(t):  # alterar assinatura → Helenâ Duarte
    im = dark(BG_NIGHT, t + 20, 6); im = leak(im, t, (255, 200, 120), .2); im = numlayer(im, t * 2 + 70)
    if t < 2.2: fr = phone('alterar1', 750 * eio(t / 1.6), 1, .5, .5)
    else: fr = phone('alterar2', 1650 + 300 * eio((t - 2.2) / 1.0), 1 + .5 * eo((t - 3.0) / .5), .5, .35)
    im = place_phone(im, fr, t, 960, 0, .95)
    g = max(0, 1 - abs(t - 2.2) / .18)
    im = word_pop(im, 'ESCOLHA A ENERGIA…', INTER('Black', 62), 150, .1, t, punch=False)
    im = tag(im, '1 ACENTO', 760, 1060, 3.3, t, GREEN, 'l')
    im = chip(im, 'HELENÂ DUARTE', W / 2, 1720, 3.6, t, GREEN, (8, 30, 20), 54)
    return grain(finish(glitch(punch(im.convert('RGB'), g), g * .7, t)), t)

ANTES = [('Expressão', '1', '8'), ('Arcano atual', '51', '58'), ('Sequência', '777', '—'), ('Dívidas', '19 · 14', '—')]
def s10(t):  # antes x depois, energias trocadas
    im = dark(BG_DEEP, t, 7, 1.0, 1.06); im = numlayer(im, t * 2 + 80)
    im = word_pop(im, 'AS ENERGIAS SE TROCAM', INTER('Black', 70), 180, .1, t)
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x1, x2 = 70, 560; cw = 450
    for x, tit, col, k in ((x1, 'HELENA DUARTE', RED, 0), (x2, 'HELENÂ DUARTE', GREEN, 1)):
        p = eo((t - .5 - k * 1.2) / .5)
        if p <= 0: continue
        d.rounded_rectangle([x, 330, x + cw, 1330], 40, fill=(16, 10, 22, int(230 * p)), outline=col + (int(255 * p),), width=4)
        d.text((x + cw / 2, 400), 'ANTES' if k == 0 else 'DEPOIS', font=INTER('Black', 34), fill=col + (int(255 * p),), anchor='mm')
        d.text((x + cw / 2, 470), tit, font=F('Corm700.ttf', 46), fill=CREAM + (int(255 * p),), anchor='mm')
        for i, (lab, a, b) in enumerate(ANTES):
            q = eo((t - .9 - k * 1.2 - i * .18) / .3)
            if q <= 0: continue
            y = 590 + i * 175
            d.text((x + 36, y), lab.upper(), font=INTER('Bold', 26), fill=(200, 190, 210, int(255 * q)), anchor='lm')
            v = b if k else a; good = k == 1
            d.text((x + 36, y + 62), v, font=INTER('Black', 64), fill=(GREEN if good else RED) + (int(255 * q),), anchor='lm')
            bw = (cw - 72) * (.85 if good else .32) * q
            d.rounded_rectangle([x + 36, y + 112, x + 36 + bw, y + 126], 7, fill=(GREEN if good else RED) + (int(200 * q),))
    im.alpha_composite(L.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(L)
    # fluxo de energia (partículas da esquerda para a direita)
    if t > 1.6:
        Fl = Image.new('RGBA', (W, H)); fd = ImageDraw.Draw(Fl)
        for i in range(40):
            ph = (t * .8 + i / 40) % 1; x = 520 + 60 * ph; y = 420 + (i * 97) % 880
            c = tuple(int(RED[j] * (1 - ph) + GREEN[j] * ph) for j in range(3))
            fd.ellipse([x - 7, y - 7, x + 7, y + 7], fill=c + (200,))
        im.alpha_composite(Fl.filter(ImageFilter.GaussianBlur(4)))
    im.alpha_composite(text_layer([('Arcano 51 Rei de Espadas → 58 Sete de Espadas', INTER('SemiBold', 34), (210, 200, 225))], 1390, eo((t - 3.4) / .5), 0, glow=False))
    im = word_pop(im, 'SEM SEQUÊNCIA. SEM DÍVIDA.', INTER('Black', 62), 1530, 3.9, t, GREEN)
    im.alpha_composite(text_layer([('Exemplo com nome fictício', INTER('SemiBold', 26), (190, 170, 200))], 1850, .8, 0, glow=False))
    return grain(finish(im.convert('RGB')), t)

def s11(t):  # uma letra, um acento, um novo rumo
    im = dark(BG_NIGHT, t + 30, 6.5, 1.12, 1.0); im = rays(im, W / 2, 1500, t, eo((t - 2.6) / 1)); im = numlayer(im, t * 3 + 90)
    def path(d, t):
        cx, cy = W / 2, 980; p = eo(t / 1.6)
        # círculo que se rompe e vira uma subida
        d.arc([cx - 200, cy - 200, cx + 200, cy + 200], 90, 90 + 300 * p, fill=(255, 120, 150, int(200 * (1 - eo((t - 2.4) / .6)))), width=6)
        q = eo((t - 2.4) / 1.6)
        if q > 0:
            pts = [(cx, cy + 200)] + [(cx + 380 * (k / 20) ** 1.3, cy + 200 - 900 * (k / 20) ** 1.6) for k in range(1, 21)]
            n = max(2, int(len(pts) * q)); d.line(pts[:n], fill=GOLD + (255,), width=8)
            ex, ey = pts[n - 1]; d.ellipse([ex - 18, ey - 18, ex + 18, ey + 18], fill=(255, 240, 200, 255))
    im.alpha_composite(golden(path, t)); im = particles(im, t + 5, eo((t - 2.4) / 1))
    im = word_pop(im, 'UMA LETRA.', INTER('Black', 104), 330, .2, t)
    im = word_pop(im, 'UM ACENTO.', INTER('Black', 104), 470, .9, t)
    im = word_pop(im, 'UM NOVO RUMO.', INTER('Black', 116), 1560, 2.6, t, GOLD)
    return grain(finish(im.convert('RGB')), t)

def s12(t):  # conhece-te
    im = dark(BG_DEEP, t, 5.5); im = glow_orb(im, W / 2, 820, 600, (150, 120, 255), .6); im = numlayer(im, t * 2 + 100)
    im.alpha_composite(golden(lambda d, t: Fm.flower(d, t, W / 2, 800, 110, eo(t / 2.6), t * 8), t)); im = particles(im, t + 9, .7)
    im.alpha_composite(text_layer([('Conhece-te a ti mesmo', F('Corm600i.ttf', 92), (255, 214, 190)), ('e escolha a energia', F('Corm500.ttf', 112)), ('que você assina.', F('Corm500.ttf', 112))], 1220, eo((t - .6) / .8), 26 * (1 - eo((t - .6) / .8))))
    return grain(finish(im.convert('RGB')), t)

def s13(t):  # chamada
    im = dark(BG_WINE, t + 8, 6); im = glow_orb(im, W / 2, 800, 560, (255, 120, 160), .6); im = particles(im, t + 12, .6); im = numlayer(im, t * 2 + 110)
    fr = phone('inicio', 0, 1); im = place_phone(im, fr, t, 820 + 10 * math.sin(t * 1.4), -4 + 4 * eo(t / .8), .72 * (0.9 + .1 * eo(t / .8)))
    fd = Image.new('RGBA', (W, H)); dd = ImageDraw.Draw(fd)
    for i in range(50): dd.rectangle([0, 1250 + i * 14, W, 1264 + i * 14], fill=(12, 2, 10, int(min(235, i * 9))))
    im.alpha_composite(fd)
    im = word_pop(im, 'DESCUBRA O QUE', INTER('Black', 76), 1370, .5, t)
    im = word_pop(im, 'O SEU NOME VIBRA.', INTER('Black', 88), 1480, .9, t, GOLD)
    b = eo((t - 1.7) / .5)
    if b > 0:
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L); bw, bh = 800, 130; bx, by = (W - bw) / 2, 1640 + 20 * (1 - b); s = 1 + .03 * math.sin(t * 5)
        d.rounded_rectangle([bx - (s - 1) * bw / 2, by, bx + bw * s - (s - 1) * bw / 2, by + bh], 65, fill=(255, 255, 255, int(255 * b)))
        d.text((W / 2, by + bh / 2), 'Calcule grátis · link na bio', font=INTER('ExtraBold', 48), fill=(130, 20, 70, int(255 * b)), anchor='mm')
        im.alpha_composite(L)
    return grain(finish(im.convert('RGB')), t)

def s14(t): return Fm.c8(t, 9.0)

SC = [('s1', s1, 4.5), ('s2', s2, 4.0), ('s3', s3, 5.0), ('s4', s4, 5.0), ('s5', s5, 6.0), ('s6', s6, 5.0), ('s7', s7, 6.0), ('s8', s8, 5.5), ('s9', s9, 5.5), ('s10', s10, 7.0), ('s11', s11, 6.0), ('s12', s12, 5.5), ('s13', s13, 5.5), ('s14', s14, 9.0)]
def render(i):
    name, fn, dur = SC[i]; n = int(round(dur * FPS)); tmp = f'{OUT}/{name}.tmp.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS; im = fn(t).convert('RGB')
        if i > 0 and t < .22 and name != 's14': im = glitch(im, 1 - t / .22, t + i)   # transição com glitch
        if i > 0 and t < .12: im = Image.blend(Image.new('RGB', (W, H), (255, 255, 255)), im, t / .12 * .7 + .3) if name in ('s3', 's7', 's11') else im
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); pr.wait(); os.replace(tmp, f'{OUT}/{name}.mp4'); print(name, flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        ims = [fn(d * .8 if n != 's14' else 3).convert('RGB').resize((180, 320)) for n, fn, d in SC]
        m = Image.new('RGB', (180 * 7, 320 * 2)); [m.paste(x, ((i % 7) * 180, (i // 7) * 320)) for i, x in enumerate(ims)]; m.save(f'{OUT}/sheet.jpg', quality=85)
    else:
        for i in map(int, sys.argv[1:]): render(i)
