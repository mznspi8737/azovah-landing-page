# Trilha do vídeo longo: ato 1 tenso (pad grave + pulso de coração), ato 2 moderno (batida, pluck), final com a logo
import numpy as np, wave
SR = 44100; D = 79.5; VS = 70.5; A2 = 29.5; N = int(D * SR); t = np.arange(N) / SR
rng = np.random.default_rng(4)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def saw(f, n, nh=8):
    tt = np.arange(n) / SR; return sum(np.sin(2 * np.pi * f * h * tt + h) / h for h in range(1, nh + 1)) * .6
L = {k: np.zeros(N) for k in ('pad', 'heart', 'tick', 'kick', 'clap', 'hat', 'bass', 'pluck', 'fx')}
def add(k, s, st):
    i = int(st * SR)
    if i >= N: return
    j = min(N, i + len(s)); L[k][i:j] += s[:j - i]
# ato 1: pad grave em Ré menor, pulso de coração
for k in range(0, int(A2 / 6) + 1):
    st = k * 6; n = int(7.5 * SR); tt = np.arange(n) / SR; env = np.minimum(1, tt / 2) * np.minimum(1, (7.5 - tt) / 1.5)
    ch = [38, 50, 53, 57] if k % 2 == 0 else [34, 46, 53, 58]
    add('pad', sum(np.sin(2 * np.pi * midi(m) * tt * (1 + .002 * j)) for j, m in enumerate(ch)) * env * .05, st)
for st in np.arange(1.0, A2 - .5, 1.0):
    for dt, a in ((0, .5), (.22, .3)):
        n = int(.3 * SR); tt = np.arange(n) / SR; add('heart', a * np.sin(2 * np.pi * (45 + 25 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 12), st + dt)
for st in np.arange(.5, A2, .5):
    n = int(.03 * SR); add('tick', .05 * np.diff(rng.standard_normal(n), prepend=0) * np.exp(-np.arange(n) / SR * 200), st)
# impactos nas frases fortes
for st in (8.5, 9.0, 13.5, 15.5, 25.0):
    n = int(1.2 * SR); tt = np.arange(n) / SR; add('fx', .5 * np.sin(2 * np.pi * (40 + 70 * np.exp(-tt * 15)) * tt) * np.exp(-tt * 3), st)
# ato 2: batida moderna 118 bpm, Lá menor → Fá → Dó → Sol
bpm = 118; beat = 60 / bpm; bar = 4 * beat
prog = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]; roots = [45, 41, 48, 43]
b = 0; st = A2
while st < VS:
    ch = prog[b % 4]; rt = roots[b % 4]; n = int(bar * SR); tt = np.arange(n) / SR
    add('pad', sum(saw(midi(x), n, 5) for x in ch) * np.minimum(1, tt / .1) * np.minimum(1, (bar - tt) / .1) * .035, st)
    for k in range(4):
        bt = st + k * beat; n = int(.35 * SR); tt = np.arange(n) / SR
        add('kick', .6 * np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9), bt)
        n2 = int(.09 * SR); h = np.diff(np.diff(rng.standard_normal(n2), prepend=0), prepend=0); add('hat', .05 * h * np.exp(-np.arange(n2) / SR * 45), bt + beat / 2)
        if k in (1, 3): n3 = int(.22 * SR); add('clap', .12 * np.diff(rng.standard_normal(n3), prepend=0) * np.exp(-np.arange(n3) / SR * 18), bt)
        for e in (0, .5):
            n4 = int(beat * .45 * SR); t4 = np.arange(n4) / SR; add('bass', .22 * np.sin(2 * np.pi * midi(rt - 12) * t4) * np.exp(-t4 * 3), bt + e * beat)
    for p, nt in zip([0, 3, 6, 8, 10, 12, 14], [ch[3] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24, ch[3] + 12, ch[2] + 12, ch[0] + 24]):
        n = int(.35 * SR); tt = np.arange(n) / SR; add('pluck', .07 * saw(midi(nt), n, 5) * np.exp(-tt * 11), st + p * beat / 4)
    st += bar; b += 1
ph = t % beat; sc = np.where(t >= A2, 1 - .6 * np.exp(-ph / .11), 1)
for k in ('pad', 'bass', 'pluck'): L[k] *= np.where(t >= A2, sc, 1)
# entrada do ato 2 com riser
n = int(2 * SR); tt = np.arange(n) / SR; add('fx', np.convolve(rng.standard_normal(n), np.ones(8) / 8, 'same') * (tt / 2) ** 2 * .2, A2 - 2)
# final: riser + acorde aberto que soa com a logo
n = int(2.5 * SR); tt = np.arange(n) / SR
add('fx', np.convolve(rng.standard_normal(n), np.ones(8) / 8, 'same') * (tt / 2.5) ** 2 * .25 + .08 * np.sin(2 * np.pi * (200 + 1200 * (tt / 2.5) ** 2) * tt) * (tt / 2.5), VS - 2.5)
n = int((D - VS) * SR); tt = np.arange(n) / SR
fin = .6 * np.sin(2 * np.pi * (45 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 3) + sum(.06 * saw(midi(x), n, 8) for x in [45, 57, 60, 64, 67, 72, 76]) * np.exp(-tt * .35)
for k2, x in enumerate([76, 79, 84, 88, 91]):
    m = int(2 * SR); t2 = np.arange(m) / SR; a = int((.4 + k2 * .1) * SR); fin[a:a + m] += (.05 * np.sin(2 * np.pi * midi(x) * t2) * np.exp(-t2 * 3))[:max(0, n - a)]
add('fx', fin, VS)
mus = sum(L.values()); mus[(t > VS - .25) & (t < VS)] *= .15
lvl = np.ones(N); lvl[t >= VS] = 1.0
mus *= np.minimum(1, t / 1.0); mus[t > D - 3] *= np.linspace(1, 0, (t > D - 3).sum())
st2 = np.stack([mus, np.concatenate([np.zeros(250), mus[:-250]])], 1); st2 = np.tanh(st2 * 1.1); st2 = st2 / np.abs(st2).max() * .93
w = wave.open('/home/claude/vid2/out/trilha.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st2 * 32767).astype('<i2').tobytes()); w.close(); print('ok')
