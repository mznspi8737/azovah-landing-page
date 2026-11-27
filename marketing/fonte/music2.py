# Trilha moderna (pop/deep house leve, 118 bpm, Am–F–C–G) + mix com a voz
import numpy as np, json, wave, subprocess, sys
O = '/home/claude/reels/v2'; M = json.load(open(O + '/meta.json')); SR = 44100
VOICE = sys.argv[1]
order = ['s1', 's2', 's3', 's4', 's6', 's7', 's5', 's8']
D = sum(M[s]['dur'] for s in order); N = int(D * SR); t = np.arange(N) / SR
VS = D - M['s8']['dur']
bpm = 118; beat = 60 / bpm; bar = 4 * beat
rng = np.random.default_rng(11)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def saw(f, n, nh=10):
    tt = np.arange(n) / SR; return sum(np.sin(2 * np.pi * f * h * tt + h) / h for h in range(1, nh + 1)) * .6
layers = {k: np.zeros(N) for k in ('kick', 'clap', 'hat', 'bass', 'chord', 'pluck', 'fx')}
def add(k, sig, st):
    i = int(st * SR)
    if i >= N or i + len(sig) <= 0: return
    j = min(N, i + len(sig)); layers[k][max(0, i):j] += sig[max(0, -i):j - i]
prog = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]  # Am7 Fmaj7 C G
roots = [45, 41, 48, 43]
nb = int(D / bar) + 2
for b in range(nb):
    st = b * bar; ch = prog[b % 4]; rt = roots[b % 4]
    # acordes (pad serrilhado filtrado)
    n = int(bar * SR); tt = np.arange(n) / SR
    pad = sum(saw(midi(x), n, 6) for x in ch) * np.minimum(1, tt / .08) * np.minimum(1, (bar - tt) / .1)
    add('chord', .05 * pad, st)
    for k in range(4):
        bt = st + k * beat
        # kick
        n = int(.35 * SR); tt = np.arange(n) / SR
        add('kick', .55 * np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9), bt)
        # hat no contratempo
        n = int(.09 * SR); h = rng.standard_normal(n); h = np.diff(h, prepend=0); h = np.diff(h, prepend=0)
        add('hat', .05 * h * np.exp(-np.arange(n) / SR * 45), bt + beat / 2)
        if k in (1, 3):
            n = int(.22 * SR); c = rng.standard_normal(n); c = np.diff(c, prepend=0)
            env = np.exp(-np.arange(n) / SR * 18)
            add('clap', .12 * c * env, bt)
        # baixo em colcheias
        for e in (0, .5):
            n = int(beat * .45 * SR); tt = np.arange(n) / SR
            add('bass', .2 * (np.sin(2 * np.pi * midi(rt - 12) * tt) + .25 * np.sin(4 * np.pi * midi(rt - 12) * tt)) * np.minimum(1, tt / .005) * np.exp(-tt * 3), bt + e * beat)
    # pluck em semicolcheias sincopadas (padrão moderno)
    pat = [0, 3, 6, 8, 10, 12, 14]
    notes = [ch[3] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24, ch[3] + 12, ch[2] + 12, ch[0] + 24]
    for p, nt in zip(pat, notes):
        n = int(.35 * SR); tt = np.arange(n) / SR
        add('pluck', .07 * saw(midi(nt), n, 5) * np.exp(-tt * 11) * np.minimum(1, tt / .002), st + p * beat / 4)
# sidechain (bombeio) em acordes, baixo e pluck
ph = (t % beat); sc = 1 - .65 * np.exp(-ph / .11)
for k in ('chord', 'bass', 'pluck'): layers[k] *= sc
# arranjo: intro só acordes+pluck, beat entra depois de 2 compassos
intro = np.clip(t / (2 * bar), 0, 1) ** 2
for k in ('kick', 'clap', 'hat', 'bass'): layers[k] *= (t > 2 * bar)
mus = sum(layers.values())
# vinheta: riser + impacto + cauda
rs = VS - 2.5; n = int(2.5 * SR); tt = np.arange(n) / SR
riser = np.convolve(rng.standard_normal(n), np.ones(6) / 6, 'same') * (tt / 2.5) ** 2 * .25
riser += .08 * np.sin(2 * np.pi * (200 + 1200 * (tt / 2.5) ** 2) * tt) * (tt / 2.5)
i = int(rs * SR); mus[i:i + n] += riser[:N - i]
mus[(t > VS - .25) & (t < VS)] *= .1   # respiro antes do impacto
n = int(M['s8']['dur'] * SR); tt = np.arange(n) / SR
hit = .6 * np.sin(2 * np.pi * (45 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 3)
hit += sum(.06 * saw(midi(x), n, 8) for x in [45, 57, 60, 64, 67, 72, 76]) * np.exp(-tt * .9)
for k2, x in enumerate([76, 79, 84, 88, 91]):
    m = int(2 * SR); t2 = np.arange(m) / SR
    s2 = .05 * np.sin(2 * np.pi * midi(x) * t2) * np.exp(-t2 * 3)
    a = int((VS + .4 + k2 * .1) * SR); hit[a - int(VS * SR): a - int(VS * SR) + m] += s2[:n - (a - int(VS * SR))]
i = int(VS * SR); mus[i:] = mus[i:] + .5 * hit[:N - i]
mus /= np.abs(mus).max()
# voz
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', VOICE, '-ac', '1', '-ar', str(SR), '/tmp/vozmix.wav'], check=True)
ww = wave.open('/tmp/vozmix.wav'); vr = np.frombuffer(ww.readframes(ww.getnframes()), '<i2').astype(np.float32) / 32768
v = np.zeros(N); i = int(.5 * SR); v[i:i + len(vr)] = vr[:N - i]; v = v / np.abs(v).max() * .9
env = np.convolve(np.abs(v), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
lvl = np.where(env > .02, .13, .22); lvl = np.convolve(lvl, np.ones(int(.4 * SR)) / int(.4 * SR), 'same')
ramp = (t >= VS - 2.5) & (t < VS); lvl[ramp] = np.linspace(lvl[ramp][0], .9, ramp.sum())
lvl[t >= VS] = .95
lvl *= np.minimum(1, t / 1.0)
out = v + mus * lvl
out[t > D - .7] *= np.linspace(1, 0, (t > D - .7).sum())
out = np.tanh(out * 1.1) / np.tanh(1.1); out = out / np.abs(out).max() * .95
w = wave.open(O + '/audio4.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes()); w.close()
open(O + '/l.txt', 'w').write(''.join(f"file '{O}/{s}.mp4'\n" for s in order)); print(D, VS)
