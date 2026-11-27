# Reels longo com narração (Kokoro pf_dora) + legendas
import sys, os, json, math, wave, subprocess
import numpy as np
sys.path.insert(0, '/home/claude/reels')
import reel as R
from reel import W, H, FPS, lora, inter, eo, eb, ctext, logo, frame, AD, LET, TRI, SEAL
from PIL import Image, ImageDraw, ImageFilter

# paletas extras
R.PAL['s6'] = ((10, 96, 66), (6, 52, 38), (2, 20, 14), (120, 255, 190))
R.PAL['s8'] = ((40, 6, 18), (18, 2, 8), (6, 0, 3), (255, 190, 120))
R.PAL['s7'] = ((160, 74, 12), (84, 32, 6), (28, 10, 2), (255, 190, 90))
for k in ('s6', 's7', 's8'):
    R.BGS[k] = R.base(*R.PAL[k][:3]); R.GLOWS[k] = R.mkglow(R.PAL[k][3])

NARR = {
 's1': ["Oi, tudo bem? Sabia que o seu nome tem números?", "E que eles contam muito sobre a sua história!"],
 's2': ["Olha que legal: na numerologia cabalística, cada letra vale um número!",
        "Olha a Helena: H vale cinco, E, cinco, L, três, E, cinco, N, cinco, e A, um.",
        "Somando tudo, dá vinte e quatro.",
        "E dois mais quatro dá seis. Esse é o número de expressão dela."],
 's3': ["Agora vem a parte mais divertida!", "Se ela colocar um acento no E, ele passa a valer sete.",
        "A soma vira vinte e seis, e o nome passa a vibrar oito.", "Um detalhe pequenininho muda a energia inteira!"],
 's4': ["Com os números do nome, a gente monta o triângulo da vida.",
        "Quando um número se repete três vezes seguidas, como esse sete, sete, sete,",
        "isso mostra um padrão que tende a voltar na sua vida."],
 's6': ["Mas calma, dá pra equilibrar!",
        "Com pequenas mudanças na assinatura, a Mariana Lopes vira Mariãna Lopês,",
        "e troca o arcano quinze, mais pesado, pelo quarenta e cinco, muito mais favorável."],
 's7': ["No AZOVAH você vê o seu mapa completo:",
        "ciclos, ano pessoal, compatibilidade no amor e o calendário dos seus melhores dias."],
 's5': ["E aí, quer descobrir o que o seu nome vibra?", "Calcule grátis no link da bio. Vem, te espero lá!"],
}
# texto exibido na legenda (com números, mais fácil de ler)
CAP = {
 's2': [None, "Helena: H 5 · E 5 · L 3 · E 5 · N 5 · A 1", "Somando tudo: 24", "2 + 4 = 6. Número de expressão."],
 's3': [None, "Com acento, o É passa a valer 7.", "A soma vira 26 e o nome vibra 8.", None],
 's4': [None, "Quando um número se repete 3 vezes seguidas, como 7 7 7,", None],
 's6': [None, None, "Troca o arcano 15, mais pesado, pelo 45, muito mais favorável."],
}
ORDER = ['s1', 's2', 's3', 's4', 's6', 's7', 's5', 's8']
VIN = 6.0
LEAD, GAP, TAIL = 0.45, 0.28, 0.7
SR = 24000
OUT = '/home/claude/reels/v2'; os.makedirs(OUT, exist_ok=True)

def say(line, i):
    from gtts import gTTS
    mp = f'/tmp/g_{i}.mp3'; wv = f'/tmp/g_{i}.wav'
    gTTS(line, lang='pt', tld='com.br').save(mp)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp, '-af', 'silenceremove=stop_periods=-1:stop_duration=0.18:stop_threshold=-42dB:stop_silence=0.16,rubberband=tempo=1.18:pitch=1.04,highpass=f=90,equalizer=f=3500:t=q:w=1:g=3', '-ac', '1', '-ar', str(SR), wv], check=True)
    w = wave.open(wv); a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768; return a, SR

def tts():
    n = [0]
    class K:
        def create(self, line, **kw):
            n[0] += 1; return say(line, n[0])
    k = K()
    meta = {}
    for s in ORDER:
        if s == 's8': meta[s] = dict(cues=[], dur=VIN); continue
        cues, chunks, t = [], [], LEAD
        for line in NARR[s]:
            a, sr = k.create(line, voice='pf_dora', speed=1.04, lang='pt-br')
            a = np.asarray(a, dtype=np.float32)
            # apara silêncio das pontas
            nz = np.where(np.abs(a) > 0.01)[0]
            if len(nz): a = a[max(0, nz[0] - 600): nz[-1] + 1200]
            cues.append([t, t + len(a) / SR]); chunks.append(a); t += len(a) / SR + GAP
        dur = t - GAP + TAIL
        buf = np.zeros(int(dur * SR) + 1, np.float32)
        for (st, en), a in zip(cues, chunks):
            i = int(st * SR); buf[i:i + len(a)] += a
        np.save(f'{OUT}/{s}.npy', buf)
        meta[s] = dict(cues=cues, dur=round(dur * FPS) / FPS)
        print(s, round(dur, 2))
    json.dump(meta, open(f'{OUT}/meta.json', 'w'))

META = json.load(open(f'{OUT}/meta.json')) if os.path.exists(f'{OUT}/meta.json') else {}

def wrap(d, txt, font, maxw):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        t2 = (cur + ' ' + w).strip()
        if d.textlength(t2, font=font) <= maxw: cur = t2
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def caption(im, s, t):
    if s == 's8': return
    cues = META[s]['cues']; idx = None
    for i, (a, b) in enumerate(cues):
        if a - .05 <= t <= b + GAP: idx = i
    if idx is None: return
    txt = (CAP.get(s, [None] * 9)[idx] if idx < len(CAP.get(s, [])) else None) or NARR[s][idx]
    a = eo((t - cues[idx][0] + .05) / .2)
    d = AD(im, 'RGBA'); f = inter(46, 'Bold')
    lines = wrap(d, txt, f, 900); lh = 60
    hgt = len(lines) * lh + 40; y0 = 1700 - hgt
    ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
    wmax = max(d.textlength(l, font=f) for l in lines)
    od.rounded_rectangle([(W - wmax) / 2 - 34, y0, (W + wmax) / 2 + 34, y0 + hgt], 28, fill=(0, 0, 0, int(150 * a)))
    im.paste(ov, (0, 0), ov)
    for i, l in enumerate(lines): ctext(d, y0 + 18 + i * lh, l, f, (255, 255, 255), a)

def P(s, t, i, dur=.5):  # progresso relativo ao início do cue i
    return (t - META[s]['cues'][i][0]) / dur

# ---------- cenas ----------
def s1(t):
    s = 's1'; im = frame(t, 's1'); d = AD(im, 'RGBA'); logo(d, eo(t / .5))
    a1 = eo(P(s, t, 0, .5)); ctext(d, 600, 'Seu nome', lora(140), (255, 255, 255), a1, 40 * (1 - a1))
    a2 = eo((t - META[s]['cues'][0][0] - 1.0) / .5); ctext(d, 770, 'tem números.', lora(140, 'Bold', True), (255, 143, 182), a2, 40 * (1 - a2))
    a3 = eo(P(s, t, 1)); ctext(d, 1000, 'E eles contam a sua história.', inter(52, 'SemiBold'), (255, 230, 238), a3)
    return im

def s2(t):
    s = 's2'; c = META[s]['cues']; im = frame(t + 9, 's2'); d = AD(im, 'RGBA'); logo(d)
    ctext(d, 400, 'Cada letra vale um número', inter(56, 'Bold'), (255, 214, 228), eo(P(s, t, 0, .4)))
    bw, gap = 146, 16; x0 = (W - (6 * bw + 5 * gap)) / 2
    span = c[1][1] - c[1][0]
    for i, (l, v) in enumerate(LET):
        st = META[s]['let'][i] - .15
        p = eb((t - st) / .45)
        if p <= 0: continue
        x = x0 + i * (bw + gap); y = 600 + 60 * (1 - p)
        box = Image.new('RGBA', (bw, 230)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, bw - 1, 229], 28, fill=(255, 255, 255, 235))
        bd.text((bw / 2, 84), l, font=lora(100), fill=(58, 7, 22), anchor='mm')
        bd.text((bw / 2, 186), str(v), font=inter(60, 'Black'), fill=(194, 24, 91), anchor='mm')
        box.putalpha(box.getchannel('A').point(lambda q: int(q * min(1, p))))
        im.paste(box, (int(x), int(y)), box)
    sp = eo(P(s, t, 2, .6))
    if sp > 0: ctext(d, 910, f'5 + 5 + 3 + 5 + 5 + 1 = {int(round(24 * sp))}', inter(60, 'Bold'), (255, 255, 255), sp)
    r = eb(P(s, t, 3, .6))
    if r > 0:
        cx, cy, Rr = W / 2, 1180, 150 * r
        d.ellipse([cx - Rr, cy - Rr, cx + Rr, cy + Rr], fill=(255, 255, 255, int(255 * min(1, r))))
        d.text((cx, cy - 4), '6', font=inter(int(170 * max(r, .1)), 'Black'), fill=(194, 24, 91), anchor='mm')
        ctext(d, 1360, 'Expressão de HELENA', inter(44, 'SemiBold'), (255, 214, 228), min(1, r))
    return im

def s3(t):
    s = 's3'; im = frame(t + 30, 's3'); d = AD(im, 'RGBA'); logo(d)
    ctext(d, 400, 'Agora com um acento:', inter(58, 'Bold'), (255, 214, 228), eo(P(s, t, 0, .4)))
    p = eb(P(s, t, 1, .6))
    if p > 0:
        f = lora(210); txt = 'Hélena'; w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, 560 + 50 * (1 - p)), txt, font=f, fill=(255, 255, 255, int(255 * min(1, p))))
        ew = d.textlength('H', font=f); e2 = d.textlength('Hé', font=f); x1 = (W - w) / 2 + ew; x2 = (W - w) / 2 + e2
        q = eo(P(s, t, 1, .4) - .8)
        if q > 0: d.rounded_rectangle([x1 - 8, 830, x1 - 8 + (x2 - x1 + 16) * q, 842], 6, fill=(232, 176, 74))
    q = eo((t - META[s]['sete'] + .1) / .5)
    if q > 0: ctext(d, 900, 'É = 5 + 2 = 7', inter(68, 'Black'), (232, 176, 74), q)
    n = eo(P(s, t, 2, .7))
    if n > 0:
        cx, cy, Rr = W / 2, 1210, 150
        d.ellipse([cx - Rr, cy - Rr, cx + Rr, cy + Rr], fill=(232, 176, 74, int(255 * n)))
        d.text((cx, cy - 4), '8' if t > META[s]['oito'] - .05 else '6', font=inter(170, 'Black'), fill=(59, 36, 0, int(255 * n)), anchor='mm')
    return im

def s4(t):
    s = 's4'; c = META[s]['cues']; im = frame(t + 50, 's4'); d = AD(im, 'RGBA'); logo(d)
    ctext(d, 360, 'O triângulo da vida', lora(88), (255, 255, 255), eo(P(s, t, 0, .4)))
    cs = 130; gap = 14
    for r, row in enumerate(TRI):
        for k, v in enumerate(row):
            p = eb((t - c[0][0] - .5 - r * .35 - k * .05) / .4)
            if p <= 0: continue
            x = W / 2 - (len(row) * cs + (len(row) - 1) * gap) / 2 + k * (cs + gap); y = 520 + r * (cs + 8)
            seq = r == 3 and t > META[s]['hl'] + .3
            fill = (194, 24, 91, 255) if seq else (255, 255, 255, int(235 * min(1, p)))
            tc = (255, 255, 255) if seq else (58, 7, 22)
            sz = cs * min(1, p)
            d.rounded_rectangle([x + (cs - sz) / 2, y + (cs - sz) / 2, x + (cs + sz) / 2, y + (cs + sz) / 2], 24, fill=fill)
            if p > .5: d.text((x + cs / 2, y + cs / 2), str(v), font=inter(62, 'Black'), fill=tc + (255,), anchor='mm')
    return im

def s6(t):
    s = 's6'; im = frame(t + 70, 's6'); d = AD(im, 'RGBA'); logo(d)
    ctext(d, 380, 'Dá pra equilibrar', lora(96), (255, 255, 255), eo(P(s, t, 0, .4)))
    a = eo(P(s, t, 1, .5)); b = eo((t - META[s]['vira'] + .1) / .5)
    f = lora(104)
    if a > 0:
        ctext(d, 560, 'Mariana Lopes', f, (200, 235, 220), a * (1 - .55 * b))
    if b > 0:
        ctext(d, 720, '↓', inter(70, 'Bold'), (120, 255, 190), b)
        txt = 'Mariãna Lopês'; w = d.textlength(txt, font=f); x = (W - w) / 2; y = 820
        d.text((x, y), txt, font=f, fill=(255, 255, 255, int(255 * b)))
        for pre, ch in (('Mari', 'ã'), ('Mariãna Lop', 'ê')):
            x1 = x + d.textlength(pre, font=f); x2 = x + d.textlength(pre + ch, font=f)
            d.rounded_rectangle([x1, y + 140, x2, y + 152], 6, fill=(120, 255, 190, int(255 * b)))
    q = eb(P(s, t, 2, .6))
    if q > 0:
        for cx, num, lab, col, tc in ((W / 2 - 230, '15', 'mais pesado', (90, 110, 104), (230, 240, 236)), (W / 2 + 230, '45', 'favorável', (120, 255, 190), (4, 40, 26))):
            Rr = 120 * min(1, q) if num == '15' else 120 * min(1, max(0, eb((t - META[s]['pelo'] - .2) / .6)))
            if Rr <= 0: continue
            d.ellipse([cx - Rr, 1180 - Rr, cx + Rr, 1180 + Rr], fill=col + (255,))
            d.text((cx, 1176), num, font=inter(int(110 * Rr / 120) + 1, 'Black'), fill=tc + (255,), anchor='mm')
            d.text((cx, 1340), 'arcano · ' + lab, font=inter(38, 'SemiBold'), fill=(230, 255, 245, 255), anchor='mm')
        if t > META[s]['pelo'] + .2: ctext(d, 1150, '→', inter(80, 'Bold'), (255, 255, 255), 1)
    return im

SHOT = Image.open('/home/claude/repo/azovah-landing-page/site/assets/shot_inicio_m.webp').convert('RGB')
def phone(h):
    w = int(h * 780 / 1688); sc = SHOT.resize((w, h), Image.LANCZOS)
    pad = 16; ph = Image.new('RGBA', (w + 2 * pad, h + 2 * pad)); pd = ImageDraw.Draw(ph)
    pd.rounded_rectangle([0, 0, w + 2 * pad - 1, h + 2 * pad - 1], 56, fill=(12, 8, 10, 255))
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 42, fill=255)
    ph.paste(sc, (pad, pad), m); return ph
PHONE = phone(980)
FEATS = ['Mapa completo', 'Ciclos da vida', 'Ano pessoal', 'Compatibilidade', 'Calendário']
def s7(t):
    s = 's7'; c = META[s]['cues']; im = frame(t + 90, 's7'); d = AD(im, 'RGBA'); logo(d)
    p = eo(P(s, t, 0, .7))
    if p > 0:
        ph = PHONE.copy(); ph.putalpha(ph.getchannel('A').point(lambda q: int(q * p)))
        im.paste(ph, (70, int(330 + 80 * (1 - p))), ph)
    span = c[1][1] - c[1][0]
    for i, ft in enumerate(FEATS):
        st = META[s]['feat'][i] - .1
        q = eb((t - st) / .45)
        if q <= 0: continue
        x = 590 + 40 * (1 - min(1, q)); y = 420 + i * 175
        d.rounded_rectangle([x, y, x + 446, y + 130], 34, fill=(255, 255, 255, int(240 * min(1, q))))
        d.ellipse([x + 26, y + 41, x + 74, y + 89], fill=(214, 110, 20, int(255 * min(1, q))))
        d.text((x + 50, y + 65), '✓' if False else str(i + 1), font=inter(30, 'Black'), fill=(255, 255, 255, 255), anchor='mm')
        d.text((x + 92, y + 65), ft, font=inter(36, 'ExtraBold'), fill=(60, 24, 2, 255), anchor='lm')
    return im

def s5(t):
    s = 's5'; im = frame(t + 110, 's5'); d = AD(im, 'RGBA')
    p = eb(t / .7)
    if p > 0:
        sg = SEAL.rotate(-t * 18, resample=Image.BICUBIC)
        sz = int(420 * (0.7 + .3 * min(1, p))); sg = sg.resize((sz, sz))
        sg.putalpha(sg.getchannel('A').point(lambda q: int(q * min(1, p))))
        im.paste(sg, (int((W - sz) / 2), int(440 - sz / 2)), sg)
    a = eo(P(s, t, 0, .5)); ctext(d, 740, 'Descubra o que', lora(104), (255, 255, 255), a, 30 * (1 - a))
    b = eo(P(s, t, 0, .5) - .6); ctext(d, 876, 'o seu nome vibra.', lora(104, 'Bold', True), (255, 143, 182), b, 30 * (1 - b))
    cc = eo(P(s, t, 1, .5))
    if cc > 0:
        bw, bh = 800, 136; x, y = (W - bw) / 2, 1080 + 30 * (1 - cc)
        sc = 1 + .03 * math.sin(t * 6)
        d.rounded_rectangle([x - (sc - 1) * bw / 2, y, x + bw * sc - (sc - 1) * bw / 2, y + bh], 68, fill=(255, 255, 255, int(255 * cc)))
        ctext(d, y + 36, 'Calcule grátis · link na bio', inter(52, 'ExtraBold'), (142, 18, 72), cc)
        ctext(d, 1270, 'azovah.com/bio', inter(46, 'Bold'), (232, 176, 74), cc)
    return im

LOGO = Image.open('/home/claude/repo/azovah-landing-page/site/assets/logo_branca.webp').convert('RGBA')
def s8(t):
    # vinheta: fundo escuro limpo + logo com animação sutil (fade, leve zoom, brilho respirando, reflexo)
    im = Image.new('RGB', (W, H))
    g = Image.new('RGB', (W, H)); gd = ImageDraw.Draw(g)
    for y in range(0, H, 4):
        k = y / H; c = (int(34 - 18 * k), int(4 - 3 * k), int(14 - 8 * k)); gd.rectangle([0, y, W, y + 4], fill=c)
    im = g
    cx, cy = W / 2, H / 2
    a = eo((t - .3) / 1.3)
    br = .5 + .5 * math.sin((t - .3) * 1.6)
    gl = Image.new('RGBA', (W, H)); gld = ImageDraw.Draw(gl)
    for r in range(460, 0, -12): gld.ellipse([cx - r * 1.4, cy - r, cx + r * 1.4, cy + r], fill=(255, 150, 190, int(a * (26 + 14 * br) * (1 - r / 460) ** 2)))
    gl = gl.filter(ImageFilter.GaussianBlur(30)); im.paste(gl, (0, 0), gl)
    sc = 0.94 + 0.06 * eo((t - .3) / 3.5)
    w = int(780 * sc); h = int(w * LOGO.height / LOGO.width)
    lg = LOGO.resize((w, h), Image.LANCZOS)
    # reflexo passando, preso ao desenho da logo
    sh = (t - 1.9) / 1.1
    if 0 < sh < 1:
        band = Image.new('L', (w, h)); bd = ImageDraw.Draw(band)
        x = -200 + sh * (w + 400)
        bd.polygon([(x, 0), (x + 70, 0), (x - 60, h), (x - 130, h)], fill=170)
        band = band.filter(ImageFilter.GaussianBlur(10))
        alpha = lg.getchannel('A')
        from PIL import ImageChops
        m = ImageChops.multiply(band, alpha)
        lg = Image.composite(Image.new('RGBA', (w, h), (255, 236, 200, 255)), lg, m)
    lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a)))
    im.paste(lg, (int(cx - w / 2), int(cy - h / 2 - 10 * (1 - a))), lg)
    if t > VIN - .7:
        k = (t - (VIN - .7)) / .7; im = Image.blend(im, Image.new('RGB', (W, H)), min(1, k))
    return im

FN = dict(s8=s8, s1=s1, s2=s2, s3=s3, s4=s4, s6=s6, s7=s7, s5=s5)
def full(s, t):
    im = FN[s](t); caption(im, s, t); return im

XF = .35
def render(i):
    s = ORDER[i]; dur = META[s]['dur']; n = int(round(dur * FPS))
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    tmp = f'{OUT}/{s}.tmp.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    nx0 = full(nxt, 0).convert('RGB') if nxt else None
    for f in range(n):
        t = f / FPS; im = full(s, t).convert('RGB')
        if nxt and t > dur - XF: im = Image.blend(im, nx0, eo((t - (dur - XF)) / XF))
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); pr.wait(); os.replace(tmp, f'{OUT}/{s}.mp4'); print(s)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'tts': tts()
    elif cmd == 'still':
        ims = []
        for s in ORDER:
            c = META[s]['cues']; t = c[-1][1] - .1 if c else 2.4
            ims.append(full(s, t).convert('RGB').resize((270, 480)))
        m = Image.new('RGB', (270 * len(ims), 480)); [m.paste(x, (i * 270, 0)) for i, x in enumerate(ims)]; m.save(f'{OUT}/sheet.jpg', quality=85)
    else: render(int(cmd))
