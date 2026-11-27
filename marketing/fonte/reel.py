# Reels AZOVAH 1080x1920 · "Seu nome tem números" · cada cena vira um arquivo, depois concat
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
LORAI = '/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf'
INT = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
def lora(s, w='Bold', it=False):
    f = ImageFont.truetype(LORAI if it else LORA, s); f.set_variation_by_axes([{'Regular':400,'Medium':500,'SemiBold':600,'Bold':700}[w]]); return f
def inter(s, w='ExtraBold'): return ImageFont.truetype(INT % w, s)
def eo(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def eb(t):  # back-out
    t = max(0, min(1, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

class AD(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
        super().__init__(im, mode); self._img = im
    def text(self, xy, txt, font=None, fill=None, anchor=None, **k):
        if fill is not None and len(fill) == 4 and fill[3] < 255:
            if fill[3] <= 0: return
            m = Image.new('L', self._img.size); ImageDraw.Draw(m).text(xy, txt, font=font, fill=fill[3], anchor=anchor)
            bb = m.getbbox()
            if bb: self._img.paste(fill[:3], bb, m.crop(bb))
        else:
            super().text(xy, txt, font=font, fill=fill, anchor=anchor, **k)

# ---------- fundo base (gradiente + números místicos + grão), pré-renderizado ----------
random.seed(7)
def base(c1, c2, c3):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        col = [int(c1[i] * (1 - t / .6) + c2[i] * (t / .6)) for i in range(3)] if t < .6 else [int(c2[i] * (1 - (t - .6) / .4) + c3[i] * ((t - .6) / .4)) for i in range(3)]
        d.line([(0, y), (W, y)], fill=tuple(col))
    L = Image.new('RGBA', (W, H)); dl = ImageDraw.Draw(L)
    for i in range(120):
        s = random.choice([30, 44, 60, 90, 140])
        dl.text((random.uniform(-40, W), random.uniform(-40, H)), random.choice('1234567899112233'), font=lora(s, 'Regular', random.random() < .4), fill=(255, 210, 225, random.randint(10, 34)))
    for i in range(220):
        x, y = random.uniform(0, W), random.uniform(0, H); r = random.choice([1, 1.5, 2])
        dl.ellipse([x - r, y - r, x + r, y + r], fill=(255, 235, 245, random.randint(50, 150)))
    return Image.alpha_composite(im.convert('RGBA'), L.filter(ImageFilter.GaussianBlur(.5)))
PAL = {'s1': ((122, 16, 40), (58, 7, 22), (20, 2, 10), (255, 120, 170)),
       's2': ((14, 84, 84), (10, 52, 56), (4, 22, 26), (255, 140, 110)),
       's3': ((30, 36, 110), (14, 18, 60), (6, 8, 28), (255, 211, 107)),
       's4': ((84, 30, 140), (44, 14, 84), (16, 4, 36), (190, 140, 255)),
       's5': ((150, 30, 60), (80, 10, 40), (24, 2, 14), (255, 170, 110))}
BGS = {k: base(*v[:3]) for k, v in PAL.items()}
BG = BGS['s1']
def mkglow(c):
    g = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(g)
    for r in range(520, 0, -8): gd.ellipse([W / 2 - r, 760 - r, W / 2 + r, 760 + r], fill=c + (int(2 + 60 * (1 - r / 520) ** 2),))
    return g.filter(ImageFilter.GaussianBlur(30))
GLOWS = {k: mkglow(v[3]) for k, v in PAL.items()}

def frame(t, k='s1', pulse=True):
    im = BGS[k].copy()
    g = GLOWS[k].copy()
    if pulse:
        a = .65 + .35 * math.sin(t * 2.2)
        g.putalpha(g.getchannel('A').point(lambda v: int(v * a)))
    return Image.alpha_composite(im, g).convert('RGB')

def ctext(d, y, txt, font, fill, a=1.0, dy=0):
    w = d.textlength(txt, font=font)
    d.text(((W - w) / 2, y + dy), txt, font=font, fill=fill[:3] + (int(255 * a),))

def logo(d, a=1):
    ctext(d, 120, 'AZOVAH', inter(46, 'Black'), (255, 255, 255), a)
    ctext(d, 178, 'N U M E R O L O G I A', inter(18, 'Bold'), (255, 208, 224), a)

# ---------- cenas ----------
def s1(t):  # gancho 3,2 s
    im = frame(t, 's1'); d = AD(im, 'RGBA')
    logo(d, eo(t / .5))
    a1 = eo((t - .2) / .5); ctext(d, 640, 'Seu nome', lora(130), (255, 255, 255), a1, 40 * (1 - a1))
    a2 = eo((t - .9) / .5); ctext(d, 800, 'tem números.', lora(130, 'Bold', True), (255, 143, 182), a2, 40 * (1 - a2))
    a3 = eo((t - 1.8) / .5); ctext(d, 1010, 'E eles contam a sua história.', inter(46, 'SemiBold'), (255, 230, 238), a3)
    return im

LET = [('H', 5), ('E', 5), ('L', 3), ('E', 5), ('N', 5), ('A', 1)]
def s2(t):  # letras e valores 4,2 s
    im = frame(t + 3, 's2'); d = AD(im, 'RGBA'); logo(d)
    ctext(d, 420, 'Cada letra vale um número', inter(50, 'Bold'), (255, 214, 228), eo(t / .4))
    bw, gap = 140, 18; x0 = (W - (6 * bw + 5 * gap)) / 2
    for i, (l, v) in enumerate(LET):
        p = eb((t - .3 - i * .28) / .45)
        if p <= 0: continue
        x = x0 + i * (bw + gap); y = 640 + 60 * (1 - p)
        box = Image.new('RGBA', (bw, 220)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, bw - 1, 219], 28, fill=(255, 255, 255, 235))
        bd.text((bw / 2, 80), l, font=lora(96), fill=(58, 7, 22), anchor='mm')
        bd.text((bw / 2, 178), str(v), font=inter(56, 'Black'), fill=(194, 24, 91), anchor='mm')
        box.putalpha(box.getchannel('A').point(lambda v: int(v * min(1, p))))
        im.paste(box, (int(x), int(y)), box)
    s = eo((t - 2.2) / .5)
    if s > 0:
        tot = int(round(24 * s))
        ctext(d, 960, f'5 + 5 + 3 + 5 + 5 + 1 = {tot}', inter(54, 'Bold'), (255, 255, 255), s)
    r = eb((t - 3.0) / .6)
    if r > 0:
        cx, cy, R = W / 2, 1230, 150 * r
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, int(255 * min(1, r))))
        d.text((cx, cy - 4), '6', font=inter(int(170 * max(r, .1)), 'Black'), fill=(194, 24, 91), anchor='mm')
        ctext(d, 1410, '2 + 4 = 6  ·  Expressão de HELENA', inter(40, 'SemiBold'), (255, 214, 228), min(1, r))
    return im

def s3(t):  # o acento 3,6 s
    im = frame(t + 7, 's3'); d = AD(im, 'RGBA'); logo(d)
    a = eo(t / .4); ctext(d, 430, 'Agora com um acento:', inter(54, 'Bold'), (255, 214, 228), a)
    p = eb((t - .3) / .6)
    if p > 0:
        f = lora(200); txt = 'Hélena'; w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, 600 + 50 * (1 - p)), txt, font=f, fill=(255, 255, 255, int(255 * min(1, p))))
        # destaque no É
        ew = d.textlength('H', font=f); e2 = d.textlength('Hé', font=f)
        x1 = (W - w) / 2 + ew; x2 = (W - w) / 2 + e2
        q = eo((t - 1.0) / .4)
        if q > 0: d.rounded_rectangle([x1 - 8, 860, x1 - 8 + (x2 - x1 + 16) * q, 872], 6, fill=(232, 176, 74))
    q = eo((t - 1.2) / .5)
    if q > 0: ctext(d, 940, 'É = 5 + 2 = 7', inter(64, 'Black'), (232, 176, 74), q)
    n = eo((t - 1.9) / .7)
    if n > 0:
        v = 6 + (2 * n); shown = 8 if n > .5 else 6
        cx, cy, R = W / 2, 1270, 150
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(232, 176, 74, int(255 * n)))
        d.text((cx, cy - 4), str(shown), font=inter(170, 'Black'), fill=(59, 36, 0, int(255 * n)), anchor='mm')
        ctext(d, 1460, 'Soma 26 e passa a vibrar 8.', inter(46, 'SemiBold'), (255, 230, 238), n)
    return im

TRI = [[5, 5, 3, 5, 5, 1], [1, 8, 8, 1, 6], [9, 7, 9, 7], [7, 7, 7], [5, 5], [1]]
def s4(t):  # triângulo 4,4 s
    im = frame(t + 11, 's4'); d = AD(im, 'RGBA'); logo(d)
    ctext(d, 380, 'O triângulo da vida', lora(84), (255, 255, 255), eo(t / .4))
    ctext(d, 490, 'mostra o que se repete', inter(46, 'SemiBold'), (255, 214, 228), eo((t - .2) / .4))
    c = 128; gap = 14
    for r, row in enumerate(TRI):
        for k, v in enumerate(row):
            p = eb((t - .5 - r * .32 - k * .05) / .4)
            if p <= 0: continue
            x = W / 2 - (len(row) * c + (len(row) - 1) * gap) / 2 + k * (c + gap); y = 640 + r * (c + 6)
            seq = r == 3 and t > 2.9
            fill = (194, 24, 91, 255) if seq else (255, 255, 255, int(235 * min(1, p)))
            tc = (255, 255, 255) if seq else (58, 7, 22)
            s = c * min(1, p)
            d.rounded_rectangle([x + (c - s) / 2, y + (c - s) / 2, x + (c + s) / 2, y + (c + s) / 2], 24, fill=fill)
            if p > .5: d.text((x + c / 2, y + c / 2), str(v), font=inter(60, 'Black'), fill=tc + (255,), anchor='mm')
    q = eo((t - 3.0) / .5)
    if q > 0:
        ctext(d, 1520, 'Sequência 777: um padrão que se repete', inter(44, 'Bold'), (255, 180, 205), q)
        ctext(d, 1585, 'e que a assinatura certa pode equilibrar.', inter(44, 'SemiBold'), (255, 230, 238), q)
    return im

def seal(size):
    S = 400; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im, 'RGBA'); c = S / 2
    pts = [(c + (S * .485 if i % 2 == 0 else S * .45) * math.cos(i * math.pi / 36), c + (S * .485 if i % 2 == 0 else S * .45) * math.sin(i * math.pi / 36)) for i in range(72)]
    d.polygon(pts, fill=(232, 176, 74)); d.ellipse([c - 172, c - 172, c + 172, c + 172], fill=(185, 120, 28))
    d.ellipse([c - 116, c - 116, c + 116, c + 116], fill=(240, 196, 110))
    d.polygon([(c, c - 70), (c + 52, c + 20), (c - 52, c + 20)], outline=(90, 54, 8), width=6)
    d.text((c, c + 52), 'AZOVAH', font=lora(26), fill=(74, 42, 5), anchor='mm')
    f = inter(21, 'ExtraBold'); txt = 'INSTITUTO DE NUMEROLOGIA CABALÍSTICA ✦ AZOVAH ✦ '
    n = len(txt)
    for i, ch in enumerate(txt):
        a = -math.pi / 2 + i * 2 * math.pi / n
        ci = Image.new('RGBA', (40, 40)); cd = ImageDraw.Draw(ci); cd.text((20, 20), ch, font=f, fill=(255, 244, 214), anchor='mm')
        ci = ci.rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
        im.alpha_composite(ci, (int(c + 144 * math.cos(a) - 20), int(c + 144 * math.sin(a) - 20)))
    return im.resize((size, size), Image.LANCZOS)
SEAL = seal(420)

def s5(t):  # chamada 4 s
    im = frame(t + 15, 's5'); d = AD(im, 'RGBA')
    p = eb(t / .7)
    if p > 0:
        s = SEAL.rotate(-t * 18, resample=Image.BICUBIC)
        s.putalpha(s.getchannel('A').point(lambda v: int(v * min(1, p))))
        sz = int(420 * (0.7 + .3 * min(1, p))); s = s.resize((sz, sz))
        im.paste(s, (int((W - sz) / 2), int(470 - sz / 2)), s)
    a = eo((t - .5) / .5); ctext(d, 780, 'Descubra o que', lora(100), (255, 255, 255), a, 30 * (1 - a))
    b = eo((t - .8) / .5); ctext(d, 910, 'o seu nome vibra.', lora(100, 'Bold', True), (255, 143, 182), b, 30 * (1 - b))
    c = eo((t - 1.4) / .5)
    if c > 0:
        bw, bh = 760, 130; x, y = (W - bw) / 2, 1140 + 30 * (1 - c)
        sc = 1 + .03 * math.sin(t * 6) if t > 2 else 1
        d.rounded_rectangle([x - (sc - 1) * bw / 2, y, x + bw * sc - (sc - 1) * bw / 2, y + bh], 65, fill=(255, 255, 255, int(255 * c)))
        ctext(d, y + 34, 'Calcule grátis · link na bio', inter(50, 'ExtraBold'), (142, 18, 72), c)
    e = eo((t - 2.0) / .5)
    ctext(d, 1380, 'AZOVAH · Instituto de Numerologia Cabalística', inter(36, 'SemiBold'), (255, 214, 228), e)
    ctext(d, 1440, 'azovah.com/bio', inter(40, 'Bold'), (232, 176, 74), e)
    return im

SC = [('s1', s1, 3.2), ('s2', s2, 4.4), ('s3', s3, 3.6), ('s4', s4, 4.4), ('s5', s5, 4.2)]
XF = .35  # fade entre cenas, dentro de cada arquivo

def render(i):
    name, fn, dur = SC[i]; n = int(dur * FPS); out = f'{name}.mp4'
    nxt = SC[i + 1][1] if i + 1 < len(SC) else None
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{name}.tmp.mp4'], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS; im = fn(t).convert('RGB')
        if nxt and t > dur - XF:
            a = (t - (dur - XF)) / XF; im = Image.blend(im, nxt(0).convert('RGB'), eo(a))
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); pr.wait(); os.replace(f'{name}.tmp.mp4', out); print(out)

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for name, fn, dur in SC: fn(dur * .8).convert('RGB').save(f'still_{name}.jpg', quality=85)
    else:
        render(int(sys.argv[1]))
