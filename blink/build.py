# Monta blink/index.html: embute os dados (lemas e arcanos do sistema) e o polígono do selo.
import json,math,os
d=os.path.dirname(os.path.abspath(__file__))
s=open(os.path.join(d,'src.html'),encoding='utf-8').read()
pts=' '.join(f"{100+(97 if i%2==0 else 90)*math.cos(i*math.pi/36):.1f},{100+(97 if i%2==0 else 90)*math.sin(i*math.pi/36):.1f}" for i in range(72))
s=s.replace('POLY',pts).replace('/*BD*/',open(os.path.join(d,'dados.js'),encoding='utf-8').read())
open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(s)
print('ok',len(s))
