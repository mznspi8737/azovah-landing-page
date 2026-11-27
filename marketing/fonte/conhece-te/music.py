# Trilha cinematográfica: pad etéreo + piano suave + pulso leve; cresce no final e toca com a logo
import numpy as np, wave
SR = 44100; D = 5.5 * 4 + 4.5 + 9 + 5.5 + 4.5 - 0.5 * 0  # 45.5
D = 50.0; N = int(D * SR); t = np.arange(N) / SR
rng = np.random.default_rng(2)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
out = np.zeros(N)
def add(sig, st):
    i = int(st * SR); j = min(N, i + len(sig))
    if i < N: out[i:j] += sig[:j - i]
# progressão: Dmaj9 – Bm7 – Gmaj7 – A(sus) (2 compassos de 4 s cada acorde)
prog = [[50, 57, 62, 66, 69, 76], [47, 54, 59, 62, 66, 73], [43, 50, 55, 59, 62, 71], [45, 52, 57, 61, 64, 69]]
CH = 4.0
pad = np.zeros(N)
for k in range(int(D / CH) + 1):
    st = k * CH; ch = prog[k % 4]; n = int((CH + 1.5) * SR); tt = np.arange(n) / SR
    env = np.minimum(1, tt / 1.6) * np.minimum(1, np.maximum(0, (CH + 1.5 - tt) / 1.5))
    s = sum(np.sin(2 * np.pi * midi(m) * tt * (1 + .0015 * j)) * (.5 if m > 60 else .8) for j, m in enumerate(ch[1:5]))
    s += .6 * np.sin(2 * np.pi * midi(ch[0] - 12) * tt)
    i = int(st * SR); j = min(N, i + n); pad[i:j] += (s * env)[:j - i] * .05
# piano: notas do acorde em arpejo lento
pia = np.zeros(N)
for k in range(int(D / CH) + 1):
    ch = prog[k % 4]; seq = [ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[5]]
    for q, m in enumerate(seq):
        st = k * CH + q * 1.0 + (.5 if q % 2 else 0) * 0
        n = int(3 * SR); tt = np.arange(n) / SR; f = midi(m)
        s = (np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt) + .12 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 1.8) * np.minimum(1, tt / .004)
        i = int(st * SR); j = min(N, i + n)
        if i < N: pia[i:j] += s[:j - i] * .07
# pulso suave (a partir da cena 5) e sininhos
pul = np.zeros(N)
for st in np.arange(22.0, 40.5, 0.5):
    n = int(.4 * SR); tt = np.arange(n) / SR
    s = .25 * np.sin(2 * np.pi * (50 + 40 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 10)
    i = int(st * SR); pul[i:i + n] += s[:max(0, min(n, N - i))]
shim = np.zeros(N)
for st in (0.6, 5.5, 11.0, 16.5, 22.0, 26.5, 35.5):
    for q, m in enumerate([86, 90, 93, 98]):
        n = int(2.5 * SR); tt = np.arange(n) / SR; s = .035 * np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * 2.5)
        i = int((st + q * .08) * SR); j = min(N, i + n); shim[i:j] += s[:j - i]
# final: riser + acorde aberto com a logo
VS = 41.0
n = int(2.5 * SR); tt = np.arange(n) / SR
riser = np.convolve(rng.standard_normal(n), np.ones(10) / 10, 'same') * (tt / 2.5) ** 2 * .12 + .05 * np.sin(2 * np.pi * (300 + 900 * (tt / 2.5) ** 2) * tt) * (tt / 2.5)
add(riser, VS - 2.5)
n = int((D - VS) * SR); tt = np.arange(n) / SR
fin = sum(.07 * np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * .5) for m in [38, 50, 57, 62, 66, 69, 74, 78])
fin += .3 * np.sin(2 * np.pi * (45 + 60 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 3)
add(fin, VS)
lvl = np.ones(N) * .75; lvl[t > VS - 2.5] = np.linspace(.75, 1.0, (t > VS - 2.5).sum())
mix = (pad + pia + pul + shim) * lvl + out
mix *= np.minimum(1, t / 1.2); mix[t > D - 1.4] *= np.linspace(1, 0, (t > D - 1.4).sum())
# leve estéreo: atraso no canal direito
L = mix; R = np.concatenate([np.zeros(300), mix[:-300]])
st = np.stack([L, R], 1); st = np.tanh(st * 1.2); st = st / np.abs(st).max() * .93
w = wave.open('/home/claude/film/out/trilha.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes()); w.close(); print('ok')
