import numpy as np, json, wave
O='/home/claude/reels/v2'; M=json.load(open(O+'/meta.json')); SR=44100
order=['s1','s2','s3','s4','s6','s7','s5','s8']
D=sum(M[s]['dur'] for s in order); N=int(D*SR); t=np.arange(N)/SR
VS=D-M['s8']['dur']   # início da vinheta
bpm=96; beat=60/bpm; bar=4*beat
def midi(n): return 440*2**((n-69)/12)
prog=[[48,55,64,67,72],[43,55,62,67,71],[45,57,64,69,72],[41,57,60,65,69]]  # C G Am F
mus=np.zeros(N)
def add(sig, st):
    i=int(st*SR); j=min(N,i+len(sig)); 
    if i<N: mus[i:j]+=sig[:j-i]
def tone(f, dur, harm=((1,1),(2,.3),(3,.12)), att=.01, dec=None):
    n=int(dur*SR); tt=np.arange(n)/SR
    s=sum(a*np.sin(2*np.pi*f*h*tt) for h,a in harm)
    env=np.minimum(1,tt/att)
    env*=np.exp(-tt*dec) if dec else np.minimum(1,(dur-tt)/.4)
    return s*env
rng=np.random.default_rng(3)
nb=int(D/bar)+2
for b in range(nb):
    st=b*bar; ch=prog[b%4]
    # pad
    for n in ch[1:4]: add(.05*tone(midi(n),bar+.3,((1,1),(2,.15)),att=.6),st)
    # baixo
    add(.12*tone(midi(ch[0]-12),bar*.95,((1,1),(2,.25)),att=.02,dec=1.2),st)
    add(.08*tone(midi(ch[0]-12),bar*.45,((1,1),(2,.25)),att=.02,dec=2),st+2*beat)
    # arpejo de sino (colcheias)
    arp=[ch[1],ch[2],ch[3],ch[4],ch[3]+12 if b%2 else ch[4],ch[3],ch[2],ch[3]]
    for k,n in enumerate(arp):
        add(.05*tone(midi(n+12),1.2,((1,1),(2.01,.4),(3.98,.1)),att=.003,dec=4.5),st+k*beat/2)
    # shaker
    for k in range(8):
        n=int(.06*SR); sh=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*60)
        sh=np.diff(sh,prepend=0)
        add((.025 if k%2 else .015)*sh,st+k*beat/2)
    # kick suave
    for k in (0,2):
        n=int(.25*SR); tt=np.arange(n)/SR
        add(.18*np.sin(2*np.pi*(55+60*np.exp(-tt*30))*tt)*np.exp(-tt*14),st+k*beat)
# vinheta: riser + acorde final + cascata de sinos
n=int(2.2*SR); tt=np.arange(n)/SR
riser=rng.standard_normal(n); riser=np.convolve(riser,np.ones(8)/8,'same')*(tt/2.2)**2*.12
riser+=.05*np.sin(2*np.pi*(300+900*(tt/2.2)**2)*tt)*(tt/2.2)
add(riser,VS-2.2)
fin=sum(.06*tone(midi(n),M['s8']['dur'],((1,1),(2,.3),(3,.1)),att=.05,dec=.5) for n in [48,55,60,64,67,72,76])
add(fin,VS)
for k,n in enumerate([72,76,79,84,88,91,96]):
    add(.06*tone(midi(n),2.5,((1,1),(2.01,.4)),att=.003,dec=2.2),VS+.5+k*.09)
# corta a música normal no início da vinheta (fica só a vinheta)
cut=int(VS*SR); fadeN=int(.4*SR)
base=mus.copy()
# voz
vv=[]
for s in order:
    if s=='s8': vv.append(np.zeros(int(round(M[s]['dur']*24000)))); continue
    a=np.load(f'{O}/{s}.npy'); n=int(round(M[s]['dur']*24000)); vv.append(np.pad(a,(0,max(0,n-len(a))))[:n])
v24=np.concatenate(vv); v=np.interp(np.arange(N)/SR*24000, np.arange(len(v24)), v24); v=v/np.abs(v).max()*.9
# ducking + volume
env=np.convolve(np.abs(v),np.ones(int(.25*SR))/int(.25*SR),'same')
duck=np.where(env>.02,.22,.38)
duck=np.convolve(duck,np.ones(int(.3*SR))/int(.3*SR),'same')
lvl=duck.copy()
ramp=(t>=VS-2.2)&(t<VS); lvl[ramp]=np.linspace(lvl[ramp][0] if ramp.any() else .3,1.0,ramp.sum())
lvl[t>=VS]=1.0
lvl*=np.minimum(1,t/1.5)
out=v+mus/np.abs(mus).max()*lvl*.9
out[t>D-.8]*=np.linspace(1,0,(t>D-.8).sum())
out=out/np.abs(out).max()*.95
w=wave.open(O+'/audio2.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('<i2').tobytes());w.close()
open(O+'/l.txt','w').write(''.join(f"file '{O}/{s}.mp4'\n" for s in order)); print(D,VS)
